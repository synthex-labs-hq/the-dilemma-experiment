#!/usr/bin/env python3
"""Automated 9:16 Vertical Video Renderer for The Dilemma Experiment Episode 2.

Takes the recorded Ubuntu screencasts, AI concept art, and voiceover audio track,
and renders a ready-to-upload MP4 (1080x1920) for YouTube Shorts and Instagram Reels.
"""

import os
import subprocess
from pathlib import Path

import imageio_ffmpeg


def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()


def run_cmd(cmd):
    print("Running:", " ".join(cmd[:6]), "...")
    res = subprocess.run(cmd, capture_output=True, check=False)
    if res.returncode != 0:
        print("Error executing command:", res.stderr.decode()[-500:])
        raise RuntimeError(f"FFmpeg failed with returncode {res.returncode}")


def render_short_beat(
    screencast_path: str,
    concept_image_path: str,
    audio_path: str,
    output_mp4: str,
    screencast_duration: float = 35.0,
):
    """Render a 9:16 vertical short from a screencast and concept image."""
    ffmpeg = get_ffmpeg()
    out_dir = Path(output_mp4).parent

    # Blurred background filter: blurred background 1080x1920 + centered crisp foreground
    bg_fg_filter = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,colorchannelmixer=aa=0.4[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    seg_intro = str(out_dir / "temp_intro.mp4")
    seg_main = str(out_dir / "temp_screencast.mp4")
    concat_txt = str(out_dir / "temp_concat.txt")

    # Segment 1: AI concept art with slow subtle zoom (5.0s)
    run_cmd([
        ffmpeg, "-y",
        "-loop", "1",
        "-t", "5.0",
        "-i", concept_image_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.001,1.08)':d=150:s=1080x1920:fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg_intro,
    ])

    # Segment 2: Screencast centered with blurred backdrop
    run_cmd([
        ffmpeg, "-y",
        "-ss", "0.5",
        "-t", str(screencast_duration),
        "-i", screencast_path,
        "-filter_complex", bg_fg_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg_main,
    ])

    # Concat segments
    with open(concat_txt, "w") as f:
        f.write(f"file '{seg_intro}'\n")
        f.write(f"file '{seg_main}'\n")

    # Final mux with audio
    run_cmd([
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_mp4,
    ])

    # Clean up temp segments
    for temp in [seg_intro, seg_main, concat_txt]:
        if os.path.exists(temp):
            os.remove(temp)

    print(f"\n🎉 SUCCESS! Rendered video saved to: {output_mp4}")


if __name__ == "__main__":
    print("Render script ready. Call render_short_beat() with your asset paths.")
