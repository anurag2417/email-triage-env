from app.data import load_emails
from app.grader import compute_reward

class EmailEnv:
    def __init__(self):
        self.emails = load_emails()
        self.index = 0

    def reset(self):
        self.index = 0
        email = self.emails[self.index]
        return email

    def state(self):
        return self.emails[self.index]

    def step(self, action):
        email = self.emails[self.index]

        reward = compute_reward(email, action)

        self.index += 1
        done = self.index >= len(self.emails)

        next_obs = None if done else self.emails[self.index]

        return next_obs, reward, done, {}