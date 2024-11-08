import streamlit as st
import chess
import chess.svg
from utils.chess_utils import is_valid_fen, make_move
from utils.api_utils import initialize_chat_model, analyze_position
from config.constants import CHESS_PROMPT, DEFAULT_FEN, STRENGTH_COLORS
import re


def render_board(fen: str, size: int = 300) -> str:
    """Render a chess board from FEN notation"""
    try:
        board = chess.Board(fen)
        return chess.svg.board(board=board, size=size)
    except Exception as e:
        st.error(f"Error rendering board: {str(e)}")
        return None


def render_move_with_board(move_text: str, initial_fen: str, move_number: int):
    """Render a single move analysis with board"""
    try:
        # Extract move details using regex
        pattern = (
            r'"([a-h][1-8][a-h][1-8])" \(([A-Z]+)\) - (.+?)(?=\. The (new )?position|$)'
        )
        match = re.search(pattern, move_text)

        if not match:
            st.warning(f"Could not parse move: {move_text}")
            return

        uci_move, strength, explanation = match.groups()

        # Calculate resulting position
        resulting_position = make_move(initial_fen, uci_move)

        # Create columns for board and explanation
        col1, col2 = st.columns([1, 2])

        with col1:
            # Display board after move
            board_html = render_board(resulting_position)
            if board_html:
                st.components.v1.html(board_html, height=320)

        with col2:
            # Create colored header for move
            color = STRENGTH_COLORS.get(strength, "#808080")
            st.markdown(
                f"""
                <div style="padding: 10px; background-color: {color}; 
                           border-radius: 5px; margin-bottom: 10px;">
                    <span style="color: white; font-size: 18px; font-weight: bold;">
                        {move_number}. {uci_move} ({strength})
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write(explanation)

    except Exception as e:
        st.error(f"Error rendering move: {str(e)}")


def render_analysis(api_key: str, model_option: str):
    """Render the analysis page"""
    st.title("Grandmaster Ilya's Analysis Board")

    fen_input = st.text_input(
        "Enter position (FEN notation):",
        value=DEFAULT_FEN,
        help="Enter a valid FEN notation string",
    )

    if fen_input:
        if not is_valid_fen(fen_input):
            st.error("Invalid FEN notation. Please check your input.")
        else:
            # Show initial position
            st.subheader("Current Position")
            initial_board = render_board(fen_input, size=400)
            if initial_board:
                st.components.v1.html(initial_board, height=420)

            if st.button("Analyze Position", key="analyze"):
                with st.spinner("Grandmaster Ilya is analyzing the position..."):
                    try:
                        chat_model = initialize_chat_model(model_option, api_key)
                        analysis = analyze_position(chat_model, CHESS_PROMPT, fen_input)

                        # Split analysis into sections
                        sections = analysis.split("\n\n")

                        for section in sections:
                            if section.startswith("ASSESSMENT:"):
                                st.markdown("## Position Assessment")
                                assessment_text = section.replace(
                                    "ASSESSMENT:", ""
                                ).strip()
                                st.markdown(assessment_text)

                            elif section.startswith("WHITE MOVES:"):
                                st.markdown("## White's Ideas")
                                moves = [
                                    m
                                    for m in section.split("\n")[1:]
                                    if m.strip() and m[0].isdigit()
                                ]
                                for i, move in enumerate(moves, 1):
                                    render_move_with_board(move, fen_input, i)

                            elif section.startswith("BLACK MOVES:"):
                                st.markdown("## Black's Ideas")
                                moves = [
                                    m
                                    for m in section.split("\n")[1:]
                                    if m.strip() and m[0].isdigit()
                                ]
                                for i, move in enumerate(moves, 1):
                                    render_move_with_board(move, fen_input, i)

                            elif section.startswith("STRATEGIC THEMES:"):
                                st.markdown("## Strategic Themes")
                                themes = section.replace(
                                    "STRATEGIC THEMES:", ""
                                ).strip()
                                st.markdown(themes)

                            elif section.startswith("RUSSIAN CHESS WISDOM:"):
                                st.markdown("## Russian Chess Wisdom")
                                wisdom = section.replace(
                                    "RUSSIAN CHESS WISDOM:", ""
                                ).strip()
                                st.markdown(wisdom)

                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
                        st.error(f"Analysis text: {analysis}")


def render_previous_analyses(fen_input: str):
    """Render previous analyses section"""
    st.write("### Previous Analyses")
    if st.session_state.get("messages"):
        for idx, msg in enumerate(st.session_state.messages[-5:], 1):
            with st.expander(f"Analysis {len(st.session_state.messages)-5+idx}"):
                st.markdown(msg["content"])
    else:
        st.info("No previous analyses yet. Try analyzing a position!")

