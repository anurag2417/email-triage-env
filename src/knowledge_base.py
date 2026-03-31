from typing import List, Dict, Any
import re


class KnowledgeBase:
    """Simulated company knowledge base with fuzzy matching"""

    def __init__(self):
        self.articles = {
            "return_policy": {
                "title": "Return and Refund Policy",
                "content": """
                Customers can request refunds within 30 days of purchase. 
                Digital products are non-refundable after download.
                Physical products require return shipping at customer expense unless defective.
                Refunds take 5-7 business days to process.
                """,
                "keywords": ["refund", "return", "money back", "30 days"]
            },
            "shipping_delays": {
                "title": "Shipping Delay Resolution",
                "content": """
                Standard shipping takes 5-7 business days. 
                Expedited shipping takes 2-3 business days.
                If order hasn't arrived after 10 business days, customer qualifies for shipping fee refund.
                File claim with carrier after 14 days.
                """,
                "keywords": ["shipping", "delay", "arrive", "package", "delivery"]
            },
            "account_billing": {
                "title": "Account and Billing Issues",
                "content": """
                Subscription cancellations processed immediately.
                Prorated refunds for unused time available within 7 days of renewal.
                Payment method updates require verification via email link.
                """,
                "keywords": ["account", "billing", "subscription", "charged", "payment"]
            },
            "technical_issues": {
                "title": "Technical Support Protocol",
                "content": """
                For login issues: reset password via 'Forgot Password' link.
                For download failures: clear cache and try different browser.
                For corrupted files: request re-download link (valid 48 hours).
                Escalate to Tier 2 if issue persists after basic troubleshooting.
                """,
                "keywords": ["login", "download", "error", "bug", "technical", "crash"]
            }
        }

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Simple keyword-based search returning relevant articles"""
        query_lower = query.lower()
        results = []

        for article_id, article in self.articles.items():
            relevance = 0
            # Check keywords
            for keyword in article["keywords"]:
                if keyword in query_lower:
                    relevance += 2
            # Check content
            if any(word in article["content"].lower() for word in query_lower.split()):
                relevance += 1

            if relevance > 0:
                results.append({
                    "id": article_id,
                    "title": article["title"],
                    "snippet": article["content"][:200],
                    "relevance_score": min(relevance / 5, 1.0)
                })

        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:3]