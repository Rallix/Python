import wave
import peaks
from sys import argv, stdout

if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./music.py 440 audio.wav")

freq = argv[1]
filename = argv[2]

if not str(filename).endswith(".wav"):
    exit("The input file must be a Waveform audio file ('*.wav').")
if not freq.isnumeric():
    exit("The input frequency is supposed to be an integer.")
try:
    with wave.open(filename, 'rb') as AUDIO:
        # frequency = int(freq)
        stdout.write(peaks.audio_fourier(AUDIO) + "\n")
except FileNotFoundError:
    exit(f"The file '{filename}' couldn't be found.")
