import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Scale, Loader2 } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setErrorMsg(err.message || 'Invalid email or password');
    }
  };
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center font-sans">
      <div className="w-full max-w-sm px-6 flex flex-col gap-8">
        
        {/* Header */}
        <div className="flex flex-col items-center text-center gap-4">
          <Scale size={32} className="text-foreground" />
          <div>
            <h2 className="font-serif font-medium text-2xl text-foreground">Welcome Back</h2>
            <p className="text-sm text-muted mt-1">Sign in to your Lexis AI Workspace</p>
          </div>
        </div>

        {/* Error Message */}
        {errorMsg && (
          <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-md border border-destructive/20 text-center font-medium">
            {errorMsg}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="login-email" className="text-xs font-medium text-muted uppercase tracking-wider">Email</label>
            <input 
              id="login-email"
              name="email"
              type="email" 
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="px-0 py-2 border-b border-border bg-transparent focus:border-foreground outline-none transition-colors duration-300 text-foreground placeholder:text-muted/50"
              placeholder="counsel@firm.com"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="login-password" className="text-xs font-medium text-muted uppercase tracking-wider">Password</label>
            <input 
              id="login-password"
              name="password"
              type="password" 
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="px-0 py-2 border-b border-border bg-transparent focus:border-foreground outline-none transition-colors duration-300 text-foreground placeholder:text-muted/50"
              placeholder="••••••••"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="mt-4 flex items-center justify-center gap-2 w-full py-3 bg-foreground text-white text-sm font-medium rounded-md hover:bg-primary transition-colors duration-300 disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center text-sm text-muted">
          Don't have an account? <Link to="/register" className="text-foreground font-medium hover:text-primary transition-colors duration-300">Register here</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
