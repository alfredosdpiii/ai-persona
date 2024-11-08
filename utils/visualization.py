import chess
import chess.svg
import json
from config.constants import STRENGTH_COLORS
from typing import List, Tuple


def generate_move_cards(moves: List[str], strengths: List[str], color: str) -> str:
    """Generate HTML for move cards"""
    cards_html = ""
    for i, (move, strength) in enumerate(zip(moves, strengths)):
        bg_color, _ = STRENGTH_COLORS.get(strength, ("#808080", 2))
        cards_html += f"""
        <div class="move-card" 
             style="background-color: {bg_color}"
             onclick="playMove('{move}', '{color}', '{strength}')">
            {i+1}. {move} ({strength})
        </div>
        """
    return cards_html


def render_chess_board_with_visualization(
    fen: str,
    white_moves: List[str],
    black_moves: List[str],
    white_strengths: List[str],
    black_strengths: List[str],
    size: int = 400,
) -> str:
    """Render chess board with move visualization"""
    board = chess.Board(fen)
    board_svg = chess.svg.board(board=board, size=size, coordinates=True)

    # Import JavaScript and CSS from static files
    with open("static/js/board.js", "r") as js_file:
        js_content = js_file.read()

    with open("static/css/styles.css", "r") as css_file:
        css_content = css_file.read()

    html_content = f"""
    <div id="chess-container" style="position: relative; width: {size}px; margin: auto;">
        <style>{css_content}</style>
        
        <div id="board-container">
            {board_svg}
        </div>
        
        <div class="control-panel">
            <button onclick="resetPosition()" class="control-button">Reset</button>
            <button onclick="playAllMoves()" class="control-button">Play All Moves</button>
            <button onclick="toggleAutoPlay()" id="autoplay-button" class="control-button">Auto Play</button>
            <div class="speed-control">
                <label>Speed:</label>
                <input type="range" min="0.5" max="2" step="0.1" value="1" onchange="updateSpeed(this.value)">
            </div>
        </div>
        
        <div class="move-list">
            <div id="white-moves">
                <h4>White Moves</h4>
                {generate_move_cards(white_moves, white_strengths, 'white')}
            </div>
            <div id="black-moves">
                <h4>Black Moves</h4>
                {generate_move_cards(black_moves, black_strengths, 'black')}
            </div>
        </div>
        
        <script>
        {js_content}
        let currentSpeed = 1;
        let autoPlayInterval = null;
        const moves = {json.dumps({
            'white': list(zip(white_moves, white_strengths)),
            'black': list(zip(black_moves, black_strengths))
        })};
        </script>
    </div>
    """

    return html_content
