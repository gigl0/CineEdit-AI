import React from 'react';
import type { PipelineResult } from '../types';

interface ResultsViewProps {
  result: PipelineResult;
  originalVideoUrl: string;
  editedVideoUrl: string; // Nuova prop
  onReset: () => void;
}

// ... (InfoCard non cambia)

export const ResultsView: React.FC<ResultsViewProps> = ({ result, originalVideoUrl, editedVideoUrl, onReset }) => {
  return (
    <div className="w-full animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-bold mb-4 text-center">Video Originale</h2>
          <video src={originalVideoUrl} controls className="w-full rounded-lg shadow-2xl"></video>
        </div>
        <div>
          <h2 className="text-2xl font-bold mb-4 text-center">Video Montato con AI</h2>
          {/* Usiamo la nuova prop qui */}
          <video src={editedVideoUrl} controls className="w-full rounded-lg shadow-2xl border-2 border-indigo-500"></video>
        </div>
      </div>

      {/* Il resto del componente rimane invariato */}
      {/* ... */}
    </div>
  );
};