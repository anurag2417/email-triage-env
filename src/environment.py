from typing import Dict, Any, Tuple, List, Optional
import uuid
from src.models import Observation, Action, ActionType, RewardSignal, TicketPriority
from src.knowledge_base import KnowledgeBase
from src.graders import EasyTaskGrader, MediumTaskGrader, HardTaskGrader


class CustomerSupportEnv:
    """OpenEnv-compliant customer support environment"""

    def __init__(self, task: str = "easy"):
        self.task = task
        self.kb = KnowledgeBase()
        self.reset()

        # Task-specific graders
        self.graders = {
            "easy": EasyTaskGrader(),
            "medium": MediumTaskGrader(),
            "hard": HardTaskGrader()
        }

    def reset(self) -> Observation:
        """Reset environment to initial state"""
        self.step_count = 0
        self.conversation_history = []
        self.kb_results = []
        self.trajectory = []
        self.done = False
        self.total_reward = 0.0

        # Load task-specific initial ticket
        self.current_ticket = self._load_ticket()

        return self._get_observation()

    def _load_ticket(self) -> Dict[str, Any]:
        """Load appropriate ticket based on task difficulty"""
        tickets = {
            "easy": {
                "id": f"TKT-{uuid.uuid4().hex[:8]}",
                "email": """Subject: Where is my order?

Hi, I ordered a laptop case on March 15th and it still hasn't arrived. 
Order #ORD-123456. Can you help me track it?
Thanks,
Sarah""",
                "priority": TicketPriority.MEDIUM,
                "category_hint": "shipping"
            },
            "medium": {
                "id": f"TKT-{uuid.uuid4().hex[:8]}",
                "email": """Subject: Request refund for defective product

Hello, I bought your premium headphones (Order ORD-789012) 2 weeks ago.
The right speaker doesn't work at all. I want a full refund of $89.99.
Please process this ASAP.
- Michael""",
                "priority": TicketPriority.HIGH,
                "category_hint": "refund"
            },
            "hard": {
                "id": f"TKT-{uuid.uuid4().hex[:8]}",
                "email": """Subject: Multiple issues - billing, technical, and refund

Dear Support,

I'm having several problems:
1. I was charged twice for my monthly subscription ($29.99 x2)
2. The mobile app keeps crashing after update
3. I want to cancel but the cancel button doesn't work

I've been a customer for 2 years and this is very frustrating.
Please resolve all issues. If not, I want a full refund for the last 3 months.

Order reference: ORD-456789
Account email: john.doe@email.com

Regards,
John Doe""",
                "priority": TicketPriority.CRITICAL,
                "category_hint": None
            }
        }

        return tickets.get(self.task, tickets["easy"])

    def _get_observation(self) -> Observation:
        """Build current observation from state"""
        # Determine available actions based on state
        available = [ActionType.SEARCH_KB, ActionType.DRAFT_REPLY]
        if self.step_count > 1:  # Allow refunds after some context
            available.append(ActionType.ISSUE_REFUND)
        if self.step_count > 3:  # Escalate only after attempts
            available.append(ActionType.ESCALATE)
        available.append(ActionType.REQUEST_INFO)  # Always available

        return Observation(
            ticket_id=self.current_ticket["id"],
            customer_email=self.current_ticket["email"],
            priority=self.current_ticket["priority"],
            category_hint=self.current_ticket.get("category_hint"),
            conversation_history=self.conversation_history.copy(),
            knowledge_base_results=self.kb_results.copy(),
            available_actions=available,
            step_count=self.step_count
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        """Execute action and return (observation, reward, done, info)"""
        if self.done:
            raise RuntimeError("Episode already done. Call reset() first.")

        self.step_count += 1
        reward_signal = RewardSignal(value=0.0, reason="", step_completion=0.0)

        # Execute action
        if action.type == ActionType.SEARCH_KB:
            query = action.params.get("query", "")
            self.kb_results = self.kb.search(query)
            reward_signal.value = 0.1
            reward_signal.reason = f"Searched KB for '{query}'"
            self.conversation_history.append(f"Agent searched: {query}")

        elif action.type == ActionType.ISSUE_REFUND:
            amount = action.params.get("amount", 0)
            order_id = action.params.get("order_id", "")
            reason = action.params.get("reason", "")

            # Validate refund
            if amount <= 1000 and order_id.startswith("ORD-"):
                reward_signal.value = 0.5
                reward_signal.reason = f"Refund of ${amount} processed for {order_id}"
                self.conversation_history.append(f"Agent issued refund: ${amount}")
            else:
                reward_signal.value = -0.2
                reward_signal.reason = "Invalid refund parameters"
                self.conversation_history.append(f"Agent attempted invalid refund")

        elif action.type == ActionType.DRAFT_REPLY:
            message = action.params.get("message", "")
            send = action.params.get("send_immediately", False)

            # Reward based on message quality
            if len(message) < 20:
                reward_signal.value = -0.1
                reward_signal.reason = "Reply too short"
            elif len(message) > 2000:
                reward_signal.value = -0.05
                reward_signal.reason = "Reply too long"
            else:
                reward_signal.value = 0.3
                reward_signal.reason = "Drafted reply"

            self.conversation_history.append(f"Agent drafted: {message[:100]}...")

            if send:
                self.done = True
                reward_signal.value += 0.4
                reward_signal.reason = "Sent final reply - episode complete"

        elif action.type == ActionType.ESCALATE:
            dept = action.params.get("department", "management")
            reward_signal.value = -0.1  # Slight penalty for escalation
            reward_signal.reason = f"Escalated to {dept}"
            self.conversation_history.append(f"Agent escalated to {dept}")
            self.done = True

        elif action.type == ActionType.REQUEST_INFO:
            question = action.params.get("question", "")
            reward_signal.value = 0.05
            reward_signal.reason = f"Requested info: {question[:50]}"
            self.conversation_history.append(f"Agent asked: {question}")

        # Progressive reward for steps (avoid loops)
        reward_signal.step_completion = min(self.step_count / 30, 0.3)
        reward_signal.value += reward_signal.step_completion * 0.1

        # Penalty for excessive steps
        if self.step_count >= 40:
            reward_signal.value -= 0.05

        # Terminal conditions
        if self.step_count >= 50:
            self.done = True
            reward_signal.value -= 0.2
            reward_signal.reason += " | Max steps reached"

        self.total_reward += reward_signal.value

        # Record trajectory for grading
        self.trajectory.append({
            "step": self.step_count,
            "action_type": action.type.value,
            "params": action.params,
            "reward": reward_signal.value,
            "observation": self._get_observation().dict()
        })

        return self._get_observation(), reward_signal.value, self.done, {
            "reward_detail": reward_signal.dict(),
            "total_reward": self.total_reward,
            "trajectory_length": len(self.trajectory)
        }

    def state(self) -> Dict[str, Any]:
        """Return current state dict for inspection"""
        return {
            "step": self.step_count,
            "done": self.done,
            "total_reward": self.total_reward,
            "ticket_id": self.current_ticket["id"],
            "history_length": len(self.conversation_history)
        }

    def grade(self) -> Dict[str, Any]:
        """Run task-specific grader on trajectory"""
        grader = self.graders.get(self.task)
        if not grader:
            return {"error": f"No grader for task {self.task}"}

        result = grader.grade(self.trajectory)
        return result.dict()