/**
 * Renders one turn of the conversation. `turn.role` is "farmer" or
 * "assistant". Assistant turns include the spoken Telugu audio (if TTS
 * succeeded) plus the English translation underneath for judges/demo
 * viewers who don't read Telugu.
 */
export default function ChatBubble({ turn }) {
  const isAssistant = turn.role === "assistant";

  return (
    <div className={`chat-row ${isAssistant ? "assistant" : "farmer"}`}>
      <div className={`chat-bubble ${isAssistant ? "assistant" : "farmer"}`}>
        <div className="chat-label">{isAssistant ? "Krishi Sahayak" : "You"}</div>
        <div className="chat-telugu">{turn.teluguText}</div>

        {turn.englishText && (
          <div className="chat-english">({turn.englishText})</div>
        )}

        {isAssistant && turn.audioBase64 && (
          <audio
            className="chat-audio"
            controls
            autoPlay
            src={`data:audio/mp3;base64,${turn.audioBase64}`}
          />
        )}

        {isAssistant && turn.sourceId && (
          <div className="chat-source">Source: {turn.sourceId}</div>
        )}
      </div>
    </div>
  );
}
