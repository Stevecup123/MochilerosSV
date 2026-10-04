const message = document.getElementById("message");
const action = document.getElementById("action");
let conversationId = null;
let eventSequence = 0;
const componentId = typeof crypto?.randomUUID === "function" ? crypto.randomUUID() : `composer-${Date.now()}`;

function post(event, text = "") {
  window.parent.postMessage(
    {
      isStreamlitMessage: true,
      type: "streamlit:setComponentValue",
      value: { event, text, event_id: `${componentId}:${++eventSequence}` },
    },
    "*",
  );
}

function setHeight() {
  message.style.height = "auto";
  message.style.height = `${Math.min(message.scrollHeight, 132)}px`;
  window.parent.postMessage(
    { isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: Math.max(56, message.offsetHeight + 14) },
    "*",
  );
}

function updateAction() {
  const hasText = message.value.trim().length > 0;
  action.textContent = hasText ? "➤" : "🎙️";
  action.setAttribute("aria-label", hasText ? "Enviar mensaje" : "Hablar con Mochileros");
  action.title = hasText ? "Enviar mensaje" : "Hablar con Mochileros";
  action.classList.toggle("send", hasText);
  setHeight();
}

function submit() {
  const text = message.value.trim();
  if (!text) return;
  message.value = "";
  updateAction();
  post("submit", text);
}

message.addEventListener("input", updateAction);
message.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    submit();
  }
});

action.addEventListener("click", () => {
  if (message.value.trim()) {
    submit();
  } else {
    post("start_voice");
  }
});

window.addEventListener("message", (event) => {
  if (event.data?.type !== "streamlit:render") return;
  const nextConversationId = event.data.args?.conversation_id ?? null;
  if (conversationId !== nextConversationId) {
    conversationId = nextConversationId;
    message.value = "";
  }
  updateAction();
});

window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }, "*");
updateAction();
