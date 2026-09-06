import { useEffect, useState } from 'react';

const STORAGE_KEY = 'theme';

/**
 * Determines the initial theme before first render:
 * 1. If the user has previously made an explicit choice, honor it.
 * 2. Otherwise, fall back to the OS-level preference.
 */
function getInitialIsDark() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'dark') return true;
  if (stored === 'light') return false;

  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

/**
 * Manages dark/light mode state, syncing it to the <html> element's
 * class list (so Tailwind's `dark:` variant works) and to localStorage
 * (so an explicit manual choice survives page reloads).
 *
 * OS preference is only consulted once, for the very first render when
 * no explicit choice has been saved yet. After any manual toggle, the
 * saved choice always takes priority over the OS setting.
 */
export function useDarkMode() {
  const [isDark, setIsDark] = useState(getInitialIsDark);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
  }, [isDark]);

  function toggle() {
    setIsDark((prev) => !prev);
  }

  return { isDark, toggle };
}