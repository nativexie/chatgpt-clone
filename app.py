import os
import openai
import gradio as gr

# using local proxy by setting environment variable, if you need a proxy to connect openai api
# os.environ["http_proxy"] = "http://127.0.0.1:10809"
# os.environ["https_proxy"] = "http://127.0.0.1:10809"
# os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

# or using API to set proxy by environment variable(you need to set OPENAI_PROXY before run this app, recommanded)
# openai.proxy = os.getenv("OPENAI_PROXY") 

#if you have OpenAI API key as an environment variable, enable the below(recommanded)
#openai.api_key = os.getenv("OPENAI_API_KEY")

#if you have OpenAI API key as a string, enable the below
openai.api_key = "sk-XXX"


start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "

def openai_chat_create(msgs):

    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages= msgs)

    print()
    print(f'{response["usage"]["prompt_tokens"]} prompt tokens used.')
    print()
    return response['choices'][0]['message']['content']

def chatgpt_clone(input, history, msg_history):
    history = history or []
    msg_history = msg_history or [{"role": "system", "content": "You are a helpful assistant."}]
    msg_history.append({"role": "user", "content": input})

    msgs = msg_history
    print("msgs: %s" % msgs)
    print()

    output = openai_chat_create(msgs)
    print("chatbot reply: %s" % output)
    print()

    msg_history.append({"role": "assistant", "content": output})
    print("msg_history: %s" % msg_history)
    print()

    history.append((input, output))
    print("history: %s" % history)
    print()

    return history, history, msg_history, ""


block = gr.Blocks()


with block:
    gr.Markdown("""<h1><center>Build Yo'own ChatGPT with OpenAI API(ChatCompletion) & Gradio</center></h1>
    """)
    chatbot = gr.Chatbot()
    message = gr.Textbox(placeholder=prompt)
    state = gr.State()
    state_msg = gr.State()
    submit = gr.Button("SEND")
    submit.click(chatgpt_clone, inputs=[message, state, state_msg], outputs=[chatbot, state, state_msg, message])

block.launch(debug = True)
