import { useState, useEffect } from "react"
import { useAuth } from "../components/AuthContext";
import './AccountPage.css';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export default function LoginPage() {
    const { user, setUser } = useAuth();
    const [details, setDetails] = useState([]);
    const [begSuccess, setBegSuccess] = useState(null);
    const [begError, setBegError] = useState(null);
    const [showPswd, setShowPswd] = useState(false);
    const [loginError, setLoginError] = useState(null);
    const [loginSuccess, setLoginSuccess] = useState(null);
    const [createError, setCreateError] = useState(null);
    const [createSuccess, setCreateSuccess] = useState(null);

    useEffect(() => {
        if (begError || begSuccess) {
            const timer = setTimeout(() => {
                setBegError(null);
                setBegSuccess(null);
            }, 2500); // 3 seconds

            return () => clearTimeout(timer);
        }
    }, [begError, begSuccess]);
    
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
            setUser(prev => ({
                ...prev,
                coins: prev.coins + 10
            }));

            setBegSuccess("You received 10 coins!");
        }
    }
    
    async function handleLogin(e) {
        e.preventDefault();
        setLoginError(null);
        setLoginSuccess(null);
        
        const formData = new FormData(e.currentTarget);
        
        const res = await fetch("/api/account/login", {
        method: 'POST',
        body: formData,
        credentials: "include"
        });
        
        const data = await res.json();
        if (data['logged-in'] === 1) {
        setLoginSuccess("Logged In!");
        setUser(data.username);
        } else {
        setLoginError(data.error);
        }
    }
    
    async function handleSignup(e) {
        e.preventDefault();
        setCreateError(null);
        setCreateSuccess(null);
        
        const formData = new FormData(e.target);
        const res = await fetch('/api/account/create', {
        method: 'POST',
        body: formData,
        });
        
        const data = await res.json();
        if (data['account-created'] === 1) {
        setCreateSuccess("Account created! Please log in.");
        } else {
        setCreateError(data.error);
        }
    }

    async function updateFavTeam(userID, teamID) {
        const data = { userID, teamID };
        fetch(`/api/account/favTeam`, { method: 'POST', headers: { "Content-Type": "application/json", }, body: JSON.stringify(data) })
        
    }

    useEffect(() => {
        if (user) {
            fetch(`/api/account/detail/${user.userID}`)
                .then(res => res.json())
                .then((data) => setDetails(data))
                .catch(err => console.error(err));
        }
    }, [user]);
    
 
    if (user) {
        return (
            <div>
                <h1>Logged in: {user.username}</h1>
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
                            setUser(prev => ({
                                ...prev,
                                favTeam: newFav
                            }));
                            updateFavTeam(user.userID, newFav);
                        }}
                        style={{color: colorList[user.favTeam]}}
                    >
                    {Object.entries(teamList).map(([teamID, tName]) => (
                        <option key={teamID}
                            value={teamID}
                            style={{ color: colorList[teamID] }}
                        >{tName}</option>
                    ))}
                </select></p>
                <p>Total Coins: <FontAwesomeIcon icon='fa-coins' /> {user.coins} <button className='beg-button' onClick={() => { handleBeg(user.userID) }} title="If you run out of coins, you can beg to get 10!">BEG</button>
                    {begError && <span style={{ color: 'red' }}> {begError}</span>}
                    {begSuccess && <span style={{ color: 'green' }}> {begSuccess}</span>}
                </p>
            </div>
        )
    } else {
        return (
            <div>
                <h1>Log In...</h1>
                <form onSubmit={handleLogin} target='_self'>
                    <label htmlFor='uname'><b>Username:</b></label><br />
                    <input type='text' placeholder="Enter Username" name="uname" required></input>
                    <br /><br />
                    <label htmlFor='pswd'><b>Password:</b></label> <br />
                    <input type='password' placeholder="Enter Password" name='pswd' required></input>
                    <br /> <br />
                    <button type="submit">Login</button>
                </form>
                {loginError && <p style={{ color: "red" }}>{loginError}</p>}
                {loginSuccess && <p style={{ color: "green" }}>{loginSuccess}</p>}
                <h1>...or Create Account</h1>
                <form onSubmit={handleSignup} target="_blank">
                    <label htmlFor='uname'><b>Username:</b></label><br />
                    <input type='text' placeholder='Create Username' name='uname' required></input>
                    <br /><br />
                    <label htmlFor="pswd"><b>Create Password:</b></label><br />
                    <input type={`${showPswd ? 'text' : 'password'}`} placeholder='Password' name='pswd' required></input>
                    <br /><br />
                    <label htmlFor="conf-pswd"><b>Confirm Password:</b></label><br />
                    <input type={`${showPswd ? 'text' : 'password'}`} placeholder="Confirm Password" name='conf_pswd' required></input>
                    <br /><br />
                    <input type='checkbox' onClick={() => setShowPswd(!showPswd)} name='show-pass'></input>
                    <label htmlFor='show-pass'> Show Password</label>
                    <br /> <br />
                    <button type='submit'>Sign-Up</button>
                </form>
                {createError && <p style={{ color: "red" }}>{createError}</p>}
                {createSuccess && <p style={{ color: "green" }}>{createSuccess}</p>}
            </div>
        )
    }
}
