import os
import matplotlib.pyplot as plt
import fileutils as fs
from threading import Event
import numpy as np

def main():

	files = os.listdir('processed')

	for file in files:
		base_name, ext = os.path.splitext(file)
		actual_file_path = os.path.join('processed', file)
		if ext == ".csv":
			robj = fs.get_csv_reader(actual_file_path)
			reader = robj.reader
			x = []
			y = []

			# reader.next()
			next(reader)

			for a, b in reader:
				x.append(float(a))
				y.append(float(b))
				# np.append(x, float(a))
				# np.append(y, float(b))

			plt.title(actual_file_path)
			plt.semilogx(x, y)
			# plt.savefig()
			# evt.wait()
			# plt.show()
			s = 'data_fft_'

			image_path = 'processed/fig_%s.png' % base_name[len(s):]
			plt.savefig(image_path)
			plt.clf()
			print('Saved:', image_path)


if __name__ == '__main__':
	main()