import streamlit as st
import chess
import chess.svg
from utils.chess_utils import is_valid_fen, make_move
from utils.api_utils import initialize_chat_model, analyze_position
from config.constants import CHESS_PROMPT, DEFAULT_FEN, STRENGTH_COLORS
import re


def parse_move(move_text: str) -> tuple:
    """
    Parse a move text into its components.
    Returns (uci_move, strength, explanation, fen)
    """
    try:
        # Extract move in quotes
        move_match = re.search(r'"([a-h][1-8][a-h][1-8])"', move_text)
        if not move_match:
            return None, None, f"Could not parse move from: {move_text}", None

        # Extract strength in parentheses
        strength_match = re.search(r"\(([A-Z]+)\)", move_text)
        if not strength_match:
            return None, None, f"Could not parse strength from: {move_text}", None

        # Extract FEN if present
        fen_match = re.search(r"position (?:becomes|will be|is) (r[^\s]+)", move_text)

        uci_move = move_match.group(1)
        strength = strength_match.group(1)
        explanation = (
            move_text.split("-")[-1].strip() if "-" in move_text else move_text
        )
        fen = fen_match.group(1) if fen_match else None

        return uci_move, strength, explanation, fen

    except Exception as e:
        return None, None, f"Error parsing move: {str(e)}", None


def render_move_with_board(move_text: str, initial_fen: str, move_number: int):
    """Render a single move analysis with board"""
    uci_move, strength, explanation, fen = parse_move(move_text)

    if not uci_move:
        st.warning(explanation)
        return

    # If no FEN was provided in the analysis, calculate it
    if not fen:
        try:
            fen = make_move(initial_fen, uci_move)
        except Exception as e:
            st.error(f"Error calculating position: {str(e)}")
            return

    # Create columns for board and explanation
    col1, col2 = st.columns([1, 2])

    with col1:
        # Display board after move
        board_html = render_board(fen)
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

        # Clean up and display the explanation
        cleaned_explanation = explanation.split("FEN")[
            0
        ].strip()  # Remove FEN notation from display
        cleaned_explanation = re.sub(
            r"The (new )?position (becomes|will be|is) r[^\s]+", "", cleaned_explanation
        )
        st.write(cleaned_explanation)


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
                        st.error(f"Raw analysis text: {analysis}")


def render_board(fen: str, size: int = 300) -> str:
    """Render a chess board from FEN notation"""
    try:
        board = chess.Board(fen)
        return chess.svg.board(board=board, size=size)
    except Exception as e:
        st.error(f"Error rendering board: {str(e)}")
        return None

