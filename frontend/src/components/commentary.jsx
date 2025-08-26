import React, { useState, useEffect } from "react";
import "./commentary.css";

export default function Commentary({ match }) {
  const [commentary, setCommentary] = useState([]);

  useEffect(() => {
    if (match.ballEvent && match.ballText) {
      setCommentary(prev => [
        {
          ball_no: `${match.currentOver}.${match.currentBall}`,
          bowler: `${match.sbowlFName} ${match.sbowlLName}`,
          batter: `${match.strikeFName} ${match.strikeLName}`,
          event: match.ballEvent,
          text: match.ballText
        },
        ...prev // keep old commentary below
      ]);
    }
  }, [match.ballEvent, match.ballText]); // runs only when new ball info changes

  return (
    <div className="ball-description" style={{ maxHeight: "300px", overflowY: "auto" }}>
      {commentary.map((ball, idx) => (
        <div className='comms-ball'>
          <div key={idx} style={{ marginBottom: "8px" }}>
                  <p>{ball.ball_no}: {ball.bowler} to {ball.batter}...</p>
                  <p><strong>{ball.event}: </strong>{ball.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}