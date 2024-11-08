import chess
from typing import Tuple, List


def is_valid_fen(fen: str) -> bool:
    """Validate FEN notation"""
    try:
        chess.Board(fen)
        return True
    except ValueError:
        return False


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

    for line in lines:
        if line.startswith("WHITE MOVES:"):
            parsing_white = True
            parsing_black = False
            continue
        elif line.startswith("BLACK MOVES:"):
            parsing_white = False
            parsing_black = True
            continue

        if parsing_white or parsing_black:
            if ". " in line and any(c.isdigit() for c in line.split(".")[0]):
                parts = line.split("(")
                if len(parts) >= 2:
                    move = parts[0].split(".")[1].strip().split()[0]
                    strength = parts[1].split(")")[0].strip().lower()

                    if len(move) >= 4:
                        if parsing_white:
                            white_moves.append(move)
                            white_strengths.append(strength)
                        else:
                            black_moves.append(move)
                            black_strengths.append(strength)

    return white_moves, black_moves, white_strengths, black_strengths
