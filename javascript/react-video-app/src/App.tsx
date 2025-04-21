import React from "react";
import VideoFeed from "./components/VideoFeed";
import CoordinatesDisplay from "./components/CoordinatesDisplay";
import "./styles/App.css";

const App: React.FC = () => {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <VideoFeed />
      <CoordinatesDisplay />
    </div>
  );
};

export default App;
