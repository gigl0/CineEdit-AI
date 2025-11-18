// src/types.ts

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
  output_video: string; // Questo sarà un percorso relativo, es: /output/video.mp4
}