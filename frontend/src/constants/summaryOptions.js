// Single source of truth for summary option values.
// These strings MUST match the backend's accepted form values exactly
// (see backend Milestone 5: length -> "short"|"medium"|"detailed",
// style -> "paragraph"|"bullet_points"|"key_takeaways").

export const SUMMARY_LENGTH_OPTIONS = [
  { value: 'short', label: 'Short' },
  { value: 'medium', label: 'Medium' },
  { value: 'detailed', label: 'Detailed' },
];

export const SUMMARY_STYLE_OPTIONS = [
  { value: 'paragraph', label: 'Paragraph' },
  { value: 'bullet_points', label: 'Bullet Points' },
  { value: 'key_takeaways', label: 'Key Takeaways' },
];

export const DEFAULT_SUMMARY_LENGTH = 'medium';
export const DEFAULT_SUMMARY_STYLE = 'paragraph';

// Client-side pre-check only. The backend's magic-byte detection
// (Milestone 3) remains the real source of truth.
export const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt'];

export const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

export const MAX_FILE_SIZE_MB = 10;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;