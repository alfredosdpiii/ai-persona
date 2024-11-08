import streamlit as st
import chess
import chess.svg
from utils.chess_utils import is_valid_fen, make_move
from utils.api_utils import initialize_chat_model, analyze_position
from config.constants import CHESS_PROMPT, DEFAULT_FEN, STRENGTH_COLORS
import re


def clean_fen(fen_text: str) -> str:
    """Clean and validate FEN notation."""
    # Remove any trailing periods
    fen = fen_text.rstrip(".")

    # Validate basic FEN structure
    fen_parts = fen.split()
    if len(fen_parts) == 6:  # Complete FEN
        return fen

    # Try to fix incomplete FEN
    if len(fen_parts) < 6:
        # Add missing parts if needed
        if len(fen_parts) >= 2:  # Has at least position and active color
            while len(fen_parts) < 6:
                if len(fen_parts) == 2:
                    fen_parts.append("KQkq")  # Castling rights
                elif len(fen_parts) == 3:
                    fen_parts.append("-")  # En passant
                elif len(fen_parts) == 4:
                    fen_parts.append("0")  # Halfmove clock
                elif len(fen_parts) == 5:
                    fen_parts.append("1")  # Fullmove number
            return " ".join(fen_parts)

    return fen


def parse_move(move_text: str) -> tuple:
    """
    Advanced move parser that handles various formats and edge cases.
    Returns (uci_move, strength, explanation, fen)
    """
    try:
        # Remove the "Could not parse move from:" prefix if present
        if "Could not parse move from:" in move_text:
            move_text = move_text.split("Could not parse move from:", 1)[1].strip()

        # Extract move using multiple patterns
        move_patterns = [
            r'"([a-h][1-8][a-h][1-8])"',  # Quoted UCI
            r"[^a-h]([a-h][1-8][a-h][1-8])[^a-h]",  # Unquoted UCI
            r'"([KQRBN][a-h]?[1-8]?[a-h][1-8])"',  # Quoted algebraic
            r"[^a-h]([KQRBN][a-h]?[1-8]?[a-h][1-8])[^a-h]",  # Unquoted algebraic
        ]

        uci_move = None
        for pattern in move_patterns:
            match = re.search(pattern, move_text)
            if match:
                uci_move = match.group(1)
                break

        # Extract strength - look for text in parentheses
        strength_match = re.search(r"\(([A-Z]+)\)", move_text)
        if not strength_match:
            return None, None, "Could not find move strength", None
        strength = strength_match.group(1)

        # Find FEN - look for chess position pattern at the end
        fen_patterns = [
            r"(?:position (?:becomes|will be|is|changes to)|FEN:)\s*(r[^\s\.]+(?:\s+[bw]\s+(?:K?Q?k?q?|-)\s+(?:-|[a-h][36])\s+\d+\s+\d+))",
            r"(r[^\s\.]+(?:\s+[bw]\s+(?:K?Q?k?q?|-)\s+(?:-|[a-h][36])\s+\d+\s+\d+))\s*\.",
            r"(r[^\s\.]+(?:\s+[bw]\s+(?:K?Q?k?q?|-)\s+(?:-|[a-h][36])\s+\d+\s+\d+))\s*$",
        ]

        fen = None
        for pattern in fen_patterns:
            match = re.search(pattern, move_text)
            if match:
                fen = clean_fen(match.group(1))
                break

        # Extract explanation - everything between strength and FEN/end
        explanation_text = move_text.split(f"({strength})")[-1]
        # Remove FEN part from explanation
        if fen:
            explanation_text = explanation_text.split(fen)[0]

        # Clean up explanation
        explanation = explanation_text.strip(" -").strip()
        explanation = re.sub(
            r"The position (?:becomes|will be|is|changes to).*$", "", explanation
        )
        explanation = re.sub(r"FEN:.*$", "", explanation).strip()

        # Final validation
        if not uci_move:
            return None, None, "Could not parse move notation", None

        return uci_move, strength, explanation, fen

    except Exception as e:
        st.debug(f"Error parsing move text: {move_text}\nError: {str(e)}")
        return None, None, f"Error parsing move: {str(e)}", None


def render_move_with_board(move_text: str, initial_fen: str, move_number: int):
    """Render a single move analysis with board"""
    uci_move, strength, explanation, fen = parse_move(move_text)

    if not uci_move:
        st.error(f"Move {move_number} parsing error: {explanation}")
        st.code(move_text)  # Show the problematic text for debugging
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
        # Create colored header for move
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
            """,
            unsafe_allow_html=True,
        )

        st.write(explanation)

        # Show FEN in an expander
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

