// import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuth } from "../components/AuthContext"
import './SchedulePage.css';

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

function MatchBetting({ match, user, played}) {
  const [showForm, setShowForm] = useState(false);
  const [bet, setBet] = useState(null);
  const [amount, setAmount] = useState(0);
  const { updateCoins } = useAuth();

  if (!user) {
    return <></>
  }

  useEffect(() => {
    fetch(`/api/bets/${user.userID}/${match.matchID}`)
      .then(res => res.json())
      .then(data => {
        if (data.bet) {
          setBet(data);
        }
        });
  }, [match.matchID, user.userID]);

  const handlePlaceBet = async (amount, homeTeamID, awayTeamID) => {
    let teamID;
    if (amount < 0) {
      teamID = homeTeamID;
    } else {
      teamID = awayTeamID;
    }

    const res = await fetch("/api/bets/place", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        userID: user.userID,
        matchID: match.matchID,
        teamID: teamID,
        amount: parseInt(Math.abs(amount), 10)
      }),
    });
    
    const newTotal = user.coins - parseInt(Math.abs(amount), 10);
    updateCoins(newTotal);

    const data = await res.json();
    if (data.success) {
      setBet({ teamID, amount });
      setShowForm(false);
    } else {
      alert(data.error);
    }
  };
  if (played === '1') {
    if (bet) {
      console.log(bet)
      // const teamName = bet.teamID === match.homeTeamID ? match.homeTeamName : match.awayTeamName;
      if (bet.payout > 0) {
        return <span> +<FontAwesomeIcon icon='coins' />{bet.payout}</span>
      }
      return (
          <span> -<FontAwesomeIcon icon='coins' />{bet.amount}</span>
      );
    }
  } else {
    if (bet) {
      console.log(bet)
      const teamName = bet.teamID === match.homeTeamID ? match.homeTeamName : match.awayTeamName;
      return <p><FontAwesomeIcon icon='coins' />{Math.abs(bet.amount)} bet on {teamName}</p>;
    }
    return (
      <>
        {!showForm && (
          <button onClick={() => setShowForm(true)}>Place a bet</button>
        )}
        {showForm && (
          <div className='bet-popup'>
            <span className='close-button' onClick={() => setShowForm(false)}>&times;</span>
            <p>You have <FontAwesomeIcon icon='coins' />{user.coins}!</p>
            <p>
              Betting: <FontAwesomeIcon icon='coins' /> {amount === 0
                ? "No bet"
                : amount < 0
                  ? `${Math.abs(amount)} on ${match.homeTeamName}`
                  : `${amount} on ${match.awayTeamName}`}
            </p>
            <div className="betting-labels" style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: `${match.homeTeamColor}` }}>{match.homeTeamName}</span>
              <span style={{ color: `${match.awayTeamColor}` }}>{match.awayTeamName}</span>
            </div>
            <input
              type='range'
              min={-user.coins}
              max={user.coins}
              step='1'
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              style={{
                width: "100%",
                accentColor: amount < 0 ? match.homeTeamColor : amount > 0 ? match.awayTeamColor : "gray",
                background: `linear-gradient(
                  to right,
                  ${match.homeTeamColor} 0%,
                  ${match.homeTeamColor} 50%,
                  ${match.awayTeamColor} 50%,
                  ${match.awayTeamColor} 100%
                )`,
                borderRadius: "6px",
                height: "8px",
                appearance: "none",
              }}
            />
            <button disabled={amount === 0} onClick={() => handlePlaceBet(amount, match.homeTeamID, match.awayTeamID)}>Place Bet</button>
          </div>
        )}
      </>
    );
  }
}

function SeasonSchedule({seasonID, user}) {
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
        {"  "}<FontAwesomeIcon icon={"circle-xmark"} onClick={() => setSelectedTeam("")}/>
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
                  if (m.matchPlayed === 1) statusText = <span><Link to={`/game/${m.matchID}`} style={{ color: `${m.winColor}` }}>{m.result}</Link> <MatchBetting match={m} user={user} played='1'/></span>;
                  else if (m.matchPlayed === -1) statusText = <Link to={`/live` } style={{backgroundColor: 'crimson', padding: '0.3rem', borderRadius: '0.2rem', }}>LIVE!</Link>;
                  else statusText = <span><Link to={`/game/${m.matchID}`}>Upcoming</Link> <MatchBetting match={m} user={user} played='0'/></span>;

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
  // const [league, setLeague] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState("1");
  const { user } = useAuth();

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
    <div className='main'>
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

      <SeasonSchedule seasonID={selectedSeason} user={user} />

    </div>
  )

}