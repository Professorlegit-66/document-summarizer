import { useRef, useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import {
  ALLOWED_EXTENSIONS,
  ALLOWED_MIME_TYPES,
  MAX_FILE_SIZE_BYTES,
  MAX_FILE_SIZE_MB,
} from '../constants/summaryOptions';

/**
 * Upload area supporting click-to-browse and drag-and-drop.
 * Performs a fast client-side pre-check (extension/MIME/size) before
 * reporting a file as selected. The backend remains the source of truth.
 */
export default function UploadArea({ selectedFile, onFileSelected, onValidationError }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const inputRef = useRef(null);

  function validateFile(file) {
    const lowerName = file.name.toLowerCase();
    const hasAllowedExtension = ALLOWED_EXTENSIONS.some((ext) =>
      lowerName.endsWith(ext)
    );
    const hasAllowedMimeType = ALLOWED_MIME_TYPES.includes(file.type);

    // Some browsers/OSes report an empty or unexpected MIME type for
    // legitimate files, so we accept if EITHER check passes.
    if (!hasAllowedExtension && !hasAllowedMimeType) {
      return 'Unsupported file type. Please upload a PDF, DOCX, or TXT file.';
    }

    if (file.size === 0) {
      return 'This file appears to be empty.';
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `This file is too large. The maximum size is ${MAX_FILE_SIZE_MB} MB.`;
    }

    return null;
  }

  function handleFile(file) {
    if (!file) return;
    const errorMessage = validateFile(file);
    if (errorMessage) {
      onValidationError(errorMessage);
      return;
    }
    onFileSelected(file);
  }

  function handleInputChange(event) {
    const file = event.target.files?.[0];
    handleFile(file);
    // Reset so selecting the same file again still fires onChange
    event.target.value = '';
  }

  function handleDrop(event) {
    event.preventDefault();
    setIsDragActive(false);
    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  }

  function handleDragOver(event) {
    event.preventDefault();
    setIsDragActive(true);
  }

  function handleDragLeave() {
    setIsDragActive(false);
  }

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleInputChange}
        className="hidden"
      />

      {selectedFile ? (
        <div className="flex flex-col items-center gap-2 text-gray-700">
          <FileText className="h-8 w-8 text-blue-600" />
          <p className="font-medium">{selectedFile.name}</p>
          <p className="text-sm text-gray-500">
            {(selectedFile.size / 1024).toFixed(1)} KB &mdash; click or drop to replace
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 text-gray-500">
          <UploadCloud className="h-8 w-8" />
          <p className="font-medium">Click to browse or drag and drop a file</p>
          <p className="text-sm">
            Supported: PDF, DOCX, TXT &mdash; up to {MAX_FILE_SIZE_MB} MB
          </p>
        </div>
      )}
    </div>
  );
}