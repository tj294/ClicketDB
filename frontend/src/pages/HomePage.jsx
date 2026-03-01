import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import './HomePage.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function HomePage() {
  const [matches, setMatches] = useState([]);
  const [league, setLeague] = useState([]);

  useEffect(() => {
        fetch(`${API_URL}/upcoming_matches`)
        .then((res) => res.json())
        .then((data) => setMatches(data))
        .catch(err => console.error(err));

        fetch(`${API_URL}/league_table`)
        .then((res) => res.json())
        .then((data) => setLeague(data))
        .catch(err => console.error(err));
  }, []);

  return (
    <div className="main" style={{ padding: "20px", fontFamily: "Trebuchet MS"}}>
       <h1>🏏 Clicket</h1>
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
          {console.table(league)}
          <tbody>
            {league.map((team, i) => (
              <tr key={i}>
                <td className='team-link'><Link to={`/team/${team.teamID}`} className='team-link' style={{color: team.color}}>{team.name}</Link></td>
                <td>{team.played}</td>
                <td>{team.wins}</td>
                <td>{team.losses}</td>
                <td>{team.ties}</td>
                <td>{team.points}</td>
                <td>{team.NRR}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h2>Upcoming Matches</h2>
        <ul>
          {matches.map((m, i) => (
            <li key={i}>
              <Link to={`/game/${m.ID}`}>{m.team1} vs {m.team2} — {m.scheduledDate}</Link>
            </li>
          ))}
        </ul>
    </div>
  );
}

