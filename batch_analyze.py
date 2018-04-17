import numpy as np
import wave
import os
import fileutils as fs
import sys

def analyze(file_fft, fund_fft):
	fundamental = zip(fund_fft[0], fund_fft[1])
	fundamental = list(fundamental)
	x = file_fft[0]
	y = file_fft[1]
	len_x = len(x)
	c = 0
	ds1 = []
	for f_x, f_y in fundamental:
		while x[c] < f_x and c < len_x:
			c = c + 1

		if c == len_x : break # we have exhaused the dataset

		ratio_b = x[c]/f_x
		ratio_a = x[c-1]/f_x
		if ratio_b == 1:
			#! this matches
			c_x = x[c]
			c_y = y[c]
			match_type = 'exact'
		# else ratio_a >= .95 and ratio_b <= 1.05: # within a 5% range
		else:
			# interpolation necessary
			x1 = x[c-1]
			x2 = x[c]
			y1 = y[c - 1]
			y2 = y[c]

			slope = (y2 - y1)/(x2-x1)

			#interpolated amplitude
			c_y = y1 + slope * (f_x - x1)
			c_x = f_x
			match_type = 'interpolated'
		# else:
		# 	print('Skipped:', x[c])
		# 	continue

		ds1.append((c_x, c_y, f_x, f_y, match_type))
	assert len(ds1) == len(fundamental)
	ds2 = []
	for index in range(0, len(ds1), 2):
		cf1, ca1, f1, a1, _ = ds1[index]
		cf2, ca2, f2, a2, _ = ds1[index + 1]

		ratio_test = ca1/ca2
		ratio_actual = a1/a2

		final_ratio = ratio_test/ratio_actual
		ds2.append(final_ratio > 0.95 and final_ratio < 1.05)

	true_count = 0
	# [true_count = true_count + 1 for value in ds2 if value == True ]
	for value in ds2:
		if value:
			true_count = true_count + 1

	print('Percent match:', true_count/len(ds2) * 100.0, '%')

def main(fund_file):
	files = os.listdir('processed')
	for file in files:
		base_name, ext = os.path.splitext(file)
		actual_file_path = os.path.join('processed', file)
		fx = []
		fy = []
		o = fs.get_csv_reader(fund_file)
		reader = o.reader
		next(reader)

		for a, b, _ in reader:
			fx.append(float(a))
			fy.append(float(b))

		fund_data = (fx, fy)

		if ext == ".csv":
			print('Analyzing:', actual_file_path)
			file_fft = fs.get_from_csv(actual_file_path)
			analyze(file_fft, fund_data)

if __name__ == '__main__':
	main(sys.argv[1])