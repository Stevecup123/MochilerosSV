const message = document.getElementById("message");
const action = document.getElementById("action");
const dictation = document.getElementById("dictation");
const dictationStatus = document.getElementById("dictation-status");
let conversationId = null;
let eventSequence = 0;
let recognition = null;
let dictationState = "idle";
let dictationBaseText = "";
let finalTranscript = "";
const componentId = typeof crypto?.randomUUID === "function" ? crypto.randomUUID() : `composer-${Date.now()}`;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function post(event, text = "") {
  window.parent.postMessage(
    { isStreamlitMessage: true, type: "streamlit:setComponentValue", value: { event, text, event_id: `${componentId}:${++eventSequence}` } },
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

function showDictationStatus(text = "", kind = "") {
  dictationStatus.hidden = !text;
  dictationStatus.textContent = text;
  dictationStatus.className = `composer-status ${kind}`;
}

function updateAction() {
  const hasText = message.value.trim().length > 0;
  action.textContent = hasText ? "➤" : "◉";
  action.setAttribute("aria-label", hasText ? "Enviar mensaje" : "Iniciar conversación por voz");
  action.title = hasText ? "Enviar mensaje" : "Iniciar conversación por voz";
  action.classList.toggle("send", hasText);
  setHeight();
}

function setDictationState(nextState, detail = "") {
  dictationState = nextState;
  dictation.classList.toggle("recording", nextState === "recording");
  dictation.classList.toggle("processing", nextState === "processing");
  dictation.disabled = nextState === "processing";
  if (nextState === "recording") showDictationStatus("Escuchando…");
  else if (nextState === "processing") showDictationStatus("Transcribiendo…");
  else if (nextState === "ready") showDictationStatus("Transcripción lista", "ready");
  else if (nextState === "error") showDictationStatus(detail || "No se pudo transcribir el audio.", "error");
  else showDictationStatus();
}

function submit() {
  const text = message.value.trim();
  if (!text || dictationState === "recording" || dictationState === "processing") return;
  message.value = "";
  setDictationState("idle");
  updateAction();
  post("submit", text);
}

function applyTranscript(interim = "") {
  const transcript = [finalTranscript, interim].filter(Boolean).join(" ").trim();
  message.value = [dictationBaseText, transcript].filter(Boolean).join(dictationBaseText && transcript ? " " : "");
  updateAction();
}

function friendlyRecognitionError(error) {
  if (error === "not-allowed" || error === "service-not-allowed") return "El permiso del micrófono fue denegado. Podés seguir escribiendo.";
  if (error === "audio-capture") return "No se detectó un micrófono disponible.";
  if (error === "network") return "No se pudo completar la transcripción. Revisá tu conexión.";
  if (error === "no-speech") return "No se detectó voz. Intentá de nuevo.";
  return "No se pudo transcribir el audio. Intentá de nuevo.";
}

function stopDictation() {
  if (dictationState !== "recording" || !recognition) return;
  setDictationState("processing");
  recognition.stop();
}

function startDictation() {
  if (!SpeechRecognition) {
    setDictationState("error", "Tu navegador no admite dictado de voz. Podés seguir escribiendo.");
    return;
  }
  dictationBaseText = message.value.trim();
  finalTranscript = "";
  recognition = new SpeechRecognition();
  recognition.lang = "es-SV";
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.onstart = () => setDictationState("recording");
  recognition.onresult = (event) => {
    let interim = "";
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const text = event.results[index][0].transcript.trim();
      if (event.results[index].isFinal) finalTranscript = [finalTranscript, text].filter(Boolean).join(" ");
      else interim = [interim, text].filter(Boolean).join(" ");
    }
    applyTranscript(interim);
  };
  recognition.onerror = (event) => {
    recognition = null;
    message.value = dictationBaseText;
    updateAction();
    setDictationState("error", friendlyRecognitionError(event.error));
  };
  recognition.onend = () => {
    if (dictationState === "error") return;
    recognition = null;
    applyTranscript();
    if (finalTranscript) {
      setDictationState("ready");
      window.setTimeout(() => { if (dictationState === "ready") setDictationState("idle"); }, 1800);
    } else {
      message.value = dictationBaseText;
      updateAction();
      setDictationState("error", "No se detectó voz. Intentá de nuevo.");
    }
  };
  try { recognition.start(); }
  catch (_) { setDictationState("error", "No se pudo iniciar el dictado. Intentá de nuevo."); }
}

message.addEventListener("input", () => {
  if (dictationState === "ready" || dictationState === "error") setDictationState("idle");
  updateAction();
});
message.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    submit();
  }
});
dictation.addEventListener("click", () => {
  if (dictationState === "recording") stopDictation();
  else if (dictationState !== "processing") startDictation();
});
action.addEventListener("click", () => {
  if (message.value.trim()) submit();
  else if (dictationState !== "recording" && dictationState !== "processing") post("start_voice");
});
window.addEventListener("message", (event) => {
  if (event.data?.type !== "streamlit:render") return;
  const nextConversationId = event.data.args?.conversation_id ?? null;
  if (conversationId !== nextConversationId) {
    if (dictationState === "recording") stopDictation();
    conversationId = nextConversationId;
    message.value = "";
    setDictationState("idle");
  }
  updateAction();
});
window.addEventListener("beforeunload", stopDictation);
window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }, "*");
updateAction();
