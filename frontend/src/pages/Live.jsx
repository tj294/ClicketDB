import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LiveRedirect() {
  const navigate = useNavigate();
  const [liveID, setLiveID] = useState(null);

  useEffect(() => {
    // Fetch team info
    const fetchData = () => {
      fetch(`http://127.0.0.1:8000/live`)
        .then((res) => res.json())
        .then((data) => {
          if (data) {
            navigate(`/game/${data}`);
          } else {
            navigate('/no-live-match');
          }
        });
    };

    fetchData();
  }, [navigate]);

  // navigate(`/game/${liveID}`);

}