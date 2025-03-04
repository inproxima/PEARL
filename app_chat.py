#external libraries
from openai import OpenAI
import streamlit as st
import streamlit_ext as ste
import json
from streamlit_chat import message

#langchain libraries
from langchain import PromptTemplate
from langchain.chains import ConversationChain 
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatAnthropic
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek

#Python libraries
import os
from dotenv import load_dotenv
import time

# Page configuration with a modern theme
st.set_page_config(
    page_title="PEARL | AI Persona Emulator",
    page_icon="💡",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={
        'Get Help': 'mailto:ssabbagh@ucalgary.ca',
        'Report a bug': 'mailto:ssabbagh@ucalgary.ca',
        'About': "PEARL: Persona Emulating Adaptive Research and Learning Bot"
    }
)

# Custom CSS for a more professional look
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        padding: 20px;
    }
    
    /* Header styling */
    h1 {
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    h2, h3 {
        color: #1E3A8A;
        font-weight: 600;
    }
    
    /* Card-like containers */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Chat container styling */
    .chat-container {
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2563EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #E5E7EB;
    }
    
    /* Selectbox styling */
    .stSelectbox>div>div>div {
        background-color: white;
        border-radius: 5px;
        border: 1px solid #E5E7EB;
    }
    
    /* Chat message styling */
    .user-avatar {
        background-color: #1E3A8A;
    }
    
    .assistant-avatar {
        background-color: #10B981;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Status indicator styling */
    .status-indicator {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    /* Divider styling */
    hr {
        margin: 1.5rem 0;
        border-color: #E5E7EB;
    }
    
    /* Logo styling */
    .logo-text {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    /* Model selector styling */
    .model-selector {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Persona input styling */
    .persona-input {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Functions
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

# Load environment variables
load_dotenv()
client_openai = OpenAI()
client_openai.api_key = os.getenv("OPENAI_API_KEY")
api_openai = client_openai.api_key

# Session state initialization
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'entity_memory' not in st.session_state:
    st.session_state.entity_memory = ConversationBufferMemory(memory_key="chat_history", input_key="input")

# Sidebar with app information
with st.sidebar:
    st.image("https://img.icons8.com/?size=100&id=b2rw9AoJdaQb&format=png&color=000000", width=80)
    with st.expander("About PEARL"):
        st.markdown("<h2>About PEARL</h2>", unsafe_allow_html=True)
        st.markdown(
            """
            PEARL (Persona Emulating Adaptive Research and Learning Bot) is designed to simulate specific personas for research interviews.
            
            This application helps researchers conduct interviews with AI-simulated personas to gather insights on various research topics.
            """
        )
    
    st.divider()
    
    st.markdown("<h3>Instructions</h3>", unsafe_allow_html=True)
    with st.expander("View detailed instructions"):
        st.markdown(
            """
            **Creating an Effective Persona Description:**
            
            When creating a persona description for PEARL to emulate, consider including:
            
            - **Demographics**: Age, gender, occupation, education level
            - **Background**: Relevant life experiences, cultural context
            - **Personality**: Key character traits, communication style
            - **Knowledge Areas**: Expertise, interests, and limitations
            
            **Example Persona Description:**
            
            *"Katarina is a 40-year-old math teacher with a Master's degree in Mathematics Education. She has been teaching for 15 years at a public high school in a suburban area. She loves helping students understand complex math concepts and is particularly passionate about making math accessible to girls. Katarina is patient, methodical, and has a dry sense of humor. She struggles with work-life balance and is considering pursuing administration roles."*
            
            **Tips for Effective Interviews:**
            
            - Start with open-ended questions
            - Follow up on interesting responses
            - Avoid leading questions
            - Be respectful of the persona's perspective
            - Take notes on key insights
            """
        )
    st.markdown("<h3>How to use</h3>", unsafe_allow_html=True)
    with st.expander("View usage instructions"):
        st.markdown(
            """
            1. Select an AI model
            2. Create a detailed persona description
            3. Click "Emulate Persona"
            4. Start chatting with your AI persona
            5. Download the conversation when finished
            """
        )
    
    st.divider()

    st.markdown("""
    <div style="text-align: center; margin-top: 1px; padding: 1px; color: #6B7280; font-size: 0.8rem;">
        <p>PEARL v8.0 | Created by Soroush Sabbaghan | © 2025</p>
        <p>Licensed under a Creative Commons Attribution 4.0 International License</p>
    </div>
    """, unsafe_allow_html=True)



# Main content
# Header with logo and title
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://img.icons8.com/?size=100&id=b2rw9AoJdaQb&format=png&color=000000", width=80)
with col2:
    st.markdown("<h1 class='logo-text'>PEARL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; margin-top: -10px;'>Persona Emulating Adaptive Research and Learning Bot</p>", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #EFF6FF; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-bottom: 30px;">
    <p style="margin: 0; color: #1E3A8A;">
        <strong>Welcome to PEARL!</strong> This AI system simulates specific personas for research interviews. 
        Create a detailed persona description, and PEARL will engage in conversation as that character, 
        helping you gather valuable research insights.
    </p>
</div>
""", unsafe_allow_html=True)

# Model selection with visual indicators
st.markdown("### 🤖 Select AI Model")
st.markdown("Choose the AI model that will power your persona simulation:")

model_col1, model_col2 = st.columns(2)
with model_col1:
    llm_model = st.selectbox(
        "AI Model",
        ["GPT 4o", "Sonnet 3.7", "Gemini Flash", "DeepSeek Chat"],
        label_visibility="collapsed"
    )

with model_col2:
    if llm_model == "GPT 4o":
        st.markdown("**OpenAI's GPT-4o**: Advanced reasoning and knowledge")
    elif llm_model == "Sonnet 3.7":
        st.markdown("**Anthropic's Claude 3.7 Sonnet**: Nuanced understanding and responses")
    elif llm_model == "Gemini Flash":
        st.markdown("**Google's Gemini Flash**: Fast, efficient responses")
    elif llm_model == "DeepSeek Chat":
        st.markdown("**DeepSeek Chat**: Specialized knowledge model")

# Initialize the selected model
with st.spinner(f"Initializing {llm_model}..."):
    if llm_model == "GPT 4o":
        llm = ChatOpenAI(api_key=api_openai, model_name="gpt-4o")
    elif llm_model == "Sonnet 3.7":
        try:
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), model_name="claude-3-7-sonnet-20250219")
        except (ImportError, AttributeError):
            llm = ChatAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), model_name="claude-3-7-sonnet-20250219", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif llm_model == "Gemini Flash":
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
        except Exception as e:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                safety_settings={"HARASSMENT": "block_none"},
            )
    elif llm_model == "DeepSeek Chat":
        llm = ChatDeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), model_name="deepseek-chat")
    else:
        # Default fallback in case none of the conditions match
        st.warning(f"Model {llm_model} not recognized. Using GPT-4o as fallback.")
        llm = ChatOpenAI(api_key=api_openai, model_name="gpt-4o")
st.markdown("</div>", unsafe_allow_html=True)

# Persona creation section
st.markdown("<div class='model-selector' style='background-color: #F0F8FF; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.markdown("### 👤 Create Your Persona")

st.markdown("""
<div style="background-color: #FFFBEB; padding: 15px; border-radius: 5px; border-left: 5px solid #F59E0B; margin-bottom: 15px;">
    <p style="margin: 0; font-size: 0.9rem;">
        <strong>📝 Persona Creation Tips:</strong> Include age, gender, occupation, education, personality traits, and relevant background information. The more detailed your description, the more realistic the simulation will be.
    </p>
</div>
""", unsafe_allow_html=True)

# Example persona in a collapsible section
with st.expander("See example persona"):
    st.markdown("""
    **Example:**
    
    Katarina is a 40-year-old math teacher with a Master's degree in Mathematics Education from the University of Michigan. She has been teaching high school algebra and calculus for 15 years at Lincoln High School in a suburban district. Katarina is patient, methodical, and passionate about making math accessible to all students. She grew up in a middle-class family in Ohio, where her father was an engineer and her mother a librarian. Katarina is married with two children, ages 10 and 13. In her free time, she enjoys solving puzzles, gardening, and volunteering as a math tutor at the local community center. She's concerned about the increasing reliance on technology in education and believes in balancing digital tools with traditional teaching methods.
    """)

profile = st.text_area(
    "Enter your persona description:",
    height=150,
    placeholder="Describe the persona you want PEARL to emulate in detail...",
    label_visibility="collapsed"
)

emulate_col1, emulate_col2 = st.columns([1, 3])
with emulate_col1:
    emulate_button = st.button("✨ Emulate Persona", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if emulate_button:
    with st.spinner("Initializing persona..."):
        # Add a small delay for visual effect
        time.sleep(0.5)
        
        # Success message with animation
        success_placeholder = st.empty()
        success_placeholder.markdown(f"""
        <div style="background-color: #ECFDF5; padding: 15px; border-radius: 10px; border-left: 5px solid #10B981; margin-bottom: 20px; animation: fadeIn 0.5s;">
            <p style="margin: 0; color: #10B981;">
                <strong>✅ Persona activated!</strong> PEARL will now emulate: {profile}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Set session state
        if 'persona_set' not in st.session_state:
            st.session_state.persona_set = True
        
        # Clear previous conversation
        st.session_state.entity_memory.clear()
        st.session_state["generated"] = []
        st.session_state["past"] = []
        st.session_state.messages = []

# Chat interface
#st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
st.markdown("### 💬 Interview Your Persona")

# Template for conversation
template = """You are following persona: {profile}. Engage in conversations with a researcher. 
Your main objective is to stay in character throughout the entire conversation, adapting to the persona's characteristics, mannerisms, and knowledge.
Please provide a coherent, engaging, and in-character response to any questions or statements you receive. You are being interviewed by a researcher, so you should answer the questions in a way that is helpful to the researcher.

Current conversation:
{chat_history}
Human: {input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    partial_variables={"profile": profile},
    template=template
)

# Create conversation chain
conversation = ConversationChain(
    llm=llm, 
    prompt=prompt, 
    memory=st.session_state.entity_memory,
)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🧠"):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask a question to your persona...", key="chat_input")

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Generate response with status indicator
    with st.status("Generating response...", expanded=True) as status:
        st.write(f"The AI is formulating a response as your persona...")
        
        # Progress indicator
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate thinking process
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        # Generate actual response
        with st.spinner():
            output = conversation.run(input=user_input)
            
        # Update status
        status.update(label="Response ready!", state="complete")
    
    # Display assistant response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(output)
    
    # Update history
    st.session_state.messages.append({"role": "assistant", "content": output})
    st.session_state['past'].append(user_input)
    st.session_state['generated'].append(output)
    
    # Auto-scroll to bottom (using JavaScript)
    #st.markdown("""
   # <script>
        #function scrollToBottom() {
            #const mainContainer = document.querySelector('.main');
            #mainContainer.scrollTop = mainContainer.scrollHeight;
        #}
        #scrollToBottom();
    #</script>
    #""", unsafe_allow_html=True)
#st.markdown("</div>", unsafe_allow_html=True)

# Download chat option
if st.session_state.messages and len(st.session_state.messages) > 1:
    #st.markdown("<div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>", unsafe_allow_html=True)
    #st.markdown("### 📥 Save Your Interview")
    #st.markdown("Download the complete conversation transcript for your research records:")
    
    conversations = [(st.session_state['past'][i], st.session_state["generated"][i]) for i in range(len(st.session_state['generated']))]
    if conversations:
        conversations_str = json.dumps(conversations)
        formatted_output = format_transcript(conversations_str)
        
        # Move download button to sidebar
        with st.sidebar:
            st.divider()
            st.markdown("<h3>Download Interview</h3>", unsafe_allow_html=True)
            ste.download_button(
                "📄 Download Transcript", 
                formatted_output, 
                "pearl_interview.txt"
            )
            st.markdown(f"<small>Interview contains {len(conversations)} exchanges</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer

            
    


