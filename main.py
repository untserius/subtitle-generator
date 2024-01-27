import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io

from moviepy.editor import VideoFileClip

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

    # with sr.AudioFile(path) as source:
    #     audio_listened = r.record(source)
    #     text = r.recognize_google_cloud(audio_listened)
    # return text

def get_large_audio_transcription_on_silence(path, output_file):
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
            print("Error:", str(e))
        else:
            chunk_duration = len(chunk) / 1000
            start_time = subtitles[-1][2] if subtitles else 0
            end_time = start_time + chunk_duration
            subtitles.append((i, start_time, end_time, chunk_text.strip()))

    save_subtitles(subtitles, output_file)

def save_subtitles(subtitles, output_file):
    with open(output_file, "w") as file:
        for i, start_time, end_time, text in subtitles:
            file.write(f"{i}\n")
            file.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
            file.write(f"{text}\n\n")

def format_timestamp(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    # for i, audio_chunk in enumerate(chunks, start=1):
    #     chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
    #     audio_chunk.export(chunk_filename, format="wav")

    #     try:
    #         text = transcribe_audio(chunk_filename)
    #     except sr.UnknownValueError as e:
    #         print("Error:", str(e))
    #     else:
    #         text = f"{text.capitalize()}."
    #         print(chunk_filename, ":", text)
    #         whole_text += text

    # with open(output_file, "w") as file:
    #     file.write(whole_text)

path = "donut.mp4"
output_file = "transcribed_text2.srt"
get_large_audio_transcription_on_silence(path, output_file)
print(f"Transcribed text saved to {output_file}")