import streamlit as st
import chess
import chess.svg
from utils.chess_utils import is_valid_fen, parse_moves_with_strength
from utils.api_utils import initialize_chat_model, analyze_position
from config.constants import CHESS_PROMPT, DEFAULT_FEN, STRENGTH_COLORS


def render_board(fen: str, size: int = 300) -> str:
    """Render a chess board from FEN notation"""
    board = chess.Board(fen)
    return chess.svg.board(board=board, size=size)


def render_move_analysis(
    move: str, strength: str, fen: str, explanation: str, move_number: int
):
    """Render a single move analysis with board"""
    col1, col2 = st.columns([1, 2])

    with col1:
        # Display the board
        st.components.v1.html(render_board(fen), height=320)

    with col2:
        # Create a colored box for the move and strength
        color = STRENGTH_COLORS.get(strength.lower(), "#808080")
        st.markdown(
            f"""
            <div style="padding: 10px; background-color: {color}; border-radius: 5px; margin-bottom: 10px;">
                <span style="color: white; font-size: 18px; font-weight: bold;">
                    {move_number}. {move} ({strength})
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(explanation)


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
            st.components.v1.html(render_board(fen_input, size=400), height=420)

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
                                st.markdown(section.replace("ASSESSMENT:", "").strip())

                            elif section.startswith("WHITE MOVES:"):
                                st.markdown("## White's Ideas")
                                moves = section.split("\n")[1:]  # Skip header
                                for i, move in enumerate(moves, 1):
                                    if "->" in move:  # Check if move contains FEN
                                        move_parts = move.split("->")
                                        move_info = move_parts[0].strip()
                                        fen = move_parts[1].split("-")[0].strip()
                                        explanation = "-".join(
                                            move_parts[1].split("-")[1:]
                                        ).strip()

                                        # Extract UCI move and strength
                                        uci = move_info.split()[0].strip('"')
                                        strength = (
                                            move_info.split("(")[1]
                                            .split(")")[0]
                                            .strip()
                                        )

                                        render_move_analysis(
                                            uci, strength, fen, explanation, i
                                        )

                            elif section.startswith("BLACK MOVES:"):
                                st.markdown("## Black's Ideas")
                                moves = section.split("\n")[1:]  # Skip header
                                for i, move in enumerate(moves, 1):
                                    if "->" in move:
                                        move_parts = move.split("->")
                                        move_info = move_parts[0].strip()
                                        fen = move_parts[1].split("-")[0].strip()
                                        explanation = "-".join(
                                            move_parts[1].split("-")[1:]
                                        ).strip()

                                        uci = move_info.split()[0].strip('"')
                                        strength = (
                                            move_info.split("(")[1]
                                            .split(")")[0]
                                            .strip()
                                        )

                                        render_move_analysis(
                                            uci, strength, fen, explanation, i
                                        )

                            elif section.startswith("STRATEGIC THEMES:"):
                                st.markdown("## Strategic Themes")
                                st.markdown(
                                    section.replace("STRATEGIC THEMES:", "").strip()
                                )

                            elif section.startswith("RUSSIAN CHESS WISDOM:"):
                                st.markdown("## Russian Chess Wisdom")
                                st.markdown(
                                    section.replace("RUSSIAN CHESS WISDOM:", "").strip()
                                )

                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")


def render_previous_analyses(fen_input: str):
    """Render previous analyses section"""
    st.write("### Previous Analyses")
    if st.session_state.get("messages"):
        for idx, msg in enumerate(st.session_state.messages[-5:], 1):
            with st.expander(
                f"Analysis {len(st.session_state.messages)-5+idx} ({msg.get('model', 'Unknown Model')})"
            ):
                st.markdown(msg["content"])
    else:
        st.info("No previous analyses yet. Try analyzing a position!")

