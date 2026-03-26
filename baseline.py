import requests
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_URL = "http://127.0.0.1:8000"


def get_action_from_ai(email):
    if "urgent" in email["subject"].lower():
        return {
            "label": "urgent",
            "priority": "high",
            "reply": "I will handle this urgently."
        }

    if "prize" in email["subject"].lower() or "click" in email["body"].lower():
        return {
            "label": "spam",
            "priority": "low",
            "reply": "This looks like spam, ignoring it."
        }

    return {
        "label": "normal",
        "priority": "medium",
        "reply": "Sure, I will review it."
    }


def run():
    total_score = 0
    steps = 0

    email = requests.get(f"{BASE_URL}/reset").json()

    while True:
        action = get_action_from_ai(email)

        res = requests.post(f"{BASE_URL}/step", json=action).json()

        total_score += res["reward"]
        steps += 1

        if res["done"]:
            break

        email = res["observation"]

    print("Total Score:", round(total_score, 2))
    print("Steps:", steps)


if __name__ == "__main__":
    run()