import os
import tempfile
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    vfx
)
from PIL import Image, ImageDraw, ImageFont


def apply_edit_plan(video_path: str, plan: dict, output_path: str = None) -> str:
    """
    Applica un piano AI a un video con MoviePy.
    Ottimizzato per GPU NVIDIA (NVENC) e RunPod.
    """
    if not output_path:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_edited.mp4"

    # Carica video (lazy load → più veloce)
    clip = VideoFileClip(video_path, audio=True)

    # ============================================================
    # 1) Effetti visivi
    # ============================================================
    fx_list = plan.get("fx", [])

    for fx_name in fx_list:
        if fx_name == "zoom_in":
            clip = clip.fx(vfx.resize, 1.15)  # zoom più smooth
        elif fx_name == "fade_in":
            clip = clip.fadein(0.8)
        elif fx_name == "fade_out":
            clip = clip.fadeout(0.8)
        elif fx_name == "color_boost":
            clip = clip.fx(vfx.colorx, 1.25)

    # ============================================================
    # 2) Color grading semplice
    # ============================================================
    color_tone = plan.get("color", "").lower()

    if "b/n" in color_tone or "bw" in color_tone:
        clip = clip.fx(vfx.blackwhite)
    elif "warm" in color_tone:
        clip = clip.fx(vfx.colorx, 1.15)
    elif "cool" in color_tone:
        clip = clip.fx(vfx.colorx, 0.85)

    # ============================================================
    # 3) Musica di sottofondo
    # ============================================================
    music_name = plan.get("music", "")
    music_path = f"data/music/{music_name.replace(' ', '_')}.mp3"

    if os.path.exists(music_path):
        try:
            music = AudioFileClip(music_path).volumex(0.35)

            # Se il video ha audio originale → mix
            if clip.audio:
                clip = clip.set_audio(music)
            else:
                clip = clip.set_audio(music)
        except Exception as e:
            print(f"[!] Errore caricamento musica: {e}")
    else:
        print(f"[!] Musica non trovata: {music_path}")

    # ============================================================
    # 4) Caption via Pillow → sempre compatibile
    # ============================================================
    caption = plan.get("caption")

    if caption:
        try:
            img_w, img_h = clip.w, 160
            img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # font cross-platform
            font_candidates = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux (RunPod)
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                "C:/Windows/Fonts/arialbd.ttf"  # Windows
            ]

            font_path = next((f for f in font_candidates if os.path.exists(f)), None)
            font = ImageFont.truetype(font_path, 50) if font_path else ImageFont.load_default()

            # Compatibilità Pillow
            try:
                text_w, text_h = draw.textsize(caption, font=font)
            except Exception:
                bbox = draw.textbbox((0, 0), caption, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]

            draw.text(
                ((img_w - text_w) // 2, (img_h - text_h) // 2),
                caption,
                font=font,
                fill=(255, 255, 255, 255)
            )

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img.save(tmp.name)

            txt_clip = (
                ImageClip(tmp.name)
                .set_duration(clip.duration)
                .set_position(("center", "bottom"))
            )

            clip = CompositeVideoClip([clip, txt_clip])

        except Exception as e:
            print(f"[x] Errore caption: {e}")

    # ============================================================
    # 5) Esportazione video (GPU NVENC)
    # ============================================================
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    clip.write_videofile(
        output_path,
        codec="h264_nvenc",       # GPU ENCODING
        audio_codec="aac",
        fps=clip.fps if clip.fps else 25,
        bitrate="12M",
        threads=8,
        verbose=False,
        logger=None
    )

    clip.close()
    return output_path
