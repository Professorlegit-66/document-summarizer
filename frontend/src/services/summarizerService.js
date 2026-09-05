// Mock implementation for Milestone 6.
//
// IMPORTANT: This function's signature and its resolve/reject shape are
// intentionally designed to match what the real fetch-based version
// (Milestone 7) will look like. When we swap it, only the body of
// summarizeDocument() changes — no component that calls this should
// need to change.

const MOCK_DELAY_MS = 1500;

const MOCK_SUMMARIES = {
  paragraph:
    'This document provides an overview of the subject matter, covering the ' +
    'main arguments and supporting evidence in a connected narrative form. ' +
    'This is placeholder text standing in for a real AI-generated summary.',
  bullet_points:
    '• First main point from the document\n' +
    '• Second main point from the document\n' +
    '• Third main point from the document',
  key_takeaways:
    'Key Takeaway 1: Placeholder insight drawn from the document.\n' +
    'Key Takeaway 2: Another placeholder insight.\n' +
    'Key Takeaway 3: A final placeholder insight.',
};

/**
 * Simulates sending a document to the backend for summarization.
 *
 * @param {File} file - the selected file (only its name is used here)
 * @param {'short'|'medium'|'detailed'} length
 * @param {'paragraph'|'bullet_points'|'key_takeaways'} style
 * @returns {Promise<{filename: string, summary: string, summary_length: string, summary_style: string}>}
 * @throws {Error} with a user-facing message, if the filename contains "fail"
 *                 (a convenient manual trigger for testing the error UI path)
 */
export async function summarizeDocument(file, length, style) {
  await wait(MOCK_DELAY_MS);

  if (file?.name?.toLowerCase().includes('fail')) {
    throw new Error(
      'The AI service is currently unavailable. Please try again in a moment.'
    );
  }

  return {
    filename: file?.name ?? 'document.txt',
    summary: MOCK_SUMMARIES[style] ?? MOCK_SUMMARIES.paragraph,
    summary_length: length,
    summary_style: style,
  };
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}