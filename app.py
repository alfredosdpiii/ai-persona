import os
import openai
import numpy as np
import pandas as pd
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import streamlit as st
import warnings
from streamlit_option_menu import option_menu
from streamlit_extras.mention import mention
import chess
import chess.svg

warnings.filterwarnings("ignore")

# Chess analysis prompt with strength ratings
CHESS_PROMPT = """You are Ilya, a world-renowned chess grandmaster with an ELO rating of 2800. You have dedicated your life to chess and have an extraordinary ability to analyze positions and teach others. You communicate in a direct, slightly confident manner, often using chess terminology naturally but always explaining concepts clearly for players of all levels.


When analyzing the following position in FEN notation:
{fen_position}

Please provide:
1. A brief positional assessment
2. 5 potential moves for White in UCI format, each with a strength rating:
   - brilliant: Game-changing, exceptional move
   - best: Optimal move in the position
   - good: Strong, solid move
   - interesting: Creative move worth considering
   - inaccurate: Slightly imprecise move
   - mistake: Problematic move

Format your response exactly like this:
ASSESSMENT:
[Your positional assessment]

WHITE MOVES:
1. [UCI move] ([strength]) - [explanation]
2. [UCI move] ([strength]) - [explanation]
3. [UCI move] ([strength]) - [explanation]
4. [UCI move] ([strength]) - [explanation]
5. [UCI move] ([strength]) - [explanation]

BLACK MOVES:
1. [UCI move] ([strength]) - [explanation]
2. [UCI move] ([strength]) - [explanation]
3. [UCI move] ([strength]) - [explanation]
4. [UCI move] ([strength]) - [explanation]
5. [UCI move] ([strength]) - [explanation]

TERMS:
[Russian chess terms with translations]"""


# Utility functions for chess visualization
def get_arrow_color(strength):
    """Get arrow color and width based on move strength"""
    colors = {
        "brilliant": ("#00ff00", 5),  # Bright green, thickest
        "best": ("#008000", 4),  # Dark green
        "good": ("#0000ff", 3),  # Blue
        "interesting": ("#ffa500", 3),  # Orange
        "inaccurate": ("#ffd700", 2),  # Yellow
        "mistake": ("#ff0000", 2),  # Red, thinnest
    }
    return colors.get(strength, ("#808080", 2))  # Default gray


def is_valid_fen(fen):
    """Validate FEN notation"""
    try:
        chess.Board(fen)
        return True
    except ValueError:
        return False


def parse_moves_with_strength(analysis_text):
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


def generate_move_css():
    """Generate CSS for move visualization"""
    return """
    .arrow {
        position: absolute;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .strength-indicator {
        position: absolute;
        padding: 4px 8px;
        border-radius: 4px;
        color: white;
        font-size: 12px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .control-panel {
        margin-top: 20px;
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .move-list {
        margin-top: 20px;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    .move-card {
        padding: 8px;
        border-radius: 4px;
        color: white;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .move-card:hover {
        transform: scale(1.05);
    }
    .control-button {
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        background-color: #4CAF50;
        color: white;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .control-button:hover {
        background-color: #45a049;
    }
    """


def generate_arrow_js():
    """Generate JavaScript for arrow animations"""
    return """
    function createArrow(from, to, strength) {
        const fromSquare = document.querySelector(`[data-square="${from}"]`);
        const toSquare = document.querySelector(`[data-square="${to}"]`);
        
        if (!fromSquare || !toSquare) return null;
        
        const fromRect = fromSquare.getBoundingClientRect();
        const toRect = toSquare.getBoundingClientRect();
        
        const [color, width] = getArrowStyle(strength);
        
        // Calculate arrow parameters
        const dx = toRect.left - fromRect.left;
        const dy = toRect.top - fromRect.top;
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;
        const length = Math.sqrt(dx * dx + dy * dy);
        
        const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        arrow.setAttribute('style', `
            position: absolute;
            left: ${fromRect.left}px;
            top: ${fromRect.top}px;
            width: ${length}px;
            height: ${width * 3}px;
            transform: rotate(${angle}deg);
            transform-origin: left center;
        `);
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', '0');
        line.setAttribute('y1', '50%');
        line.setAttribute('x2', '100%');
        line.setAttribute('y2', '50%');
        line.setAttribute('stroke', color);
        line.setAttribute('stroke-width', width);
        
        arrow.appendChild(line);
        return arrow;
    }
    """


def render_chess_board_with_visualization(
    fen, white_moves, black_moves, white_strengths, black_strengths, size=400
):
    """Render chess board with move visualization"""
    board = chess.Board(fen)

    # Generate the base board SVG
    board_svg = chess.svg.board(board=board, size=size, coordinates=True)

    # Create the complete HTML with controls and JavaScript
    html_content = f"""
    <div id="chess-container" style="position: relative; width: {size}px; margin: auto;">
        <style>{generate_move_css()}</style>
        
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
        {generate_arrow_js()}
        let currentSpeed = 1;
        let autoPlayInterval = null;
        const moves = {json.dumps({
            'white': list(zip(white_moves, white_strengths)),
            'black': list(zip(black_moves, black_strengths))
        })};
        
        // Add the rest of your JavaScript functions here
        </script>
    </div>
    """

    return html_content


