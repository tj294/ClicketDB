import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import './TeamPage.css';
import { Link } from "react-router-dom";

export default function TeamPage() {
  const { id } = useParams(); // The team ID from the URL
  const [teamData, setTeamData] = useState(null);


  useEffect(() => {
    // Fetch team info
    fetch(`http://127.0.0.1:8000/team/${id}`)
      .then((res) => res.json())
      .then((data) => setTeamData(data));
  }, [id]);

  if (!teamData) {
    return <p>Loading team details...</p>;
  }

  return (
    <div style={{ padding: "1rem", fontFamily: "Trebuchet MS"}}>
      <h1>{teamData.team.name}</h1>
      <table className='history'>
        <thead>
          <tr>
            <th>Played</th>
            <th>Won</th>
            <th>Lost</th>
            <th>Tied</th>
            <th>Points</th>
            <th>NRR</th>
          </tr>
        </thead>
        <tbody className='history'>
          <tr>
            <td>{teamData.team.played}</td>
            <td>{teamData.team.won}</td>
            <td>{teamData.team.lost}</td>
            <td>{teamData.team.tied}</td>
            <td>{teamData.team.won * 2.0 + teamData.team.tied}</td>
            <td>{teamData.team.NRR}</td>
            </tr>
        </tbody>
      </table>

      <h2>Playing XI</h2>
      <table className='playing-xi'>
        <thead className='playing-xi'>
          <tr className='playing-xi'>
            <th>Name</th>
            <th>Power</th>
            <th>Technique</th>
            <th>Aggression</th>
            <th>Patience</th>
            <th>Pace</th>
            <th>Movement</th>
            <th>Accuracy</th>
            <th>Length</th>
            <th>Overall</th>
          </tr>
        </thead>
        <tbody>
          {teamData.players.map(player => (
            <tr className='playing-xi' key={player.id}>
              <td><Link to={`/player/${player.playerID}`}>{player.fname} {player.lname}</Link></td>
              <td>{player.power?.toFixed(3)}</td>
              <td>{player.technique?.toFixed(3)}</td>
              <td>{player.aggression?.toFixed(3)}</td>
              <td>{player.patience?.toFixed(3)}</td>
              <td>{player.pace?.toFixed(3)}</td>
              <td>{player.movement?.toFixed(3)}</td>
              <td>{player.accuracy?.toFixed(3)}</td>
              <td>{player.length?.toFixed(3)}</td>
              <td><strong>{
                ((player.power + player.technique + player.aggression + player.patience +player.pace + player.movement + player.accuracy + player.length) / 8).toFixed(3)
                }</strong></td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
}
