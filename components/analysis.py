import streamlit as st
from utils.chess_utils import is_valid_fen, parse_moves_with_strength
from utils.api_utils import initialize_chat_model, analyze_position
from utils.visualization import render_chess_board_with_visualization
from config.constants import CHESS_PROMPT, DEFAULT_FEN


def render_analysis(api_key: str, model_option: str):
    """Render the analysis page"""
    st.title("Position Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        # FEN input with immediate board update
        fen_input = st.text_input(
            "Enter chess position in FEN notation:",
            value=DEFAULT_FEN,
            help="Enter a valid FEN notation string representing your chess position",
            key="fen_input",
        )

        # Show current board state immediately when FEN changes
        if fen_input:
            if not is_valid_fen(fen_input):
                st.error("Invalid FEN notation. Please check your input.")
            else:
                # Render initial board without analysis
                initial_board = render_chess_board_with_visualization(
                    fen_input, [], [], [], []
                )
                st.components.v1.html(initial_board, height=600)

                if st.button("Analyze Position", key="analyze"):
                    with st.spinner("Analyzing position... (this may take a moment)"):
                        try:
                            # Initialize chat model and analyze position
                            chat_model = initialize_chat_model(model_option, api_key)
                            analysis = analyze_position(
                                chat_model, CHESS_PROMPT, fen_input
                            )

                            # Parse moves and strengths
                            (
                                white_moves,
                                black_moves,
                                white_strengths,
                                black_strengths,
                            ) = parse_moves_with_strength(analysis)

                            # Render interactive board with analysis
                            analysis_board = render_chess_board_with_visualization(
                                fen_input,
                                white_moves,
                                black_moves,
                                white_strengths,
                                black_strengths,
                            )
                            st.components.v1.html(analysis_board, height=800)

                            st.markdown("### Grandmaster Ilya's Analysis")
                            st.markdown(analysis)

                            # Store analysis in session state
                            if "messages" not in st.session_state:
                                st.session_state.messages = []

                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": analysis,
                                    "model": model_option,
                                    "white_moves": white_moves,
                                    "black_moves": black_moves,
                                    "white_strengths": white_strengths,
                                    "black_strengths": black_strengths,
                                }
                            )

                        except Exception as e:
                            st.error(f"An error occurred during analysis: {str(e)}")

    with col2:
        render_previous_analyses(fen_input)


def render_previous_analyses(fen_input: str):
    """Render previous analyses section"""
    st.write("### Previous Analyses")
    if st.session_state.get("messages"):
        for idx, msg in enumerate(
            st.session_state.messages[-5:], 1
        ):  # Show last 5 analyses
            with st.expander(
                f"Analysis {len(st.session_state.messages)-5+idx} ({msg.get('model', 'Unknown Model')})"
            ):
                st.markdown(msg["content"])
                if st.button(f"Replay Analysis #{idx}", key=f"replay_{idx}"):
                    html_content = render_chess_board_with_visualization(
                        fen_input,
                        msg.get("white_moves", []),
                        msg.get("black_moves", []),
                        msg.get("white_strengths", []),
                        msg.get("black_strengths", []),
                    )
                    st.components.v1.html(html_content, height=800)
    else:
        st.info("No previous analyses yet. Try analyzing a position!")
