import os
import openai
import gradio as gr

# using local proxy by setting environment variable, if you need a proxy to connect openai api
#os.environ["http_proxy"] = "http://127.0.0.1:10809"
#os.environ["https_proxy"] = "http://127.0.0.1:10809"
#os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

# or using API to set proxy by environment variable(you need to set OPENAI_PROXY before run this app, recommanded)
#openai.proxy = os.getenv("OPENAI_PROXY") 

# if you have OpenAI API key as an environment variable, enable the below(recommanded)
#openai.api_key = os.getenv("OPENAI_API_KEY")

# if you have OpenAI API key as a string, enable the below
openai.api_key = "sk-XXX"

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "

# refine output format for code
def parse_text(text):
    lines = text.split("\n")
    for i,line in enumerate(lines):
        if "```" in line:
            items = line.split('`')
            if items[-1]:
                lines[i] = f'<pre><code class="{items[-1]}">'
            else:
                lines[i] = f'</code></pre>'
        else:
            if i>0:
                line = line.replace("<", "&lt;")
                line = line.replace(">", "&gt;")
                lines[i] = '<br/>'+line.replace(" ", "&nbsp;")
    return "".join(lines)

def chatgpt_stream(input, history, chat_counter, chatbot=[]):
    history = history or []
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": input})

    print(f"chat_counter - {chat_counter}")
    print()
    if chat_counter != 0 :
        messages=[{"role": "system", "content": "You are a helpful assistant."}]
        for data in chatbot:
          temp1 = {}
          temp1["role"] = "user" 
          temp1["content"] = data[0] 
          temp2 = {}
          temp2["role"] = "assistant" 
          temp2["content"] = data[1]
          messages.append(temp1)
          messages.append(temp2)
        temp3 = {}
        temp3["role"] = "user" 
        temp3["content"] = input
        messages.append(temp3)

    chat_counter+=1

    history.append(input)
 
    print("messages: %s" % messages)
    print()
    response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages= messages,
                    stream=True)

    token_counter = 0 
    partial_words = "" 
    counter=0
    for chunk in response:
        # print(chunk)
        #Skipping first chunk
        if counter == 0:
          counter+=1
          continue

        # check whether each "delta" is non-empty
        if chunk['choices'][0]["delta"]:
            partial_words = partial_words + chunk['choices'][0]["delta"]["content"]
            if token_counter == 0:
                history.append(" " + partial_words)
            else:
                history[-1] = parse_text(partial_words)
            chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2) ]  # convert to tuples of list
            token_counter+=1
            yield chat, history, "", chat_counter  


block = gr.Blocks()


with block:
    gr.Markdown("""<h1><center>Build Yo'own ChatGPT with OpenAI API(ChatCompletion) & Gradio</center></h1>
    """)
    chatbot = gr.Chatbot()
    message = gr.Textbox(placeholder=prompt)
    state = gr.State()
    submit = gr.Button("SEND")

    chat_counter = gr.Number(value=0, visible=False, precision=0)
    message.submit(chatgpt_stream, inputs=[message, state, chat_counter, chatbot], outputs=[chatbot, state, message, chat_counter])
    submit.click(chatgpt_stream, inputs=[message, state, chat_counter, chatbot], outputs=[chatbot, state, message, chat_counter])

block.queue().launch(debug = True)
