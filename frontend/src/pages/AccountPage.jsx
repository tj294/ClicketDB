import { useState, useEffect } from "react"
import { useAuth } from "../components/AuthContext";
import './AccountPage.css';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export default function LoginPage() {
    const { user, setUser } = useAuth();
    const [details, setDetails] = useState([]);
    const [begSuccess, setBegSuccess] = useState(null);
    const [begError, setBegError] = useState(null);

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

    const colorList = {
        1: '#B00060',
        2: '#00B050',
        3: '#E97132',
        4: '#FE01B7',
        5: '#0055FF',
        6: '#EF000E',
        7: '#00EFE1',
        8: '#32AAE9',
        9: '#01FE48',
        10: '#7BD23C',
        11: '#933CD2',
        12: '#DCAE00'
    }

    async function handleBeg(userID) {
        setBegError(null);
        setBegSuccess(null);

        const res = await fetch(`/api/account/${userID}/beg`, {
            method: 'POST'
        })
        const data = await res.json();
        if (data['status'] === 1) {
            setBegError(data.error);
            
        } else {
            window.location.reload();
        }
    }

    async function updateFavTeam(userID, teamID) {
        const data = { userID, teamID };
        fetch(`/api/account/favTeam`, { method: 'POST', headers: { "Content-Type": "application/json", }, body: JSON.stringify(data) })
        
    }

    useEffect(() => {
        if (user) {
            fetch(`/api/account/detail/${user}`)
                .then(res => res.json())
                .then((data) => setDetails(data))
                .catch(err => console.error(err));
        }
    }, [user]);
    
    console.log(details);
 
    if (user) {
        return (
            <div>
                <h1>Logged in: {details.uname}</h1>
                {console.log(colorList[12])}
                <p>Favourite Team: 
                    <select value={details.favTeam ?? ""}
                        name='favTeam'
                        id='favTeam'
                        onChange={(e) => {
                            const newFav = e.target.value;
                            setDetails((prev) => ({
                                ...prev,
                                favTeam: newFav,
                            }));
                            updateFavTeam(details.ID, newFav);
                        }}
                        style={{color: colorList[details.favTeam]}}
                    >
                    {Object.entries(teamList).map(([teamID, tName]) => (
                        <option key={teamID}
                            value={teamID}
                            style={{ color: colorList[teamID] }}
                        >{tName}</option>
                    ))}
                </select></p>
                <p>Total Coins: <FontAwesomeIcon icon='fa-coins' /> {details.coins} <button className='beg-button' onClick={() => { handleBeg(details.ID) }}>BEG</button>
                    {begError && <span style={{ color: 'red' }}> {begError}</span>}
                </p>
            </div>
        )
    } else {
        return (
            <div>
                <h1>Log In</h1>
                <form>
                    <h2>Username</h2>
                    <h2>Password</h2>
                </form>
            </div>
        )
    }
}
