import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import TeamPage from "./pages/TeamPage";
import TeamsList from "./pages/TeamsList";
import Live from "./pages/Live";
import Navbar from "./components/navbar";
import PlayerPage from "./pages/PlayerPage";
// import GamePage from "./pages/GamePage";
import GamePage from "./pages/wsGamePage";
import SchedulePage from "./pages/SchedulePage";

export default function App() {
        return (
                <div>
                <Navbar />
                <Routes>
                        <Route path='/' element={<HomePage />} />
                        <Route path='/team/:id' element={<TeamPage />} />
                        <Route path='/teams' element={<TeamsList />} />
                        <Route path='/live' element={<Live />} />
                        <Route path='/player/:id' element={<PlayerPage />} />
                        <Route path='/game/:id' element={<GamePage />} />
                        <Route path='/schedule' element={<SchedulePage />} />
                </Routes>
                </div>
        );
}