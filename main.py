import gradio
import openai
import os
import json

from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv('OPENAI.API_KEY')


messages = [{"role": "system", "content": "You are helpful and supportive"}]
cost = 0

def save_history(history):
    with open("saved_history.json", "w") as f:
        json.dump(history, f)

def load_history():
    try:
        with open("saved_history.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def add_text(history, text):
    global messages
    history = history+[(text,'')]
    messages = messages+[{"role":"user", "content":text}]
    save_history(history)
    return history, ""


def generate_response(history):
    global messages, cost
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages, temperature=0.2)
    response_msg=response.choices[0].message.content
    cost = cost + (response.usage['total_tokens'])*(0.002/1000)
    messages = messages + [{"role":"assistant", "content":response_msg}]

    for ch in response_msg:
        history[-1][1]+=ch
        yield history

    save_history(history)

def calc_cost():
    global cost

    return round(cost,3)

history_ = load_history()


with gradio.Blocks(theme=gradio.themes.Soft(primary_hue=gradio.themes.colors.violet, secondary_hue=gradio.themes.colors.violet)) as demo:
    gradio.Markdown("""
            <h1><center>AI ChatBot</center></h1>
        """)
    radio = gradio.Radio(value='gpt-3.5-turbo', choices=['gpt-3.5-turbo'] ,label='model')
    chatbot = gradio.Chatbot(value=[], elem_id="chatbot").style(height=650)

    with gradio.Row():
        with gradio.Column(scale=0.90):
            textbox = gradio.Textbox(show_label=False, placeholder="Ask me anything...").style(container=False)

        with gradio.Column(scale=0.10):
            cost_view = gradio.Textbox(label='usage in $',value=0)
    textbox.submit(add_text, [chatbot, textbox], [chatbot, textbox], queue=False).then(
            generate_response, inputs =[chatbot,],outputs = chatbot,).then(
            calc_cost, outputs=cost_view)


demo.queue()
demo.launch(share=True)

