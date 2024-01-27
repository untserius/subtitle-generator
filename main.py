import os
import io
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from moviepy.editor import VideoFileClip

# import tkinter as tk
# from tkinter import filedialog


# Set the path to your Google Cloud service account key JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\Study\Keys\silken-setting-411607-c24dc2d5768b.json"
print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))


r = sr.Recognizer()

def transcribe_audio(audio_chunk):
    audio_io = io.BytesIO()
    audio_chunk.export(audio_io, format="wav")
    audio_io.seek(0)
    audio = sr.AudioFile(audio_io)

    with audio as source:
        audio_data = r.record(source)
    text = r.recognize_google_cloud(audio_data)
    return text

def extract_audio_from_video(video_path):
    clip = VideoFileClip(video_path)
    audio = clip.audio
    return audio

def create_subtitle(path, output_file):
    sound = AudioSegment.from_file(path)

    chunks = split_on_silence(sound,
            min_silence_len = 500,
            silence_thresh = sound.dBFS-14,
            keep_silence = 500,
    )

    folder_name = "audio-chunks"

    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""


    subtitles = []

    for i, chunk in enumerate(chunks, start=1):
        try:
            chunk_text = transcribe_audio(chunk)
        except sr.UnknownValueError as e:
            print("", str(e))
        else:
            chunk_duration = len(chunk) / 1000
            start_time = subtitles[-1][2] if subtitles else 0
            end_time = start_time + chunk_duration
            subtitles.append((i, start_time, end_time, chunk_text.strip()))

    save_subtitles(subtitles, output_file)
    burn_subtitles(path, output_file)

def save_subtitles(subtitles, output_file):
    with open(output_file, "w") as file:
        for i, start_time, end_time, text in subtitles:
            file.write(f"{i}\n")
            file.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
            file.write(f"{text}\n\n")

def burn_subtitles(video_path, subtitle_path):
    output_video_path = os.path.splitext(video_path)[0] + "_with_subtitles.mp4"
    command = f'ffmpeg -i "{video_path}" -vf "subtitles={subtitle_path}" "{output_video_path}" -y'
    subprocess.run(command, shell=True)

def format_timestamp(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# root = tk.Tk()
# root.title("Video Subtitle Generator")

# video_path = filedialog.askopenfilename(title="Select Video File", filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))

# if video_path:
#         output_file = "transcribed_text.srt"
#         create_subtitle(video_path, output_file)
#         result_label.config(text=f"Subtitles generated and burned onto video.\nOutput saved to {output_file}")


# def create_subtitle(video_path, output_file):

#     result_label.config(text="Transcription and subtitle generation completed.")


# select_button = tk.Button(root, text="Select Video File", command=generate_subtitles)
# select_button.pack(pady=10)

# result_label = tk.Label(root, text="")
# result_label.pack(pady=10)

# root.mainloop()

path = "test3.mp4"
output_file = "test3.srt"
create_subtitle(path, output_file)
print(f"Transcribed text saved to {output_file}")