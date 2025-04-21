import React, { useState, useEffect } from "react";
import VideoFeed from "./components/VideoFeed";
import CoordinatesDisplay from "./components/CoordinatesDisplay";
import axios from "axios";
import "./styles/App.css";

const App: React.FC = () => {
  const [sessionId, setSessionId] = useState<number | null>(null);

  // Create a new session
  const createSession = async () => {
    try {
      const response = await axios.post("http://localhost:5050/create-session");
      setSessionId(response.data.sessionId);
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  // Close the current session
  const closeSession = async () => {
    if (!sessionId) return;

    try {
      await axios.post(`http://localhost:5050/close-session/${sessionId}`);
    } catch (error) {
      console.error(`Error closing session ${sessionId}:`, error);
    } finally {
      setSessionId(null); // Reset sessionId to null
    }
  };

  // Cleanup effect - runs when sessionId changes or component unmounts
  useEffect(() => {
    if (!sessionId) return; // Skip if no sessionId yet

    // Handle window close/refresh
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      // Synchronous request to ensure it completes before browser closes
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `http://localhost:5050/close-session/${sessionId}`, false);
      xhr.send();

      // Standard beforeunload boilerplate
      e.preventDefault();
      e.returnValue = '';
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup function for component unmount
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);

      // Close session when component unmounts (if not due to window close)
      axios.post(`http://localhost:5050/close-session/${sessionId}`)
        .catch(error => console.error(`Error closing session ${sessionId}:`, error));
    };
  }, [sessionId]);

  return (
    <div style={{ display: "flex", height: "100vh", position: "relative" }}>
      <VideoFeed
        sessionId={sessionId}
        onSessionStart={createSession}
        onSessionEnd={closeSession}
      />
      {sessionId && <CoordinatesDisplay sessionId={sessionId} />}
    </div>
  );
};

export default App;
