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
  const fromSquare = document.querySelector(`[data-square="${from}"]`);
  const toSquare = document.querySelector(`[data-square="${to}"]`);

  if (!fromSquare || !toSquare) return null;

  const fromRect = fromSquare.getBoundingClientRect();
  const toRect = toSquare.getBoundingClientRect();

  const [color, width] = getArrowStyle(strength);

  // Calculate arrow parameters
  const dx = toRect.left - fromRect.left;
  const dy = toRect.top - fromRect.top;
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  const length = Math.sqrt(dx * dx + dy * dy);

  const arrow = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  arrow.setAttribute(
    "style",
    `
        position: absolute;
        left: ${fromRect.left}px;
        top: ${fromRect.top}px;
        width: ${length}px;
        height: ${width * 3}px;
        transform: rotate(${angle}deg);
        transform-origin: left center;
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

  const from = move.substring(0, 2);
  const to = move.substring(2, 4);

  // Highlight squares
  const toSquare = board.querySelector(`[data-square="${to}"]`);
  if (toSquare) {
    toSquare.style.backgroundColor =
      color === "white"
        ? "rgba(144, 238, 144, 0.5)"
        : "rgba(135, 206, 235, 0.5)";
  }
}

function playMove(move, color, strength) {
  const from = move.substring(0, 2);
  const to = move.substring(2, 4);

  // Create and show arrow
  const arrow = createArrow(from, to, strength);
  if (arrow) {
    document.getElementById("board-container").appendChild(arrow);
    arrow.style.opacity = "1";

    // Create strength indicator
    const indicator = document.createElement("div");
    indicator.classList.add("strength-indicator");
    indicator.textContent = strength.toUpperCase();
    indicator.style.backgroundColor = getArrowStyle(strength)[0];
    document.getElementById("board-container").appendChild(indicator);

    // Remove after animation
    setTimeout(() => {
      arrow.remove();
      indicator.remove();
      updatePosition(move, color);
    }, 1000);
  }
}

function playAllMoves() {
  let delay = 0;
  moves.white.forEach(([move, strength]) => {
    setTimeout(() => playMove(move, "white", strength), delay);
    delay += 1500;
  });

  moves.black.forEach(([move, strength]) => {
    setTimeout(() => playMove(move, "black", strength), delay);
    delay += 1500;
  });
}

let currentMove = 0;
let isPlaying = false;
let autoPlayInterval = null;

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
}

function resetPosition() {
  const board = document.querySelector("#board-container");
  if (board) {
    // Remove all highlights and arrows
    const squares = board.querySelectorAll("[data-square]");
    squares.forEach((square) => {
      square.style.backgroundColor = "";
    });

    // Remove any existing arrows
    const arrows = document.querySelectorAll(".arrow");
    arrows.forEach((arrow) => arrow.remove());

    // Remove any strength indicators
    const indicators = document.querySelectorAll(".strength-indicator");
    indicators.forEach((indicator) => indicator.remove());
  }
  currentMove = 0;
}
