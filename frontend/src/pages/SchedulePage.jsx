import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
// import './LeaguePage.css';

const API_URL = import.meta.env.VITE_API_URL;

function SeasonSchedule({seasonID}) {
  const [season, setSeason] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/season/${seasonID}`)
    .then(res => res.json())
    .then(data => {
      setSeason(data || []);
      setLoading(false);
    })
    .catch(err => {
      console.error("Failed to fetch season:", err);
      setSeason([]);
      setLoading(false);
    });
  }, [seasonID]);

  if (loading) return <p>Loading season {seasonID}...</p>;
  if (season.length === 0) return <p>No matches found for season {seasonID}.</p>;

  // Group matches by round
  const rounds = season.reduce((acc, match) => {
    if (!acc[match.round]) acc[match.round] = [];
    acc[match.round].push(match);
    return acc;
  }, {});

  return (
    <div>
      {/* <p>This is the info for Season {seasonID}.</p>
      <ul>
          {season.map((m, i) => (
            <li key={i}>
              Round {m.round} Match {m.matchNo}: <Link to={`/team/${m.homeTeamID}`}>{m.homeTeamName}</Link> vs <Link to={`/team/${m.awayTeamID}`}>{m.awayTeamName}</Link> — {m.scheduledDate}
            </li>
            // <li></li>
          ))}
        </ul> */}
      {Object.entries(rounds).map(([round, matches]) => {
          const roundDate = new Date(matches[0].scheduledDate);
          const roundDateStr = roundDate.toLocaleDateString(undefined, {
            weekday: 'long',
            day: 'numeric',
            month: 'short',
            year: 'numeric'
          });

          return (
            <div key={round} style={{ marginBottom: "2rem" }}>
              <h3>
                Round {round} - {roundDateStr}
              </h3>
              <ul>
                {matches.map((m, i) => {
                  const time = new Date(m.scheduledDate).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  });

                  let statusText = "";
                  if (m.matchPlayed === 1) statusText = <Link to={`/game/${m.matchID}`} style={{color: `${m.winColor}`}}>{m.result}</Link>;
                  else if (m.matchPlayed === -1) statusText = <Link to={`/live` } style={{backgroundColor: 'crimson', padding: '0.3rem', borderRadius: '0.2rem', }}>LIVE!</Link>;
                  else statusText = <Link to={`/game/${m.matchID}`}>Upcoming</Link>;

                  return (
                    <li key={i}>
                      {time} - <Link to={`/team/${m.homeTeamID}`} style={{color: `${m.homeTeamColor}`}}>{m.homeTeamName}</Link> vs <Link to={`/team/${m.awayTeamID}`} style={{color: `${m.awayTeamColor}`}}>{m.awayTeamName}</Link>{" "}
                      {statusText && <strong>- {statusText}</strong>}
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })
      }
    </div>
  );
}

export default function SchedulePage() {
  const [matches, setMatches] = useState([]);
  const [league, setLeague] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState("1");

  // useEffect(() => {
  //       fetch("http://127.0.0.1:8000/upcoming_matches")
  //       .then(res => res.json())
  //       .catch(data => setMatches(data));
  // }, []);

  return (
    <div>
      <h1>Fixtures & Results</h1>
      <label> <select name='dropdown' 
      value={selectedSeason}
      onChange={e => setSelectedSeason(e.target.value)}
      >
          <option value="1">Season 1</option>
          <option value="2">Season 2</option>
          <option value="3">Season 3</option>
        </select>
      </label>

    <SeasonSchedule seasonID={selectedSeason} />

    </div>
  )

}