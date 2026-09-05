import { AlertCircle } from 'lucide-react';

/**
 * Reusable error banner. Renders any human-readable error string —
 * used today for client-side validation and mock errors, and reused
 * unchanged in Milestone 7 for real backend error responses.
 */
export default function ErrorMessage({ message }) {
  if (!message) return null;

  return (
    <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-red-700">
      <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0" />
      <p className="text-sm">{message}</p>
    </div>
  );
}