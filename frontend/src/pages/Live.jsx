import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_URL = import.meta.env.VITE_API_URL;

export default function LiveRedirect() {
  const navigate = useNavigate();
  const [liveID, setLiveID] = useState(null);

  useEffect(() => {
    // Fetch team info
    const fetchData = () => {
      fetch(`${API_URL}/live`)
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

export function NoLivePage() {
  return (
    <div>
      <h1>No Upcoming Matches</h1>
    </div>
  )
}