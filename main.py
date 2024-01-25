import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft
from scipy.signal import spectrogram

SAMPLE_RATE = 16000
CENTER_FREQ = 1500
CARRIERS = 16 # must be pair
BANDWIDTH = 2400
BAUD_RATE = 100
GUARD_INTERVAL_SYMBOLS = BAUD_RATE * 3
GUARD_TIME_SYMBOLS = BAUD_RATE / 10

def get_carrier_frequencies():
    carriers = []
    spacing = BANDWIDTH / CARRIERS
    for i in range(0, int(CARRIERS / 2)):
        carriers.append(CENTER_FREQ + (i+1) * spacing)
        carriers.append(CENTER_FREQ - (i+1) * spacing)

    carriers.sort()
    return carriers

def modulate(data: bytes, carriers: list):
    npa = np.frombuffer(data, dtype=np.uint8)
    bits = np.unpackbits(npa)

    # append zeros at the end of data to have an integer number of symbols
    if bits.size % len(carriers):
        zeros = np.zeros(len(carriers) - (bits.size % len(carriers)), dtype=np.uint8)
        bits = np.append(bits, zeros)

    symbols = int(bits.size / len(carriers))

    whole_signal = np.zeros(0)

    for offset in range(0, bits.size, len(carriers)):
        symbol_bits = bits[offset:offset+len(carriers)]

        print(symbol_bits)

        signal = np.zeros(int(SAMPLE_RATE / BAUD_RATE))
        for i, bit in enumerate(symbol_bits):
            time = np.arange(0, 1 / BAUD_RATE, 1 / SAMPLE_RATE)
            signal = signal + (bit * np.sin(2 * np.pi * carriers[i] * time))


        whole_signal = np.append(whole_signal, signal)

    whole_time = np.arange(0, symbols / BAUD_RATE, 1 / SAMPLE_RATE)
    fixed_carrier_signal = np.sin(2 * np.pi * CENTER_FREQ * whole_time)
    whole_signal = whole_signal + fixed_carrier_signal


    frequencies, times, Sxx = spectrogram(whole_signal, SAMPLE_RATE)
    # Plot the spectrogram as a color map
    plt.pcolormesh(times, frequencies, Sxx, shading='auto')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.title('Spectrogram')
    plt.colorbar(label='Power/Frequency (dB/Hz)')

    # Show the plot
    plt.show()


    plt.figure(figsize=(10, 4))
    plt.subplot(2, 1, 1)
    plt.plot(whole_time, whole_signal)
    plt.title('Modulated Signal')
    plt.show()


    return whole_signal        

data = b"Hello World!"

signal = modulate(data, get_carrier_frequencies())

