// Secret area: halftone "Hello P!" with the login form, then the chat once someone is logged in.
// An existing session cookie skips straight to the chat; logging out returns to the login form.
import { useEffect, useState } from 'react';
import HalftoneWordmarkFooter from '@/components/ui/halftone-wordmark-footer';
import LoginPanel from './LoginPanel.jsx';
import ChatScreen from './ChatScreen.tsx';
import { logout, me, peer } from '../api.js';

const PHONE_QUERY = '(max-width: 640px)';

// True on phone-width screens; tracks rotation and window resizes.
function useIsPhone() {
  const [isPhone, setIsPhone] = useState(() => window.matchMedia(PHONE_QUERY).matches);
  useEffect(() => {
    const mq = window.matchMedia(PHONE_QUERY);
    const onChange = () => setIsPhone(mq.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);
  return isPhone;
}

export default function SecretScreen() {
  // undefined = still checking, null = logged out, object = { me, peer }.
  const [session, setSession] = useState(undefined);
  const isPhone = useIsPhone();

  async function startChat(user) {
    setSession({ me: user, peer: await peer() });
  }

  useEffect(() => {
    let alive = true;
    me().then(async (user) => {
      if (!alive) return;
      if (user) await startChat(user);
      else setSession(null);
    });
    return () => { alive = false; };
  }, []);

  async function handleLogout() {
    await logout();
    setSession(null);
  }

  if (session) return <ChatScreen me={session.me} peer={session.peer} onLogout={handleLogout} />;

  return (
    <div className="secret">
      <HalftoneWordmarkFooter
        wordmark="Hello P!"
        label=""
        meta=""
        columns={[]}
        backToTop={false}
        height="100dvh"
        dotGap={isPhone ? 4 : 6}
        radius={isPhone ? 56 : 80}
      />
      <div className="secret-top">
        {session === null && <LoginPanel onLogin={startChat} />}
      </div>
    </div>
  );
}
