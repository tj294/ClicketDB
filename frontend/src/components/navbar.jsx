import React, { useState } from "react";
import './navbar.css';
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Navbar = () => {
  const [show, setShow] = useState(false);
  const [showPswd, setShowPswd] = useState(false);
  const [loginError, setLoginError] = useState(null);
  const [loginSuccess, setLoginSuccess] = useState(null);
  const [createError, setCreateError] = useState(null);
  const [createSuccess, setCreateSuccess] = useState(null);
  const [accMenu, setAccMenu] = useState(null);
  const { user, setUser } = useAuth();
  
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
  
  return (
    <div>
      <nav className="navbar">
        <div className="navbar-left">
          <a href='/' className='logo'>Clicket</a>
        </div>
        <div className='navbar-center'>
          <ul className='nav-links'>
            <li className='live'>
              <a href='/live'>Live</a>
            </li>
            <li>
              <a href='/teams'>Teams</a>
            </li>
            <li>
              <a href='/schedule'>Schedule</a>
            </li>
          </ul>
        </div>
        <div className='navbar-right'>
          {user ? (
            // <>
            //   <span>Acc: {user} </span>
            //   <button onClick={() => {
            //     fetch("/api/account/logout", { method: "POST", credentials: "include" })
            //     .then(() => setUser(null));
            //   }}>Logout</button>
            // </>
            <>
              <a className='acc-name' onClick={() => setAccMenu(!accMenu)}><FontAwesomeIcon icon='fa-user' /> Acc: {user.username}</a>
              <div className={`${accMenu ? 'account-menu' : 'hidden'}`}>
                <a href='/account'>Account Details</a>
                <a onClick={() => {
                  fetch("/api/account/logout", { method: "POST", credentials: "include" })
                  .then(() => setUser(null));
                }}>Log Out</a>
              </div>
            </>
          ) : (
            <div className = 'login' onClick = { () => setShow(!show) }>Login</div>
          )}
        </div>
      </nav>
      
      
      <div className={`${show ? 'log-in-window' : 'hidden'}`}>
        <span className='close' onClick={()=>setShow(!show)}>&times;</span>
        <form onSubmit={handleLogin} target='_self'>
          <div className='log-in-form'>
            <h2>Log In</h2>
            <label htmlFor='uname'><b>Username:</b></label><br />
            <input type='text' placeholder="Enter Username" name="uname" required></input>
            <br /><br />
            <label htmlFor='pswd'><b>Password:</b></label> <br />
            <input type='password' placeholder="Enter Password" name='pswd' required></input>
            <br /> <br />
            <button type="submit">Login</button>
            <br />
          </div>
        </form>
        {/* Messages */}  
        {loginError && <p style={{ color: "red" }}>{loginError}</p>}
        {loginSuccess && <p style={{ color: "green" }}>{loginSuccess}</p>}
        <div className='separator'>
          <span className='sep-text'>OR</span>
        </div>
        <form onSubmit={handleSignup} target="_blank">
          <div className='sign-up-form'>
            <h2>Sign Up</h2>
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
          </div>
        </form>
        {/* Messages */}  
        {createError && <p style={{ color: "red" }}>{createError}</p>}
        {createSuccess && <p style={{ color: "green" }}>{createSuccess}</p>}
      </div>
    </div>
  );    
};

export default Navbar;
