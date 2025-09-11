import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
// import './LeaguePage.css';

const API_URL = import.meta.env.VITE_API_URL;
const teamList = {
        1: 'Lincoln Lightning',
        2: 'Birmingham Bullfrogs',
        3: 'Cornwall Catastrophes',
        4: 'Brighton Beachcombers',
        5: 'Manchester Monsters',
        6: 'Cardiff Cwtchers',
        7: 'Bristol Bats',
        8: 'Devon Devils',
        9: 'Parliamentary Penpushers',
        10: 'Glasgow Goofballs',
        11: 'Edinburgh XI',
        12: 'Yorkshire Puddings'
}
    
function SeasonSchedule({seasonID}) {
  const [season, setSeason] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTeam, setSelectedTeam] = useState("");

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

  const filtered = selectedTeam ? season.filter(
    m => m.homeTeamID.toString() === selectedTeam || m.awayTeamID.toString() === selectedTeam
  ) : season;

  // Group matches by round
  const rounds = filtered.reduce((acc, match) => {
    if (!acc[match.round]) acc[match.round] = [];
    acc[match.round].push(match);
    return acc;
  }, {});

  return (
    <div>
      {/* Filter Dropdown */}
      <br></br>
      <label>
        Filter by team: {" "}
        <select value={selectedTeam} onChange={e => setSelectedTeam(e.target.value)}>
          <option value=''>All Teams</option>
          {Object.entries(teamList).map(([id, name]) => (
            <option key={id} value={id}>{name}</option>
          ))}
        </select>
      </label>

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
  const [seasons, setSeasons] = useState([]);
  const [league, setLeague] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState("1");

  useEffect(() => {
    fetch("/api/season/all")
      .then(res => res.json())
      .then(data => {
        setSeasons(data);
        if (data.length > 0) {
          const latest = Math.max(...data);
          setSelectedSeason(latest.toString());
        }
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h1>Fixtures & Results</h1>

      {seasons.length > 0 && (
        <label>
          <select name='dropdown' 
        value={selectedSeason}
        onChange={e => setSelectedSeason(e.target.value)}
        >
            {seasons.map(season => (
              <option key={season} value={season}>Season {season}</option>
          ))}
        </select>
      </label>
      )}

    <SeasonSchedule seasonID={selectedSeason} />

    </div>
  )

}