// Click handling for the landing screen: stub(label) sends the browser to REDIRECT_URL.
// Only the theme button uses toast() instead, so it stays on this page.
import { createContext, useCallback, useContext, useRef, useState } from 'react';

export const REDIRECT_URL = 'https://pdcampus.in/mock-tests/ssc-cgl/';

const StubContext = createContext({ stub: () => {}, toast: () => {} });
export const useStub = () => useContext(StubContext).stub;
export const useToast = () => useContext(StubContext).toast;

export function StubProvider({ children }) {
  const [msg, setMsg] = useState('');
  const [show, setShow] = useState(false);
  const timer = useRef();

  const toast = useCallback((text) => {
    setMsg(text);
    setShow(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setShow(false), 1600);
  }, []);

  const stub = useCallback(() => window.location.assign(REDIRECT_URL), []);

  return (
    <StubContext.Provider value={{ stub, toast }}>
      {children}
      <div id="toast" role="status" className={show ? 'show' : ''}>{msg}</div>
    </StubContext.Provider>
  );
}

// Link that redirects like every other element.
// Stops propagation so a link inside a clickable card doesn't also fire the card's handler.
export function StubLink({ label, children, ...rest }) {
  const stub = useStub();
  return (
    <a href={REDIRECT_URL} onClick={(e) => { e.preventDefault(); e.stopPropagation(); stub(label); }} {...rest}>
      {children}
    </a>
  );
}
