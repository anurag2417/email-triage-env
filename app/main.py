from fastapi import FastAPI
from app.env import EmailEnv
from app.models import Action
from app.tasks import get_tasks

app = FastAPI()

env = EmailEnv()

@app.get("/reset")
def reset():
    return env.reset()

@app.get("/state")
def state():
    return env.state()

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/tasks")
def tasks():
    return get_tasks()

@app.get("/")
def home():
    return {"message": "Email Triage OpenEnv is running"}