import { useMemo, useState } from "react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Bine ai venit. Spune-mi ce fel de atmosferă, temă sau poveste cauți, iar eu îți voi recomanda o carte potrivită.",
    },
  ]);

  const [bookHistory, setBookHistory] = useState([]);
  const [currentRecommendation, setCurrentRecommendation] = useState(null);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);

  const [audioUrl, setAudioUrl] = useState("");
  const [imageUrl, setImageUrl] = useState("");

  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);

  const lastAssistantMessage = useMemo(
    () => [...messages].reverse().find((m) => m.role === "assistant"),
    [messages]
  );

  const handleSelectBook = (book) => {
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: book.response,
      },
    ]);

    setCurrentRecommendation(book);
  };

  const sendMessage = async (customText = null) => {
    const text = (customText ?? input).trim();
    if (!text) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      const raw = await res.text();

      if (!res.ok) {
        throw new Error(raw);
      }

      const data = JSON.parse(raw);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);

      const recommendation = {
        title: data.title,
        response: data.response,
        visual_hint: data.visual_hint,
      };

      setCurrentRecommendation(recommendation);

      setBookHistory((prev) => {
        if (!recommendation.title) return prev;
        if (prev.some((b) => b.title === recommendation.title)) return prev;
        return [...prev, recommendation];
      });
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `A apărut o problemă la conectarea cu backend-ul: ${error.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleListen = async () => {
    if (!lastAssistantMessage) return;

    try {
      setIsGeneratingAudio(true);

      const res = await fetch("http://127.0.0.1:8000/tts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: lastAssistantMessage.content }),
      });

      const raw = await res.text();

      if (!res.ok) {
        throw new Error(raw);
      }

      const data = JSON.parse(raw);
      setAudioUrl(data.audio_url);
    } catch (error) {
      alert(`TTS error: ${error.message}`);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!currentRecommendation?.visual_hint) return;

    try {
      setIsGeneratingImage(true);

      const res = await fetch("http://127.0.0.1:8000/generate-image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: currentRecommendation.visual_hint,
        }),
      });

      const raw = await res.text();
      const data = JSON.parse(raw);

      if (!res.ok) {
        throw new Error(data.detail || "Nu s-a putut genera imaginea.");
      }

      setImageUrl(data.image_url);
    } catch (error) {
      alert(`Image generation error: ${error.message}`);
    } finally {
      setIsGeneratingImage(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = async () => {
        try {
          const audioBlob = new Blob(chunks, { type: "audio/webm" });
          const formData = new FormData();
          formData.append("audio", audioBlob, "voice.webm");

          const res = await fetch("http://127.0.0.1:8000/stt", {
            method: "POST",
            body: formData,
          });

          const raw = await res.text();

          if (!res.ok) {
            throw new Error(raw);
          }

          const data = JSON.parse(raw);
          setInput(data.text || "");
        } catch (error) {
          alert(`STT error: ${error.message}`);
        }
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      alert("Nu am putut accesa microfonul.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="page">
      <div className="app-shell">
        <aside className="left-rail">
          <div className="brand-block">
            <span className="eyebrow">Your personal reading corner</span>
            <h1 className="title">Smart Librarian</h1>
            <p className="subtitle">
              Recomandări de cărți într-o atmosferă calmă, caldă și ușor de explorat.
            </p>
          </div>

          <div className="rail-card recommendation-card">
            <span className="card-label">Current recommendation</span>
            <div className="recommendation-content">
              <p>
                {lastAssistantMessage
                  ? lastAssistantMessage.content
                  : "Aici va apărea ultima recomandare."}
              </p>
            </div>
          </div>

          <div className="rail-card bookshelf-card">
            <span className="card-label">Mini bookshelf</span>

            <div className="bookshelf-list">
              {bookHistory.length === 0 ? (
                <p className="bookshelf-empty">
                  Nu ai încă recomandări în sesiunea curentă.
                </p>
              ) : (
                bookHistory.map((book, index) => (
                  <button
                    key={`${book.title}-${index}`}
                    className="book-item"
                    onClick={() => handleSelectBook(book)}
                  >
                    <span className="book-spine">📚</span>
                    <span className="book-title">{book.title}</span>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="rail-card prompt-card">
            <span className="card-label">Try asking</span>
            <button
              className="prompt-chip"
              onClick={() => sendMessage("Vreau o carte despre prietenie și magie")}
            >
              Prietenie și magie
            </button>
            <button
              className="prompt-chip"
              onClick={() =>
                sendMessage("Ce recomanzi pentru cineva care iubește povești de război?")
              }
            >
              Povești de război
            </button>
            <button
              className="prompt-chip"
              onClick={() =>
                sendMessage("Vreau o carte despre libertate și control social")
              }
            >
              Libertate și control social
            </button>
          </div>
        </aside>

        <main className="main-panel">
          <section className="conversation-panel">
            <div className="section-top">
              <div>
                <span className="section-kicker">Conversation</span>
                <h2>Găsește o carte potrivită stării tale</h2>
              </div>
            </div>

            <div className="chat-box">
              {messages.map((msg, index) => (
                <div
                  key={`${msg.role}-${index}-${msg.content}`}
                  className={`message-row message-enter ${
                    msg.role === "user" ? "user-row" : "assistant-row"
                  }`}
                >
                  <div className={`message-card ${msg.role}`}>
                    <span className="message-role">
                      {msg.role === "user" ? "You" : "Librarian"}
                    </span>
                    <p>{msg.content}</p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message-row assistant-row">
                  <div className="message-card assistant loading-card">
                    <span className="message-role">Librarian</span>
                    <p>Pregătesc o recomandare pentru tine...</p>
                  </div>
                </div>
              )}
            </div>

            <div className="composer">
              <textarea
                className="message-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ex: Aș vrea o carte fantasy cu aventură, emoție și o lume memorabilă..."
              />

              <div className="composer-actions">
                <button
                  className="soft-button"
                  onClick={isRecording ? stopRecording : startRecording}
                >
                  {isRecording ? "Stop recording" : "Voice input"}
                </button>

                <button
                  className="soft-button"
                  onClick={handleListen}
                  disabled={isGeneratingAudio || !lastAssistantMessage}
                >
                  {isGeneratingAudio ? "Preparing audio..." : "Listen"}
                </button>

                <button
                  className="primary-button"
                  onClick={() => sendMessage()}
                  disabled={isLoading}
                >
                  {isLoading ? "Sending..." : "Send"}
                </button>
              </div>
            </div>
          </section>
        </main>

        <aside className="right-rail">
          <div className="media-card visual-card">
            <div className="media-header">
              <div>
                <span className="section-kicker">Visual interpretation</span>
                <h3>Create artwork</h3>
                <p>O imagine inspirată de ultima recomandare.</p>
              </div>

              <button
                className="primary-button alt"
                onClick={handleGenerateImage}
                disabled={isGeneratingImage || !currentRecommendation?.visual_hint}
              >
                {isGeneratingImage ? "Creating..." : "Generate image"}
              </button>
            </div>

            <div className="visual-frame">
              {isGeneratingImage ? (
                <div className="empty-state">
                  <div className="loader" />
                  <p>Se creează ilustrația...</p>
                </div>
              ) : imageUrl ? (
                <img
                  src={imageUrl}
                  alt="Generated illustration"
                  className="generated-image"
                />
              ) : (
                <div className="empty-state">
                  <div className="book-cover-placeholder">
                    <span>Cover Art</span>
                  </div>
                  <p>Imaginea generată va apărea aici.</p>
                </div>
              )}
            </div>
          </div>

          <div className="media-card audio-card">
            <span className="section-kicker">Audio</span>
            <h3>Listen to the recommendation</h3>
            <p>Ascultă răspunsul într-un format mai natural și relaxat.</p>

            {audioUrl ? (
              <audio controls src={audioUrl} className="audio-player" />
            ) : (
              <div className="audio-empty">
                Nu ai generat încă audio pentru ultimul răspuns.
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}