// FitEvidence AI — frontend logic
// Handles asking a question, chip shortcuts, and rendering all UI states.

const form = document.getElementById("ask-form");
const input = document.getElementById("question-input");
const askButton = document.getElementById("ask-button");
const chipRow = document.getElementById("chip-row");

const stateEmpty = document.getElementById("state-empty");
const stateLoading = document.getElementById("state-loading");
const stateError = document.getElementById("state-error");
const stateErrorText = document.getElementById("state-error-text");
const stateNoResults = document.getElementById("state-noresults");
const answerCard = document.getElementById("answer-card");

const answerQuestion = document.getElementById("answer-question");
const answerText = document.getElementById("answer-text");
const sourcesRow = document.getElementById("sources-row");

function showState(name) {
  stateEmpty.hidden = name !== "empty";
  stateLoading.hidden = name !== "loading";
  stateError.hidden = name !== "error";
  stateNoResults.hidden = name !== "noresults";
  answerCard.hidden = name !== "answer";
}

function setLoading(isLoading) {
  askButton.disabled = isLoading;
  askButton.classList.toggle("is-loading", isLoading);
}

function labelForIndex(i) {
  return `REP ${i + 1}`;
}

function renderSources(sources) {
  sourcesRow.innerHTML = "";
  sources.forEach((src, i) => {
    const tag = document.createElement("div");
    tag.className = "source-tag";

    const rep = document.createElement("span");
    rep.className = "rep-label";
    rep.textContent = labelForIndex(i);

    const file = document.createElement("span");
    file.className = "rep-file";
    file.textContent = src;

    tag.appendChild(rep);
    tag.appendChild(file);
    sourcesRow.appendChild(tag);
  });
}

async function askQuestion(question) {
  showState("loading");
  setLoading(true);

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
console.log("===== API RESPONSE =====");
console.log(data);
console.log("answer =", data.answer);
console.log("typeof answer =", typeof data.answer);
    if (!res.ok) {
      showState("error");
      stateErrorText.textContent = data.error || "Something went wrong on the server.";
      return;
    }

    if (!data.answer) {
      showState("noresults");
      return;
    }

    answerQuestion.textContent = question;
    answerText.textContent = data.answer;
    renderSources(data.sources || []);
    showState("answer");
  } catch (err) {
    showState("error");
    stateErrorText.textContent = "Couldn't reach the server. Make sure it's still running.";
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  askQuestion(question);
});

chipRow.addEventListener("click", (e) => {
  const chip = e.target.closest(".chip");
  if (!chip) return;
  const question = chip.dataset.q;
  input.value = question;
  askQuestion(question);
});
