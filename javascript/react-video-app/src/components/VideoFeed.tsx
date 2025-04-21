import React from "react";

const VideoFeed: React.FC = () => {
  return (
    <div style={{ flex: 1, borderRight: "1px solid #ccc" }}>
      <h2>Video Feed</h2>
      <img
        src="http://localhost:5000/video_feed"
        alt="Video Feed"
        style={{ width: "100%", height: "auto" }}
      />
    </div>
  );
};

export default VideoFeed;