import React, { useState, useEffect } from "react";
import axios from "axios";

interface CoordinatesDisplayProps {
  sessionId: number;
}

interface Coordinate {
  BL: [number, number];
  BR: [number, number];
  TL: [number, number];
  TR: [number, number];
}

const CoordinatesDisplay: React.FC<CoordinatesDisplayProps> = ({ sessionId }) => {
  const [coords, setCoords] = useState<Coordinate[]>([]);

  useEffect(() => {
    const fetchCoords = async () => {
      try {
        const response = await axios.get(`http://localhost:5050/latest-coords/${sessionId}`);
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          setCoords(response.data);
        }
      } catch (error) {
        console.error("Error fetching coordinates:", error);
      }
    };

    fetchCoords();
    const intervalId = setInterval(fetchCoords, 1000);
    
    return () => clearInterval(intervalId);
  }, [sessionId]);

  return (
    <div style={{ flex: 1, padding: "20px" }}>
      <h2>Smile Coordinates</h2>
      {coords.length > 0 ? (
        <div>
          {coords.map((coord, index) => (
            <div key={index} style={{ marginBottom: "20px" }}>
              <h3>Detected Smile {index + 1}:</h3>
              <p>Bottom Left: ({coord.BL[0]}, {coord.BL[1]})</p>
              <p>Bottom Right: ({coord.BR[0]}, {coord.BR[1]})</p>
              <p>Top Left: ({coord.TL[0]}, {coord.TL[1]})</p>
              <p>Top Right: ({coord.TR[0]}, {coord.TR[1]})</p>
            </div>
          ))}
        </div>
      ) : (
        <p>No smile detected yet. Try smiling at the camera!</p>
      )}
    </div>
  );
};

export default CoordinatesDisplay;