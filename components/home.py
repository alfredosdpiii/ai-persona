import streamlit as st
from utils.visualization import render_chess_board_with_visualization
from config.constants import DEFAULT_FEN


def render_home():
    """Render the home page"""
    st.title("Welcome to Chess Grandmaster Ilya's Analysis Platform! ♟️")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("""
        ### Zdravstvuyte! (Hello!)
        
        I am Grandmaster Ilya, and I'm here to help you improve your chess game! With my 2800 ELO rating 
        and years of experience in professional chess, I can provide deep insights into any position.
        
        ### What I Offer:
        - Deep positional analysis with move strength ratings
        - Animated move suggestions with arrow indicators
        - Strategic recommendations
        - Russian chess terminology with translations
        
        ### How to Use:
        1. Go to the Analysis section
        2. Enter your position in FEN notation
        3. Get professional-level analysis with interactive visualizations
        """)

    with col2:
        st.write("### Example Starting Position:")
        # Show initial board
        html_content = render_chess_board_with_visualization(
            DEFAULT_FEN, [], [], [], []
        )
        st.components.v1.html(html_content, height=600)
