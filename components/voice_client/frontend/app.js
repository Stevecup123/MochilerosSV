(() => {
  "use strict";
  const READY = "streamlit:componentReady", RENDER = "streamlit:render", VALUE = "streamlit:setComponentValue", HEIGHT = "streamlit:setFrameHeight";
  const CALLS_URL = "https://api.openai.com/v1/realtime/calls";
  let state = "permission_required", stream = null, pc = null, dc = null, audio = null, closeTimer = null;
  let lastRevision = -1, generation = 0, config = null, messages = [], configured = false, sequence = 0, activeResponseId = null, intentionalClose = false;
  let stateTimer = null, disconnectTimer = null, cleaningUp = false;
  const componentId = typeof crypto?.randomUUID === "function" ? crypto.randomUUID() : `component-${Date.now()}`;
  const sentMessages = new Set(), userFinals = new Set(), assistantFinals = new Set(), assistantTranscriptFinals = new Map(), responseStarts = new Set(), audioStarts = new Set(), committedTurns = new Set(), cancelledResponses = new Set();
  const CONNECT_TIMEOUT_MS = 60000, PROCESSING_TIMEOUT_MS = 45000, SPEAKING_TIMEOUT_MS = 120000, DISCONNECT_GRACE_MS = 10000, RECENT_EVENT_LIMIT = 256, RECENT_TRANSCRIPT_LIMIT = 128;

  const post = (type, payload) => window.parent.postMessage({ isStreamlitMessage: true, type, ...payload }, "*");
  function report(event, detail = "", revision = lastRevision, extra = {}) {
    sequence += 1;
    post(VALUE, { value: { event, detail, browser_voice_state: state, browser_event_id: `${componentId}:${sequence}`, command_revision: revision, voice_generation: generation, ...extra } });
  }
  const canUseMic = () => Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  function prepareAudio() {
    if (!audio) {
      audio = new Audio(); audio.autoplay = true; audio.preload = "none";
      audio.addEventListener("error", () => failSession("REMOTE_AUDIO_ERROR", "No se pudo preparar el audio de respuesta.", lastRevision));
    }
    return audio;
  }
  function clearTimers() {
    if (closeTimer) window.clearTimeout(closeTimer); closeTimer = null;
    if (stateTimer) window.clearTimeout(stateTimer); stateTimer = null;
    if (disconnectTimer) window.clearTimeout(disconnectTimer); disconnectTimer = null;
  }
  function prune(collection, limit) { while (collection.size > limit) collection.delete(collection.keys().next().value); }
  function armStateTimeout(expectedStates, timeout, event, detail, revision) {
    if (stateTimer) window.clearTimeout(stateTimer);
    stateTimer = window.setTimeout(() => {
      stateTimer = null;
      if (expectedStates.includes(state)) failSession(event, detail, revision);
    }, timeout);
  }
  function closeConnection() {
    clearTimers();
    configured = false; activeResponseId = null; intentionalClose = true;
    if (dc) { dc.onmessage = dc.onopen = dc.onerror = dc.onclose = null; if (dc.readyState !== "closed") dc.close(); dc = null; }
    if (pc) { pc.ontrack = pc.onconnectionstatechange = null; pc.close(); pc = null; }
    if (audio) { audio.pause(); audio.srcObject = null; }
  }
  function cleanup(notify = true) {
    if (cleaningUp) return;
    cleaningUp = true; clearTimers(); closeConnection();
    if (stream) { stream.getTracks().forEach((track) => track.stop()); stream = null; }
    sentMessages.clear(); userFinals.clear(); assistantFinals.clear(); assistantTranscriptFinals.clear(); responseStarts.clear(); audioStarts.clear(); committedTurns.clear(); cancelledResponses.clear();
    state = "stopped"; if (notify) report("MIC_STOPPED", "La sesión de voz se cerró.");
  }
  function failSession(event, detail, revision) {
    if (cleaningUp) return;
    cleanup(false); report(event, detail, revision);
  }
  function waitIce(connection) {
    if (connection.iceGatheringState === "complete") return Promise.resolve();
    return new Promise((resolve) => {
      const finish = () => { connection.removeEventListener("icegatheringstatechange", listener); connection.removeEventListener("connectionstatechange", stateListener); resolve(); };
      const listener = () => { if (connection.iceGatheringState === "complete") finish(); };
      const stateListener = () => { if (["closed", "failed"].includes(connection.connectionState)) finish(); };
      connection.addEventListener("icegatheringstatechange", listener); connection.addEventListener("connectionstatechange", stateListener);
    });
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
      failSession("REALTIME_SESSION_CONFIGURATION_ERROR", "No se pudo configurar la conversación por voz.", lastRevision);
    }
  }
  function userFinal(event) {
    const item = event.item_id, index = Number(event.content_index ?? 0), key = `${item}:${index}`;
    if (typeof item !== "string" || typeof event.transcript !== "string" || !event.transcript.trim() || userFinals.has(key)) return;
    userFinals.add(key); prune(userFinals, RECENT_EVENT_LIMIT); report("VOICE_USER_TRANSCRIPT_FINAL", "", lastRevision, { openai_item_id: item, content_index: index, transcript: event.transcript });
  }
  function rememberAssistantFinal(response, item, index, transcript) {
    const key = `${response}:${item}:${index}`;
    if (typeof response !== "string" || cancelledResponses.has(response) || typeof item !== "string" || typeof transcript !== "string" || !transcript.trim() || assistantFinals.has(key)) return;
    assistantFinals.add(key); prune(assistantFinals, RECENT_EVENT_LIMIT);
    assistantTranscriptFinals.set(key, { openai_response_id: response, openai_item_id: item, content_index: index, transcript: transcript.trim() });
    prune(assistantTranscriptFinals, RECENT_TRANSCRIPT_LIMIT);
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
    else if (event.type === "session.updated") { if (stateTimer) window.clearTimeout(stateTimer); stateTimer = null; configured = true; state = "listening"; syncHistory(true); report("REALTIME_SESSION_CONFIGURED", "Sesión de voz lista."); }
    else if (event.type === "input_audio_buffer.speech_started") {
      if (activeResponseId) {
        const interruptedResponseId = activeResponseId;
        cancelledResponses.add(interruptedResponseId); prune(cancelledResponses, RECENT_TRANSCRIPT_LIMIT);
        activeResponseId = null;
        // En WebRTC, limpia el búfer remoto que aún no se reprodujo y cancela esta respuesta.
        send({ type: "response.cancel", response_id: interruptedResponseId });
        send({ type: "output_audio_buffer.clear" });
        report("VOICE_RESPONSE_INTERRUPTED", "", lastRevision, { openai_response_id: interruptedResponseId });
      }
      if (stateTimer) window.clearTimeout(stateTimer); stateTimer = null;
      state = "listening"; report("VOICE_TURN_STARTED", "", lastRevision, { openai_item_id: event.item_id });
    }
    else if (event.type === "input_audio_buffer.speech_stopped") { state = "processing"; armStateTimeout(["processing"], PROCESSING_TIMEOUT_MS, "VOICE_RESPONSE_ERROR", "La respuesta de voz tardó demasiado.", lastRevision); report("VOICE_TURN_ENDED", "", lastRevision, { openai_item_id: event.item_id }); }
    else if (event.type === "input_audio_buffer.committed" && typeof event.item_id === "string" && !committedTurns.has(event.item_id)) {
      committedTurns.add(event.item_id); prune(committedTurns, RECENT_EVENT_LIMIT);
      // Con create_response:false, este es el único disparador de la respuesta.
      if (!send({ type: "response.create", response: { output_modalities: ["audio"] } })) {
        state = "error"; report("VOICE_RESPONSE_ERROR", "No pude generar la respuesta de voz.");
      }
    }
    else if (event.type === "conversation.item.input_audio_transcription.completed") userFinal(event);
    else if (event.type === "response.created" && event.response?.id && !responseStarts.has(event.response.id)) { activeResponseId = event.response.id; responseStarts.add(event.response.id); prune(responseStarts, RECENT_EVENT_LIMIT); state = "speaking"; armStateTimeout(["speaking"], SPEAKING_TIMEOUT_MS, "VOICE_RESPONSE_ERROR", "La respuesta de voz tardó demasiado.", lastRevision); report("VOICE_RESPONSE_STARTED", "", lastRevision, { openai_response_id: event.response.id }); }
    else if (event.type === "response.output_audio.delta" && event.response_id) { if (!audioStarts.has(event.response_id)) { audioStarts.add(event.response_id); prune(audioStarts, RECENT_EVENT_LIMIT); report("VOICE_RESPONSE_AUDIO_STARTED", "", lastRevision, { openai_response_id: event.response_id }); } state = "speaking"; armStateTimeout(["speaking"], SPEAKING_TIMEOUT_MS, "VOICE_RESPONSE_ERROR", "La respuesta de voz dejó de emitir audio.", lastRevision); }
    else if (event.type === "response.output_audio_transcript.done") rememberAssistantFinal(event.response_id, event.item_id, Number(event.content_index ?? 0), event.transcript);
    else if (event.type === "response.done") {
      const responseId = event.response?.id;
      const assistantVoiceMessage = event.response?.status === "completed" ? finalAssistantMessage(event) : null;
      if (stateTimer) window.clearTimeout(stateTimer); stateTimer = null;
      if (activeResponseId === responseId) activeResponseId = null;
      state = "listening";
      // Un solo valor final para Streamlit: evita que un evento de cierre reemplace
      // el transcript consolidado antes de que Python ejecute su siguiente rerun.
      report("VOICE_RESPONSE_DONE", "", lastRevision, { openai_response_id: responseId, assistant_voice_message: assistantVoiceMessage });
    }
    else if (event.type === "response.cancelled") { const responseId = event.response?.id || event.response_id; if (typeof responseId === "string") { cancelledResponses.add(responseId); prune(cancelledResponses, RECENT_TRANSCRIPT_LIMIT); } if (activeResponseId === responseId) activeResponseId = null; }
    else if (event.type === "session.closed") cleanup(true);
    else if (event.type === "error") failSession(event.error?.code === "input_audio_transcription_failed" ? "VOICE_TRANSCRIPTION_ERROR" : "VOICE_RESPONSE_ERROR", "No pude procesar ese mensaje de voz. Intentá de nuevo.", lastRevision);
  }
  async function openMic(revision) {
    if (!canUseMic()) { state = "unavailable"; report("MIC_NOT_SUPPORTED", "Tu navegador no permite acceso al micrófono.", revision); return; }
    cleaningUp = false; clearTimers();
    if (pc || dc) closeConnection();
    intentionalClose = false;
    if (stream) { state = "ready"; report("MIC_READY", "El micrófono ya está preparado.", revision); return; }
    state = "requesting_permission"; armStateTimeout(["requesting_permission"], CONNECT_TIMEOUT_MS, "MIC_INITIALIZATION_ERROR", "El permiso de micrófono tardó demasiado.", revision); report("MIC_PERMISSION_REQUESTED", "Solicitando permiso de micrófono.", revision);
    try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); prepareAudio(); state = "ready"; report("MIC_READY", "El micrófono está preparado.", revision); }
    catch (error) { state = "error"; report(error?.name === "NotAllowedError" ? "MIC_PERMISSION_DENIED" : "MIC_INITIALIZATION_ERROR", "No se pudo acceder al micrófono. Revisá los permisos del navegador.", revision); }
  }
  async function connect(secret, revision) {
    // En un rerun Streamlit puede montar otro iframe después de consumir la
    // credencial. No es un fallo de credencial ni debe invalidar la sesión
    // WebRTC que ya está produciendo audio en el iframe existente.
    if (!secret || !stream || cleaningUp) return;
    try {
      if (pc || dc) closeConnection();
      intentionalClose = false; cleaningUp = false;
      report("REALTIME_CREDENTIAL_CONSUMED", "", revision);
      const connection = new RTCPeerConnection(); pc = connection;
      const channel = connection.createDataChannel("oai-events"); dc = channel;
      channel.onmessage = onRealtimeEvent;
      channel.onopen = configureSession;
      channel.onerror = () => failSession("REALTIME_CONNECTION_ERROR", "No se pudo conectar con el servicio de voz.", revision);
      channel.onclose = () => { if (!intentionalClose) failSession("REALTIME_CLOSED_UNEXPECTEDLY", "La conexión de voz se cerró. Podés reanudarla.", revision); };
      connection.addTrack(stream.getAudioTracks()[0], stream);
      connection.ontrack = (event) => { const player = prepareAudio(); player.srcObject = event.streams[0]; player.play().then(() => report("REMOTE_AUDIO_READY", "", revision), () => failSession("REMOTE_AUDIO_ERROR", "El navegador bloqueó el audio de respuesta.", revision)); };
      connection.onconnectionstatechange = () => {
        if (connection !== pc || intentionalClose) return;
        if (["failed", "closed"].includes(connection.connectionState)) failSession("REALTIME_CONNECTION_ERROR", "La conexión de voz se cerró.", revision);
        else if (connection.connectionState === "disconnected") {
          if (disconnectTimer) window.clearTimeout(disconnectTimer);
          disconnectTimer = window.setTimeout(() => { if (connection === pc && connection.connectionState === "disconnected") failSession("REALTIME_CONNECTION_ERROR", "La conexión de voz se interrumpió.", revision); }, DISCONNECT_GRACE_MS);
        } else if (disconnectTimer) { window.clearTimeout(disconnectTimer); disconnectTimer = null; }
      };
      armStateTimeout(["ready", "connecting", "requesting_permission"], CONNECT_TIMEOUT_MS, "REALTIME_CONNECTION_ERROR", "La conexión de voz tardó demasiado.", revision);
      await connection.setLocalDescription(await connection.createOffer()); await waitIce(connection);
      const response = await fetch(CALLS_URL, { method: "POST", headers: { Authorization: `Bearer ${secret}`, "Content-Type": "application/sdp" }, body: connection.localDescription.sdp });
      if (!response.ok || connection !== pc || cleaningUp) throw new Error("sdp"); await connection.setRemoteDescription({ type: "answer", sdp: await response.text() }); report("REALTIME_SDP_APPLIED", "", revision);
    } catch (_) { if (!cleaningUp) failSession("REALTIME_SDP_ERROR", "No se pudo establecer la conexión de voz.", revision); }
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
