import wave
import numpy as np
import matplotlib.pyplot as plt
from sys import argv, stdout
from struct import unpack

# viz https://plot.ly/matplotlib/fft/


def fourier(audio) -> str:
    py.plot_mpl(fig, filename='mpl-basic-fft')
    return "FINAL OUTPUT"


if len(argv) != 2:
    exit("The program expects to be called with a single command-line argument:\n"
         "./peaks.py audio.wav")
filename = argv[1]
if not str(filename).endswith(".wav"):
    exit("The passed file must be a Waveform audio file ('*.wav').")


try:
    with wave.open(filename, 'rb') as AUDIO:
        stdout.write(fourier(AUDIO) + "\n")
except FileNotFoundError:
    exit(f"The file '{filename}' couldn't be found.")
