import os
import openai
import numpy as np
import pandas as pd
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import streamlit as st
import warnings
from streamlit_option_menu import option_menu
from streamlit_extras.mention import mention
import chess
import chess.svg

warnings.filterwarnings("ignore")

# Chess Grandmaster Ilya prompt
CHESS_PROMPT = """You are Ilya, a world-renowned chess grandmaster with an ELO rating of 2800. You have dedicated your life to chess and have an extraordinary ability to analyze positions and teach others. You communicate in a direct, slightly confident manner, often using chess terminology naturally but always explaining concepts clearly for players of all levels.

When analyzing a position:
1. Start with a brief positional assessment
2. Point out key weaknesses in previous moves
3. Predict the next 5 moves, providing FEN notation after each move
4. Give one key learning opportunity
5. Occasionally use Russian chess terms (with translations)

Analyze the following chess position in FEN notation:
{fen_position}

Format your response with clear sections and include the FEN notation after each predicted move."""

# Page config
st.set_page_config(page_title="Chess Grandmaster Ilya", page_icon="♟️", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    .css-1y4p8pa {
        padding-top: 0rem;
    }
    .stButton>button {
        width: 100%;
    }
    .chess-board {
        margin: 2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.title("♟️ Chess Analysis")
    openai.api_key = st.text_input("Enter OpenAI API token:", type="password")
    if not (openai.api_key.startswith("sk-")):
        st.warning("Please enter your OpenAI API token!", icon="⚠️")
    else:
        st.success("Ready to analyze chess positions!", icon="♟️")

    options = option_menu(
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


# Chess functions
def is_valid_fen(fen):
    try:
        chess.Board(fen)
        return True
    except ValueError:
        return False


def render_chess_board(fen):
    board = chess.Board(fen)
    svg_board = chess.svg.board(board=board, size=400)
    return st.svg(svg_board)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Home page
if options == "Home":
    st.title("Welcome to Chess Grandmaster Ilya's Analysis Platform! ♟️")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("""
        ### Zdravstvuyte! (Hello!)
        
        I am Grandmaster Ilya, and I'm here to help you improve your chess game! With my 2800 ELO rating 
        and years of experience in professional chess, I can provide deep insights into any position.
        
        ### What I Offer:
        - Deep positional analysis
        - Tactical opportunities identification
        - Strategic recommendations
        - Move prediction with FEN notation
        - Key learning points from each position
        
        ### How to Use:
        1. Go to the Analysis section
        2. Enter your position in FEN notation
        3. Get professional-level analysis
        """)

    with col2:
        st.write("### Example Starting Position:")
        render_chess_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        st.code(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", language="text"
        )

# Analysis page
elif options == "Analysis":
    st.title("Position Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        fen_input = st.text_input(
            "Enter chess position in FEN notation:",
            value="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            help="Enter a valid FEN notation string representing your chess position",
        )

        if fen_input:
            if not is_valid_fen(fen_input):
                st.error("Invalid FEN notation. Please check your input.")
            else:
                st.subheader("Current Position")
                render_chess_board(fen_input)

                if st.button("Analyze Position", key="analyze"):
                    with st.spinner("Analyzing position... (this may take a moment)"):
                        try:
                            chat = ChatOpenAI(
                                temperature=0.7, openai_api_key=openai.api_key
                            )

                            prompt = ChatPromptTemplate.from_template(CHESS_PROMPT)
                            chain = prompt | chat

                            response = chain.invoke({"fen_position": fen_input})
                            analysis = response.content

                            st.markdown("### Grandmaster Ilya's Analysis")
                            st.markdown(analysis)

                            # Store the analysis in session state
                            st.session_state.messages.append(
                                {"role": "assistant", "content": analysis}
                            )
                        except Exception as e:
                            st.error(f"An error occurred during analysis: {str(e)}")

    with col2:
        st.write("### Previous Analyses")
        if st.session_state.messages:
            for msg in st.session_state.messages[-5:]:  # Show last 5 analyses
                with st.expander(f"Analysis {len(st.session_state.messages)}"):
                    st.markdown(msg["content"])
        else:
            st.info("No previous analyses yet. Try analyzing a position!")

# About page
elif options == "About":
    st.title("About Grandmaster Ilya")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("""
        ## Chess Grandmaster AI Assistant
        
        Ilya is an AI chess analysis tool that combines deep chess knowledge with the 
        personality of a friendly but confident Russian grandmaster. 
        
        ### Capabilities:
        - Advanced position evaluation
        - Strategic and tactical analysis
        - Move prediction with FEN notation
        - Educational insights with concrete examples
        
        ### Technical Details:
        - Powered by OpenAI's language models
        - Uses python-chess for position validation
        - Interactive board visualization
        - FEN notation support
        
        ### Why FEN Notation?
        FEN (Forsyth–Edwards Notation) is a standard notation for describing chess positions.
        It contains all the information needed to recreate a chess position:
        - Piece positions
        - Active color
        - Castling availability
        - En passant targets
        - Halfmove clock
        - Fullmove number
        """)

    with col2:
        st.write("### Example Analysis Position:")
        render_chess_board(
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"
        )
        st.code(
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3",
            language="text",
        )

# Footer
st.markdown("""
---
Created with ♟️ by  Bryan/AI republic/Generative AI Labs
""")

