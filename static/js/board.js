// Global variables
let currentSpeed = 1.0;
let isPlaying = false;
let autoPlayInterval = null;
let moveQueue = [];

// Arrow style mapping
function getArrowStyle(strength) {
  const styles = {
    brilliant: ["#00ff00", 5],
    best: ["#008000", 4],
    good: ["#0000ff", 3],
    interesting: ["#ffa500", 3],
    inaccurate: ["#ffd700", 2],
    mistake: ["#ff0000", 2],
  };
  return styles[strength] || ["#808080", 2];
}

function createArrow(from, to, strength) {
  const board = document.getElementById("board-container");
  if (!board) return null;

  const fromSquare = board.querySelector(`[data-square="${from}"]`);
  const toSquare = board.querySelector(`[data-square="${to}"]`);

  if (!fromSquare || !toSquare) return null;

  const fromRect = fromSquare.getBoundingClientRect();
  const toRect = toSquare.getBoundingClientRect();
  const boardRect = board.getBoundingClientRect();

  const [color, width] = getArrowStyle(strength);

  // Calculate arrow parameters relative to board container
  const dx = toRect.left - fromRect.left;
  const dy = toRect.top - fromRect.top;
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  const length = Math.sqrt(dx * dx + dy * dy);

  const arrow = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  arrow.classList.add("arrow");
  arrow.setAttribute(
    "style",
    `
        position: absolute;
        left: ${fromRect.left - boardRect.left}px;
        top: ${fromRect.top - boardRect.top}px;
        width: ${length}px;
        height: ${width * 3}px;
        transform: rotate(${angle}deg);
        transform-origin: left center;
        pointer-events: none;
    `,
  );

  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", "0");
  line.setAttribute("y1", "50%");
  line.setAttribute("x2", "100%");
  line.setAttribute("y2", "50%");
  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", width);

  arrow.appendChild(line);
  return arrow;
}

function updatePosition(move, color) {
  const board = document.querySelector("#board-container");
  if (!board) return;

  // Clear previous highlights
  const squares = board.querySelectorAll("[data-square]");
  squares.forEach((square) => {
    square.style.backgroundColor = "";
  });

  const from = move.substring(0, 2);
  const to = move.substring(2, 4);

  // Highlight squares
  const fromSquare = board.querySelector(`[data-square="${from}"]`);
  const toSquare = board.querySelector(`[data-square="${to}"]`);

  if (fromSquare) {
    fromSquare.style.backgroundColor = "rgba(255, 255, 0, 0.3)";
  }
  if (toSquare) {
    toSquare.style.backgroundColor =
      color === "white"
        ? "rgba(144, 238, 144, 0.5)"
        : "rgba(135, 206, 235, 0.5)";
  }
}

function playMove(move, color, strength) {
  return new Promise((resolve) => {
    const from = move.substring(0, 2);
    const to = move.substring(2, 4);

    // Create and show arrow
    const arrow = createArrow(from, to, strength);
    if (arrow) {
      const board = document.getElementById("board-container");
      board.appendChild(arrow);
      arrow.style.opacity = "1";

      // Create strength indicator
      const indicator = document.createElement("div");
      indicator.classList.add("strength-indicator");
      indicator.textContent = strength.toUpperCase();
      indicator.style.backgroundColor = getArrowStyle(strength)[0];
      board.appendChild(indicator);

      // Update position and remove arrow after animation
      updatePosition(move, color);

      setTimeout(() => {
        arrow.remove();
        indicator.remove();
        resolve();
      }, 1000 / currentSpeed);
    } else {
      resolve();
    }
  });
}

async function playAllMoves() {
  if (!moves || !moves.white || !moves.black) return;

  resetPosition();

  // Play white moves
  for (const [move, strength] of moves.white) {
    await playMove(move, "white", strength);
    await new Promise((resolve) => setTimeout(resolve, 500 / currentSpeed));
  }

  // Play black moves
  for (const [move, strength] of moves.black) {
    await playMove(move, "black", strength);
    await new Promise((resolve) => setTimeout(resolve, 500 / currentSpeed));
  }
}

function toggleAutoPlay() {
  const button = document.getElementById("autoplay-button");
  if (isPlaying) {
    clearInterval(autoPlayInterval);
    button.textContent = "Auto Play";
    isPlaying = false;
  } else {
    button.textContent = "Stop";
    isPlaying = true;
    playAllMoves();
  }
}

function updateSpeed(speed) {
  currentSpeed = parseFloat(speed);
  console.log("Speed updated to:", currentSpeed);
}

function resetPosition() {
  const board = document.querySelector("#board-container");
  if (board) {
    // Remove all highlights
    const squares = board.querySelectorAll("[data-square]");
    squares.forEach((square) => {
      square.style.backgroundColor = "";
    });

    // Remove any existing arrows
    const arrows = board.querySelectorAll(".arrow");
    arrows.forEach((arrow) => arrow.remove());

    // Remove any strength indicators
    const indicators = board.querySelectorAll(".strength-indicator");
    indicators.forEach((indicator) => indicator.remove());
  }
}

// Initialize when the page loads
document.addEventListener("DOMContentLoaded", () => {
  const speedControl = document.querySelector('input[type="range"]');
  if (speedControl) {
    speedControl.addEventListener("input", (e) => {
      updateSpeed(e.target.value);
    });
  }
});
