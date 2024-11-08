import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.mention import mention
import openai
import warnings

from config.constants import MODELS
from utils.api_utils import validate_api_key
from components.home import render_home
from components.analysis import render_analysis
from components.about import render_about

warnings.filterwarnings("ignore")

# App configuration
st.set_page_config(page_title="Chess Grandmaster Ilya", page_icon="♟️", layout="wide")


# Sidebar configuration
def configure_sidebar():
    with st.sidebar:
        st.title("♟️ Chess Analysis")

        # API Key Form
        with st.form(key="api_key_form"):
            api_key = st.text_input("Enter OpenAI API token:", type="password")
            submit_button = st.form_submit_button("Set API Key")

            if submit_button:
                if not validate_api_key(api_key):
                    st.warning("Please enter a valid OpenAI API token!", icon="⚠️")
                else:
                    openai.api_key = api_key
                    st.success("API key set successfully!", icon="♟️")
                    st.session_state.api_key = api_key

        # Show current API key status
        if "api_key" in st.session_state and st.session_state.api_key:
            st.success("Ready to analyze chess positions!", icon="♟️")
        else:
            st.warning("Please set your OpenAI API token!", icon="⚠️")

        # Model selection
        model_option = st.selectbox(
            "Select GPT Model:",
            options=MODELS,
            help="Select the OpenAI model to use for analysis.",
        )

        # Option Menu
        selected_option = option_menu(
            "Dashboard",
            ["Home", "Analysis", "About"],
            icons=["house", "chess", "info-circle"],
            menu_icon="book",
            default_index=0,
            styles={
                "icon": {"color": "#dec960", "font-size": "20px"},
                "nav-link": {
                    "font-size": "17px",
                    "text-align": "left",
                    "margin": "5px",
                    "--hover-color": "#262730",
                },
                "nav-link-selected": {"background-color": "#262730"},
            },
        )

        return selected_option, model_option


def main():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Configure sidebar and get selected options
    selected_option, model_option = configure_sidebar()

    # Render appropriate page based on selection
    if selected_option == "Home":
        render_home()
    elif selected_option == "Analysis":
        if "api_key" in st.session_state:
            render_analysis(st.session_state.api_key, model_option)
        else:
            st.warning("Please set your OpenAI API key in the sidebar first!")
    else:  # About
        render_about()

    # Footer
    st.markdown("""
    ---
    Created with ♟️ by Bryan/AI republic/Generative AI Labs
    """)


# Custom CSS
def load_css():
    st.markdown(
        """
        <style>
            .css-1y4p8pa {
                padding-top: 0rem;
            }
            .stButton>button {
                width: 100%;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    load_css()
    main()

