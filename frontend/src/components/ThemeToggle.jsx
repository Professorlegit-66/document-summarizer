import { Sun, Moon } from 'lucide-react';
import { FOCUS_RING } from '../constants/styles';

/**
 * Icon button that toggles between light and dark mode.
 * Owns no state — current mode and the toggle handler come from props,
 * both sourced from the useDarkMode hook in App.jsx.
 */
export default function ThemeToggle({ isDark, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`rounded-full p-2 text-gray-500 transition-colors hover:bg-gray-100
        dark:text-gray-400 dark:hover:bg-gray-800 ${FOCUS_RING}`}
    >
      {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  );
}