from typing import List, Optional
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from app.services.scene_detector import detect_scenes
from app.utils.ffmpeg_utils import crop_center_to_9_16

def auto_edit(
    input_path: str,
    output_path: str,
    max_duration_s: int = 60,
    scene_threshold: int = 30,
    music_path: Optional[str] = None,
    target_w: int = 1080,
    target_h: int = 1920,
    fps: int = 30,
) -> int:
    """
    Taglia automaticamente alle scene e monta fino a max_duration_s.
    Ritorna la durata esportata (secondi).
    """
    base = VideoFileClip(input_path)

    scene_bounds = detect_scenes(input_path, threshold=scene_threshold)
    clips = []
    total = 0.0

    if scene_bounds:
        for (start, end) in scene_bounds:
            seg_dur = max(0.0, end - start)
            if seg_dur < 0.5:
                continue
            take = min(seg_dur, max_duration_s - total)
            if take <= 0:
                break
            c = base.subclip(start, start + take)
            c = crop_center_to_9_16(c, target_w, target_h)
            clips.append(c)
            total += take
            if total >= max_duration_s:
                break
    else:
        # fallback: prendi i primi N secondi
        sub = base.subclip(0, min(max_duration_s, int(base.duration)))
        sub = crop_center_to_9_16(sub, target_w, target_h)
        clips = [sub]
        total = sub.duration

    final = concatenate_videoclips(clips, method="compose")
    if music_path:
        music = AudioFileClip(music_path).subclip(0, final.duration)
        final = final.set_audio(music.set_duration(final.duration))

    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=fps)

    dur = int(final.duration)
    final.close()
    for c in clips: c.close()
    base.close()
    return dur