def generate_move_cards(moves, strengths, color):
    """Generate HTML for move cards"""
    cards_html = ""
    for i, (move, strength) in enumerate(zip(moves, strengths)):
        bg_color, _ = get_arrow_color(strength)
        cards_html += f"""
        <div class="move-card" 
             style="background-color: {bg_color}"
             onclick="playMove('{move}', '{color}', '{strength}')">
            {i+1}. {move} ({strength})
        </div>
        """
    return cards_html


# Streamlit app configuration
st.set_page_config(page_title="Chess Grandmaster Ilya", page_icon="♟️", layout="wide")

# Sidebar
with st.sidebar:
    st.title("♟️ Chess Analysis")
    openai.api_key = st.text_input("Enter OpenAI API token:", type="password")
    model_option = st.selectbox(
        "Select GPT Model:",
        options=[
            "gpt-4-1106-preview",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        help="Select the OpenAI model to use for analysis.",
    )

    if not (openai.api_key.startswith("sk-")):
        st.warning("Please enter your OpenAI API token!", icon="⚠️")
    else:
        st.success("Ready to analyze chess positions!", icon="♟️")

    options = option_menu(
        "Dashboard",
        ["Home", "Analysis", "About"],
        icons=["house", "chess", "info-circle"],
        menu_icon="book",
        default_index=0,
        styles={
            "icon": {"color": "#dec960", "font-size": "20px"},
            "nav-link": {
                "font-size": "17px",
                "text-align": "left",
                "margin": "5px",
                "--hover-color": "#262730",
            },
            "nav-link-selected": {"background-color": "#262730"},
        },
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Home page
if options == "Home":
    st.title("Welcome to Chess Grandmaster Ilya's Analysis Platform! ♟️")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("""
        ### Zdravstvuyte! (Hello!)
        
        I am Grandmaster Ilya, and I'm here to help you improve your chess game! With my 2800 ELO rating 
        and years of experience in professional chess, I can provide deep insights into any position.
        
        ### What I Offer:
        - Deep positional analysis with move strength ratings
        - Animated move suggestions with arrow indicators
        - Strategic recommendations
        - Russian chess terminology with translations
        
        ### How to Use:
        1. Go to the Analysis section
        2. Enter your position in FEN notation
        3. Get professional-level analysis with interactive visualizations
        """)

    with col2:
        st.write("### Example Starting Position:")
        # Show initial board
        html_content = render_chess_board_with_visualization(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", [], [], [], []
        )
        st.components.v1.html(html_content, height=600)

# Analysis page
elif options == "Analysis":
    st.title("Position Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        fen_input = st.text_input(
            "Enter chess position in FEN notation:",
            value="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            help="Enter a valid FEN notation string representing your chess position",
        )

        if fen_input:
            if not is_valid_fen(fen_input):
                st.error("Invalid FEN notation. Please check your input.")
            else:
                if st.button("Analyze Position", key="analyze"):
                    with st.spinner("Analyzing position... (this may take a moment)"):
                        try:
                            # Initialize chat model
                            chat = ChatOpenAI(
                                model=model_option,
                                temperature=0.7,
                                openai_api_key=openai.api_key,
                            )

                            # Create and execute prompt
                            prompt = ChatPromptTemplate.from_template(CHESS_PROMPT)
                            chain = prompt | chat
                            response = chain.invoke({"fen_position": fen_input})
                            analysis = response.content

                            # Parse moves and strengths
                            (
                                white_moves,
                                black_moves,
                                white_strengths,
                                black_strengths,
                            ) = parse_moves_with_strength(analysis)

                            # Render interactive board
                            html_content = render_chess_board_with_visualization(
                                fen_input,
                                white_moves,
                                black_moves,
                                white_strengths,
                                black_strengths,
                            )

                            st.components.v1.html(html_content, height=800)

                            st.markdown("### Grandmaster Ilya's Analysis")
                            st.markdown(analysis)

                            # Store analysis
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
                        else:
                            # Show initial board without analysis
                            html_content = render_chess_board_with_visualization(
                                fen_input, [], [], [], []
                            )
                    st.components.v1.html(html_content, height=600)

    with col2:
        st.write("### Previous Analyses")
        if st.session_state.messages:
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

# About page
elif options == "About":
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
            ["good"],  # Example moves with strengths
        )
        st.components.v1.html(html_content, height=600)
        st.code(
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3",
            language="text",
        )

# Footer
st.markdown("""
---
Created with ♟️ by Bryan/AI republic/Generative AI Labs
""")

# CSS for consistent styling
st.markdown(
    """
<style>
    .css-1y4p8pa {
        padding-top: 0rem;
    }
    .stButton>button {
        width: 100%;
    }
    .chess-board {
        margin: 2rem 0;
    }
    .move-list {
        margin-top: 1rem;
    }
    .strength-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 1rem 0;
    }
    .strength-item {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .strength-color {
        width: 20px;
        height: 20px;
        border-radius: 50%;
    }
</style>
""",
    unsafe_allow_html=True,
)
