import streamlit as st
from utils.visualization import render_chess_board_with_visualization


def render_about():
    """Render the about page"""
    st.title("About Grandmaster Ilya")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("""
        ## Chess Grandmaster AI Assistant
        
        Ilya is an AI chess analysis tool that combines deep chess knowledge with the 
        personality of a friendly but confident Russian grandmaster. 
        
        ### Capabilities:
        - Advanced position evaluation
        - Move strength analysis with visual indicators
        - Interactive move animations with arrows
        - Strategic and tactical analysis
        - Educational insights with concrete examples
        
        ### Technical Details:
        - Powered by OpenAI's advanced language models (GPT-4)
        - Uses python-chess for position validation
        - Interactive board visualization with move animations
        - FEN notation support
        - Move strength indicators:
          - Brilliant: Bright green arrow (game-changing moves)
          - Best: Dark green arrow (optimal moves)
          - Good: Blue arrow (strong moves)
          - Interesting: Orange arrow (creative moves)
          - Inaccurate: Yellow arrow (slight imprecisions)
          - Mistake: Red arrow (problematic moves)
        
        ### Why FEN Notation?
        FEN (Forsyth–Edwards Notation) is a standard notation for describing chess positions.
        It contains all the information needed to recreate a chess position:
        - Piece positions
        - Active color
        - Castling availability
        - En passant targets
        - Halfmove clock
        - Fullmove number
        
        ### Model Information:
        - GPT-4 Turbo: Best for detailed analysis and complex positions
        - GPT-4: High-quality analysis with consistent performance
        - GPT-3.5 Turbo: Quick analysis for simpler positions
        """)

    with col2:
        st.write("### Example Analysis Position:")
        html_content = render_chess_board_with_visualization(
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3",
            ["e4e5"],
            ["c6d4"],
            ["best"],
            ["good"],
        )
        st.components.v1.html(html_content, height=600)
        st.code(
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3",
            language="text",
        )
