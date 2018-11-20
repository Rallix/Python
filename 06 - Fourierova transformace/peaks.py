import wave
import numpy as np
# import matplotlib.pyplot as plt
from sys import argv, stdout
from typing import Tuple, Optional
from struct import unpack


def merge_channels(data: np.array):
    """Sloučí kanály stereo záznamu."""
    merged = []
    for i in range(0, data.size, 2):
        merged.append(np.average(data[i] + data[i+1]))
    return np.array(merged)


def fourier(audio: wave.Wave_read) -> Tuple[Optional[int], Optional[int]]:
    """Fourierova analýza vstupních dat, vracející (nejnižší, nejvyšší) frekvenci."""
    # data
    length = audio.getnframes()
    sample_rate = audio.getframerate()
    windows_count = length // sample_rate
    channels = 1 if audio.getnchannels() == 1 else 2  # Stereo (2) vs. Mono (1)
    frames = sample_rate * windows_count

    data = np.array(unpack(f"{channels * frames}h", audio.readframes(frames)))
    if channels == 2:
        data = merge_channels(data)

    # amplitudy
    low, high = None, None
    for i in range(windows_count):
        bounds = (i * sample_rate, i * sample_rate + sample_rate)
        window = data[bounds[0]:bounds[1]]
        amplitudes = np.abs(np.fft.rfft(window))
        average = np.average(amplitudes)

        # peaks
        peak = lambda amp: amp >= 20 * average  # ze zadání
        for j in range(len(amplitudes)):
            amplitude = amplitudes[j]
            if not peak(amplitude):
                continue
            if not low:
                low = j
                high = j
            elif j > high:
                high = j
    if not any((low, high)):
        return None, None
    return (high, low) if high < low else (low, high)  # Může být totiž prohozené


def audio_fourier(audio: wave.Wave_read) -> str:
    """Zpracuje hudební soubor Fourierovou analýzou a vrátí textový výsledek."""
    low, high = fourier(audio)
    if not any((low, high)):
        return "no peaks"
    else:
        return f"low = {low}, high = {high}"


if len(argv) != 2:
    exit("The program expects to be called with a single command-line argument:\n"
         "./peaks.py audio.wav")
filename = argv[1]
if not str(filename).endswith(".wav"):
    exit("The input file must be a Waveform audio file ('*.wav').")
try:
    with wave.open(filename, 'rb') as AUDIO:
        stdout.write(audio_fourier(AUDIO) + "\n")
except FileNotFoundError:
    exit(f"The file '{filename}' couldn't be found.")
