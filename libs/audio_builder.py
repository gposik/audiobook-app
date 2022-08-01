from typing import List
from pydub import AudioSegment

FORMAT = "ogg"


def detect_leading_silence(
    sound: AudioSegment, silence_threshold: float = -50.0, chunk_size: int = 10
) -> str:
    """
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    """
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[
        trim_ms : trim_ms + chunk_size
    ].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def concatenate_sounds(audio_paths: List[str]) -> AudioSegment:
    """receives a list of audio paths and returns a unified AudioSegment"""
    sound = AudioSegment.empty()
    for path in audio_paths:
        sound = AudioSegment.from_file(path, format=FORMAT)
        start_trim = detect_leading_silence(sound)
        end_trim = detect_leading_silence(sound.reverse())
        duration = len(sound)
        trimmed_sound = sound[start_trim : duration - end_trim]
        sound += trimmed_sound
    return sound
