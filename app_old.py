#external libraries
import openai
import streamlit as st
import streamlit_ext as ste
import json

#langchain libraries
from langchain.chains import ConversationChain 
from langchain.chains.conversation.memory import  ConversationBufferMemory, ConversationSummaryMemory, CombinedMemory
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

#Python libraries
import os
from dotenv import load_dotenv, set_key, find_dotenv


#page setting
st.set_page_config(page_title="PEARL", page_icon="🤖", initial_sidebar_state="expanded")

hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
"""
#st.markdown(hide_st_style, unsafe_allow_html=True)

#functions 
def clear_chat():
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("Haman:" + st.session_state["past"][i])
        save.append("AI:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state ["generated"] 
    st.session_state["past"] = []
    st.session_state ["input"] = ""
    st.session_state["entity_memory"] = CombinedMemory(memories=[ConversationBufferMemory(memory_key="chat_history_lines", input_key="input"), ConversationSummaryMemory(llm=llm, input_key="input")])

def get_text():
    input_text = st.text_area("Human: ", st.session_state["input"], key="input", label_visibility='hidden')
    return input_text

def format_transcript(data):
    transcript = json.loads(data)
    result = ""
    for item in transcript:
        if len(item) == 2:
            question, answer = item
            answer = answer.replace("\\n", "\n")
            result += f"{question}\n{answer}\n"
        else:
            st.write(f"Skipping item due to irregular structure: {item}")
    return result

#Sidebar settings
st.sidebar.header("About")
st.sidebar.markdown(
"""
This application was created by [Soroush Sabbaghan](mailto:ssabbagh@ucalgary.ca) using [Streamlit](https://streamlit.io/), [LangChain](https://github.com/hwchase17/langchain), and [OpenAI API](https://openai.com/api/)'s 
the most updated model [gpt-3.5-turbo](https://platform.openai.com/docs/models/overview) for educational purposes. 
"""
)


st.sidebar.header("Copyright")
st.sidebar.markdown(
    """
- This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/)
"""
)

#API and Topic session states
if "generated" not in st.session_state:
    st.session_state ["generated"] = []
if "past" not in st.session_state:
    st. session_state ["past"] = []
if "input" not in st.session_state:
    st.session_state ["input"] = ""
if "stored_session" not in st.session_state:
    st. session_state["stored_session"] = []

#Page design and input
st.title("Hi! I'm PEARL 👋")
st.subheader("Persona Emulating Adaptive Research and Learning Bot")
st.markdown("""___""")
st.subheader("Step 1:")
st.subheader("Please input your OpenAI API key:")
url = "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key"
api = st.text_input("If you don't know your OpenAI API key click [here](%s)." % url, type="password", placeholder="Your API Key")
if st.button("Check key"):
    if api is not None:
    #Delete any files in tempDir
        try:
            # Send a test request to the OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt="What is the capital of France?",
                temperature=0.5
            )
            st.markdown("""---""")
            st.success("API key is valid!")
            st.warning("""
            **Instructions:** When creating a persona description for a chatbot to be interviewed by a researcher, consider the target audience and determine the age, gender, occupation, and personality traits of the persona. Use clear and concise language, avoid technical jargon, and keep the tone and voice consistent throughout the description.

            **Example Persona Description:**

            Katarina is a 40-year-old math teacher with a Master's degree in Mathematics Education. She has been teaching for 15 years and loves helping students understand math concepts. Katarina is patient and kind. 

            Once you are satisfied, click on Submit! """)
            st.markdown("""---""")
        except Exception as e:
            st.error("API key is invalid: {}".format(e))
#st.markdown("""---""") 

#API settings for langchain use
env_path = find_dotenv()
if env_path == "":
    with open(".env", "w") as env_file:
        env_file.write("# .env\n")
        env_path = ".env"

# Load .env file
load_dotenv(dotenv_path=env_path)
set_key(env_path, "OPENAI_API_KEY", api)
openai.api_key = os.environ["OPENAI_API_KEY"] 


#chatbot
#st.divider()
placeholder_1 = st.empty()
placeholder_2 = st.empty()
placeholder_1.subheader("Step 2:")
placeholder_2.subheader("Write the persona you'd like to interview in text-box 👇")


#Creating converational memory
llm = OpenAI(temperature=0.5, openai_api_key=api, model_name="gpt-3.5-turbo")
conv_memory = ConversationBufferMemory(memory_key = "chat_history_lines", input_key = "input")
summary_memory = ConversationSummaryMemory(llm=llm, input_key="input")
memory = CombinedMemory(memories = [conv_memory, summary_memory])

if 'entity_memory' not in st.session_state:
    st.session_state.entity_memory = memory

template = """The purse of the AI bot is to take a persona given by the human researcher at the start of the conversation so that the human researcher could interview it. 
The AI bot will begin the conversation by telling the human the persona and that it is ready to be interviewd. The AI bot will only answer one question at a time. 

Summary of conversation:
{history}
Current conversation:
{chat_history_lines}
Human: {input}
AI:"""

PROMPT = PromptTemplate(
input_variables=["history", "input", "chat_history_lines"], template=template)

#creat chian
conversation = ConversationChain(llm=llm, prompt = PROMPT, memory = st.session_state.entity_memory)
    
    
#variables 
user_input = get_text()


#Chat process
if st.button("Submit"):
    if user_input is not None:
        placeholder_1.empty()
        placeholder_2.empty()
        st.subheader("Ask your questions in the textbox above 👆")
        with st.spinner("Responding..."):
            
            #message_log.append({"role": "user", "content": user_input})
            output = conversation.run(input=user_input)
            #message_log.append({"role": "assistant", "content": output})
            #store the output
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            #store all outputs
            conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]

    with st.expander("conversation", expanded=True):
        for i in range(len(st.session_state['generated'])-1,-1,-1):
            st.info(st.session_state["past"][i]) 
            st.success (st. session_state["generated"][i], icon="🤖")
    st.markdown("""___""")
    if conversations:
        conversations_str = json.dumps(conversations)
        formatted_output = format_transcript(conversations_str)
        ste.download_button("Download Chat", formatted_output, "chat.txt")
            
    


