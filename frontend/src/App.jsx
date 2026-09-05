import { useState } from 'react';
import UploadArea from './components/UploadArea';
import SummaryOptions from './components/SummaryOptions';
import LoadingIndicator from './components/LoadingIndicator';
import ResultDisplay from './components/ResultDisplay';
import ErrorMessage from './components/ErrorMessage';
import { summarizeDocument } from './services/summarizerService';
import { DEFAULT_SUMMARY_LENGTH, DEFAULT_SUMMARY_STYLE } from './constants/summaryOptions';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [length, setLength] = useState(DEFAULT_SUMMARY_LENGTH);
  const [style, setStyle] = useState(DEFAULT_SUMMARY_STYLE);

  // status: 'idle' | 'loading' | 'success' | 'error'
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const isSubmitDisabled = !selectedFile || status === 'loading';

  async function handleSubmit() {
    setStatus('loading');
    setErrorMessage(null);
    setResult(null);

    try {
      const response = await summarizeDocument(selectedFile, length, style);
      setResult(response);
      setStatus('success');
    } catch (err) {
      setErrorMessage(err.message);
      setStatus('error');
    }
  }

  function handleValidationError(message) {
    setErrorMessage(message);
    setStatus('error');
  }

  return (
    <div className="min-h-screen bg-white p-8">
      <div className="mx-auto flex max-w-md flex-col gap-6">
        <UploadArea
          selectedFile={selectedFile}
          onFileSelected={(file) => {
            setSelectedFile(file);
            setErrorMessage(null);
            setStatus('idle');
          }}
          onValidationError={handleValidationError}
        />

        <SummaryOptions
          length={length}
          style={style}
          onLengthChange={setLength}
          onStyleChange={setStyle}
        />

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className="rounded-lg bg-blue-600 py-2.5 font-medium text-white transition-colors
            hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          Summarize
        </button>

        {status === 'loading' && <LoadingIndicator />}
        {status === 'error' && <ErrorMessage message={errorMessage} />}
        {status === 'success' && <ResultDisplay result={result} />}
      </div>
    </div>
  );
}