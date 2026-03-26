def evaluate_reply(reply, email):
    if not reply:
        return 0

    score = 0

    keywords = []

    if email["true_label"] == "urgent":
        keywords = ["meeting", "today", "urgent", "deadline"]
    elif email["true_label"] == "spam":
        keywords = ["ignore", "spam", "unsubscribe"]
    else:
        keywords = ["review", "thanks", "sure", "okay"]

    match_count = 0
    for word in keywords:
        if word in reply.lower():
            match_count += 1

    score += min(match_count / len(keywords), 1.0)

    if len(reply) > 20:
        score += 0.2

    return min(score, 1.0)


def compute_reward(email, action):
    score = 0

    if action.label == email["true_label"]:
        score += 0.4

    if action.priority == email["true_priority"]:
        score += 0.3

    reply_score = evaluate_reply(action.reply, email)
    score += 0.3 * reply_score

    return round(score, 2)