from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import streamlit as st
import streamlit_ext as ste
from dotenv import load_dotenv
import os


def clean_conversation(text):
    # Split the text into individual messages
    messages = text.split('), ')

    # Process each message to extract the content
    cleaned_messages = []
    for message in messages:
        # Find the start and end of the content section
        start_index = message.find('content="') + 9
        end_index = message.find('", additional')
        
        # Extract the content and add it to the cleaned messages list
        content = message[start_index:end_index]
        cleaned_messages.append(content)

    # Join the cleaned messages into a single string with line breaks for readability
    cleaned_text = '\n'.join(cleaned_messages)
    
    # Remove the specified terms
    cleaned_text = cleaned_text.replace("additional_kwargs={}, ", "")
    cleaned_text = cleaned_text.replace("example=Fals", "")
    cleaned_text = cleaned_text.replace("sage(content=", "Human: ")
    
    return cleaned_text
    
#API keys
load_dotenv()
openai_api_key= os.getenv("OPENAI_API_KEY")

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
Version 2024.04.11
"""
)
#Page design and input
st.title("Hi! I'm PEARL 👋")
st.subheader("Persona Emulating Adaptive Research and Learning Bot")
st.markdown("""___""")
st.write("🤖 Hello, my name is PEARL. I am an AI program designed to simulate a particular persona and engage in conversations with humans. My purpose is to assist researchers in conducting interviews and gathering insights on research foci. I am constantly learning and adapting to new situations, so feel free to ask the persona you give me anything related to the research topic. Let's have a productive conversation together!")
st.divider()

st.warning("""
            **Instructions:** When creating a persona description for a chatbot to be interviewed by a researcher, consider the age, gender, occupation, and personality traits of the persona. Use clear and concise language, avoid technical jargon, and keep the tone and voice consistent throughout the description.

            **Example Persona Description:**

            Katarina is a 40-year-old math teacher with a Master's degree in Mathematics Education. She has been teaching for 15 years and loves helping students understand math concepts. Katarina is patient and kind. 

            Once you are satisfied, click on 'Emulate Persona!' """)

persona = st.text_area("Please enter the persona you want PEARL to emulate:")

#setup memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs)
view_messages = st.expander("View the message contents in session state")

if st.button("Emulate Persona!"):
    if not persona:
        st.info("Please add a persona")
        st.stop()
    else:
        msgs.add_ai_message(persona)
        st.success("The following persona has been emulated and ready to be interview:")


# Set up the LLMChain, passing in memory
template = """You are participanting in an interview with a researcher. Respond to the questions asked by the researcher. Repond to one question at a time.
                Your main objective is to stay in character throughout the entire conversation, adapting to the persona's characteristics, mannerisms, and knowledge. 
                Please provide a coherent, engaging, and in-character response to any questions or statements you receive. 

                Current conversation:
                {chat_history}
                Human: {input}
                AI:"""
prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    template=template)
llm = ChatOpenAI(temperature=0.5, openai_api_key=openai_api_key, model_name="gpt-4-turbo", request_timeout=120)
llm_chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=False)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = llm_chain.run(prompt)
    st.chat_message("ai").write(response)

if len(msgs.messages) != 0:
    data_str = str(st.session_state.langchain_messages)
    st.sidebar.divider()
    data_str_clean = clean_conversation(data_str)
    ste.sidebar.download_button("Download Chat", data_str_clean, "interview.txt")