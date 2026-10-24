import os
import subprocess
import cv2
import numpy as np
import imageio_ffmpeg

SUBMISSION_DIR = r"C:\Users\sethi\HomeMind\submission"
FPS = 30
TRANSITION_FRAMES = 15 # 0.5s smooth crossfade

# Polished scene definitions matching synthesize_narration_polished.py allocations
POLISHED_SCENE_DEFS = [
    {
        "id": "scene1",
        "image": "scene1_problem.png",
        "duration_sec": 11.65,
        "badge": "THE PROBLEM",
        "caption": "Notification Fatigue: Smart sensors detect raw events, but lack home context."
    },
    {
        "id": "scene2",
        "image": "scene2_dashboard.png",
        "duration_sec": 15.67,
        "badge": "MEET HOMEMIND",
        "caption": "HomeMind: Context, Memory & Decision Layer across Ring, Alexa+ and Fire TV"
    },
    {
        "id": "scene3",
        "image": "scene3_watch.png",
        "duration_sec": 18.00,
        "badge": "INTENT & MCP",
        "caption": "Alexa+ Simulation: set_temporary_watch tool creates targeted monitoring window"
    },
    {
        "id": "scene4a",
        "image": "scene4_alert.png",
        "duration_sec": 15.00,
        "badge": "WATCH MATCH & ALERT",
        "caption": "Simulated Ring Doorbell matches active watch -> Decision Engine escalates alert"
    },
    {
        "id": "scene4b",
        "image": "scene4_focus.png",
        "duration_sec": 15.00,
        "badge": "FOCUS MODE",
        "caption": "Attention Management: In Focus Mode, routine motion is logged quietly without audio chimes"
    },
    {
        "id": "scene5",
        "image": "scene5_recall.png",
        "duration_sec": 17.00,
        "badge": "CONVERSATIONAL MEMORY",
        "caption": "what_happened MCP tool queries short-term memory to synthesize a natural summary"
    },
    {
        "id": "scene6",
        "image": "scene6_architecture.png",
        "duration_sec": 16.59,
        "badge": "ARCHITECTURE",
        "caption": "\"HomeMind: A smarter home doesn't just detect events. It understands when they matter.\""
    }
]

def render_frame_with_dedicated_bar(img, badge, caption, is_ui=False):
    """
    Renders the frame with the UI scaled and centered above a dedicated 70px caption bar,
    ensuring zero occlusion of chat inputs, buttons, or header badges.
    """
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

    if is_ui:
        # Crop side margins (from 1902 width, content is x=270..1630)
        # Crop x from 100 to 1804 (width 1704), y from 8 to 972 (height 964)
        crop = img[8:972, 100:1804]
        ui_resized = cv2.resize(crop, (1920, 1010), interpolation=cv2.INTER_LANCZOS4)
        frame[0:1010, 0:1920] = ui_resized
    else:
        # Title and architecture cards: scale to fit 1920x1010 cleanly
        card_resized = cv2.resize(img, (1920, 1010), interpolation=cv2.INTER_LANCZOS4)
        frame[0:1010, 0:1920] = card_resized

    # Dedicated Caption Bar in y=1010..1080 (70px)
    cv2.rectangle(frame, (0, 1010), (1920, 1080), (10, 15, 26), -1)
    # Accent dividing line
    cv2.line(frame, (0, 1010), (1920, 1010), (99, 102, 241), 2)

    # Badge Pill on Left
    badge_w = 12 + len(badge) * 11 + 12
    cv2.rectangle(frame, (30, 1024), (30 + badge_w, 1066), (30, 41, 59), -1)
    cv2.rectangle(frame, (30, 1024), (30 + badge_w, 1066), (16, 185, 129), 1)
    cv2.putText(
        frame,
        badge,
        (42, 1052),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (52, 211, 153), # Emerald text
        2,
        cv2.LINE_AA
    )

    # Caption text
    text_x = 30 + badge_w + 20
    cv2.putText(
        frame,
        caption,
        (text_x, 1052),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (248, 250, 252), # Crisp white
        2,
        cv2.LINE_AA
    )

    return frame

def generate_polished_video():
    raw_video_path = os.path.join(SUBMISSION_DIR, "temp_video_polished.mp4")
    final_output_path = os.path.join(SUBMISSION_DIR, "HomeMind_Final_Demo_Video_Polished.mp4")
    narration_wav = os.path.join(SUBMISSION_DIR, "narration_voiceover_polished.wav")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(raw_video_path, fourcc, float(FPS), (1920, 1080))

    if not out.isOpened():
        raise RuntimeError("Failed to initialize OpenCV VideoWriter")

    print(f"Rendering polished visual stream to: {raw_video_path}")

    scene_frames = []
    for sc in POLISHED_SCENE_DEFS:
        img_path = os.path.join(SUBMISSION_DIR, sc["image"])
        raw_img = cv2.imread(img_path)
        if raw_img is None:
            raise FileNotFoundError(f"Could not load image: {img_path}")

        is_ui = sc["id"] not in ["scene1", "scene6"]
        frame = render_frame_with_dedicated_bar(raw_img, sc["badge"], sc["caption"], is_ui=is_ui)
        total_f = int(round(sc["duration_sec"] * FPS))
        scene_frames.append({
            "frame": frame,
            "count": total_f,
            "id": sc["id"]
        })

    total_rendered_frames = 0
    for i, sc in enumerate(scene_frames):
        current_frame = sc["frame"]
        total_f = sc["count"]
        print(f"Writing {sc['id']} ({total_f} frames / {total_f/FPS:.2f}s)...")

        if i < len(scene_frames) - 1:
            hold_frames = total_f - TRANSITION_FRAMES
            next_frame = scene_frames[i + 1]["frame"]

            for _ in range(hold_frames):
                out.write(current_frame)
                total_rendered_frames += 1

            for tf in range(TRANSITION_FRAMES):
                alpha = (tf + 1) / float(TRANSITION_FRAMES)
                blend = cv2.addWeighted(next_frame, alpha, current_frame, 1.0 - alpha, 0)
                out.write(blend)
                total_rendered_frames += 1
        else:
            for _ in range(total_f):
                out.write(current_frame)
                total_rendered_frames += 1

    out.release()
    raw_dur = total_rendered_frames / float(FPS)
    print(f"\nVisual stream rendered: {total_rendered_frames} frames ({raw_dur:.2f}s)")

    # Muxing with FFmpeg to H.264 + AAC
    print(f"\nMuxing video and narration with FFmpeg...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    mux_cmd = [
        ffmpeg_exe, "-y",
        "-i", raw_video_path,
        "-i", narration_wav,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_output_path
    ]

    res = subprocess.run(mux_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg muxing failed: {res.stderr}")

    # Remove temporary raw stream
    try:
        os.remove(raw_video_path)
    except:
        pass

    print(f"SUCCESS! Polished Final Video Created: {final_output_path}")

    # Inspect final file
    inspect_cmd = [ffmpeg_exe, "-i", final_output_path]
    insp = subprocess.run(inspect_cmd, capture_output=True, text=True)
    print("\nFinal Media Stream Details:")
    for line in insp.stderr.split("\n"):
        if "Duration:" in line or "Stream #" in line:
            print("  " + line.strip())

if __name__ == "__main__":
    generate_polished_video()
