#!/usr/bin/python3
import numpy as np
import wave
import sys
import fileutils as fs
from scipy.fftpack import fft
from os import path
from pprint import pformat

EXT_CSV = '.csv'

def main(file, bit_depth):
  f = wave.open(file, 'rb')
  signal = f.readframes(-1)
  data = np.fromstring(signal, bit_depth)
  _len = len(data)
  rate = f.getframerate()
  channels = f.getnchannels()

  compute = True

  if channels == 1:

    x = np.linspace(0, rate, _len)
    yf = fft(data)
    yf = np.abs(yf)

    half_y = yf[:int(_len/2)]
    half_x = x[:int(_len/2)]    

  elif channels == 2:
    x = np.linspace(0, rate, _len/channels)
    
    # considering only left data
    l_data = data[::2]
    assert(len(l_data) == _len/channels)
    yf = np.abs(fft(l_data))
    assert len(x) == len(yf)

    half_x = x[: int(_len/channels/2)]
    half_y = yf[: int(_len/channels/2)]

  else:
    compute = False
    print('nothing done')

  if compute:
    csv_obj = fs.get_csv_writer('samples/data_fft.csv', 'f', 'a')
    fft_writer = csv_obj.writer
    [fft_writer.writerow([f, a]) for f,a in zip(half_x, half_y)]
    file_base = path.basename(file)
    file_without_ext, ext = path.splitext(file_base)
    unique_file_csv = 'samples/data_fft_%s%s' % (file_without_ext, EXT_CSV)
    csv_obj.fd.close()
    fs.copy('samples/data_fft.csv', unique_file_csv)
    print('Saved fft:', unique_file_csv)
    max_y = max(half_y)

    csv_obj = fs.get_csv_writer('samples/fundamental_frequencies.csv', 'f', 'a', 'na')
    writer = csv_obj.writer

    fft_set = [ (f,a, a/max_y) for f, a, in zip(half_x, half_y)]
    result = [(f,a,na) for f, a, na in fft_set if f < 20000 and na > 0.5]
    for row in result:
      writer.writerow(row)

    freq_unique_file = 'samples/fundamental_frequencies_%s%s' % (file_without_ext, EXT_CSV)
    csv_obj.fd.close()
    fs.copy('samples/fundamental_frequencies.csv', freq_unique_file)
    print('Saved fundamentals:', freq_unique_file)
    # print('Fundamental Frequencies:', pformat(result, indent=2))

if __name__ == '__main__':
    file = sys.argv[1]
    bit_width = sys.argv[2]
    main(file, bit_width)
