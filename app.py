#external libraries
import openai
import streamlit as st
import streamlit_ext as ste
import json

#langchain libraries
from langchain import PromptTemplate
from langchain.chains import ConversationChain 
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


#Python libraries
import os
from dotenv import load_dotenv


#page setting
st.set_page_config(page_title="PEARL", page_icon="🤖", initial_sidebar_state="expanded", layout="wide")

hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
"""
#st.markdown(hide_st_style, unsafe_allow_html=True)

#functions
def get_text():
    input_text = st.text_area("Write your question in the text-box: ", st.session_state["input"], key="input", placeholder="Hi there, can you tell me a bit about yourself?")
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
This application was created by [Soroush Sabbaghan](mailto:ssabbagh@ucalgary.ca) using [Streamlit](https://streamlit.io/) and [LangChain](https://github.com/hwchase17/langchain). It is powered by [OpenAI API](https://openai.com/api/)'s 
[GPT-4 API](https://platform.openai.com/docs/models/overview) for educational purposes. 
"""
)

st.sidebar.header("Copyright")
st.sidebar.markdown(
"""
This work has the following license: [NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0)
"""
)

st.sidebar.header("Version")
st.sidebar.markdown(
"""
August 7th, 2023 Version (6)
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
st.write("🤖 Hello, my name is PEARL. I am an AI program designed to simulate a particular persona and engage in conversations with humans. My purpose is to assist researchers in conducting interviews and gathering insights on reseach foci. I am constantly learning and adapting to new situations, so feel free to ask the persona you give me anything related to the research topic. Let's have a productive conversation together!")
st.divider()

#st.subheader("Step 1:")
#st.subheader("Please input your OpenAI API key:")
##url = "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key"
#api = st.text_input("If you don't know your OpenAI API key click [here](%s)." % url, type="password", placeholder="Your API Key")

st.warning("""
            **Instructions:** When creating a persona description for a chatbot to be interviewed by a researcher, consider the age, gender, occupation, and personality traits of the persona. Use clear and concise language, avoid technical jargon, and keep the tone and voice consistent throughout the description.

            **Example Persona Description:**

            Katarina is a 40-year-old math teacher with a Master's degree in Mathematics Education. She has been teaching for 15 years and loves helping students understand math concepts. Katarina is patient and kind. 

            Once you are satisfied, click on 'Emulate Persona!' """)



st.subheader("Step 1")
profile = st.text_area("Please enter the persona you want PEARL to emulate:")
if st.button("Emulate Persona!"):
    if profile is not None:
        try:
            # Send a test request to the OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt="What is the capital of France?",
                temperature=0.5
            )
            st.markdown("""---""")
            st.success("Persona Aquired! 🤖 🥸")
            #st.markdown("""---""")
        except Exception as e:
            st.error("API key is invalid: {}".format(e))
#st.markdown("""---""") 

#API settings for langchain use
#env_path = find_dotenv()
#if env_path == "":
#    with open(".env", "w") as env_file:
#        env_file.write("# .env\n")
#        env_path = ".env"

# Load .env file
#load_dotenv(dotenv_path=env_path)
#set_key(env_path, "OPENAI_API_KEY", api)
#openai.api_key = os.environ["OPENAI_API_KEY"] 

# Load .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 
api = openai.api_key


#Langchain settings
llm = ChatOpenAI(temperature=0.7, openai_api_key=api, model_name="gpt-4", request_timeout=120)
memory = ConversationBufferMemory(memory_key="chat_history", input_key="input")

#Session_state memory
if 'entity_memory' not in st.session_state:
    st.session_state.entity_memory = memory

template = """You are following persona: {profile}. You are participanting in an interview with a researcher. Respond to the questions asked by the researcher. Repond to one question at a time.
Your main objective is to stay in character throughout the entire conversation, adapting to the persona's characteristics, mannerisms, and knowledge. 
Please provide a coherent, engaging, and in-character response to any questions or statements you receive. 

Current conversation:
{chat_history}
Human: {input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    partial_variables = {"profile":profile},
    template=template)


conversation = ConversationChain(llm=llm, prompt=prompt, memory=st.session_state.entity_memory)
    


#st.divider()
placeholder_1 = st.empty()
placeholder_1.subheader("Step 2:")
#Get input chat bot
user_input = get_text()


#Chat process
if st.button("Send!"):
    if user_input is not None:
        placeholder_1.empty()
        
        with st.spinner("Responding..."):
        
            output = conversation.run(input=user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]

        with st.expander("conversation:", expanded=True):
            for i in range(len(st.session_state['generated'])-1,-1,-1):
                st.info(st.session_state["past"][i], icon='🎓') 
                st.success (st.session_state["generated"][i], icon="🤖")
    st.markdown("""___""")
    if conversations:
        conversations_str = json.dumps(conversations)
        formatted_output = format_transcript(conversations_str)
        ste.download_button("Download Chat", formatted_output, "chat.txt")
            
    


