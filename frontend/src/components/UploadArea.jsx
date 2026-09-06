import { useRef, useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import {
  ALLOWED_EXTENSIONS,
  ALLOWED_MIME_TYPES,
  MAX_FILE_SIZE_BYTES,
  MAX_FILE_SIZE_MB,
} from '../constants/summaryOptions';
import { FOCUS_RING } from '../constants/styles';

/**
 * Upload area supporting click-to-browse, drag-and-drop, and keyboard
 * activation (Enter/Space) for accessibility, since this isn't a native
 * <button> element.
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

  function handleKeyDown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      inputRef.current?.click();
    }
  }

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={
        selectedFile
          ? `Selected file: ${selectedFile.name}. Click or press Enter to choose a different file.`
          : 'Click or press Enter to choose a file to upload, or drag and drop a file here.'
      }
      className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors ${FOCUS_RING}
        ${
          isDragActive
            ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950'
            : 'border-gray-300 bg-gray-50 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700'
        }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleInputChange}
        className="hidden"
        tabIndex={-1}
      />

      {selectedFile ? (
        <div className="flex flex-col items-center gap-2 text-gray-700 dark:text-gray-200">
          <FileText className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          <p className="font-medium">{selectedFile.name}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {(selectedFile.size / 1024).toFixed(1)} KB &mdash; click or drop to replace
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 text-gray-500 dark:text-gray-400">
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