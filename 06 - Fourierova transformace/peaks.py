import wave
import numpy as np
# import matplotlib.pyplot as plt
from sys import argv, stdout
from typing import Tuple, Optional
from struct import unpack

# viz https://plot.ly/matplotlib/fft/


def fourier_stereo(audio: wave.Wave_read) -> Tuple[int, int]:
    frames = audio.getnframes()
    sample_rate = audio.getframerate()
    windows = frames // sample_rate
    low, high = None, None
    for i in range(windows):
        # data
        data = np.array(unpack(f"<{sample_rate*2}h", audio.readframes(sample_rate)))
        # amplitudy
        amplitudes = np.abs(np.fft.rfft(data))
        average = np.average(amplitudes)
        # peaks
        for j in range(len(amplitudes)):
            amplitude = amplitudes[j]
            if amplitude < 20 * average:
                continue
            # high TODO: --> max
            if not high:
                high = j  # uchovat high
            elif amplitude > amplitudes[high]:
                high = j
            # low TODO: <-- min
            if not low:
                low = j
            elif amplitude < amplitudes[low]:
                low = j
    return low, high


def fourier_mono(audio: wave.Wave_read) -> Tuple[int, int]:
    frames = audio.getnframes()
    sample_rate = audio.getframerate()
    windows = frames // sample_rate
    low, high = None, None
    for i in range(windows):
        # data
        data = unpack(f"<{sample_rate}h", audio.readframes(sample_rate))
        # amplitudy
        amplitudes = np.abs(np.fft.rfft(data))
        average = np.average(amplitudes)
        # peaks
        for j in range(len(amplitudes)):
            amplitude = amplitudes[j]
            if amplitude < 20 * average:
                continue
            if not high:
                high = j
            elif amplitude > amplitudes[high]:
                high = j
            if not low:
                low = j
            elif amplitude < amplitudes[low]:
                low = j
    return low, high


def fourier(audio: wave.Wave_read) -> Tuple[Optional[int], Optional[int]]:
    frames = audio.getnframes()
    sample_rate = audio.getframerate()
    windows = frames // sample_rate
    channels = 2 if audio.getnchannels() == 2 else 1  # Stereo vs. Mono
    low, high = None, None
    for i in range(windows):
        # data
        data = unpack(f"<{sample_rate*channels}h", audio.readframes(sample_rate))
        # amplitudy
        amplitudes = np.abs(np.fft.rfft(data))
        average = np.average(amplitudes)
        # peaks
        for j in range(len(amplitudes)):
            amplitude = amplitudes[j]
            if amplitude < 20 * average:
                continue
            if not high:
                high = j
            elif amplitude > amplitudes[high]:
                high = j
            if not low:
                low = j
            elif amplitude < amplitudes[low]:
                low = j
    if not any((low, high)):
        return None, None
    return (high, low) if high < low else (low, high)  # Může být totiž prohozené


def process_audio(audio: wave.Wave_read) -> str:
    low, high = fourier(audio)

    # if audio.getnchannels() == 2:
    #     low, high = fourier_stereo(audio)
    # else:
    #     low, high = fourier_mono(audio)
    if not any((low, high)):
        return "no peaks"
    else:
        return f"low = {low}, high = {high}"


if len(argv) != 2:
    exit("The program expects to be called with a single command-line argument:\n"
         "./peaks.py audio.wav")
filename = argv[1]
if not str(filename).endswith(".wav"):
    exit("The passed file must be a Waveform audio file ('*.wav').")
try:
    with wave.open(filename, 'rb') as AUDIO:
        stdout.write(process_audio(AUDIO) + "\n")
except FileNotFoundError:
    exit(f"The file '{filename}' couldn't be found.")
