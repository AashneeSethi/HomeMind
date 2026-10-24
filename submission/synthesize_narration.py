import os
import win32com.client
import wave

SUBMISSION_DIR = r"C:\Users\sethi\HomeMind\submission"

# Concise, punchy script precisely timed for ~110 seconds total video
SCENES = [
    {
        "id": "scene1",
        "image": "scene1_problem.png",
        "target_duration": 15.0,
        "caption": "The Smart Home Problem: Every sensor interrupts. None understand context.",
        "text": "Today's smart homes are louder than ever. Every camera chime, backyard leaf flutter, or hallway sensor triggers an isolated push notification, interrupting dinner or focus work. Devices detect events, but they don't understand context."
    },
    {
        "id": "scene2",
        "image": "scene2_dashboard.png",
        "target_duration": 15.0,
        "caption": "HomeMind: Context, Memory, and Decision Layer across Ring, Alexa & Fire TV",
        "text": "Meet HomeMind. HomeMind is an intelligent context, memory, and decision layer for the ambient home. Built with Python, FastAPI, and Model Context Protocol servers, HomeMind unifies Ring, Alexa, and Fire TV into one cohesive intelligence."
    },
    {
        "id": "scene3",
        "image": "scene3_watch.png",
        "target_duration": 18.0,
        "caption": "Alexa+ Agent Skill: set_temporary_watch tool execution with countdown",
        "text": "Rather than configuring brittle automation routines, users express intent conversationally. When I ask: Watch the front door for 30 minutes, HomeMind executes the set temporary watch MCP tool. A dynamic monitoring window is established with live countdown."
    },
    {
        "id": "scene4a",
        "image": "scene4_alert.png",
        "target_duration": 12.0,
        "caption": "Watch Match: Doorbell press escalates an immediate active alert",
        "text": "Now let's simulate a physical Ring event. When a visitor presses the front doorbell, HomeMind correlates it with our active watch and immediately escalates an alert."
    },
    {
        "id": "scene4b",
        "image": "scene4_focus.png",
        "target_duration": 13.0,
        "caption": "Attention Management: In Focus Mode, motion is logged silently without audio chime",
        "text": "Now watch what happens in Focus mode. When perimeter motion occurs, HomeMind suppresses intrusive audible chimes, logging the event quietly while keeping you in your flow."
    },
    {
        "id": "scene5",
        "image": "scene5_recall.png",
        "target_duration": 17.0,
        "caption": "Conversational Memory: what_happened MCP tool synthesizes recent history",
        "text": "When you're ready to catch up, there's no need to scrub through camera feeds. Simply ask Alexa: What happened at the front door? HomeMind queries short-term memory, synthesizing recent events into a clear natural response."
    },
    {
        "id": "scene6",
        "image": "scene6_architecture.png",
        "target_duration": 20.0,
        "caption": "\"A smarter home doesn't just detect events. It understands when they matter.\"",
        "text": "HomeMind is powered by FastAPI, Pydantic, 6 Model Context Protocol tools, and a 28-test verified suite. The architecture is ready for Amazon Agent Skills and AWS cloud deployment. HomeMind: A smarter home doesn't just detect events. It understands when they matter."
    }
]

def synthesize():
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = 1 # Professional, crisp presentation pace
    
    combined_wav_path = os.path.join(SUBMISSION_DIR, "narration_voiceover.wav")
    temp_files = []
    
    for s in SCENES:
        temp_path = os.path.join(SUBMISSION_DIR, f"temp_{s['id']}.wav")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        stream.Open(temp_path, 3, False)
        speaker.AudioOutputStream = stream
        speaker.Speak(s["text"])
        stream.Close()
        temp_files.append((temp_path, s))
        
    combined_frames = []
    wave_params = None
    
    for temp_path, s in temp_files:
        with wave.open(temp_path, 'rb') as w:
            if wave_params is None:
                wave_params = w.getparams()
            frames = w.readframes(w.getnframes())
            actual_dur = w.getnframes() / w.getframerate()
            target_dur = max(s["target_duration"], actual_dur + 0.5)
            s["final_duration"] = target_dur
            print(f"[{s['id']}] spoken: {actual_dur:.2f}s -> scene duration: {target_dur:.2f}s")
            
            combined_frames.append(frames)
            # Add padding silence to fill scene duration
            silence_sec = target_dur - actual_dur
            silence_frames = int(silence_sec * w.getframerate())
            silence = b'\x00' * (silence_frames * w.getsampwidth() * w.getnchannels())
            combined_frames.append(silence)
            
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
        print(f"\nMaster Narration WAV: {combined_wav_path}")
        print(f"Total Video Narration Duration: {total_sec:.2f}s ({total_sec/60:.2f} minutes)")

if __name__ == "__main__":
    synthesize()
