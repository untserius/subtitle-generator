import os

# Set the path to your Google Cloud service account key JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\Study\Keys\silken-setting-411607-c24dc2d5768b.json"

print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

r = sr.Recognizer()

def transcribe_audio(path):
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        text = r.recognize_google_cloud(audio_listened)
    return text

def get_large_audio_transcription_on_silence(path):
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

    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}."
            print(chunk_filename, ":", text)
            whole_text += text

    return whole_text

path = "output_audio.wav"
print("\nFull text:", get_large_audio_transcription_on_silence(path))