import { useState } from "react";
import './TeamsList.css';

export default function TeamList() {
  const [teamData, setTeamData] = useState(null);


  return (
    <div style={{ padding: "1rem" }}>
      <h1>Teams</h1>
      <ul>
        <li><a className='team-link' href='/team/1'>Birmingham Bullfrogs</a></li>
        <li><a className='team-link' href='/team/2'>Yorkshire Puddings</a></li>
        <li><a className='team-link' href='/team/3'>Parliamentary Penpushers</a></li>
        <li><a className='team-link' href='/team/4'>Edinburgh XI</a></li>
        <li><a className='team-link' href='/team/5'>Devon Devils</a></li>
        <li><a className='team-link' href='/team/6'>Cardiff Cwtchers</a></li>
        <li><a className='team-link' href='/team/7'>Brighton Beachcombers</a></li>
        <li><a className='team-link' href='/team/8'>Cornwall Catastrophes</a></li>
        <li><a className='team-link' href='/team/9'>Manchester Monsters</a></li>
        <li><a className='team-link' href='/team/10'>Bristol Bats</a></li>
        <li><a className='team-link' href='/team/11'>Glasgow Goofballs</a></li>
        <li><a className='team-link' href='/team/12'>Nottingham Nightingales</a></li>
      </ul>
    </div>
  )
}