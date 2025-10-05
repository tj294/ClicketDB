import React, { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import "./GamePage.css";
import Collapsible from "../components/collapsible";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const API_URL = import.meta.env.VITE_API_URL;

export default function AboutPage() {
  return (
    <div>
      <h1>What is Clicket?</h1>
      <p>Clicket is a simulated cricket league created by Tom Joshi-Hartley where randomly generated players compete in live, simulated cricket matches. Matches run on the hour between 9am and 9pm, and you can bet <FontAwesomeIcon icon='coins' /> coins on the results of the matches. Currently, coins cannot be spent, but stay tuned!</p>
        
      <p>Clicket is a `splort', in the same vein as <a href='https://www.blaseball.com'>Blaseball</a> (R.I.V), the <a href='https://www.thedigitalfootball.com/'>Digital Football League</a>, <a href='https://mmolb.com'>MMOLB</a> and more! It was heavily inspired by Blaseball, and many of the names in the namelists are cribbed from it. Thanks to <a href='https://www.thegameband.com/'>The Game Band</a> for creating Blaseball!</p>

      <h2>Who am I?</h2>
      <p>Clicket was created and is maintained by me, Tom Joshi-Hartley! When I'm not working on Clicket, I can be found playing and watching cricket, or researching astrophysical fluid flows at the University of Exeter.</p>

      <h2>Roadmap</h2>
      <p>Below, in no particular order, are a list of planned additions in Clicket's future. Implementation depends on me having enough time to work on them.</p>
      <ul>
        <li>Improve the simulation to make player stats more important.</li>
        <li>Add the ability to spend coins on votes to improve your favourite team by adding attributes with special effects to players and teams.</li>
        <li>Add player retirements and player generation to keep the simulation fresh!</li>
      </ul>
    </div>
  )
}
