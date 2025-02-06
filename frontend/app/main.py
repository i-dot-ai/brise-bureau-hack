from research_by_topic import research_by_topic
import iai_design_system as ds
import pandas as pd
import streamlit as st
from backend_interface import BackendClient
from unstructured.partition.docx import partition_docx
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.text import partition_text

import frontend.app.iai_design_system as ds
import os
from shared_utils.mermaid import process_map_to_mermaid
from shared_utils.render_mermaid import render_mermaid
from shared_utils.workers import process_chatbot_decision
from shared_utils.prompts import get_process_mapping_prompt
from shared_utils.chatbot import Summariser, Chatbot
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from unstructured.partition.pdf import partition_pdf
import time
import logging
import asyncio
from frontend.app.utils import init_session_state
from shared_utils.chatbot import Summariser
from shared_utils.mermaid import process_map_to_mermaid
from shared_utils.render_mermaid import render_mermaid
from shared_utils.workers import process_chatbot_decision

import streamlit as st

from PIL import Image

# Page icon
brise_icon = Image.open('frontend/app/brisebureau_logo.png')

# Set the page configuration as the first Streamlit command
st.set_page_config(
    page_title="BriseBureau",
    page_icon=brise_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state first
init_session_state()
ds.init()

# Then create backend client
backend_client = BackendClient()

IAI_PINK = "#C50878"

chatbot = Chatbot()
summariser = Summariser()


@st.cache_data
def themed_data():
    responses_df = pd.read_json(
        "frontend/example_data/detailed_synthetic_data_mapped_francais.json"
    )
    return responses_df


# Update chat history
def update_chat_history(chat_history):
    chat_history.markdown("<div id='chat-box' style='height: 400px; overflow-y: scroll; display: flex; flex-direction: column-reverse;'>"
                          + "".join([f"<div style='text-align: right;'><p style='background-color: #DCF8C6; display: inline-block; padding: 10px; border-radius: 10px;'>You: {chat['content'] if chat['role'] == 'user' else ''}</p></div>"
                                     f"<div style='text-align: left;'><p style='background-color: #F1F0F0; display: inline-block; padding: 10px; border-radius: 10px;'>Bot: {chat['content'] if chat['role'] == 'assistant' else ''}</p></div>"
                                     for chat in st.session_state.conversation])
                          + "</div>", unsafe_allow_html=True)


async def summarize_and_translate(text, num_docs):
    summary_response_en = await asyncio.to_thread(
        summariser.get_summary,
        user_input=text,
        number_of_documents=num_docs,
        language="en",
    )
    summary_response_fr = await asyncio.to_thread(
        summariser.get_summary,
        user_input=text,
        number_of_documents=num_docs,
        language="fr",
    )
    return summary_response_en, summary_response_fr


def process_map_upload():
    uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

    if st.session_state.file_summary is not None:
        st.write(st.session_state.file_summary)
    if st.session_state.file_summary is None:
        if not uploaded_files:
            st.error("Please upload a file")
            return

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".docx"):
                elements = partition_docx(file=uploaded_file)
            elif uploaded_file.name.endswith(".pdf"):
                elements = partition_pdf(file=uploaded_file)
            else:
                elements = partition_text(file=uploaded_file)

            text = "\n".join(
                [
                    element.text if hasattr(element, "text") else str(element)
                    for element in elements
                ]
            )
            st.session_state.uploaded_file_text = text

            with st.spinner("Processing..."):
                summary_response_en, summary_response_fr = asyncio.run(
                    summarize_and_translate(text, len(uploaded_files))
                )

            col1, col2 = st.columns(2)
            with col1:
                st.write("In English:")
                st.write(summary_response_en)
                st.session_state.file_summary = summary_response_en
                st.session_state.conversation.append({
                    "role": "user",
                    "content": "Summarise my response"
                })
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": summary_response_en
                })
                st.markdown(
                    """
                    <style>
                    div[data-testid="stBlock"] {
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 5px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.write("In French:")
                st.write(summary_response_fr)
                # st.session_state.file_summary = summary_response_fr
                st.markdown(
                    """
                    <style>
                    div[data-testid="stBlock"] {
                        background-color: #e0e0e0;
                        padding: 10px;
                        border-radius: 5px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )


def chatbot_page():

    # Start with an empty conversation (working)
    # Bring in the document summary (working)
    # Create the process map from the document (not working)
    # Start the chatbot with the process map prompting user with question - is this complete/
    # Then chat as normal (fix)

    # Display conversation history in a scrollable box
    chat_history = st.empty()
    chat_history.markdown("<div id='chat-box' style='height: 400px; overflow-y: scroll;'>"
                          + "".join([f"<div style='text-align: right;'><p style='background-color: #DCF8C6; display: inline-block; padding: 10px; border-radius: 10px;'>You: {chat['content'] if chat['role'] == 'user' else ''}</p></div>"
                                     f"<div style='text-align: left;'><p style='background-color: #F1F0F0; display: inline-block; padding: 10px; border-radius: 10px;'>Assistant: {chat['content'] if chat['role'] == 'assistant' else ''}</p></div>"
                                     for chat in st.session_state.conversation])
                          + "</div>", unsafe_allow_html=True)

    # User input
    user_input = st.text_input("You:", "")

    if st.session_state.file_summary is not None:
        base_map = chatbot.get_process_map_initial(st.session_state.file_summary)
        logging.info(base_map)
        st.session_state.process_map = base_map

    if st.button("Send"):
        with st.spinner("Generating response..."):
            if user_input:
                # Get bot response
                bot_response = chatbot.get_response(
                    user_input, st.session_state.process_map
                )
                messages, all_successful = process_chatbot_decision(
                    st.session_state.process_map, bot_response
                )
                # Update conversation history
                st.session_state.conversation.append({"role": "user", "content": user_input})
                for message in messages:
                    st.session_state.conversation.append({"role": "assistant", "content": message})
                chat_history.markdown(
                    "<div id='chat-box' style='height: 400px; overflow-y: scroll;'>"
                    + "".join(
                        [
                            f"<div style='text-align: right;'><p style='background-color: #DCF8C6; display: inline-block; padding: 10px; border-radius: 10px;'>You: {chat['user']}</p></div>"
                            f"<div style='text-align: left;'><p style='background-color: #F1F0F0; display: inline-block; padding: 10px; border-radius: 10px;'>Assistant: {chat['bot']}</p></div>"
                            for chat in st.session_state.conversation
                        ]
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )
    # Display conversation history
    # for chat in st.session_state.conversation:
    #     st.write(f"You: {chat['user']}")
    #     st.write(f"Bot: {chat['bot']}")

    # Display process map as Mermaid diagram if it exists
    if "process_map" in st.session_state:
        st.markdown("# Process Map")
        mermaid_diagram = process_map_to_mermaid(st.session_state.process_map)
        render_mermaid(mermaid_diagram)


#         st.markdown(f"""```mermaid
# {mermaid_diagram}
# ```""")
# Simulate response generation
# Get the response from the chatbot


# Update the conversation history in session state


def consultation_analysis():
    st.subheader(
        "Avez-vous des commentaires sur la construction d'une nouvelle centrale nucléaire à Normandie?"
    )

    # Get options for multiselect
    all_data = themed_data()

    # Display a summary
    st.subheader("Les trois principaux thèmes sont:")
    themes_by_counts_df = all_data["themes"].value_counts().reset_index()

    for row in themes_by_counts_df.head(3).iterrows():
        st.write(row[1]["themes"])

    total_responses = len(all_data["response_id"].unique())
    st.write(f"Nombre total de réponses à la consultation: {total_responses}")

    # Explore the data in detail
    st.subheader("Explorez les données")
    # Get options for multiselect
    age_groups_options = all_data["age_group"].unique()
    themes_options = all_data["themes"].unique()
    city_options = all_data["city"].unique()
    positions_options = all_data["position"].unique()

    # Create multiselect
    chosen_themes = st.multiselect(
        "Select themes", options=themes_options, default=themes_options
    )
    chosen_age_groups = st.multiselect(
        "Select age groups", options=age_groups_options, default=age_groups_options
    )
    chosen_cities = st.multiselect(
        "Select location", options=city_options, default=city_options
    )
    chosen_positions = st.multiselect(
        "Select position", options=positions_options, default=positions_options
    )

    # Filter the data
    df = all_data
    filtered_df = df[
        (df["themes"].isin(chosen_themes))
        & (df["age_group"].isin(chosen_age_groups))
        & (df["city"].isin(chosen_cities))
        & (df["age_group"].isin(chosen_age_groups))
        & (df["position"].isin(chosen_positions))
    ]

    # Display the data
    themes_by_counts = filtered_df["themes"].value_counts().sort_values(ascending=False)
    st.bar_chart(themes_by_counts, horizontal=True, color=IAI_PINK)
    st.dataframe(filtered_df)


# st.set_page_config(
#     page_title="Your Page Title",
#     page_icon=":smiley:",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# Main function to control app flow
def main():

    st.sidebar.image(brise_icon)
    st.sidebar.title("i.AI's BriseBureau")


    # Custom CSS for sidebar styling
    st.markdown(
        """
        <style>
        /* Main sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            padding: 2rem 1rem;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        }
        
        /* Remove default streamlit margins and padding */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0;
        }
        
        /* Hide the sidebar collapse arrow */
        button[kind="header"] {
            display: none !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            padding: 0 !important;
        }
        
        /* Style all buttons in sidebar */
        [data-testid="stSidebar"] button {
            width: 100%;
            height: auto !important;
            padding: 0.75rem 1rem !important;
            margin: 0 !important;
            background-color: transparent;
            border: none;
            border-radius: 0;
            color: #1f1f1f;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebar"] button:hover {
            background-color: #f8f9fa;
            color: #C50878;
        }
        
        [data-testid="stSidebar"] button.active {
            background-color: #fdf2f7;
            color: #C50878;
            font-weight: 500;
            border-left: 3px solid #C50878;
        }
        
        /* Logo positioning */
        .iai-logo {
            position: fixed;
            bottom: 2rem;
            left: 1rem;
            padding: 1rem;
            border-top: 1px solid #dee2e6;
            width: calc(100% - 2rem);
            text-align: center;
        }
        
        /* Hide default Streamlit branding */
        #MainMenu, footer {
            visibility: hidden;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session state for current page if not exists
    if "current_page" not in st.session_state:
        st.session_state.current_page = "File upload"

    # Sidebar content
    st.sidebar.markdown(
        '<h3 style="margin-bottom: 1rem;">Navigation</h3>', unsafe_allow_html=True
    )

    # Create navigation using Streamlit buttons
    if st.sidebar.button(
        "File upload",
        key="nav_file_upload",
        help="Upload and process documents",
        use_container_width=True,
    ):
        st.session_state.current_page = "File upload"
        st.rerun()

    if st.sidebar.button(
        "Chatbot",
        key="nav_chatbot",
        help="Interact with the AI assistant",
        use_container_width=True,
    ):
        st.session_state.current_page = "Chatbot"
        st.rerun()

    if st.sidebar.button(
        "Consultation analysis",
        key="nav_analysis",
        help="View consultation data analysis",
        use_container_width=True,
    ):
        st.session_state.current_page = "Consultation analysis"
        st.rerun()

    if st.sidebar.button(
        "Research by topic",
        key="nav_research",
        help="View research by topic",
        use_container_width=True,
    ):
        st.session_state.current_page = "Research by topic"
        st.rerun()

    # Page content based on selection
    if st.session_state.current_page == "File upload":
        st.title("Upload files to generate summary")
        process_map_upload()
    elif st.session_state.current_page == "Chatbot":
        st.title("A basic chatbot")
        chatbot_page()
    elif st.session_state.current_page == "Consultation analysis":
        st.title("Consultation analysis")
        consultation_analysis()
    elif st.session_state.current_page == "Research by topic":
        st.title("Research by topic")
        research_by_topic()


if __name__ == "__main__":
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    main()

# Optional i.AI logo at bottom of sidebar
st.sidebar.markdown(
    """
    <a class="iai-logo" href="https://ai.gov.uk">
        <img src="https://ai.gov.uk/img/i-dot-ai-Official-Logo.svg" alt="i.AI (opens in new tab)" height="40"/>
    </a>
""",
    unsafe_allow_html=True,
)
