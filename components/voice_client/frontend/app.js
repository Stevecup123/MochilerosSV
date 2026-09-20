(() => {
  "use strict";
  const READY = "streamlit:componentReady", RENDER = "streamlit:render", VALUE = "streamlit:setComponentValue", HEIGHT = "streamlit:setFrameHeight";
  const CALLS_URL = "https://api.openai.com/v1/realtime/calls";
  let state = "permission_required", stream = null, pc = null, dc = null, audio = null, closeTimer = null;
  let lastRevision = -1, generation = 0, config = null, messages = [], configured = false, sequence = 0, activeResponseId = null, intentionalClose = false;
  const componentId = typeof crypto?.randomUUID === "function" ? crypto.randomUUID() : `component-${Date.now()}`;
  const sentMessages = new Set(), userFinals = new Set(), assistantFinals = new Set(), assistantTranscriptFinals = new Map(), responseStarts = new Set(), audioStarts = new Set(), committedTurns = new Set(), cancelledResponses = new Set();

  const post = (type, payload) => window.parent.postMessage({ isStreamlitMessage: true, type, ...payload }, "*");
  function report(event, detail = "", revision = lastRevision, extra = {}) {
    sequence += 1;
    post(VALUE, { value: { event, detail, browser_voice_state: state, browser_event_id: `${componentId}:${sequence}`, command_revision: revision, voice_generation: generation, ...extra } });
  }
  const canUseMic = () => Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  function prepareAudio() {
    if (!audio) {
      audio = new Audio(); audio.autoplay = true; audio.preload = "none";
      audio.addEventListener("error", () => report("REMOTE_AUDIO_ERROR", "No se pudo preparar el audio de respuesta."));
    }
    return audio;
  }
  function cleanup(notify = true) {
    if (closeTimer) window.clearTimeout(closeTimer); closeTimer = null; configured = false;
    sentMessages.clear(); userFinals.clear(); assistantFinals.clear(); assistantTranscriptFinals.clear(); responseStarts.clear(); audioStarts.clear(); committedTurns.clear(); cancelledResponses.clear(); activeResponseId = null;
    if (dc) { dc.onmessage = dc.onopen = dc.onerror = null; if (dc.readyState !== "closed") dc.close(); dc = null; }
    if (pc) { pc.ontrack = pc.onconnectionstatechange = null; pc.close(); pc = null; }
    if (stream) { stream.getTracks().forEach((track) => track.stop()); stream = null; }
    if (audio) { audio.pause(); audio.srcObject = null; audio.removeAttribute("src"); audio.load(); }
    state = "stopped"; if (notify) report("MIC_STOPPED", "La sesión de voz se cerró.");
  }
  function waitIce(connection) {
    if (connection.iceGatheringState === "complete") return Promise.resolve();
    return new Promise((resolve) => { const listener = () => { if (connection.iceGatheringState === "complete") { connection.removeEventListener("icegatheringstatechange", listener); resolve(); } }; connection.addEventListener("icegatheringstatechange", listener); });
  }
  function send(event) { if (!dc || dc.readyState !== "open") return false; dc.send(JSON.stringify(event)); return true; }
  function validMessage(message) { return message && typeof message.message_id === "string" && ["user", "assistant"].includes(message.role) && typeof message.content === "string" && message.content.trim(); }
  function sendHistoryMessage(message) {
    if (!validMessage(message) || sentMessages.has(message.message_id)) return;
    if (send({ type: "conversation.item.create", item: { type: "message", role: message.role, content: [{ type: message.role === "user" ? "input_text" : "output_text", text: message.content.trim() }] } })) sentMessages.add(message.message_id);
  }
  function syncHistory(initial) { if (configured) messages.forEach((message) => { if (initial || message.origin === "text") sendHistoryMessage(message); }); }
  function configureSession() {
    const transcription = { model: config?.transcription_model, language: config?.transcription_language };
    if (!transcription.model || !send({ type: "session.update", session: { type: "realtime", model: config?.model, output_modalities: ["audio"], instructions: config?.instructions, audio: { input: { transcription, turn_detection: config?.turn_detection }, output: { voice: config?.voice } } } })) {
      state = "error"; report("REALTIME_SESSION_CONFIGURATION_ERROR", "No se pudo configurar la conversación por voz.");
    }
  }
  function userFinal(event) {
    const item = event.item_id, index = Number(event.content_index ?? 0), key = `${item}:${index}`;
    if (typeof item !== "string" || typeof event.transcript !== "string" || !event.transcript.trim() || userFinals.has(key)) return;
    userFinals.add(key); report("VOICE_USER_TRANSCRIPT_FINAL", "", lastRevision, { openai_item_id: item, content_index: index, transcript: event.transcript });
  }
  function rememberAssistantFinal(response, item, index, transcript) {
    const key = `${response}:${item}:${index}`;
    if (typeof response !== "string" || cancelledResponses.has(response) || typeof item !== "string" || typeof transcript !== "string" || !transcript.trim() || assistantFinals.has(key)) return;
    assistantFinals.add(key);
    assistantTranscriptFinals.set(key, { openai_response_id: response, openai_item_id: item, content_index: index, transcript: transcript.trim() });
  }
  function fallbackResponse(event) {
    const response = event.response; if (!response?.id) return;
    (response.output || []).forEach((item) => (item.content || []).forEach((content, index) => rememberAssistantFinal(response.id, item.id, index, content.transcript || (content.type === "output_text" ? content.text : null))));
  }
  function finalAssistantMessage(event) {
    const responseId = event.response?.id;
    if (typeof responseId !== "string" || cancelledResponses.has(responseId)) return null;
    fallbackResponse(event);
    return Array.from(assistantTranscriptFinals.values()).find((message) => message.openai_response_id === responseId) || null;
  }
  function onRealtimeEvent(message) {
    let event; try { event = JSON.parse(message.data); } catch (_) { return; }
    // Diagnóstico temporal: solo metadatos de protocolo, nunca audio ni secretos.
    console.debug(`[VOICE DEBUG] type=${event.type} item_id=${event.item_id || "-"} response_id=${event.response_id || event.response?.id || "-"} status=${event.response?.status || "-"}`);
    if (event.type === "session.created") report("REALTIME_SESSION_ESTABLISHED", "Sesión de voz establecida.", lastRevision, { openai_session_id: event.session?.id || null });
    else if (event.type === "session.updated") { configured = true; state = "listening"; syncHistory(true); report("REALTIME_SESSION_CONFIGURED", "Sesión de voz lista."); }
    else if (event.type === "input_audio_buffer.speech_started") {
      if (activeResponseId) {
        const interruptedResponseId = activeResponseId;
        cancelledResponses.add(interruptedResponseId);
        activeResponseId = null;
        // En WebRTC, limpia el búfer remoto que aún no se reprodujo y cancela esta respuesta.
        send({ type: "response.cancel", response_id: interruptedResponseId });
        send({ type: "output_audio_buffer.clear" });
        report("VOICE_RESPONSE_INTERRUPTED", "", lastRevision, { openai_response_id: interruptedResponseId });
      }
      state = "listening"; report("VOICE_TURN_STARTED", "", lastRevision, { openai_item_id: event.item_id });
    }
    else if (event.type === "input_audio_buffer.speech_stopped") { state = "processing"; report("VOICE_TURN_ENDED", "", lastRevision, { openai_item_id: event.item_id }); }
    else if (event.type === "input_audio_buffer.committed" && typeof event.item_id === "string" && !committedTurns.has(event.item_id)) {
      committedTurns.add(event.item_id);
      // Con create_response:false, este es el único disparador de la respuesta.
      if (!send({ type: "response.create", response: { output_modalities: ["audio"] } })) {
        state = "error"; report("VOICE_RESPONSE_ERROR", "No pude generar la respuesta de voz.");
      }
    }
    else if (event.type === "conversation.item.input_audio_transcription.completed") userFinal(event);
    else if (event.type === "response.created" && event.response?.id && !responseStarts.has(event.response.id)) { activeResponseId = event.response.id; responseStarts.add(event.response.id); state = "speaking"; report("VOICE_RESPONSE_STARTED", "", lastRevision, { openai_response_id: event.response.id }); }
    else if (event.type === "response.output_audio.delta" && event.response_id && !audioStarts.has(event.response_id)) { audioStarts.add(event.response_id); state = "speaking"; report("VOICE_RESPONSE_AUDIO_STARTED", "", lastRevision, { openai_response_id: event.response_id }); }
    else if (event.type === "response.output_audio_transcript.done") rememberAssistantFinal(event.response_id, event.item_id, Number(event.content_index ?? 0), event.transcript);
    else if (event.type === "response.done") {
      const responseId = event.response?.id;
      const assistantVoiceMessage = event.response?.status === "completed" ? finalAssistantMessage(event) : null;
      if (activeResponseId === responseId) activeResponseId = null;
      state = "listening";
      // Un solo valor final para Streamlit: evita que un evento de cierre reemplace
      // el transcript consolidado antes de que Python ejecute su siguiente rerun.
      report("VOICE_RESPONSE_DONE", "", lastRevision, { openai_response_id: responseId, assistant_voice_message: assistantVoiceMessage });
    }
    else if (event.type === "response.cancelled") { const responseId = event.response?.id || event.response_id; if (typeof responseId === "string") cancelledResponses.add(responseId); if (activeResponseId === responseId) activeResponseId = null; }
    else if (event.type === "session.closed") cleanup(true);
    else if (event.type === "error") { state = "error"; report(event.error?.code === "input_audio_transcription_failed" ? "VOICE_TRANSCRIPTION_ERROR" : "VOICE_RESPONSE_ERROR", "No pude procesar ese mensaje de voz. Intentá de nuevo."); }
  }
  async function openMic(revision) {
    if (!canUseMic()) { state = "unavailable"; report("MIC_NOT_SUPPORTED", "Tu navegador no permite acceso al micrófono.", revision); return; }
    if (stream) { state = "ready"; report("MIC_READY", "El micrófono ya está preparado.", revision); return; }
    state = "requesting_permission"; report("MIC_PERMISSION_REQUESTED", "Solicitando permiso de micrófono.", revision);
    try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); prepareAudio(); state = "ready"; report("MIC_READY", "El micrófono está preparado.", revision); }
    catch (error) { state = "error"; report(error?.name === "NotAllowedError" ? "MIC_PERMISSION_DENIED" : "MIC_INITIALIZATION_ERROR", "No se pudo acceder al micrófono. Revisá los permisos del navegador.", revision); }
  }
  async function connect(secret, revision) {
    // En un rerun Streamlit puede montar otro iframe después de consumir la
    // credencial. No es un fallo de credencial ni debe invalidar la sesión
    // WebRTC que ya está produciendo audio en el iframe existente.
    if (!secret || !stream) return;
    try {
      intentionalClose = false;
      report("REALTIME_CREDENTIAL_CONSUMED", "", revision); pc = new RTCPeerConnection(); dc = pc.createDataChannel("oai-events");
      dc.addEventListener("message", onRealtimeEvent); dc.addEventListener("open", configureSession); dc.addEventListener("error", () => { state = "error"; report("REALTIME_CONNECTION_ERROR", "No se pudo conectar con el servicio de voz.", revision); }); dc.addEventListener("close", () => { if (!intentionalClose) { state = "error"; report("REALTIME_CLOSED_UNEXPECTEDLY", "La conexión de voz se cerró. Podés reanudarla.", revision); } });
      pc.addTrack(stream.getAudioTracks()[0], stream);
      pc.addEventListener("track", (event) => { const player = prepareAudio(); player.srcObject = event.streams[0]; player.play().then(() => report("REMOTE_AUDIO_READY", "", revision), () => report("REMOTE_AUDIO_ERROR", "El navegador bloqueó el audio de respuesta.", revision)); });
      pc.addEventListener("connectionstatechange", () => { if (pc?.connectionState === "failed") { state = "error"; report("REALTIME_CONNECTION_ERROR", "No se pudo conectar con el servicio de voz.", revision); } });
      await pc.setLocalDescription(await pc.createOffer()); await waitIce(pc);
      const response = await fetch(CALLS_URL, { method: "POST", headers: { Authorization: `Bearer ${secret}`, "Content-Type": "application/sdp" }, body: pc.localDescription.sdp });
      if (!response.ok) throw new Error("sdp"); await pc.setRemoteDescription({ type: "answer", sdp: await response.text() }); report("REALTIME_SDP_APPLIED", "", revision);
    } catch (_) { state = "error"; report("REALTIME_SDP_ERROR", "No se pudo establecer la conexión de voz.", revision); cleanup(false); }
  }
  function stop() { intentionalClose = true; if (dc?.readyState === "open") { try { dc.send(JSON.stringify({ type: "session.close" })); closeTimer = window.setTimeout(() => cleanup(true), 2000); return; } catch (_) {} } cleanup(true); }
  function handle(args) {
    messages = Array.isArray(args.conversation_messages) ? args.conversation_messages : []; config = args.realtime_config || config; syncHistory(false);
    const revision = Number(args.command_revision ?? -1); if (revision === lastRevision) return; lastRevision = revision;
    if (["START_MIC", "CONNECT_REALTIME"].includes(args.command)) generation = Number(args.voice_generation ?? generation);
    if (args.command === "START_MIC") void openMic(revision);
    // La credencial se borra en Python justo después de consumirse. Un render
    // posterior con la misma revisión no debe convertir ese borrado seguro en error.
    else if (args.command === "CONNECT_REALTIME" && args.client_secret) void connect(args.client_secret, revision);
    else if (["STOP_SESSION", "RESET_VOICE"].includes(args.command)) stop();
  }
  window.addEventListener("message", (event) => { if (event.data?.type === RENDER) handle(event.data.args || {}); });
  window.addEventListener("beforeunload", () => cleanup(false)); window.addEventListener("pagehide", () => cleanup(false));
  post(READY, { apiVersion: 1 }); post(HEIGHT, { height: 0 });
  if (!canUseMic()) { state = "unavailable"; report("MIC_NOT_SUPPORTED", "Tu navegador no permite acceso al micrófono.", -1); } else report("MIC_PERMISSION_REQUIRED", "El micrófono se solicitará al activarlo.", -1);
})();
