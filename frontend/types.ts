// frontend/types.ts

export interface NarrativeSection {
  title: string;
  summary: string;
  start_sec: number;
  end_sec: number;
  keywords: string[];
}

export interface AnalysisResult {
  narrative_sections: NarrativeSection[];
  full_transcript?: string;
}

export interface EditPlan {
  mood: string;
  music: string;
  caption: string;
  fx: string[];
  color: string;
}

export interface PipelineResult {
  ok: boolean;
  video_path: string;
  transcript: string;
  plan: EditPlan;
  output_video: string;
}

export interface ClipResult {
  ok: boolean;
  output_video: string;
}