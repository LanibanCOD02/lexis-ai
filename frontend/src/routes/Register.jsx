import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Scale, Loader2 } from 'lucide-react';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');
    
    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match');
      return;
    }

    try {
      await register(email, password);
      setSuccessMsg('Registration successful. Redirecting to login...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center font-sans">
      <div className="w-full max-w-sm px-6 flex flex-col gap-8">
        
        {/* Header */}
        <div className="flex flex-col items-center text-center gap-4">
          <Scale size={32} className="text-foreground" />
          <div>
            <h2 className="font-serif font-medium text-2xl text-foreground">Create Account</h2>
            <p className="text-sm text-muted mt-1">Join Lexis AI to research case law</p>
          </div>
        </div>

        {errorMsg && (
          <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-md border border-destructive/20 text-center font-medium">
            {errorMsg}
          </div>
        )}
        
        {successMsg && (
          <div className="p-3 bg-green-50 text-green-700 text-sm rounded-md border border-green-200 text-center font-medium">
            {successMsg}
          </div>
        )}

        <form onSubmit={handleRegister} className="flex flex-col gap-5">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="register-email" className="text-xs font-medium text-muted uppercase tracking-wider">Email</label>
            <input 
              id="register-email"
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
            <label htmlFor="register-password" className="text-xs font-medium text-muted uppercase tracking-wider">Password</label>
            <input 
              id="register-password"
              name="password"
              type="password" 
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="px-0 py-2 border-b border-border bg-transparent focus:border-foreground outline-none transition-colors duration-300 text-foreground placeholder:text-muted/50"
              placeholder="••••••••"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="register-confirm-password" className="text-xs font-medium text-muted uppercase tracking-wider">Confirm Password</label>
            <input 
              id="register-confirm-password"
              name="confirmPassword"
              type="password" 
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              required
              className="px-0 py-2 border-b border-border bg-transparent focus:border-foreground outline-none transition-colors duration-300 text-foreground placeholder:text-muted/50"
              placeholder="••••••••"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading || !!successMsg}
            className="mt-4 flex items-center justify-center gap-2 w-full py-3 bg-foreground text-white text-sm font-medium rounded-md hover:bg-primary transition-colors duration-300 disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div className="text-center text-sm text-muted">
          Already have an account? <Link to="/login" className="text-foreground font-medium hover:text-primary transition-colors duration-300">Sign in here</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
