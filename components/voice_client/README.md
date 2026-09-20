# Voice client

Componente local de Streamlit para conversación de voz por WebRTC con OpenAI Realtime. No contiene claves permanentes ni guarda audio.

## Estados técnicos del navegador

- `unavailable`: el navegador no expone `getUserMedia`.
- `permission_required`: todavía no se pidió permiso.
- `requesting_permission`: se solicitó el permiso.
- `ready`: el `MediaStream` está abierto y preparado.
- `listening`: la conexión WebRTC inicial está establecida.
- `processing`: Realtime confirmó el fin del turno y prepara la respuesta.
- `speaking`: Realtime está generando/reproduciendo audio remoto.
- `stopped`: los tracks y recursos temporales se liberaron.
- `error`: ocurrió un error de permisos, inicialización o detención.

Estos estados no sustituyen `voice_state` de Python: describen únicamente el estado físico del navegador.

## Eventos JavaScript → Python

El componente devuelve un objeto JSON con `event`, `browser_voice_state`, `browser_event_id` y `command_revision`.

- `MIC_PERMISSION_REQUIRED`
- `MIC_PERMISSION_REQUESTED`
- `MIC_READY`
- `MIC_STOPPED`
- `MIC_NOT_SUPPORTED`
- `MIC_PERMISSION_DENIED`
- `MIC_INITIALIZATION_ERROR`
- `MIC_STOP_ERROR`
- `REALTIME_CREDENTIAL_CONSUMED`
- `REALTIME_SDP_APPLIED`
- `REALTIME_CONNECTED`
- `REALTIME_SESSION_ESTABLISHED`
- `REALTIME_SESSION_CONFIGURED`
- `VOICE_TURN_STARTED` / `VOICE_TURN_ENDED`
- `VOICE_USER_TRANSCRIPT_FINAL`
- `VOICE_RESPONSE_STARTED` / `VOICE_RESPONSE_AUDIO_STARTED` / `VOICE_RESPONSE_DONE`
- `VOICE_ASSISTANT_TRANSCRIPT_FINAL`
- `REALTIME_SDP_ERROR`
- `REALTIME_CONNECTION_ERROR`
- `REMOTE_AUDIO_READY`
- `REMOTE_AUDIO_ERROR`

## Comandos Python → JavaScript

- `START_MIC`: solicita permiso y abre exclusivamente el `MediaStream` del navegador.
- `CONNECT_REALTIME`: usa una credencial efímera recibida temporalmente para negociar WebRTC.
- `STOP_SESSION`: solicita el cierre de sesión y libera todos los recursos locales.
- `RESET_VOICE`: libera recursos y devuelve el componente a un estado inicial.

Los comandos incluyen `command_revision` para que el navegador no procese dos veces el mismo comando durante un rerun de Streamlit.

## Stage 8: VAD, turnos e historial

Al abrir el canal de datos, el navegador envía `session.update` con `server_vad`, `threshold: 0.5`, `prefix_padding_ms: 300`, `silence_duration_ms: 700`, `create_response: false` e `interrupt_response: false`. Tras el evento oficial `input_audio_buffer.committed`, el navegador envía una sola vez `response.create` con salida de audio. La transcripción de entrada usa `gpt-4o-mini-transcribe` con idioma `es`.

`input_audio_buffer.speech_started` y `input_audio_buffer.speech_stopped` actualizan los estados de turno. Solo `conversation.item.input_audio_transcription.completed` agrega el mensaje final del usuario. Solo `response.output_audio_transcript.done` (con respaldo en `response.done`) agrega el mensaje final del asistente. La deduplicación usa los IDs oficiales `item_id`, `response_id` y `content_index`; no compara solo texto.

La sesión Realtime conserva su conversación nativa entre turnos. Cuando comienza una sesión nueva, se siembra una vez el historial visible existente. Durante una sesión activa, únicamente los nuevos mensajes de texto se sincronizan hacia Realtime; los turnos de voz no se reinsertan porque ya forman parte de su conversación nativa.

El audio de respuesta llega en el track remoto WebRTC y se reproduce mediante un elemento `Audio`; ningún audio cruza Streamlit, se guarda como archivo o usa TTS separado.

Referencia oficial: https://developers.openai.com/api/docs/guides/realtime-conversations y https://developers.openai.com/api/docs/guides/realtime-vad

## Cleanup

`STOP_SESSION`, `RESET_VOICE`, `beforeunload` y `pagehide` detienen los `MediaStreamTrack`, cierran `RTCPeerConnection` y el canal de datos, pausan el elemento `Audio` y cierran un `AudioContext` si existe. Cuando WebRTC entrega una pista remota, se asocia al elemento `Audio` y el navegador gestiona su reproducción.

## Arquitectura Stage 7

1. Python usa la clave permanente exclusivamente para crear un client secret temporal con `POST /v1/realtime/client_secrets`.
2. La credencial se entrega una sola vez al iframe mediante argumentos internos del componente y se borra del estado de Streamlit cuando JavaScript informa que la consumió.
3. El navegador crea `RTCPeerConnection`, agrega el track del micrófono, crea el canal `oai-events` y negocia SDP con `POST /v1/realtime/calls` usando solo la credencial temporal.
4. La clave permanente nunca se envía al navegador, URL, almacenamiento web o logs.

El modelo configurado es `gpt-realtime-2.1`, indicado en la guía WebRTC de OpenAI consultada el 19 de septiembre de 2026. La guía también documenta el client secret, las pistas multimedia WebRTC y el canal de datos: https://developers.openai.com/api/docs/guides/voice-webrtc

Queda pendiente para Stage 9: barge-in/cancelación avanzada, reconexión y recuperación automática. No se implementaron en este stage.

## Stage 9: interrupción y recuperación controlada

Si llega `input_audio_buffer.speech_started` mientras existe una respuesta activa, el componente marca su `response_id` como cancelado, envía `response.cancel` y `output_audio_buffer.clear`. Así el búfer WebRTC de salida se limpia antes de procesar el nuevo turno. Los transcriptos finales de un `response_id` cancelado se descartan y no entran al historial. Un cierre inesperado del data channel informa un error recuperable; el botón existente permite crear una sesión nueva, sin reconexión automática agresiva.
