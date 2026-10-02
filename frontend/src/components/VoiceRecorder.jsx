import { useRef, useState } from "react";

/**
 * Mic button that records audio via the browser's MediaRecorder API and
 * hands the recorded Blob to onRecordingComplete once the user stops.
 * Falls back gracefully (hides itself) if the browser has no mic support —
 * the text input in App.jsx remains usable either way.
 */
export default function VoiceRecorder({ onRecordingComplete, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const supported =
    typeof navigator !== "undefined" &&
    !!navigator.mediaDevices &&
    typeof MediaRecorder !== "undefined";

  async function startRecording() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());
        onRecordingComplete(blob);
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (err) {
      setError("Microphone access denied or unavailable.");
      console.error(err);
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  }

  if (!supported) {
    return <p className="mic-unsupported">Microphone recording isn't supported in this browser — use the text box below instead.</p>;
  }

  return (
    <div className="voice-recorder">
      <button
        type="button"
        className={`mic-button ${isRecording ? "recording" : ""}`}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled}
        aria-label={isRecording ? "Stop recording" : "Start recording"}
      >
        {isRecording ? "⏹" : "🎤"}
      </button>
      <span className="mic-label">
        {isRecording ? "Listening… tap to stop" : "Tap to speak in Telugu"}
      </span>
      {error && <p className="mic-error">{error}</p>}
    </div>
  );
}
