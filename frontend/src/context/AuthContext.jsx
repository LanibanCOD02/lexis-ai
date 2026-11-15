import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// Utility to hash passwords using Web Crypto API
async function hashPassword(password) {
  const msgUint8 = new TextEncoder().encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Utility to get users
const getLocalUsers = () => {
  const users = localStorage.getItem('lexis_users');
  return users ? JSON.parse(users) : [];
};

// Utility to save users
const saveLocalUsers = (users) => {
  localStorage.setItem('lexis_users', JSON.stringify(users));
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true); // Start true to check session

  useEffect(() => {
    // Check session on load
    const sessionStr = localStorage.getItem('lexis_session');
    if (sessionStr) {
      try {
        const session = JSON.parse(sessionStr);
        if (session && session.email) {
          setUser({ email: session.email, role: 'Lawyer' });
          setToken(session.email); // using email as a dummy token for route protection
        }
      } catch(e) {
        localStorage.removeItem('lexis_session');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      if (!email || !password) {
        throw new Error("Email and password are required.");
      }

      const users = getLocalUsers();
      const existingUser = users.find(u => u.email.toLowerCase() === email.toLowerCase());
      
      if (!existingUser) {
        throw new Error("Invalid credentials.");
      }

      const hashed = await hashPassword(password);
      if (existingUser.passwordHash !== hashed) {
        throw new Error("Invalid credentials.");
      }

      // Success
      const sessionData = { email: existingUser.email };
      localStorage.setItem('lexis_session', JSON.stringify(sessionData));
      setUser({ email: existingUser.email, role: 'Lawyer' });
      setToken(existingUser.email);
      
      return true;
    } catch (err) {
      console.error(err);
      throw err; // Throw to be caught by UI
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password) => {
    setLoading(true);
    try {
      if (!email || !password) {
        throw new Error("Email and password are required.");
      }
      
      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        throw new Error("Please enter a valid email address.");
      }

      if (password.length < 6) {
        throw new Error("Password must be at least 6 characters.");
      }

      const users = getLocalUsers();
      const existingUser = users.find(u => u.email.toLowerCase() === email.toLowerCase());
      
      if (existingUser) {
        throw new Error("An account with this email already exists.");
      }

      const hashed = await hashPassword(password);
      const newUser = { email: email.toLowerCase(), passwordHash: hashed };
      
      users.push(newUser);
      saveLocalUsers(users);

      // Auto login after register
      const sessionData = { email: newUser.email };
      localStorage.setItem('lexis_session', JSON.stringify(sessionData));
      setUser({ email: newUser.email, role: 'Lawyer' });
      setToken(newUser.email);

      return true;
    } catch (error) {
      console.error("Registration failed:", error);
      throw error; // Throw to be caught by UI
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('lexis_session');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {!loading && children} 
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
