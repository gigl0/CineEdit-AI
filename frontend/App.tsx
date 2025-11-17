
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { ProcessingIndicator } from './components/ProcessingIndicator';
import { ResultsView } from './components/ResultsView';
import type { PipelineResult } from './types';
import { ErrorDisplay } from './components/ErrorDisplay';

type ProcessingState = 'idle' | 'processing' | 'success' | 'error';

const App: React.FC = () => {
  const [processingState, setProcessingState] = useState<ProcessingState>('idle');
  const [processingMessage, setProcessingMessage] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [originalVideoUrl, setOriginalVideoUrl] = useState<string | null>(null);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((file: File) => {
    if (originalVideoUrl) {
      URL.revokeObjectURL(originalVideoUrl);
    }
    setVideoFile(file);
    const url = URL.createObjectURL(file);
    setOriginalVideoUrl(url);
    setProcessingState('idle');
    setResult(null);
    setError(null);
  }, [originalVideoUrl]);

  const runPipeline = async () => {
    if (!videoFile) return;

    setProcessingState('processing');
    setProcessingMessage('Il tuo video è in fase di elaborazione. Potrebbero volerci alcuni minuti...');
    setError(null);

    const formData = new FormData();
    formData.append('file', videoFile);

    try {
      const response = await fetch('http://localhost:8000/pipeline/full', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Errore sconosciuto dal server.' }));
        throw new Error(errorData.detail || 'La richiesta al server è fallita.');
      }

      const data: PipelineResult = await response.json();
      setResult(data);
      setProcessingState('success');
    } catch (err: any) {
      setError(err.message || 'Impossibile comunicare con il server. Assicurati che il backend sia in esecuzione su http://localhost:8000.');
      setProcessingState('error');
    }
  };

  const handleReset = () => {
    setProcessingState('idle');
    setVideoFile(null);
    setResult(null);
    setError(null);
    if(originalVideoUrl) {
      URL.revokeObjectURL(originalVideoUrl);
      setOriginalVideoUrl(null);
    }
  };
  
  const renderContent = () => {
    switch (processingState) {
      case 'processing':
        return <ProcessingIndicator message={processingMessage} />;
      case 'success':
        return result && originalVideoUrl && <ResultsView result={result} originalVideoUrl={originalVideoUrl} onReset={handleReset} />;
      case 'error':
        return <ErrorDisplay message={error || "Errore sconosciuto"} onReset={handleReset} />;
      case 'idle':
      default:
        return (
          <FileUpload onFileSelect={handleFileSelect}>
            {videoFile && (
              <div className="mt-8 text-center">
                <p className="text-lg text-slate-300 mb-4">Video selezionato: <span className="font-semibold text-white">{videoFile.name}</span></p>
                <video src={originalVideoUrl || ''} controls className="max-w-md mx-auto rounded-lg shadow-lg"></video>
                <button
                  onClick={runPipeline}
                  className="mt-6 bg-indigo-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-indigo-700 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-indigo-500 shadow-lg text-xl"
                >
                  Avvia Montaggio AI
                </button>
              </div>
            )}
          </FileUpload>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 sm:p-8 flex flex-col items-center">
      <Header />
      <main className="w-full max-w-7xl mt-8">
        {renderContent()}
      </main>
    </div>
  );
};

export default App;
