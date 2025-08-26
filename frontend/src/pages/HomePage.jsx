import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import './HomePage.css';

export default function HomePage() {
  const [matches, setMatches] = useState([]);
  const [league, setLeague] = useState([]);

  useEffect(() => {
        axios.get("/upcoming_matches")
        .then(res => setMatches(res.data))
        .catch(err => console.error(err));

        axios.get("/league_table")
        .then(res => setLeague(res.data))
        .catch(err => console.error(err));
  }, []);

  return (
    <div className="main" style={{ padding: "20px", fontFamily: "Trebuchet MS"}}>
       <h1>🏏 Clicket</h1>
        <h2>Upcoming Matches</h2>
        <ul>
          {matches.map((m, i) => (
            <li key={i}>
              <Link to={`/game/${m.ID}`}>{m.team1} vs {m.team2} — {m.scheduledDate}</Link>
            </li>
          ))}
        </ul>
      <h2>League Table</h2>
      <div className="league-table">
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
                <td className='team-link'><Link to={`/team/${team.ID}`} className='team-link'>{team.name}</Link></td>
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
    </div>
  );
}

