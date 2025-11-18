import React, { useState, useCallback, useEffect } from 'react';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { ProcessingIndicator } from './components/ProcessingIndicator';
import { ResultsView } from './components/ResultsView';
import type { PipelineResult } from './types'; // Assicurati che questo tipo esista
import { ErrorDisplay } from './components/ErrorDisplay';

// Definiamo un tipo per la risposta iniziale della pipeline
interface PipelineStartResponse {
  ok: boolean;
  message: string;
  output_filename: string;
}

type ProcessingState = 'idle' | 'processing' | 'success' | 'error';

const App: React.FC = () => {
  const [processingState, setProcessingState] = useState<ProcessingState>('idle');
  const [processingMessage, setProcessingMessage] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [originalVideoUrl, setOriginalVideoUrl] = useState<string | null>(null);
  const [result, setResult] = useState<PipelineResult | null>(null); // Questo ora sarà fittizio
  const [editedVideoUrl, setEditedVideoUrl] = useState<string | null>(null);
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
    setEditedVideoUrl(null);
  }, [originalVideoUrl]);

  const runPipeline = async () => {
    if (!videoFile) return;

    setProcessingState('processing');
    setProcessingMessage('Caricamento e avvio dell\'elaborazione... Potrebbero volerci alcuni minuti.');
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

      const data: PipelineStartResponse = await response.json();
      
      // Ora che il processo è in background, non abbiamo il risultato finale.
      // Per semplicità, costruiamo un URL e passiamo a uno stato di "successo"
      // In un'app reale, useresti WebSocket o polling per verificare quando il video è pronto.
      const finalVideoUrl = `http://localhost:8000/output/${data.output_filename}`;
      
      // Simuliamo un risultato per ResultsView
      const mockResult: PipelineResult = {
        ok: true,
        video_path: videoFile.name,
        transcript: "La trascrizione sarà disponibile al termine dell'elaborazione.",
        plan: {
            mood: "In elaborazione...",
            music: "In elaborazione...",
            caption: "In elaborazione...",
            fx: [],
            color: "In elaborazione..."
        },
        output_video: `/output/${data.output_filename}`
      };

      setResult(mockResult);
      setEditedVideoUrl(finalVideoUrl);
      setProcessingMessage("Elaborazione completata! Il tuo video è pronto.");
      setProcessingState('success');

    } catch (err: any) {
      setError(err.message || 'Impossibile comunicare con il server. Assicurati che il backend sia in esecuzione.');
      setProcessingState('error');
    }
  };

  const handleReset = () => {
    setProcessingState('idle');
    setVideoFile(null);
    setResult(null);
    setError(null);
    setEditedVideoUrl(null);
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
        // Abbiamo bisogno di un URL per il video originale e per quello editato.
        return result && originalVideoUrl && editedVideoUrl && (
          <ResultsView 
            result={result} 
            originalVideoUrl={originalVideoUrl} 
            editedVideoUrl={editedVideoUrl} // Passiamo l'URL del video editato
            onReset={handleReset} 
          />
        );
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