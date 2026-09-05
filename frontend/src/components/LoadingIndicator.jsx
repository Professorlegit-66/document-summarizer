import { Loader2 } from 'lucide-react';

/**
 * Shown while a summarization request is in flight.
 * Purely presentational — no props needed beyond whether it's visible,
 * which the parent controls by conditionally rendering this component.
 */
export default function LoadingIndicator() {
  return (
    <div className="flex items-center justify-center gap-2 rounded-lg bg-blue-50 py-3 text-blue-700">
      <Loader2 className="h-5 w-5 animate-spin" />
      <span className="text-sm font-medium">Processing your document…</span>
    </div>
  );
}