import React from "react";

interface VideoFeedProps {
  sessionId: number;
}

const VideoFeed: React.FC<VideoFeedProps> = ({ sessionId }) => {
  return (
    <div style={{ flex: 1, borderRight: "1px solid #ccc" }}>
      <h2>Video Feed</h2>
      <img
        src={`http://localhost:5050/video_feed/${sessionId}`}
        alt="Video Feed"
        style={{ width: "100%", height: "auto" }}
      />
    </div>
  );
};

export default VideoFeed;