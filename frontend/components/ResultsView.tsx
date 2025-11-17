import React from 'react';
import type { PipelineResult } from '../types';

interface ResultsViewProps {
  result: PipelineResult;
  originalVideoUrl: string;
  onReset: () => void;
}

const InfoCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="bg-slate-800 rounded-lg p-4 shadow-md">
    <h3 className="text-lg font-semibold text-indigo-400 mb-2">{title}</h3>
    {children}
  </div>
);

export const ResultsView: React.FC<ResultsViewProps> = ({ result, originalVideoUrl, onReset }) => {
  const editedVideoUrl = `http://localhost:8000${result.output_video}`;

  return (
    <div className="w-full animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-bold mb-4 text-center">Video Originale</h2>
          <video src={originalVideoUrl} controls className="w-full rounded-lg shadow-2xl"></video>
        </div>
        <div>
          <h2 className="text-2xl font-bold mb-4 text-center">Video Montato con AI</h2>
          <video src={editedVideoUrl} controls className="w-full rounded-lg shadow-2xl border-2 border-indigo-500"></video>
        </div>
      </div>

      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
        <InfoCard title="Piano di Montaggio AI">
          <ul className="space-y-2 text-slate-300">
            <li><strong>Mood:</strong> {result.plan.mood}</li>
            <li><strong>Musica:</strong> {result.plan.music}</li>
            <li><strong>Color Grading:</strong> {result.plan.color}</li>
            <li><strong>Caption:</strong> "{result.plan.caption}"</li>
            <li>
              <strong>Effetti:</strong>
              <div className="flex flex-wrap gap-2 mt-1">
                {result.plan.fx.map(effect => (
                  <span key={effect} className="bg-slate-700 text-xs font-medium px-2.5 py-1 rounded-full">{effect}</span>
                ))}
              </div>
            </li>
          </ul>
        </InfoCard>

        <InfoCard title="Trascrizione Audio">
          <p className="text-slate-300 text-sm leading-relaxed max-h-48 overflow-y-auto pr-2">
            {result.transcript}
          </p>
        </InfoCard>
      </div>
      
      <div className="text-center mt-12">
        <button
          onClick={onReset}
          className="bg-slate-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-slate-700 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-slate-500 shadow-lg text-xl"
        >
          Monta un Altro Video
        </button>
      </div>
    </div>
  );
};