#!/usr/bin/env python3
"""Automated 9:16 Vertical Video Renderer for The Dilemma Experiment Episode 1.

Takes the recorded screencasts, AI vertical visual, and enhanced audio track,
and renders a polished, ready-to-upload MP4 (1080x1920) for YouTube Shorts and Instagram Reels.
"""

import os
import subprocess

import imageio_ffmpeg


def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()

def run_cmd(cmd):
    print("Running:", " ".join(cmd[:6]), "...")
    res = subprocess.run(cmd, capture_output=True, check=False)
    if res.returncode != 0:
        print("Error executing command:", res.stderr.decode()[-500:])
        raise RuntimeError(f"FFmpeg failed with returncode {res.returncode}")

def main():
    ffmpeg = get_ffmpeg()
    base_dir = "/home/vayana/Desktop/personal/projects/synthex/the-dilemma-experiment"
    audio_path = os.path.join(base_dir, "experiments/episode_01/narration-enhanced-v2.mp3")
    image_path = "/home/vayana/.gemini/antigravity-ide/brain/7dd1b922-d2f8-436d-ac4a-e145e2534478/dilemma_ep1_vertical_1789115650806.jpg"
    
    sc1 = "/home/vayana/Videos/Screencasts/Screencast from 09-13-2026 06:25:45 PM.webm"
    sc2 = "/home/vayana/Videos/Screencasts/Screencast from 09-13-2026 06:26:57 PM.webm"
    sc3 = "/home/vayana/Videos/Screencasts/Screencast from 09-13-2026 06:27:25 PM.webm"
    
    out_dir = os.path.join(base_dir, "experiments/episode_01")
    trimmed_audio = os.path.join(out_dir, "narration_trimmed.wav")
    final_output = os.path.join(out_dir, "synthex_short_ep1.mp4")

    print("=== Step 1: Trimming audio lead-in silence ===")
    # Trim first 3.0 seconds so voice starts immediately at 0:00
    # Also trim end after 74.0s
    run_cmd([
        ffmpeg, "-y",
        "-ss", "3.0",
        "-to", "74.0",
        "-i", audio_path,
        "-af", "silenceremove=stop_periods=-1:stop_duration=0.8:stop_threshold=-38dB:detection=rms,asetpts=N/SR/TB",
        trimmed_audio
    ])

    # Probe trimmed audio duration
    probe_cmd = [
        ffmpeg, "-i", trimmed_audio
    ]
    probe_res = subprocess.run(probe_cmd, capture_output=True, check=False).stderr.decode()
    dur_line = [l for l in probe_res.splitlines() if "Duration:" in l]
    print("Trimmed Audio Duration:", dur_line[0] if dur_line else "Unknown")

    print("\n=== Step 2: Preparing 9:16 Vertical Video Segments ===")
    
    # Segment 1: AI Concept Art with subtle zoom (0.0s to 7.5s)
    seg1 = os.path.join(out_dir, "seg1.mp4")
    run_cmd([
        ffmpeg, "-y",
        "-loop", "1",
        "-t", "7.5",
        "-i", image_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.001,1.1)':d=225:s=1080x1920:fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg1
    ])

    # Helper filter for 16:9 screen recordings inside 9:16 vertical canvas:
    # Blurred background filling 1080x1920, sharp crisp foreground scaled to width=1080 centered vertically
    bg_fg_filter = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,colorchannelmixer=aa=0.4[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    # Segment 2: Screencast 1 (Simulation CLI) - 15 seconds
    seg2 = os.path.join(out_dir, "seg2.mp4")
    run_cmd([
        ffmpeg, "-y",
        "-ss", "1.0",
        "-t", "16.0",
        "-i", sc1,
        "-filter_complex", bg_fg_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg2
    ])

    # Segment 3: Screencast 3 (VS Code Domain code & Tit for Tat) - 18 seconds
    seg3 = os.path.join(out_dir, "seg3.mp4")
    run_cmd([
        ffmpeg, "-y",
        "-ss", "0.5",
        "-t", "18.0",
        "-i", sc3,
        "-filter_complex", bg_fg_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg3
    ])

    # Segment 4: Screencast 2 (74 tests passing) - 7 seconds
    seg4 = os.path.join(out_dir, "seg4.mp4")
    run_cmd([
        ffmpeg, "-y",
        "-ss", "0.5",
        "-t", "7.0",
        "-i", sc2,
        "-filter_complex", bg_fg_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg4
    ])

    # Segment 5: Outro with AI Concept Art / Final Screen - 10 seconds
    seg5 = os.path.join(out_dir, "seg5.mp4")
    run_cmd([
        ffmpeg, "-y",
        "-loop", "1",
        "-t", "10.0",
        "-i", image_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        seg5
    ])

    print("\n=== Step 3: Concatenating Segments and Muxing Audio ===")
    # Concat file list
    concat_txt = os.path.join(out_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        f.write(f"file '{seg1}'\n")
        f.write(f"file '{seg2}'\n")
        f.write(f"file '{seg3}'\n")
        f.write(f"file '{seg4}'\n")
        f.write(f"file '{seg5}'\n")

    # Mux with audio, cut to shortest
    run_cmd([
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", trimmed_audio,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_output
    ])

    print("\n🎉 SUCCESS! Rendered video saved to:")
    print(final_output)

if __name__ == "__main__":
    main()
