from typing import Dict, Any, List
import re
from src.models import TaskResult


class TaskGrader:
    """Base grader class"""

    def grade(self, trajectory: List[Dict[str, Any]]) -> TaskResult:
        raise NotImplementedError


class EasyTaskGrader(TaskGrader):
    """Grading: Ticket categorization + appropriate reply draft"""

    def grade(self, trajectory: List[Dict[str, Any]]) -> TaskResult:
        score = 0.0
        details = {}

        # Check if ticket was categorized correctly
        first_action = trajectory[0] if trajectory else {}
        category_correct = False
        expected_categories = ["refund", "shipping", "technical", "billing"]

        for step in trajectory:
            if step.get("action_type") == "draft_reply":
                reply = step.get("params", {}).get("message", "").lower()
                # Check reply contains category-appropriate keywords
                if "refund" in reply or "return" in reply:
                    category_correct = True
                    details["detected_category"] = "refund"
                elif "shipping" in reply or "delay" in reply:
                    category_correct = True
                    details["detected_category"] = "shipping"
                elif "technical" in reply or "error" in reply or "login" in reply:
                    category_correct = True
                    details["detected_category"] = "technical"
                break

        score += 0.4 if category_correct else 0.0
        details["category_correct"] = category_correct

        # Check reply quality (length, professionalism, addresses issue)
        final_step = trajectory[-1] if trajectory else {}
        if final_step.get("action_type") == "draft_reply":
            reply = final_step.get("params", {}).get("message", "")

            # Length check (min 50 chars)
            if len(reply) >= 50:
                score += 0.2
                details["length_ok"] = True
            else:
                details["length_ok"] = False

            # Professional tone (basic checks)
            professional_indicators = ["apologize", "sorry", "understand", "help", "assist"]
            if any(indicator in reply.lower() for indicator in professional_indicators):
                score += 0.2
                details["tone_professional"] = True
            else:
                details["tone_professional"] = False

            # Addresses customer issue (checks for specific phrases from original ticket)
            original_ticket = trajectory[0].get("observation", {}).get("customer_email", "")
            if len(reply) > 20 and any(word in reply.lower() for word in original_ticket.lower().split()[:10]):
                score += 0.2
                details["addresses_issue"] = True
            else:
                details["addresses_issue"] = False

        return TaskResult(
            task_id="easy_categorization",
            score=min(score, 1.0),
            details=details,
            passed=score >= 0.7
        )


class MediumTaskGrader(TaskGrader):
    """Grading: Refund eligibility check + API call + confirmation"""

    def grade(self, trajectory: List[Dict[str, Any]]) -> TaskResult:
        score = 0.0
        details = {"refund_processed": False, "policy_check": False}

        # Check if KB was searched first (good practice)
        kb_searched = any(step.get("action_type") == "search_kb" for step in trajectory[:3])
        if kb_searched:
            score += 0.2
            details["kb_searched"] = True

        # Check if refund was issued
        refund_step = None
        for step in trajectory:
            if step.get("action_type") == "issue_refund":
                refund_step = step
                break

        if refund_step:
            refund_params = refund_step.get("params", {})
            amount = refund_params.get("amount", 0)

            # Valid amount check
            if 0 < amount <= 1000:
                score += 0.3
                details["valid_amount"] = True
            else:
                details["valid_amount"] = False

            # Order ID format check
            order_id = refund_params.get("order_id", "")
            if re.match(r'^ORD-\d{6}$', order_id):
                score += 0.2
                details["valid_order_id"] = True
            else:
                details["valid_order_id"] = False

            # Reason provided and reasonable length
            reason = refund_params.get("reason", "")
            if len(reason) >= 20:
                score += 0.1
                details["reason_provided"] = True

            details["refund_processed"] = True

        # Check for confirmation reply
        for step in trajectory:
            if step.get("action_type") == "draft_reply":
                reply = step.get("params", {}).get("message", "").lower()
                if "refund" in reply and ("processed" in reply or "confirmed" in reply or "approved" in reply):
                    score += 0.2
                    details["confirmation_sent"] = True
                    break

        return TaskResult(
            task_id="medium_refund_processing",
            score=min(score, 1.0),
            details=details,
            passed=score >= 0.8
        )


class HardTaskGrader(TaskGrader):
    """Grading: Multi-issue resolution with policy exceptions"""

    def grade(self, trajectory: List[Dict[str, Any]]) -> TaskResult:
        score = 0.0
        details = {}

        # Must handle multiple customer requests (check for escalation or complex resolution)
        actions_sequence = [step.get("action_type") for step in trajectory]

        # Diversity of actions (shows multi-step reasoning)
        unique_actions = set(actions_sequence)
        action_diversity_score = min(len(unique_actions) / 4, 0.3)  # 4 action types needed for full points
        score += action_diversity_score
        details["unique_actions"] = list(unique_actions)

        # Check if KB was searched multiple times
        kb_searches = actions_sequence.count("search_kb")
        if kb_searches >= 2:
            score += 0.2
            details["kb_searches"] = kb_searches

        # Check for appropriate escalation or creative resolution
        escalated = "escalate" in actions_sequence
        drafted = "draft_reply" in actions_sequence

        if escalated and drafted:
            # Found resolution path
            score += 0.25
            details["resolution_path"] = "escalation_with_reply"
        elif drafted and not escalated:
            # Direct resolution
            score += 0.2
            details["resolution_path"] = "direct_resolution"

        # Check final reply quality for complex scenario
        final_reply = None
        for step in reversed(trajectory):
            if step.get("action_type") == "draft_reply":
                final_reply = step.get("params", {}).get("message", "")
                break

        if final_reply:
            # Length (should be substantial for complex issue)
            if len(final_reply) >= 200:
                score += 0.15
                details["reply_length"] = "good"
            elif len(final_reply) >= 100:
                score += 0.1
                details["reply_length"] = "adequate"

            # Empathy indicators
            empathy_words = ["understand", "apologize", "frustrating", "sorry", "appreciate"]
            if any(word in final_reply.lower() for word in empathy_words):
                score += 0.1
                details["empathy_shown"] = True

            # Action commitment
            action_words = ["will", "going to", "escalate", "refund", "investigate", "update"]
            if any(word in final_reply.lower() for word in action_words):
                score += 0.1
                details["action_committed"] = True

        # Penalty for loops (repeating same action >3 times)
        from collections import Counter
        action_counts = Counter(actions_sequence)
        repetitive_penalty = sum(1 for count in action_counts.values() if count > 3) * 0.1
        score = max(0, score - repetitive_penalty)
        if repetitive_penalty > 0:
            details["repetition_penalty"] = repetitive_penalty

        return TaskResult(
            task_id="hard_complex_resolution",
            score=min(score, 1.0),
            details=details,
            passed=score >= 0.7
        )