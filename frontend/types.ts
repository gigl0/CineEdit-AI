export interface EditPlan {
  mood: string;
  music: string;
  caption: string;
  fx: string[];
  color: string;
  error?: string;
}

export interface PipelineResult {
  ok: boolean;
  video_path: string;
  transcript: string;
  plan: EditPlan;
  output_video: string;
}