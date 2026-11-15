const form = document.getElementById("answer-form");
const input = document.getElementById("answer");
const conversation = document.getElementById("conversation");
const notice = document.getElementById("notice");
const hintButton = document.getElementById("hint");

function showNotice(text) {
  notice.textContent = text || "";
}

function showState(state) {
  document.getElementById("puzzle").textContent = state.puzzle;
  document.getElementById("progress").textContent =
    state.completed ? "Room escaped!" : `Puzzle ${state.progress + 1} of ${state.total}`;
  document.getElementById("hint-count").textContent = `Hints remaining: ${state.hints_remaining}`;
  conversation.replaceChildren();
  for (const message of state.messages) {
    const item = document.createElement("p");
    item.className = `message ${message.role}`;
    item.textContent = `${message.role === "player" ? "You" : "Room"}: ${message.text}`;
    conversation.append(item);
  }
  const disabled = state.completed;
  input.disabled = disabled;
  form.querySelector("button").disabled = disabled;
  hintButton.disabled = disabled || state.hints_remaining === 0;
  conversation.scrollTop = conversation.scrollHeight;
}

async function postJson(url, body = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The request could not be completed.");
  return data;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showNotice("");
  try {
    const state = await postJson("/api/message", {message: input.value});
    showState(state);
    input.value = "";
    input.focus();
  } catch (error) {
    showNotice(error.message);
  }
});

hintButton.addEventListener("click", async () => {
  showNotice("");
  try {
    showState(await postJson("/api/hint"));
  } catch (error) {
    showNotice(error.message);
  }
});

document.getElementById("restart").addEventListener("click", async () => {
  showNotice("");
  try {
    showState(await postJson("/api/restart"));
    input.focus();
  } catch (error) {
    showNotice(error.message);
  }
});

fetch("/api/state")
  .then((response) => response.json())
  .then(showState)
  .catch(() => showNotice("Could not load the game. Refresh the page to try again."));
