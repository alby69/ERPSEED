import { createContext, useState, useEffect, useContext } from 'react';
import { apiFetch } from '../utils';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    apiFetch('/me')
      .then(async (res) => {
        if (res.ok) {
          setUser(await res.json());
        }
      })
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (accessToken, refreshToken, remember = false) => {
    const storage = remember ? localStorage : sessionStorage;
    
    // Pulisci l'altro storage per evitare conflitti
    if (remember) {
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }

    storage.setItem('access_token', accessToken);
    if (refreshToken) storage.setItem('refresh_token', refreshToken);

    // Aggiorna immediatamente lo stato utente
    try {
      const res = await apiFetch('/me');
      if (res.ok) setUser(await res.json());
    } catch (e) {
      console.error("Error retrieving user after login", e);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};