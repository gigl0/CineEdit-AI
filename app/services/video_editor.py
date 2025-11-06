import os
import tempfile
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, vfx, ImageClip
from PIL import Image, ImageDraw, ImageFont

def apply_edit_plan(video_path: str, plan: dict, output_path: str = None) -> str:
    """
    Applica un piano di montaggio AI a un video.
    Compatibile con Windows e senza dipendenze da ImageMagick.
    """
    if not output_path:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_edited.mp4"

    clip = VideoFileClip(video_path)

    # === 1. Effetti visivi ===
    fx_list = plan.get("fx", [])
    for fx_name in fx_list:
        if fx_name == "zoom_in":
            clip = clip.fx(vfx.resize, 1.1)
        elif fx_name == "fade_in":
            clip = clip.fadein(1)
        elif fx_name == "fade_out":
            clip = clip.fadeout(1)
        elif fx_name == "color_boost":
            clip = clip.fx(vfx.colorx, 1.2)

    # === 2. Colore / Mood ===
    color_tone = plan.get("color", "")
    if "b/n" in color_tone.lower():
        clip = clip.fx(vfx.blackwhite)
    elif "warm" in color_tone.lower():
        clip = clip.fx(vfx.colorx, 1.1)
    elif "cool" in color_tone.lower():
        clip = clip.fx(vfx.colorx, 0.9)

    # === 3. Musica di sottofondo ===
    music_genre = plan.get("music", "")
    music_path = f"data/music/{music_genre.replace(' ', '_')}.mp3"
    if os.path.exists(music_path):
        bg_music = AudioFileClip(music_path).volumex(0.3)
        clip = clip.set_audio(bg_music)
    else:
        print(f"[!] Musica non trovata: {music_path} (procedo senza)")

    # === 4. Caption con Pillow (no ImageMagick) ===
    caption = plan.get("caption")
    if caption:
        try:
            img_w, img_h = clip.w, 150
            font_path = "C:\\Windows\\Fonts\\arialbd.ttf"
            font = ImageFont.truetype(font_path, 48)

            img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Compatibilità Pillow <10 e >=10
            try:
                text_w, text_h = draw.textsize(caption, font=font)
            except AttributeError:
                bbox = draw.textbbox((0, 0), caption, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]

            text_x = (img_w - text_w) // 2
            text_y = (img_h - text_h) // 2

            draw.text((text_x, text_y), caption, font=font, fill=(255, 255, 255, 255))

            # Salva immagine temporanea
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img.save(tmp.name)

            # Aggiungi la caption al video
            txt_clip = ImageClip(tmp.name).set_duration(clip.duration)
            txt_clip = txt_clip.set_position(("center", "bottom"))
            clip = CompositeVideoClip([clip, txt_clip])

        except Exception as e:
            print(f"[x] Errore creazione caption con Pillow: {e}")

    # === 5. Esporta video finale ===
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=clip.fps,
        verbose=False,
        logger=None
    )

    clip.close()
    return output_path
