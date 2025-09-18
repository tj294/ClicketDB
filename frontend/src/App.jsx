import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import TeamPage from "./pages/TeamPage";
import TeamsList from "./pages/TeamsList";
import Live, { NoLivePage } from "./pages/Live";
import Navbar from "./components/navbar";
import PlayerPage from "./pages/PlayerPage";
import AboutPage from "./pages/AboutPage";
import GamePage from "./pages/wsGamePage";
import SchedulePage from "./pages/SchedulePage";
import AccountPage from "./pages/AccountPage";
import { AuthProvider } from "./components/AuthContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'
library.add(fas, far, fab)

export default function App() {
        return (
                <AuthProvider>
                        <Navbar />
                        <Routes>
                                <Route path='/' element={<HomePage />} />
                                <Route path='/team/:id' element={<TeamPage />} />
                                <Route path='/teams' element={<TeamsList />} />
                                <Route path='/live' element={<Live />} />
                                <Route path='/no-live-match' element={<NoLivePage/>} />
                                <Route path='/player/:id' element={<PlayerPage />} />
                                <Route path='/game/:id' element={<GamePage />} />
                                <Route path='/schedule' element={<SchedulePage />} />
                                <Route path='/account' element={<AccountPage />} />
                                <Route path='/about' element={<AboutPage />} />
                        </Routes>
                </AuthProvider>
        );
}