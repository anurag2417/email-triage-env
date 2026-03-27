import gradio as gr
import requests

BASE_URL = "http://127.0.0.1:7860"

current_email = {}


def load_email():
    global current_email
    res = requests.get(f"{BASE_URL}/reset")
    current_email = res.json()

    return (
        current_email["sender"],
        current_email["subject"],
        current_email["body"]
    )


def submit_action(label, priority, reply):
    global current_email

    payload = {
        "label": label,
        "priority": priority,
        "reply": reply
    }

    res = requests.post(f"{BASE_URL}/step", json=payload)
    data = res.json()

    reward = data["reward"]

    return f"Reward: {reward}"


with gr.Blocks() as demo:
    gr.Markdown("# 📧 Email Triage Simulator")

    sender = gr.Textbox(label="Sender", interactive=False)
    subject = gr.Textbox(label="Subject", interactive=False)
    body = gr.Textbox(label="Body", interactive=False)

    label = gr.Dropdown(["urgent", "normal", "spam"], label="Label")
    priority = gr.Dropdown(["high", "medium", "low"], label="Priority")
    reply = gr.Textbox(label="Reply")

    load_btn = gr.Button("Load Email")
    submit_btn = gr.Button("Submit")

    output = gr.Textbox(label="Result")

    load_btn.click(load_email, outputs=[sender, subject, body])
    submit_btn.click(submit_action, inputs=[label, priority, reply], outputs=output)

demo.launch(server_name="0.0.0.0", server_port=7860)