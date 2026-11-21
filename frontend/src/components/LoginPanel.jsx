// Minimal username / password / Start form floating in the empty top area of the secret screen.
// On success it calls onLogin(user); what happens after login is decided by the parent.
import { useState } from 'react';
import { login } from '../api.js';

export default function LoginPanel({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    if (busy) return;
    if (!username.trim() || !password) {
      setError('Enter both username and password');
      return;
    }
    setBusy(true);
    setError('');
    try {
      onLogin(await login(username.trim(), password));
    } catch (err) {
      setError(err.message);
      setPassword('');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="login" onSubmit={submit} noValidate>
      <input
        className="login-field"
        type="text"
        placeholder="username"
        autoComplete="username"
        autoCapitalize="off"
        spellCheck="false"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        autoFocus
      />
      <input
        className="login-field"
        type="password"
        placeholder="password"
        autoComplete="current-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="login-start" type="submit" disabled={busy}>
        {busy ? '…' : 'Start'}
      </button>
      <p className="login-error" role="alert">{error}</p>
    </form>
  );
}
