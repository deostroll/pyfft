import numpy as np
import wave
import os
from pprint import pprint
import fileutils as fs
import matplotlib.pyplot as plt

files = list(map(lambda x: os.path.join('data', x), os.listdir('data')))
processed = list(map(lambda x: os.path.join('processed', x), os.listdir('processed')))

# pprint(files)

def plot_fft(file):
	data = fs.get_from_csv(file)
	plt.clf()
	plt.semilogx(*data)
	plt.title(file)
	plt.show()

