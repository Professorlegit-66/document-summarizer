import { useState } from 'react';
import { Copy, Check, Download } from 'lucide-react';

/**
 * Displays the generated summary with style-aware formatting,
 * plus Copy and Download-as-.txt actions.
 */
export default function ResultDisplay({ result }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const { filename, summary, summary_style: summaryStyle } = result;

  async function handleCopy() {
    await navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload() {
    const blob = new Blob([summary], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = buildDownloadFilename(filename);
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-gray-200 p-4">
      <SummaryContent summary={summary} summaryStyle={summaryStyle} />

      <div className="flex gap-2 border-t border-gray-100 pt-3">
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 text-green-600" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" />
              Copy
            </>
          )}
        </button>

        <button
          type="button"
          onClick={handleDownload}
          className="flex items-center gap-1.5 rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <Download className="h-4 w-4" />
          Download .txt
        </button>
      </div>
    </div>
  );
}

function SummaryContent({ summary, summaryStyle }) {
  if (summaryStyle === 'paragraph') {
    return <p className="whitespace-pre-wrap text-sm text-gray-800">{summary}</p>;
  }

  // bullet_points and key_takeaways both arrive as newline-separated lines
  const lines = summary.split('\n').filter((line) => line.trim().length > 0);

  return (
    <ul className="flex flex-col gap-1.5 text-sm text-gray-800">
      {lines.map((line, index) => (
        <li key={index} className="flex gap-2">
          <span className="text-blue-600">&bull;</span>
          <span>{stripLeadingBullet(line)}</span>
        </li>
      ))}
    </ul>
  );
}

// Removes a leading "• " if the source text already included one,
// since we render our own bullet marker.
function stripLeadingBullet(line) {
  return line.replace(/^[•\-*]\s*/, '').trim();
}

function buildDownloadFilename(originalFilename) {
  const baseName = originalFilename?.replace(/\.[^/.]+$/, '') || 'summary';
  return `${baseName}-summary.txt`;
}