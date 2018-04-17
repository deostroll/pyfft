import os
import matplotlib.pyplot as plt
import fileutils as fs
from threading import Event
import numpy as np
import sys
import wave

def main(bit_depth='Int16'):

	files = os.listdir('processed')
	s = 'audio_'
	for file in files:
		base_name, ext = os.path.splitext(file)
		actual_file_path = os.path.join('processed', file)
		if ext == ".wav":
			f = wave.open(actual_file_path, 'rb')
			params = f.getparams()
			rate = params.framerate
			if params.nchannels == 1:
				raw = f.readframes(-1)
				data = np.fromstring(raw, bit_depth)
				x = np.linspace(0, len(data)/rate, num=len(data))
				plt.title('Wave form: %s' % actual_file_path)
				plt.plot(x, data)
				image_path = 'processed/fig_wav_%s.png' % base_name[len(s):]
				plt.savefig(image_path)
				print('Saved :', image_path)
				plt.clf()

if __name__ == '__main__':
	if len(sys.argv[1:]):
		main(sys.argv[1])
	else:
		main()
