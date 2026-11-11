import gradio as gr
from gradio_client import Client, handle_file
from gtts import gTTS
import subprocess
import os
import uuid

token = os.environ.get("HF_TOKEN")

def generate_av(image_path, script_text):
    if not image_path or not script_text:
        return None
    
    # 1. Fetch silent animation from Stable Video Diffusion
    client = Client("multimodalart/stable-video-diffusion", token=token)
    result = client.predict(
        image=handle_file(image_path),
        seed=0,
        randomize_seed=True,
        motion_bucket_id=127,
        fps_id=6,
        api_name="/video"
    )
    silent_video_path = result[0]['video']
    
    # 2. Generate AI Voice locally
    audio_path = f"/tmp/{uuid.uuid4()}_audio.mp3"
    tts = gTTS(text=script_text, lang='en', slow=False)
    tts.save(audio_path)
    
    # 3. Stitch them together using FFmpeg
    # Loops the short video to match the length of the voiceover
    output_video = f"/tmp/{uuid.uuid4()}_final.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", 
        "-i", silent_video_path,
        "-i", audio_path,
        "-c:v", "libx264", 
        "-c:a", "aac",
        "-shortest", 
        "-pix_fmt", "yuv420p",
        output_video
    ]
    subprocess.run(cmd, check=True)
    
    return output_video

with gr.Blocks() as demo:
    gr.Markdown("# 🎬 Audio-Video Pipeline App")
    with gr.Row():
        with gr.Column():
            img_in = gr.Image(type="filepath", label="Upload Infographic")
            text_in = gr.Textbox(label="Type the text to be spoken", lines=3)
        vid_out = gr.Video(label="Generated Video with Voiceover")
        
    btn = gr.Button("Generate Animation & Audio")
    btn.click(generate_av, inputs=[img_in, text_in], outputs=[vid_out])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)