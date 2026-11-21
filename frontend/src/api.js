// Calls to the backend auth API under /api/auth (proxied to FastAPI by Vite in dev).
// The session lives in an httpOnly "sid" cookie, so every call must send credentials.

async function request(path, options = {}) {
  const res = await fetch(path, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

/** Logs in and sets the session cookie; resolves to the user or throws an Error with a
 * message fit to show on screen (wrong password, lockout, server unreachable). */
export async function login(username, password) {
  let res;
  try {
    res = await request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new Error('Cannot reach the server');
  }
  if (res.ok) return res.data.user;
  if (res.status === 401) throw new Error('Invalid username or password');
  if (res.status === 429) throw new Error(res.data.detail || 'Too many attempts. Try again later.');
  if (res.status === 422) throw new Error('Enter both username and password');
  throw new Error('Something went wrong. Try again.');
}

async function getUser(path) {
  try {
    const res = await request(path);
    return res.ok ? res.data.user : null;
  } catch {
    return null;
  }
}

/** Returns the logged-in user, or null when there is no valid session or no server. */
export const me = () => getUser('/api/auth/me');

/** Returns the other person this user chats with, or null if they don't exist yet. */
export const peer = () => getUser('/api/auth/peer');

/** Ends the session server-side and clears the cookie; network errors are ignored. */
export async function logout() {
  await request('/api/auth/logout', { method: 'POST' }).catch(() => {});
}

/** Conversation with the other user, oldest first; pass the last id you have to get only newer.
 * Throws on network or auth failure so the caller can keep what it already shows. */
export async function listMessages(after) {
  const res = await request('/api/messages' + (after != null ? `?after=${after}` : ''));
  if (!res.ok) throw new Error(res.data.detail || 'Could not load messages');
  return res.data.messages;
}

/** Saves a message to the other user and resolves to the stored message (with id and time). */
export async function sendMessage(body) {
  const res = await request('/api/messages', { method: 'POST', body: JSON.stringify({ body }) });
  if (!res.ok) throw new Error(res.data.detail || 'Message not sent');
  return res.data;
}
