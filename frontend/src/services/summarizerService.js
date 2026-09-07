// Milestone 7: real implementation, replacing the Milestone 6 mock.
//
// summarizeDocument()'s signature and resolve/reject shape are unchanged
// from the mock version, so no component needs to change.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const STATUS_MESSAGES = {
  400: 'The file appears to be empty. Please choose a different file.',
  413: 'This file is too large to process. Please try a smaller file.',
  415: "This file type isn't supported. Please upload a PDF, DOCX, or TXT file.",
  422: "We couldn't read this file. It may be corrupted or contain no readable text.",
  429: "You've made too many requests. Please wait a bit before trying again.",
  502: 'The AI service returned an unexpected response. Please try again.',
  503: 'The summarization service is temporarily unavailable. Please try again in a moment.',
  504: 'The request took too long to process. Please try again with a shorter document.',
};

/**
 * Sends a document to the backend for AI summarization.
 *
 * @param {File} file
 * @param {'short'|'medium'|'detailed'} length
 * @param {'paragraph'|'bullet_points'|'key_takeaways'} style
 * @returns {Promise<{filename: string, summary: string, summary_length: string, summary_style: string}>}
 * @throws {Error} with a user-facing message on any failure
 */
export async function summarizeDocument(file, length, style) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('length', length);
  formData.append('style', style);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      body: formData,
    });
  } catch (networkError) {
    // fetch only throws on true network failure (backend unreachable,
    // no response received at all) — not on 4xx/5xx HTTP responses.
    throw new Error(
      "Couldn't connect. Please check your internet connection and try again."
    );
  }

  if (!response.ok) {
    const message =
      STATUS_MESSAGES[response.status] ??
      'Something unexpected happened. Please try again.';
    throw new Error(message);
  }

  return response.json();
}