import os
import win32com.client
import wave

SUBMISSION_DIR = r"C:\Users\sethi\HomeMind\submission"

POLISHED_SCENES = [
    {
        "id": "scene1",
        "badge": "THE PROBLEM",
        "image": "scene1_problem.png",
        "target_duration": 8.0,
        "caption": "Notification Fatigue: Smart sensors detect raw events, but lack home context.",
        "text": "Today's smart homes suffer from notification fatigue. Every camera flutter or sensor triggers an isolated push alert. Devices detect events, but they don't understand context."
    },
    {
        "id": "scene2",
        "badge": "MEET HOMEMIND",
        "image": "scene2_dashboard.png",
        "target_duration": 13.0,
        "caption": "HomeMind: Context, Memory & Decision Layer across Ring, Alexa+ and Fire TV",
        "text": "Meet HomeMind. An intelligent context, memory, and decision layer for the ambient home. Built with Python, FastAPI, and Model Context Protocol servers, HomeMind maintains an evolving state of your home across Ring, Alexa, and Fire TV."
    },
    {
        "id": "scene3",
        "badge": "INTENT & MCP",
        "image": "scene3_watch.png",
        "target_duration": 18.0,
        "caption": "Alexa+ Simulation: set_temporary_watch tool creates targeted monitoring window",
        "text": "Rather than configuring brittle automation routines, users express intent conversationally. When I ask our simulated Alexa client: 'Watch the front door for 30 minutes', HomeMind executes the set temporary watch MCP tool, establishing an active monitoring window with a live countdown."
    },
    {
        "id": "scene4a",
        "badge": "WATCH MATCH & ALERT",
        "image": "scene4_alert.png",
        "target_duration": 15.0,
        "caption": "Simulated Ring Doorbell matches active watch -> Decision Engine escalates alert",
        "text": "Now let's simulate a physical Ring event. When a visitor presses the front doorbell, HomeMind correlates it with our active watch and immediately escalates an alert, routing it multimodally across devices."
    },
    {
        "id": "scene4b",
        "badge": "FOCUS MODE",
        "image": "scene4_focus.png",
        "target_duration": 15.0,
        "caption": "Attention Management: In Focus Mode, routine motion is logged quietly without audio chimes",
        "text": "Now watch what happens in Focus mode. When perimeter motion occurs, HomeMind's Decision Engine suppresses intrusive audible chimes, logging the event quietly in memory while preserving your focus."
    },
    {
        "id": "scene5",
        "badge": "CONVERSATIONAL MEMORY",
        "image": "scene5_recall.png",
        "target_duration": 17.0,
        "caption": "what_happened MCP tool queries short-term memory to synthesize a natural summary",
        "text": "When you're ready to catch up, there's no need to scrub through camera feeds. Simply ask: 'What happened at the front door?' HomeMind queries its MemoryManager, synthesizing recent events into a clear natural response."
    },
    {
        "id": "scene6",
        "badge": "ARCHITECTURE",
        "image": "scene6_architecture.png",
        "target_duration": 12.0,
        "caption": "\"HomeMind: A smarter home doesn't just detect events. It understands when they matter.\"",
        "text": "HomeMind is powered by FastAPI, 6 MCP tools, and 28 verified tests. Ready for Alexa+ Agent Skills and AWS cloud deployment. HomeMind: A smarter home doesn't just detect events. It understands when they matter."
    }
]

def synthesize():
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = 1 # Professional presentation pace
    
    combined_wav_path = os.path.join(SUBMISSION_DIR, "narration_voiceover_polished.wav")
    temp_files = []
    
    for s in POLISHED_SCENES:
        temp_path = os.path.join(SUBMISSION_DIR, f"temp_pol_{s['id']}.wav")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        stream.Open(temp_path, 3, False)
        speaker.AudioOutputStream = stream
        speaker.Speak(s["text"])
        stream.Close()
        temp_files.append((temp_path, s))
        
    combined_frames = []
    wave_params = None
    final_scenes = []
    
    for temp_path, s in temp_files:
        with wave.open(temp_path, 'rb') as w:
            if wave_params is None:
                wave_params = w.getparams()
            frames = w.readframes(w.getnframes())
            actual_dur = w.getnframes() / w.getframerate()
            target_dur = max(s["target_duration"], actual_dur + 0.4)
            s["final_duration"] = target_dur
            print(f"[{s['id']}] spoken: {actual_dur:.2f}s -> allocated duration: {target_dur:.2f}s")
            
            combined_frames.append(frames)
            # Add padding silence to match allocated scene duration
            silence_sec = target_dur - actual_dur
            silence_frames = int(silence_sec * w.getframerate())
            silence = b'\x00' * (silence_frames * w.getsampwidth() * w.getnchannels())
            combined_frames.append(silence)
            
            final_scenes.append(s)
            
        try:
            os.remove(temp_path)
        except:
            pass

    with wave.open(combined_wav_path, 'wb') as out_w:
        out_w.setparams(wave_params)
        for chunk in combined_frames:
            out_w.writeframes(chunk)
            
    with wave.open(combined_wav_path, 'rb') as verify_w:
        total_sec = verify_w.getnframes() / verify_w.getframerate()
        print(f"\nPolished Master Narration WAV: {combined_wav_path}")
        print(f"Total Video Narration Duration: {total_sec:.2f}s ({total_sec/60:.2f} minutes)")
        
    return final_scenes

if __name__ == "__main__":
    synthesize()
