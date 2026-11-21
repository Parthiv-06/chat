// Landing screen that swaps to the secret "Hello P!" screen when the theme button is pressed.
// The switch lives in memory only, so a page reload always lands back on the landing screen.
import { useState } from 'react';
import { StubProvider } from './stub.jsx';
import Navbar from './components/Navbar.jsx';
import Hero from './components/Hero.jsx';
import Content from './components/Content.jsx';
import Footer from './components/Footer.jsx';
import SecretScreen from './components/SecretScreen.jsx';

export default function App() {
  const [secret, setSecret] = useState(false);

  if (secret) return <SecretScreen />;

  return (
    <StubProvider>
      <Navbar onThemeToggle={() => setSecret(true)} />
      <Hero />
      <Content />
      <Footer />
    </StubProvider>
  );
}
