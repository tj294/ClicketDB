import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
// import "./PlayerPage.css";

export default function PlayerPage() {
  const { id } = useParams(); // The team ID from the URL
  const [playerData, setPlayerData] = useState(null);


  useEffect(() => {
    // Fetch team info
    fetch(`http://127.0.0.1:8000/player/${id}`)
      .then((res) => res.json())
      .then((data) => setPlayerData(data));
  }, [id]);

  if (!playerData) {
    return <p>Error 404: Player Page not implemented</p>;
  }

  return (
    <div>
      <h1>{playerData.player.fname} {playerData.player.lname}</h1>
      <h2><Link to={`/team/${playerData.team.teamID}`}>{playerData.team.name}</Link></h2>
      <h3>Career Stats</h3>
      {playerData.player.matches_played != 1 ? <p>From {playerData.player.matches_played} matches.</p> : <p>From {playerData.player.matches_played} match.</p>}
      <h4>Batting Stats</h4>
      <table style={{alignSelf: 'left', marginLeft: 0, }}>
        <thead>
          <tr>
            <th>Innings</th>
            <th>Runs</th>
            <th>Balls Faced</th>
            <th>Highest Score</th>
            <th title="Runs Scored per Dismissal">Batting Ave.</th>
            <th title="Runs Scored per ball (%)">Strike Rate</th>
            <th>50s</th>
            <th>100s</th>
            <th>4s</th>
            <th>6s</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{playerData.player.innings_batted}</td>
            <td>{playerData.player.runs_scored}</td>
            <td>{playerData.player.balls_faced}</td>
            <td><Link to={`/game/${playerData.player.best_bat_ID}`}>{playerData.player.highest_score} ({playerData.player.highest_balls_faced})</Link></td>
            <td>{playerData.player.bat_average.toFixed(2)}</td>
            <td>{playerData.player.bat_sr.toFixed(2)}</td>
            <td>{playerData.player.fifties}</td>
            <td>{playerData.player.hundreds}</td>
            <td>{playerData.player.fours}</td>
            <td>{playerData.player.sixes}</td>
          </tr>
        </tbody>
      </table>
      <h4>Bowling Stats</h4>
      <table style={{alignSelf: 'left', marginLeft: 0,}}>
        <thead>
          <tr>
            <th>Innings</th>
            <th>Overs</th>
            <th>Maidens</th>
            <th title="Runs Conceded">Runs</th>
            <th title="Wickets Taken">Wickets</th>
            <th>Best</th>
            <th title="Runs Conceded per Wicket">Average</th>
            <th title="Runs Conceded per Over">Economy</th>
            <th title="Balls Bowled per Wicket">Strike Rate</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{playerData.player.innings_bowled}</td>
            <td>{playerData.player.overs_bowled}</td>
            <td>{playerData.player.maidens_bowled}</td>
            <td>{playerData.player.runs_conceded}</td>
            <td>{playerData.player.wickets_taken}</td>
            <td><Link to={`/game/${playerData.player.best_bowl_ID}`}>{playerData.player.best_figures_wickets}-{playerData.player.best_figures_runs}</Link></td>
            <td>{playerData.player.bowl_ave.toFixed(2)}</td>
            <td>{playerData.player.economy.toFixed(2)}</td>
            <td>{playerData.player.bowl_sr.toFixed(2)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
};