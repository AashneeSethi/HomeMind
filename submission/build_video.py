import os
import cv2
import numpy as np

SUBMISSION_DIR = r"C:\Users\sethi\HomeMind\submission"
FPS = 30
TRANSITION_FRAMES = 15 # 0.5s crossfade between scenes

SCENE_DEFS = [
    {
        "id": "scene1",
        "image": "scene1_problem.png",
        "duration_sec": 15.54,
        "title": "THE SMART HOME DILEMMA",
        "caption": "Sensors fire isolated notifications for every flutter. Devices lack contextual awareness."
    },
    {
        "id": "scene2",
        "image": "scene2_dashboard.png",
        "duration_sec": 16.32,
        "title": "HOMEMIND AMBIENT CONTROL CENTER",
        "caption": "Context, Memory & Decision Layer across Ring, Alexa+ and Fire TV (FastAPI :8081 + React :5173)"
    },
    {
        "id": "scene3",
        "image": "scene3_watch.png",
        "duration_sec": 18.00,
        "title": "ALEXA+ AGENT SKILL: TEMPORARY WATCH",
        "caption": "User: \"Watch the front door for 30 minutes\" -> set_temporary_watch MCP tool creates live countdown"
    },
    {
        "id": "scene4a",
        "image": "scene4_alert.png",
        "duration_sec": 12.00,
        "title": "RING EVENT: WATCH MATCH & ALERT",
        "caption": "Visitor rings doorbell -> matches active watch -> Decision Engine immediately escalates alert"
    },
    {
        "id": "scene4b",
        "image": "scene4_focus.png",
        "duration_sec": 13.00,
        "title": "ATTENTION MANAGEMENT: FOCUS MODE",
        "caption": "Occupancy mode set to Focus -> perimeter motion logged silently without disruptive audible chime"
    },
    {
        "id": "scene5",
        "image": "scene5_recall.png",
        "duration_sec": 17.00,
        "title": "CONVERSATIONAL SHORT-TERM MEMORY",
        "caption": "User: \"What happened at the front door?\" -> what_happened MCP tool synthesizes clear summary"
    },
    {
        "id": "scene6",
        "image": "scene6_architecture.png",
        "duration_sec": 20.00,
        "title": "HOMEMIND COGNITIVE ARCHITECTURE",
        "caption": "\"A smarter home doesn't just detect events. It understands when they matter.\""
    }
]

def render_lower_third(frame, title, caption):
    """Draw a clean, modern lower-third caption bar on the frame."""
    h, w, _ = frame.shape
    bar_h = 100
    y_start = h - bar_h - 30
    y_end = h - 30
    x_start = 60
    x_end = w - 60

    # Create semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (x_start, y_start), (x_end, y_end), (15, 23, 42), -1)
    
    # Border
    cv2.rectangle(overlay, (x_start, y_start), (x_end, y_end), (99, 102, 241), 2)
    
    # Glow / accent bar on left
    cv2.rectangle(overlay, (x_start, y_start), (x_start + 8, y_end), (16, 185, 129), -1)

    alpha = 0.88
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Title (small cyan/indigo uppercase badge)
    cv2.putText(
        frame,
        title,
        (x_start + 24, y_start + 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (254, 215, 170), # soft amber/orange badge
        2,
        cv2.LINE_AA
    )

    # Caption text
    cv2.putText(
        frame,
        caption,
        (x_start + 24, y_start + 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (248, 250, 252), # white
        2,
        cv2.LINE_AA
    )

    return frame

def generate_video():
    output_mp4 = os.path.join(SUBMISSION_DIR, "HomeMind_Demo_Video_1080p.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_mp4, fourcc, float(FPS), (1920, 1080))

    if not out.isOpened():
        raise RuntimeError("Failed to initialize OpenCV VideoWriter")

    print(f"Rendering HomeMind Demo Video to: {output_mp4}")
    
    # Pre-render all scene keyframes with lower-thirds
    scene_frames = []
    for sc in SCENE_DEFS:
        img_path = os.path.join(SUBMISSION_DIR, sc["image"])
        raw_img = cv2.imread(img_path)
        if raw_img is None:
            raise FileNotFoundError(f"Could not load scene image: {img_path}")
        
        # Ensure 1920x1080
        if raw_img.shape[0] != 1080 or raw_img.shape[1] != 1920:
            raw_img = cv2.resize(raw_img, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
            
        frame_with_captions = render_lower_third(raw_img.copy(), sc["title"], sc["caption"])
        total_scene_frames = int(round(sc["duration_sec"] * FPS))
        scene_frames.append({
            "frame": frame_with_captions,
            "count": total_scene_frames,
            "id": sc["id"]
        })

    total_rendered_frames = 0
    
    for i, sc in enumerate(scene_frames):
        current_frame = sc["frame"]
        total_f = sc["count"]
        print(f"Writing {sc['id']} ({total_f} frames / {total_f/FPS:.2f}s)...")

        # If not the last scene, reserve transition frames for crossfade
        if i < len(scene_frames) - 1:
            hold_frames = total_f - TRANSITION_FRAMES
            next_frame = scene_frames[i + 1]["frame"]
            
            # Static hold
            for _ in range(hold_frames):
                out.write(current_frame)
                total_rendered_frames += 1

            # Crossfade transition
            for tf in range(TRANSITION_FRAMES):
                alpha = (tf + 1) / float(TRANSITION_FRAMES)
                blend = cv2.addWeighted(next_frame, alpha, current_frame, 1.0 - alpha, 0)
                out.write(blend)
                total_rendered_frames += 1
        else:
            # Last scene plays through
            for _ in range(total_f):
                out.write(current_frame)
                total_rendered_frames += 1

    out.release()
    
    final_dur = total_rendered_frames / float(FPS)
    print(f"\nVideo rendering complete!")
    print(f"Total Frames: {total_rendered_frames}")
    print(f"Duration: {final_dur:.2f} seconds ({final_dur/60:.2f} minutes)")
    print(f"Resolution: 1920x1080 @ {FPS} fps")
    print(f"Saved: {output_mp4}")

if __name__ == "__main__":
    generate_video()
