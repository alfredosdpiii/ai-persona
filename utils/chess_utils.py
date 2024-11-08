import chess
from typing import Tuple, List
import re
from config.constants import STRENGTH_COLORS, EVALUATION_SYMBOLS


def is_valid_fen(fen: str) -> bool:
    """Validate FEN notation"""
    try:
        chess.Board(fen)
        return True
    except ValueError:
        return False


def clean_strength_rating(strength: str) -> str:
    """Convert chess symbols to strength ratings"""
    symbol_to_strength = {
        "!!": "brilliant",
        "!": "best",
        "⩲": "good",
        "?!": "interesting",
        "??": "inaccurate",
        "⩱": "mistake",
    }

    # First try to match exact symbols
    strength = strength.strip().lower()
    for symbol, rating in symbol_to_strength.items():
        if symbol in strength:
            return rating

    # If no symbol found, try to match the word
    for rating in STRENGTH_COLORS.keys():
        if rating in strength:
            return rating

    return "good"  # default if no match found


def parse_moves_with_strength(
    analysis_text: str,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Extract UCI moves and their strength ratings from the analysis text"""
    white_moves = []
    black_moves = []
    white_strengths = []
    black_strengths = []

    lines = analysis_text.split("\n")
    parsing_white = False
    parsing_black = False

    # Regular expression to match move lines
    move_pattern = r"(\d+)\.\s+([a-h][1-8][a-h][1-8])\s*\(([^)]+)\)"

    for line in lines:
        if line.startswith("WHITE MOVES:"):
            parsing_white = True
            parsing_black = False
            continue
        elif line.startswith("BLACK MOVES:"):
            parsing_white = False
            parsing_black = True
            continue
        elif line.startswith("STRATEGIC THEMES:"):
            break

        if parsing_white or parsing_black:
            match = re.search(move_pattern, line)
            if match:
                move_number, move, strength = match.groups()
                strength = clean_strength_rating(strength)

                if parsing_white:
                    white_moves.append(move)
                    white_strengths.append(strength)
                else:
                    black_moves.append(move)
                    black_strengths.append(strength)

    return white_moves, black_moves, white_strengths, black_strengths


def get_position_evaluation_symbol(evaluation_text: str) -> str:
    """Extract position evaluation symbol from assessment text"""
    text = evaluation_text.lower()

    if "winning for white" in text or "decisive advantage for white" in text:
        return EVALUATION_SYMBOLS["decisive_white"]
    elif "winning for black" in text or "decisive advantage for black" in text:
        return EVALUATION_SYMBOLS["decisive_black"]
    elif "much better for white" in text:
        return EVALUATION_SYMBOLS["white_much_better"]
    elif "much better for black" in text:
        return EVALUATION_SYMBOLS["black_much_better"]
    elif "better for white" in text:
        return EVALUATION_SYMBOLS["white_better"]
    elif "better for black" in text:
        return EVALUATION_SYMBOLS["black_better"]
    elif "equal" in text or "balanced" in text:
        return EVALUATION_SYMBOLS["equal"]
    elif "unclear" in text or "complex" in text:
        return EVALUATION_SYMBOLS["unclear"]

    return ""  # Return empty string if no clear evaluation found

