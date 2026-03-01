import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
        const [user, setUser] = useState(null);

        // Check cookie on page load
        useEffect(() => {
                fetch("/api/account/me", { credentials: "include" })
                        .then(res => res.json())
                        .then(data => {
                                if (data['logged-in'] === 1) {
                                        setUser({
                                                userID: data.userID,
                                                username: data.username,
                                                coins: data.coins,
                                                favTeam: data.favTeam,
                                        });
                                } else {
                                        setUser(null);
                                }
                        })
                        .catch(err => {
                                console.error("Failed to fetch user:", err)
                                setUser(null);
                        });
        }, []);

        const updateCoins = (newAmount) => {
                setUser((prev) => ({
                        ...prev,
                        coins: newAmount,
                }));
        };

        return (
                <AuthContext.Provider value={{ user, setUser, updateCoins }}>
                        {children}
                </AuthContext.Provider>
        );
}

export function useAuth() {
        return useContext(AuthContext);
}