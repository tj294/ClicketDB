import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

function App() {
  const [matches, setMatches] = useState([]);
  const [league, setLeague] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/upcoming_matches")
      .then(res => setMatches(res.data))
      .catch(err => console.error(err));

    axios.get("http://127.0.0.1:8000/league_table")
      .then(res => setLeague(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>🏏 Clicket</h1>

      <h2>Upcoming Matches</h2>
      <ul>
        {matches.map((m, i) => (
          <li key={i}>
            {m.ID}: {m.team1} vs {m.team2} — {m.scheduledDate}
          </li>
        ))}
      </ul>

      <h2>League Table</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Team</th>
            <th>Played</th>
            <th>Won</th>
            <th>Lost</th>
            <th>Tied</th>
            <th>Points</th>
            <th>NRR</th>
          </tr>
        </thead>
        <tbody>
          {league.map((team, i) => (
            <tr key={i}>
              <td><Link to={`google.com`}>{team.name}</Link></td>
              <td>{team.played}</td>
              <td>{team.won}</td>
              <td>{team.lost}</td>
              <td>{team.tied}</td>
              <td>{team.won * 2.0 + team.tied*1.0}</td>
              <td>{team.NRR}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
