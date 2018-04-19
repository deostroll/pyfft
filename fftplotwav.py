#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
# import json
# import csv
import fileutils as fs
# import struct
from scipy.fftpack import fft

# file = sys.argv[1]
# bit_depth = sys.argv[2]


def main(file, bit_depth):
    f = wave.open(file, 'rb')
    signal = f.readframes(-1)
    data = np.fromstring(signal, bit_depth)

    rate = f.getframerate()
    channels = f.getnchannels()

    show = True
    if channels == 1:

        _len = len(data)
        x = np.linspace(0, rate, _len)
        # print('Length d:', len(data))
        # print('Length x:', len(x))
        yf = fft(data)
        # print('Length:', len(yf))
        yf = np.abs(yf)

        half_y = yf[:int(_len/2)]
        half_x = x[:int(_len/2)]
        csvobj = fs.get_csv_writer('data_fft.csv', 'f', 'a')
        fft_writer = csvobj.writer
        [fft_writer.writerow([f, a]) for f,a in zip(half_x, half_y)]
        # plt.semilogx(half_x, half_y)
        
    elif channels == 2:
        _len = len(data)/channels
        x = np.linspace(
            0,
            rate,
            num=_len
        )
        # left channel
        ldata = data[::2]

        # right channel
        rdata = data[1::2]

        half_x = x[:int(_len/2)]
        half_y = ldata[:int(_len/2)]
        
        # plt.semilogx(x[:int(_len/2)], ldata[:int(_len/2)])
        # plt.plot(x[:int(_len/2)], rdata[:int(_len/2)])

    else:
        show = False

    if show:
        plt.semilogx(half_x, half_y)
        plt.title('FFT plot: %s' % file)
        plt.show()


if __name__ == '__main__':
    file = sys.argv[1]
    bit_width = sys.argv[2]
    main(file, bit_width)
