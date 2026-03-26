def load_emails():
    return [
        {
            "id": 1,
            "sender": "boss@company.com",
            "subject": "Urgent meeting",
            "body": "We need to discuss the deadline today.",
            "true_label": "urgent",
            "true_priority": "high"
        },
        {
            "id": 2,
            "sender": "promo@spam.com",
            "subject": "You won a prize!!!",
            "body": "Click here to claim reward",
            "true_label": "spam",
            "true_priority": "low"
        },
        {
            "id": 3,
            "sender": "colleague@company.com",
            "subject": "Code review",
            "body": "Please review my PR when free.",
            "true_label": "normal",
            "true_priority": "medium"
        }
    ]