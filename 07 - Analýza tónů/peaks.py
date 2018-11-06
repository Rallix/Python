import wave
import numpy as np
from typing import Tuple, Optional
from struct import unpack


def fourier(audio: wave.Wave_read) -> Tuple[Optional[int], Optional[int]]:
    """Fourierova analýza vstupních dat, vracející (nejnižší, nejvyšší) frekvenci."""
    frames = audio.getnframes()
    sample_rate = audio.getframerate()
    windows = frames // sample_rate
    channels = audio.getnchannels()  # Stereo (2) vs. Mono (1)
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
            # 'high'
            if not high:
                high = j
            elif amplitude > amplitudes[high]:
                high = j
            # 'low'
            if not low:
                low = j
            elif amplitude < amplitudes[low]:
                low = j
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
