import React, { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import "./GamePage.css";
import Collapsible from "../components/collapsible";

const API_URL = import.meta.env.VITE_API_URL;
const WS_URL = import.meta.env.VITE_WS_URL;
const protocol = location.protocol === "https:" ? "wss:" : "ws:";

export default function GamePage() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [tab, setTab] = useState("overview");

  useEffect(() => {
    // open websocket
    const ws = new WebSocket(`${protocol}//${location.host}/ws/game/${id}`);

    // when a message arrives:
    ws.onopen = () => console.log("WebSocket open!")
    ws.onerror = (err) => console.error("WebSocket error:", err);
    ws.onclose = () => console.log("WebSocket closed.");
    
    ws.onmessage = (event) => {
      console.log("WebSocket sending data:")
      const data = JSON.parse(event.data);
      setMatch(data);
      console.log(data);
    };

    // Close socket when unmounts
    return () => ws.close(); 
  }, [id]);
  
  function SecondInningsScorecard( ) {
    const hasStarted = Array.isArray(match.sbattingCard);

    return (
      <div className='second-innings'>
        <Collapsible 
          id="second-innings"
          startOpen={false}
          disabled={!hasStarted}
          autoOpenWhenEnabled={true}
          label={
            <>
              <strong style={{fontSize: 20}}>{match.bsName}</strong> &nbsp;&nbsp;
                {hasStarted ? `T: ${match.bfRuns} runs from 20 overs` : "Yet to Bat"}
            </>
          }
        >
          {hasStarted ? (
            <>
              <table className='score-table'>
                <thead style={{textAlign: "left"}}>
                  <tr>
                    <th>Batter</th>
                    <th>R</th>
                    <th>B</th>
                    <th style={{textAlign:"right"}}>How Out</th>
                  </tr>
                </thead>
                <tbody>
                  {match.sbattingCard.map((player, idx) => (
                    <tr key={idx}>
                      <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                      <td>{player.runs}</td>
                      <td>{player.balls}</td>
                      <td style={{textAlign:"right"}}>{player.howOut}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p>
                Yet to Bat:{" "}
                {match.syetToBat.map((player, idx) => (
                  <React.Fragment key={idx}>
                    <Link to={`/player/${player.ID}`}>{player.name}</Link>,{" "}
                  </React.Fragment>
                ))}
              </p>
            </>
          ) : (
            <p style={{padding: "10px", fontSize: 15}}>Yet To Bat</p>
          )}
        </Collapsible>
      </div>
    );
  };

  if (!match) {
    return <div>Match not found.</div>
  }
  if (match.status === "Upcoming") {
    const roundDate = new Date(match.date);
    const roundDateStr = roundDate.toLocaleDateString([],{
      weekday: 'long',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
    const roundTimeStr = roundDate.toLocaleTimeString([],{
      hour: '2-digit',
      minute: '2-digit'
    })
    return (
      <div>
        <div className='match-title'>
          <h3>{match.homeTeam} vs {match.awayTeam}, Season {match.season} Match {match.match}</h3>
        </div>
        <div className='container'>
          <div className='team-totals'>
            <p><strong><Link to={`/team/${match.homeTeamID}`} style={{color: `${match.homeTeamColor}`}}>{match.homeTeam}</Link></strong></p>
            <p><strong><Link to={`/team/${match.awayTeamID}`} style={{color: `${match.awayTeamColor}`}}>{match.awayTeam}</Link></strong></p>
            <p>Match begins at {roundTimeStr} on {roundDateStr}</p>
          </div>
          <div className='squads'>
            <div className='squad' id='home-squad'>
              <h3 style={{color: `${match.homeTeamColor}`}}>{match.homeTeam}</h3>
              {match.homePlayers.map((player, idx) => (
                <p key={player.playerID}>{idx+1}: <Link to={`/player/${player.playerID}`}>{player.fname} {player.lname}</Link></p>
              ))}
            </div>
            <div className='squad' id='away-squad'>
              <h3 style={{color: `${match.awayTeamColor}`}}>{match.awayTeam}</h3>
              {match.awayPlayers.map((player, idx) => (
                <p key={player.playerID}>{idx+1}: <Link to={`/player/${player.playerID}`}>{player.fname} {player.lname}</Link></p>
              ))}
            </div>
          </div>
          <div className='points'>
            <strong>Points</strong>
            <table id='points-table'>
              <thead>
                <tr>
                  <th>Team</th>
                  <th title='Matches Played'>M</th>
                  <th title='Wins'>W</th>
                  <th title='Losses'>L</th>
                  <th title='Points'>PTS</th>
                  <th title='Net Run Rate'>NRR</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><Link to={`/team/${match.homeTeamID}`} style={{color: `${match.homeTeamColor}`}}>{match.homeTeam}</Link></td>
                  <td>{match.homeTeamTable.M}</td>
                  <td>{match.homeTeamTable.W}</td>
                  <td>{match.homeTeamTable.L}</td>
                  <td><strong>{match.homeTeamTable.PTS}</strong></td>
                  <td>{match.homeTeamTable.NRR.toFixed(2)}</td>
                </tr>
                <tr>
                  <td><Link to={`/team/${match.awayTeamID}`} style={{color: `${match.awayTeamColor}`}}>{match.awayTeam}</Link></td>
                  <td>{match.awayTeamTable.M}</td>
                  <td>{match.awayTeamTable.W}</td>
                  <td>{match.awayTeamTable.L}</td>
                  <td><strong>{match.awayTeamTable.PTS}</strong></td>
                  <td>{match.awayTeamTable.NRR.toFixed(2)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  } else if (match.status === "played") {
    let bsScore = match.bsRuns.toString().concat('/',match.bsWickets).concat(' (', match.bsOvers).concat('', '/20)');
    return (
      <div>
        {tab === "overview" && (
        <div>
            <div className='match-title'><h3>{match.homeTeam} vs {match.awayTeam}, Season {match.season} Match {match.match}</h3></div>
          <div className="container">
            <div className='team-totals'>
              <p><strong><Link to={`/team/${match.bfID}`} style={{color: `${match.homeTeamColor}`}}>{match.bfName}</Link></strong> {match.bfRuns}/{match.bfWickets} ({match.bfOvers}/20.0) CRR: {match.bfCRR.toFixed(2)}</p>

              <p><strong><Link to={`/team/${match.bsID}`} style={{color: `${match.awayTeamColor}`}}>{match.bsName}</Link></strong> {bsScore}</p>

              <p>{match.ballText}</p>
              <div className='tab-buttons'>
                <button onClick={() => setTab("overview")} className='tab-button' id="overview-button">Overview</button>
                <button className='tab-button' onClick={() => setTab("scoreboard")} id='scoreboard-button'>Scoreboard</button>
              </div>
            </div>
            <div className='summary'>
              <div className='batters'>
                <table className='summary-table'>
                  <thead className='summary-thead'>
                    <tr>
                      <th>
                        Batters
                      </th>
                      <th title='Runs Scored'>
                        R
                      </th>
                      <th title='Balls Faced'>
                        B
                      </th>
                      <th title='Fours'>
                        4s
                      </th>
                      <th title='Sixes'>
                        6s
                      </th>
                      <th title='Strike Rate'>
                        SR
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td id='striker'><Link to={`/player/${match.strikeID}`}>{match.strikeFName} {match.strikeLName}</Link></td>
                      <td>{match.strikeRuns}</td>
                      <td>{match.strikeBalls}</td>
                      <td>{match.strikeFours}</td>
                      <td>{match.strikeSixes}</td>
                      <td>{match.strikeSR.toFixed(2)}</td>
                    </tr>
                    <tr>
                      <td id='non-striker'><Link to={`/player/${match.nstrikeID}`}>{match.nstrikeFName} {match.nstrikeLName}</Link></td>
                      <td>{match.nstrikeRuns}</td>
                      <td>{match.nstrikeBalls}</td>
                      <td>{match.nstrikeFours}</td>
                      <td>{match.nstrikeSixes}</td>
                      <td>{match.nstrikeSR.toFixed(2)}</td>
                    </tr>
                    <tr className="summary-thead">
                      <td>Bowlers</td>
                      <td>O</td>
                      <td>M</td>
                      <td>R</td>
                      <td>W</td>
                      <td>Econ.</td>
                    </tr>
                    <tr>
                      <td id='striker'><Link to={`/player/${match.sbowlID}`}>{match.sbowlFName} {match.sbowlLName}</Link></td>
                      <td>{match.sbowlOvers}</td>
                      <td>{match.sbowlMaidens}</td>
                      <td>{match.sbowlRuns}</td>
                      <td>{match.sbowlWickets}</td>
                      <td>{match.sbowlEcon.toFixed(2)}</td>
                    </tr>
                    <tr>
                      <td id='non-striker'><Link to={`/player/${match.nsbowlID}`}>{match.nsbowlFName} {match.nsbowlLName}</Link></td>
                      <td>{match.nsbowlOvers}</td>
                      <td>{match.nsbowlMaidens}</td>
                      <td>{match.nsbowlRuns}</td>
                      <td>{match.nsbowlWickets}</td>
                      <td>{match.nsbowlEcon.toFixed(2)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              {/* <div className='bowlers'>
                <table className='summary-table'>
                  <thead className='summary-thead'>
                    <tr>
                      <th>
                        Bowlers
                      </th>
                      <th title='Overs'>
                        O
                      </th>
                      <th title='Maidens'>
                        M
                      </th>
                      <th title='Runs Conceded'>
                        R
                      </th>
                      <th title='Wickets Taken'>
                        W
                      </th>
                      <th title='Economy'>
                        Econ. 
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td id='striker'><Link to={`/player/${match.sbowlID}`}>{match.sbowlFName} {match.sbowlLName}</Link></td>
                      <td>{match.sbowlOvers}</td>
                      <td>{match.sbowlMaidens}</td>
                      <td>{match.sbowlRuns}</td>
                      <td>{match.sbowlWickets}</td>
                      <td>{match.sbowlEcon.toFixed(2)}</td>
                    </tr>
                    <tr>
                      <td id='non-striker'><Link to={`/player/${match.nsbowlID}`}>{match.nsbowlFName} {match.nsbowlLName}</Link></td>
                      <td>{match.nsbowlOvers}</td>
                      <td>{match.nsbowlMaidens}</td>
                      <td>{match.nsbowlRuns}</td>
                      <td>{match.nsbowlWickets}</td>
                      <td>{match.nsbowlEcon.toFixed(2)}</td>
                    </tr>
                  </tbody>
                </table>
              </div> */}
            </div>
            <div className='info-line'>
              <span className='recent-balls'>
                <p><strong>Over {match.currentOver}.{match.currentBall} |<wbr /> </strong> {match.overResults}</p>
              </span>
              <span className='last-bat'>
                <p>{match.lBat}</p>
              </span>
            </div>
            <div className='ball-description' style={{ maxHeight: "500px", overflowY: "auto" }}>
              {match.log.toReversed().map((ball, idx) => (
                <div className={ball.tag} key={idx}>
                  <div className="ball-update">
                    {console.log(ball)}
                    {(ball.tag==='ball-comm') ? (
                      <div className='comm-label'>
                        <div className="ball-number">
                          <span>{ball.label.split(":")[0]}</span>
                        </div>
                        <div className='ball-value'>
                          <span className={`value-${ball.value}`}>{ball.value}</span>
                        </div>
                      </div>
                    ) : (
                      <></>
                    )}
                    <div className="ball-text">
                      <p style={{marginBottom: 0}}>{ball.tag==='ball-comm' ? ball.label.split(': ')[1] : ball.label}</p>
                      <p>{ball.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        )}

        {tab === "scoreboard" && (
          <div>
            <div className='match-title'><h3>{match.homeTeam} vs {match.awayTeam}, Season {match.season} Match {match.match}</h3></div>
            <div className='team-totals-sc'>
              <p><strong><Link to={`/team/${match.bfID}`}>{match.bfName}</Link></strong> {match.bfRuns}/{match.bfWickets} ({match.bfOvers}/20.0) CRR: {match.bfCRR.toFixed(2)}</p>

              <p><strong><Link to={`/team/${match.bsID}`}>{match.bsName}</Link></strong> {bsScore}</p>
              
              <p>{match.ballText}</p>
              <div className='tab-buttons'>
                <button onClick={() => setTab("overview")} className='tab-button' style={{borderBottomLeftRadius:"1em"}} id='overview-button'>Overview</button>
                <button className='tab-button' onClick={() => setTab("scoreboard")} style={{borderBottomRightRadius:"1em"}} id='scoreboard-button'>Scoreboard</button>
              </div>
            </div>
            <div className='scorecard'>
              {/* <div className='first-innings'> */}
                <Collapsible 
                  id='first-inning'
                  startOpen={true}
                  label={<><strong style={{fontSize: 20}}>{match.bfName}</strong></>}
                  teamColor={`${match.homeTeamColor}`}
                >
                  <table className='score-table'>
                    <thead style={{textAlign: "left"}}>
                      <tr>
                        <th style={{width: "25%"}}>Batter</th>
                        <th style={{width: "25%"}}>How Out</th>
                        <th style={{width: "10%", textAlign:"center"}}>R</th>
                        <th style={{width: "10%", textAlign:"center"}}>B</th>
                        <th style={{width: "10%", textAlign:"center"}}>4s</th>
                        <th style={{width: "10%", textAlign:"center"}}>6s</th>
                        <th style={{width: "10%", textAlign:"right"}}>SR</th>
                      </tr>
                    </thead>
                    <tbody>
                      {match.fbattingCard.map((player, idx) => (
                        <tr key={idx}>
                          <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                          <td>{player.howOut}</td>
                          <td style={{textAlign:"center"}}>{player.runs}</td>
                          <td style={{textAlign:"center"}}>{player.balls}</td>
                          <td style={{textAlign:"center"}}>{player.fours}</td>
                          <td style={{textAlign:"center"}}>{player.sixes}</td>
                          <td style={{textAlign:"right"}}>{player.SR.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>  
                  <p>
                  Yet to Bat: {match.fyetToBat.map((player, idx) => (
                    <React.Fragment key={idx}><Link to={`/player/${player.ID}`}>{player.name}</Link>, </React.Fragment>
                  ))}
                  </p><hr />
                  <table className='score-table'>
                    <thead>
                      <tr>
                        <th style={{width: "50%", textAlign: "left"}}>Bowler</th>
                        <th style={{width: "10%", textAlign: "center"}}>O</th>
                        <th style={{width: "10%", textAlign: "center"}}>M</th>
                        <th style={{width: "10%", textAlign: "center"}}>R</th>
                        <th style={{width: "10%", textAlign: "center"}}>W</th>
                        <th style={{width: "10%", textAlign:"right"}}>Econ.</th>
                      </tr>
                    </thead>
                    <tbody>
                      {match.fbowlingCard.map((player, idx) => (
                        <tr key={idx}>
                          <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                          <td style={{textAlign:"center"}}>{player.overs.toFixed(1)}</td>
                          <td style={{textAlign:"center"}}>{player.maidens}</td>
                          <td style={{textAlign:"center"}}>{player.runs}</td>
                          <td style={{textAlign:"center"}}><strong>{player.wickets}</strong></td>
                          <td style={{textAlign:"right"}}>{player.econ}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Collapsible>
              {/* </div> */}
            </div>
            <div className={match.sbattingCard ? 'scorecard' : 'fake-scorecard'}>
              <div className={'second-innings'}>
                {match.sbattingCard ? (
                  <Collapsible
                    id='second-innings'
                    startOpen={true}
                    label={<><strong style={{fontSize: 20}}>{match.bsName}</strong>&nbsp;&nbsp;T: {match.bfRuns+1} in 20 overs</>}
                    teamColor={`${match.awayTeamColor}`}
                  >
                    <table className='score-table'>
                      <thead style={{textAlign: "left"}}>
                        <tr>
                          <th style={{width: "25%"}}>Batter</th>
                          <th style={{width: "25%"}}>How Out</th>
                          <th style={{width: "10%", textAlign:"center"}}>R</th>
                          <th style={{width: "10%", textAlign:"center"}}>B</th>
                          <th style={{width: "10%", textAlign:"center"}}>4s</th>
                          <th style={{width: "10%", textAlign:"center"}}>6s</th>
                          <th style={{width: "10%", textAlign:"right"}}>SR</th>
                        </tr>
                      </thead>
                      <tbody style={{textAlign: "left"}}>
                        {match.sbattingCard.map((player, idx) => (
                          <tr key={idx}>
                            <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                            <td>{player.howOut}</td>
                            <td style={{textAlign:"center"}}>{player.runs}</td>
                            <td style={{textAlign:"center"}}>{player.balls}</td>
                            <td style={{textAlign:"center"}}>{player.fours}</td>
                            <td style={{textAlign:"center"}}>{player.sixes}</td>
                            <td style={{textAlign:"right"}}>{player.SR.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p>
                      Yet to Bat:{" "}
                      {match.syetToBat.map((player, idx) => (
                        <React.Fragment key={idx}>
                          <Link to={`/player/${player.ID}`}>{player.name}</Link>,{" "}
                        </React.Fragment>
                      ))}
                    </p><hr />
                    <table className='score-table'>
                      <thead>
                        <tr>
                          <th style={{width: "50%", textAlign: "center"}}>Bowler</th>
                          <th style={{width: "10%", textAlign: "center"}}>O</th>
                          <th style={{width: "10%", textAlign: "center"}}>M</th>
                          <th style={{width: "10%", textAlign: "center"}}>R</th>
                          <th style={{width: "10%", textAlign: "center"}}>W</th>
                          <th style={{width: "10%", textAlign:"right"}}>Econ.</th>
                        </tr>
                      </thead>
                      <tbody>
                        {match.sbowlingCard.map((player, idx) => (
                          <tr key={idx}>
                            <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                            <td style={{textAlign:"center"}}>{player.overs.toFixed(1)}</td>
                            <td style={{textAlign:"center"}}>{player.maidens}</td>
                            <td style={{textAlign:"center"}}>{player.runs}</td>
                            <td style={{textAlign:"center"}}><strong>{player.wickets}</strong></td>
                            <td style={{textAlign:"right"}}>{player.econ}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Collapsible>
                ) : (
                    <div>
                      <p style={{paddingLeft: "1em"}}><strong style={{fontSize: 20}}>{match.bsName}</strong>&nbsp;&nbsp; Yet to Bat</p>
                    </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  } else if (match.status === "Live") {
    let bsScore;
    if (!(match.bsOvers === "YTB")) {
      // Second Innings
      bsScore = match.bsRuns.toString().concat('/',match.bsWickets).concat(' (', match.bsOvers).concat('', '/20)').concat(' CRR: ', match.bsCRR.toFixed(2)).concat(', Req. RR: ', match.bsRRR.toFixed(2))
    } else {
      // First Innings
      bsScore = "Yet To Bat";
    }

    return (
      <div>

        {tab === "overview" && (
        <div>
          <div className='match-title'><h3>{match.homeTeam} vs {match.awayTeam}, Season {match.season} Match {match.match}</h3></div>
            <div className='container'>
              <div className='team-totals'>
                <p><strong><Link to={`/team/${match.bfID}`} style={{color: `${match.homeTeamColor}`}}>{match.bfName}</Link></strong> {match.bfRuns}/{match.bfWickets} ({match.bfOvers}/20.0) CRR: {match.bfCRR.toFixed(2)}</p>

                <p><strong><Link to={`/team/${match.bsID}`} style={{color: `${match.awayTeamColor}`}}>{match.bsName}</Link></strong> {bsScore}</p>
                <div className='tab-buttons'>
                  <button onClick={() => setTab("overview")} className='tab-button' id="overview-button">Overview</button>
                  <button className='tab-button' onClick={() => setTab("scoreboard")} id='scoreboard-button'>Scoreboard</button>
                </div>
              </div>
              <div className='summary'>
                <div className='batters'>
                  <table className='summary-table'>
                    <thead className='summary-thead'>
                      <tr>
                        <th>
                          Batters
                        </th>
                        <th title='Runs Scored'>
                          R
                        </th>
                        <th title='Balls Faced'>
                          B
                        </th>
                        <th title='Fours'>
                          4s
                        </th>
                        <th title='Sixes'>
                          6s
                        </th>
                        <th title='Strike Rate'>
                          SR
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td id='striker'><Link to={`/player/${match.strikeID}`}>{match.strikeFName} {match.strikeLName}</Link></td>
                        <td>{match.strikeRuns}</td>
                        <td>{match.strikeBalls}</td>
                        <td>{match.strikeFours}</td>
                        <td>{match.strikeSixes}</td>
                        <td>{match.strikeSR.toFixed(2)}</td>
                      </tr>
                      <tr>
                        <td id='non-striker'><Link to={`/player/${match.nstrikeID}`}>{match.nstrikeFName} {match.nstrikeLName}</Link></td>
                        <td>{match.nstrikeRuns}</td>
                        <td>{match.nstrikeBalls}</td>
                        <td>{match.nstrikeFours}</td>
                        <td>{match.nstrikeSixes}</td>
                        <td>{match.nstrikeSR.toFixed(2)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div className='bowlers'>
                  <table className='summary-table'>
                    <thead className='summary-thead'>
                      <tr>
                        <th>
                          Bowlers
                        </th>
                        <th title='Overs'>
                          O
                        </th>
                        <th title='Maidens'>
                          M
                        </th>
                        <th title='Runs Conceded'>
                          R
                        </th>
                        <th title='Wickets Taken'>
                          W
                        </th>
                        <th title='Economy'>
                          Econ. 
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td id='striker'><Link to={`/player/${match.sbowlID}`}>{match.sbowlFName} {match.sbowlLName}</Link></td>
                        <td>{match.sbowlOvers}</td>
                        <td>{match.sbowlMaidens}</td>
                        <td>{match.sbowlRuns}</td>
                        <td>{match.sbowlWickets}</td>
                        <td>{match.sbowlEcon.toFixed(2)}</td>
                      </tr>
                      <tr>
                        <td id='non-striker'><Link to={`/player/${match.nsbowlID}`}>{match.nsbowlFName} {match.nsbowlLName}</Link></td>
                        <td>{match.nsbowlOvers}</td>
                        <td>{match.nsbowlMaidens}</td>
                        <td>{match.nsbowlRuns}</td>
                        <td>{match.nsbowlWickets}</td>
                        <td>{match.nsbowlEcon.toFixed(2)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div className='info-line'>
                <span className='recent-balls'>
                  <p><strong>Over {match.currentOver}.{match.currentBall} | </strong> {match.overResults}</p>
                </span>
                <span className='last-bat'>
                  <p>{match.lBat}</p>
                </span>
              </div>
              <div className='ball-description' style={{ maxHeight: "500px", overflowY: "auto" }}>
                  {match.log.toReversed().map((ball, idx) => (
                    <div className={ball.tag} key={idx}>
                      <div className="ball-update">
                        {(ball.tag==='ball-comm') ? (
                          <>
                            <div className="ball-number">
                              <span>{ball.label.split(":")[0]}</span>
                            </div>
                            <div className='ball-value'>
                              {console.log(match.overResults.split(" "))}
                              <span className={`value-${ball.value}`}>{ball.value}</span>
                            </div>
                          </>
                        ) : (
                          <></>
                        )}
                        <div className="ball-text">
                          <p>{ball.tag==='ball-comm' ? ball.label.split(': ')[1] : ball.label}</p>
                          <p>{ball.desc}</p>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
        </div>
        )}

        {tab === "scoreboard" && (
          <div>
            <div className='match-title'><h3>{match.homeTeam} vs {match.awayTeam}, Season {match.season} Match {match.match}</h3></div>
            <div className='team-totals-sc'>
              <p><strong><Link to={`/team/${match.bfID}`} style={{color: `${match.homeTeamColor}`}}>{match.bfName}</Link></strong> {match.bfRuns}/{match.bfWickets} ({match.bfOvers}/20.0) CRR: {match.bfCRR.toFixed(2)}</p>

              <p><strong><Link to={`/team/${match.bsID}`} style={{color: `${match.awayTeamColor}`}}>{match.bsName}</Link></strong> {bsScore}</p>
              <div className='tab-buttons'>
                <button onClick={() => setTab("overview")} className='tab-button' style={{borderBottomLeftRadius:"1em"}} id='overview-button'>Overview</button>
                <button className='tab-button' onClick={() => setTab("scoreboard")} style={{borderBottomRightRadius:"1em"}} id='scoreboard-button'>Scoreboard</button>
              </div>
            </div>
            <div className='scorecard'>
              <div className='first-innings'>
                <Collapsible 
                  id='first-inning'
                  startOpen={true}
                  label={<><strong style={{fontSize: 20}}>{match.bfName}</strong></>}
                  teamColor={`${match.homeTeamColor}`}
                >
                  <table className='score-table'>
                    <thead style={{textAlign: "left"}}>
                      <tr>
                        <th>Batter</th>
                        <th>R</th>
                        <th>B</th>
                        <th style={{textAlign:"right"}}>How Out</th>
                      </tr>
                    </thead>
                    <tbody>
                      {match.fbattingCard.map((player, idx) => (
                        <tr key={idx}>
                          <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                          <td>{player.runs}</td>
                          <td>{player.balls}</td>
                          <td style={{textAlign:"right"}}>{player.howOut}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>  
                  <p>
                  Yet to Bat: {match.fyetToBat.map((player, idx) => (
                    <React.Fragment key={idx}><Link to={`/player/${player.ID}`}>{player.name}</Link>, </React.Fragment>
                  ))}
                  </p>
                </Collapsible>
              </div>
            </div>
            <div className={match.sbattingCard ? 'scorecard' : 'fake-scorecard'} style={{backgroundColor: `${match.awayTeamColor}`}}>
              <div className={'second-innings'}>
                {match.sbattingCard ? (
                  <Collapsible
                    id='second-innings'
                    startOpen={true}
                    label={<><strong style={{fontSize: 20}}>{match.bsName}</strong>&nbsp;&nbsp;T: {match.bfRuns+1} in 20 overs</>}
                    teamColor={`${match.awayTeamColor}`}
                  >
                    <table className='score-table'>
                      <thead style={{textAlign: "left"}}>
                        <tr>
                          <th>Batter</th>
                          <th>R</th>
                          <th>B</th>
                          <th style={{textAlign:"right"}}>How Out</th>
                        </tr>
                      </thead>
                      <tbody>
                        {match.sbattingCard.map((player, idx) => (
                          <tr key={idx}>
                            <td><Link to={`/player/${player.ID}`}>{player.name}</Link></td>
                            <td>{player.runs}</td>
                            <td>{player.balls}</td>
                            <td style={{textAlign:"right"}}>{player.howOut}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p>
                      Yet to Bat:{" "}
                      {match.syetToBat.map((player, idx) => (
                        <React.Fragment key={idx}>
                          <Link to={`/player/${player.ID}`}>{player.name}</Link>,{" "}
                        </React.Fragment>
                      ))}
                    </p>
                  </Collapsible>
                ) : (
                    <div>
                      <p style={{paddingLeft: "1em"}}><strong style={{fontSize: 20}}>{match.bsName}</strong>&nbsp;&nbsp; Yet to Bat</p>
                    </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }
}
