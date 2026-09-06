import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';

const ROTATING_MESSAGES = [
  'Reading your document…',
  'This may take a few minutes for longer documents.',
  'Still working — no need to resubmit.',
  'Breaking things down and summarizing…',
  'Almost there, hang tight…',
];

const MESSAGE_INTERVAL_MS = 8000;

function formatElapsed(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Shown while a summarization request is in flight.
 *
 * Since a document may be chunked into several pieces on the backend
 * (Milestone 8), a single request can take multiple minutes. Rather than
 * attempt real per-chunk progress reporting (which would require polling,
 * SSE, or WebSockets — a bigger architectural change deferred to a future
 * milestone), this gives an honest, indeterminate sense of progress:
 * an elapsed-time counter plus rotating reassurance messages.
 *
 * Purely presentational from the parent's point of view — no props needed.
 * Internal timers reset naturally each time this mounts, since the parent
 * only renders it while status === 'loading'.
 */
export default function LoadingIndicator() {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const tick = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(tick);
  }, []);

  useEffect(() => {
    const rotate = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % ROTATING_MESSAGES.length);
    }, MESSAGE_INTERVAL_MS);

    return () => clearInterval(rotate);
  }, []);

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center gap-2 rounded-lg bg-blue-50 py-4 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
    >
      <div className="flex items-center gap-2">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span className="text-sm font-medium">{ROTATING_MESSAGES[messageIndex]}</span>
      </div>
      <span className="font-mono text-xs text-blue-500 dark:text-blue-400">
        {formatElapsed(elapsedSeconds)}
      </span>
    </div>
  );
}