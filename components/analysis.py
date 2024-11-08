import streamlit as st
import chess
import chess.svg
from utils.chess_utils import is_valid_fen, make_move
from utils.api_utils import initialize_chat_model, analyze_position
from config.constants import CHESS_PROMPT, DEFAULT_FEN, STRENGTH_COLORS
import re


def parse_move(move_text: str) -> tuple:
    """
    Parse a move text into its components by working backwards.
    Returns (uci_move, strength, explanation, fen)
    """
    try:
        # If it starts with "Could not parse move from:", clean it up first
        if move_text.startswith("Could not parse move from:"):
            move_text = move_text.split(": ", 1)[1]

        # Split from the end
        # First get the FEN which is always at the end
        fen_pattern = r"(?:.*?)([rk][^\s]+(?:\s+[bw]\s+(?:K?Q?k?q?|-)\s+(?:-|[a-h][36])\s+\d+\s+\d+))(?:\s*|$)"
        fen_match = re.search(fen_pattern, move_text)
        if fen_match:
            fen = fen_match.group(1)
            # Remove the FEN part from move text
            move_text = move_text[: move_text.rfind(fen)].strip()
        else:
            fen = None

        # Now find the last occurrence of a move number and work from there
        move_pattern = r'(\d+)\.\s*(?:")?([a-h][1-8][a-h][1-8])(?:")?\s*\(([A-Z]+)\)'
        move_match = re.search(move_pattern, move_text)

        if not move_match:
            return None, None, f"Could not parse move format from: {move_text}", None

        move_num, uci_move, strength = move_match.groups()

        # Get the explanation - everything between strength and FEN
        explanation_text = move_text.split(f"({strength})")[-1]
        # Clean up the explanation
        explanation = re.sub(
            r"The position (?:becomes|will be|is|changes to).*$", "", explanation_text
        )
        explanation = explanation.strip(" -").strip()

        return uci_move, strength, explanation, fen

    except Exception as e:
        st.debug(f"Error parsing move text: {move_text}\nError: {str(e)}")
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
            st.error(f"Error calculating position for move {uci_move}: {str(e)}")
            return

    # Create columns for board and move info
    col1, col2 = st.columns([1, 2])

    with col1:
        # Display board after move
        board_html = render_board(fen)
        if board_html:
            st.components.v1.html(board_html, height=320)

    with col2:
        # Create colored header for move with custom styling
        color = STRENGTH_COLORS.get(strength, "#808080")
        st.markdown(
            f"""
            <div style="padding: 12px; 
                        background-color: {color}; 
                        border-radius: 6px; 
                        margin-bottom: 12px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <span style="color: white; 
                           font-size: 20px; 
                           font-weight: bold; 
                           font-family: 'Monaco', monospace;">
                    {move_number}. {uci_move} ({strength})
                </span>
            </div>
            <div style="font-size: 16px; margin-bottom: 16px;">
                {explanation}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Show FEN in an expander for verification
        with st.expander("Show FEN"):
            st.code(fen)


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

