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
                                        setUser(data.username);
                                }
                        });
        }, []);

        return (
                <AuthContext.Provider value={{ user, setUser }}>
                        {children}
                </AuthContext.Provider>
        );
}

export function useAuth() {
        return useContext(AuthContext);
}