import numpy as np
import wave
import os
import fileutils as fs
import sys

def get_data_from_csv(file):
	data_raw = fs.get_from_csv(file)
	x = []
	y = []
	for a, b in zip(*data_raw):
		x.append(float(a))
		y.append(float(b))
	return file, x, y

def write_data_to_csv(file, data):
	x, y = data
	o = fs.get_csv_writer(file, 'f', 'a')
	w = o.writer
	[ w.writerow(rec) for rec in zip(x, y)]
	o.fd.close()

def main():

	s = 'data_fft_'
	for x in os.listdir('processed'):
		actual_file_path = os.path.join('processed', x)
		file_name = os.path.basename(actual_file_path)
		base_name, ext = os.path.splitext(file_name)

		if ext == '.csv' and base_name.startswith('data_fft_'):
			_, x, y = get_data_from_csv(actual_file_path)
			x=np.array(x)
			y=np.array(y)

			ymax = max(y)

			yn = y/ymax

			
			filtered = np.array ([ (a, b) for a, b, c in zip(x, y, yn) if c > 0.5 ])

			_x = filtered[:, 0]
			_y = filtered[:, 1]

			_x = _x - np.min(_x)
			_y = _y - np.min(_y)

			norm_file = 'processed/norm_%s.csv' % (base_name[len(s):])
			write_data_to_csv(norm_file, (_x, _y))

if __name__ == '__main__':
	main()

			



			


