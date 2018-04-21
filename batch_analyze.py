#!/usr/bin/python3
import numpy as np
import wave
import os
import fileutils as fs
import sys

def filter_peaks(data):
	x , y = data
	max_y = max(y)
	
	x = np.array(x)
	y = np.array(y)

	z = y / max_y

	res = np.array([ (a, b) for a, b, c in zip(x,y,z) if c > 0.5 ])

	return res[:,0], res[:1]

def normed(data):
	x, y = data

	_x = x - np.min(x)
	_y = y - np.min(y)

	return (_x, _y)

def main(sample_fft):

	# begin - calculatin the normalized dataset for sample fft
	sample_fft_data = fs.get_from_csv(sample_fft)
	sample_fft_peaks = filter_peaks(sample_fft_data)
	sample_fft_normed = normed(sample_fft_peaks)
	sx, _ = sample_fft_normed
	swidth = np.max(sx)
	print(sample_fft)
	print('\tWidth:', swidth)

	# end - calculatin the normalized dataset for sample fft
	files = os.listdir('processed')
	s = 'data_fft_'
	for file in files:
		base_name, ext = os.path.splitext(file)
		actual_file_path = os.path.join('processed', file)
		
		if ext == ".csv" and base_name.startswith(s):
			fft_data = fs.get_from_csv(actual_file_path)
			fft_peaks = filter_peaks(fft_data)
			fft_normed = normed(fft_peaks)
			x = fft_normed[0]
			width = np.max(x)
			print(actual_file_path)
			print('\tWidth:', width)
			ratio = swidth/width if swidth > width else width/swidth
			print('\tRatio:', ratio)

if __name__ == '__main__':
	main(sys.argv[1])