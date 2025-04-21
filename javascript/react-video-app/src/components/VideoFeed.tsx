import React from "react";
import axios from "axios";

interface VideoFeedProps {
  sessionId: number | null;
  onSessionStart: () => void;
  onSessionEnd: () => void;
}

const VideoFeed: React.FC<VideoFeedProps> = ({
  sessionId,
  onSessionStart,
  onSessionEnd,
}) => {
  // Toggle function for video feed
  const toggleVideoFeed = () => {
    if (sessionId !== null) {
      onSessionEnd();
    } else {
      onSessionStart();
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: 1, borderRight: "1px solid #ccc" }}>
       { /* Video Feed */
          sessionId === null
            ? <h2>Video Feed</h2>
            : <img
                src={`http://localhost:5050/video_feed/${sessionId}`}
                alt="Video Feed"
                style={{ width: "100%", height: "auto" }}
              ></img>
        }
        {/* Toggle Button */}
        <button
          onClick={toggleVideoFeed}
          style={{
            margin: "20px 0",
            padding: "10px 15px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            opacity: 1
          }}
        >
          {sessionId === null ? "Start Video Feed" : "Stop Video Feed"}
        </button>
      </div>
    </div>
  );
};

export default VideoFeed;