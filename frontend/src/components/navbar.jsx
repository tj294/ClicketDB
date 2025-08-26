import React from "react";
import './navbar.css';

const Navbar = () => {
    return (
    
        <nav className="navbar">
            <div className="navbar-left">
                <a href='/' className='logo'>
                Clicket</a>
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

            </div>
        </nav>
    );    
};

export default Navbar;