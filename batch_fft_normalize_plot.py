import numpy as np
import wave
import os
import fileutils as fs
import sys
import matplotlib.pyplot as plt

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

def get_normed_data(data):
	x , y  = data
	return (x - np.min(x), y - np.min(y))



def main(compare_file):

	_, ix, iy = get_data_from_csv(compare_file)

	inormed = get_normed_data((ix, iy))

	plt.plot(inormed[0], inormed[1])
	ln, = plt.plot([],[], label='test')
	
	def plot(b, image):
		ln.set_data(b[0], b[1])
		plt.savefig(image)

	s = 'norm_'
	
	for x in os.listdir('processed'):
		actual_file_path = os.path.join('processed', x)
		file_name = os.path.basename(actual_file_path)
		base_name, ext = os.path.splitext(file_name)

		if ext == '.csv' and base_name.startswith(s):
			_, x, y = get_data_from_csv(actual_file_path)
			normed = (x, y)
			image_file = 'processed/fig_norm_compare_%s.png' % (base_name[len(s):])
			plot(normed, image_file)
			print("Saved:", image_file)

if __name__ == '__main__':
	main(sys.argv[1])

			



			


