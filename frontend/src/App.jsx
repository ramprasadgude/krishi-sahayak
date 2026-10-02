import { useState, useRef, useEffect } from "react";
import VoiceRecorder from "./components/VoiceRecorder.jsx";
import ChatBubble from "./components/ChatBubble.jsx";
import { sendTextQuery, sendVoiceQuery } from "./api.js";

const SAMPLE_QUESTIONS = [
  "నా వరి పంటకు ఏ ఎరువు వేయాలి?", // Which fertilizer should I use for my paddy crop?
  "నేను PM-Kisan పథకానికి అర్హుడినా?", // Am I eligible for PM-Kisan?
  "మిరపలో తెగుళ్లను ఎలా నియంత్రించాలి?", // How do I control pests in chilli?
];

export default function App() {
  const [turns, setTurns] = useState([]);
  const [textInput, setTextInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, isLoading]);

  function addFarmerTurn(teluguText) {
    setTurns((prev) => [...prev, { role: "farmer", teluguText }]);
  }

  function addAssistantTurn(response) {
    setTurns((prev) => [
      ...prev,
      {
        role: "assistant",
        teluguText: response.telugu_answer,
        englishText: response.english_answer,
        audioBase64: response.audio_base64,
        sourceId: response.matched_source_id,
      },
    ]);
  }

  async function runQuery(queryFn, teluguQuestionForDisplay) {
    setErrorMessage(null);
    setIsLoading(true);
    if (teluguQuestionForDisplay) addFarmerTurn(teluguQuestionForDisplay);

    try {
      const response = await queryFn();
      // If we didn't already show the farmer's turn (voice path — we only
      // know the transcript after the call), show it now, right before the
      // assistant's reply.
      if (!teluguQuestionForDisplay) {
        setTurns((prev) => [...prev, { role: "farmer", teluguText: response.telugu_question }]);
      }
      addAssistantTurn(response);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleRecordingComplete(audioBlob) {
    runQuery(() => sendVoiceQuery(audioBlob), null);
  }

  function handleTextSubmit(e) {
    e.preventDefault();
    const text = textInput.trim();
    if (!text) return;
    setTextInput("");
    runQuery(() => sendTextQuery(text), text);
  }

  function askSample(question) {
    runQuery(() => sendTextQuery(question), question);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌾 Krishi Sahayak</h1>
        <p>Speak your question in Telugu — crop advice, fertilizer, pests, or PM-Kisan scheme help.</p>
      </header>

      <main className="chat-window">
        {turns.length === 0 && (
          <div className="empty-state">
            <p>Try asking one of these, or tap the mic:</p>
            <div className="sample-questions">
              {SAMPLE_QUESTIONS.map((q) => (
                <button key={q} className="sample-chip" onClick={() => askSample(q)} disabled={isLoading}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {turns.map((turn, i) => (
          <ChatBubble key={i} turn={turn} />
        ))}

        {isLoading && (
          <div className="chat-row assistant">
            <div className="chat-bubble assistant loading">Krishi Sahayak is thinking…</div>
          </div>
        )}

        {errorMessage && <p className="error-banner">{errorMessage}</p>}

        <div ref={chatEndRef} />
      </main>

      <footer className="app-footer">
        <VoiceRecorder onRecordingComplete={handleRecordingComplete} disabled={isLoading} />

        <form className="text-form" onSubmit={handleTextSubmit}>
          <input
            type="text"
            placeholder="...or type your question in Telugu"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !textInput.trim()}>
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}
