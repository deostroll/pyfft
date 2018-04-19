import numpy as np
import wave
import os
from pprint import pprint
import fileutils as fs
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

files = list(map(lambda x: os.path.join('data', x), os.listdir('data')))
processed = list(map(lambda x: os.path.join('processed', x), os.listdir('processed')))
samples = list(map(lambda x: os.path.join('samples', x), os.listdir('samples')))
# pprint(files)



def plot_fft(file):
	data = fs.get_from_csv(file)
	plt.clf()
	plt.semilogx(*data)
	plt.title(file)
	plt.show()

def plot_fft_data(*args):
	# ncols =  2
	# if len(args) % 2 == 0:
	# 	nrows = int(len(args)/2)
	# else:
	# 	nrows = int((len(args) + 1)/2)

	# fig, plots = plt.subplots(nrows, ncols, figsize=(15,7), sharey=True)
	
	index = 0
	for item in args:
		x , y = item
		# ax = plots[index]
		# ax.semilogx(np.array(x, dtype=float), np.array(y, dtype=float))
		# ax.set_title('Plot: %s' % (index))
		x = np.array(x, dtype=float)
		y = np.array(y, dtype=float)
		plt.semilogx(x, y, label=index)
		index = index + 1
	plt.legend()
	plt.show()

fund = []

for x in samples:
	filename = os.path.basename(x)
	base_name, ext = os.path.splitext(filename)
	if base_name.startswith('data_fft_') and ext == ".csv":
		res = fs.get_from_csv(x)
		fund.append(res)
	else:
		fund.append(None)

test_data_raw = [ (x, fs.get_from_csv(x)) for x in processed if x.endswith(".csv") ]
test = []
# pprint(test_data_raw[0])
for item in test_data_raw:
	# pprint(len(item))
	file, raw_data = item
	x = []
	y = []
	
	for a, b in zip(raw_data[0], raw_data[1]):
		x.append(float(a))
		y.append(float(b))

	test.append( (file, x, y) )

def cycle(file, x, y):
	fig, ax = plt.subplots()
	ax.set_ylim([0, 5000000])
	plt.semilogx(x, y, label='sample')
	ln, = plt.semilogx([], [])
	
	def animate(index):
		# print('Amimate:', index)
		test_file, x, y = test[index]
		ln.set_data(x, y)
		# ln.set_label(index)
		plt.title(test_file)
		return ln,

	ani = FuncAnimation(fig, 
		func=animate, 
		frames=np.arange(len(test)), 
		# blit=True,
		# init_func=lambda: (ln, ),
		interval=1000)
	# plt.labels()
	# ani.save('movie.mp4')
	plt.show()
	# print('done')

# f = 'samples/data_fft_KPAC_mono_snap.csv'
# sample_data = fs.get_from_csv(f)
# x = []
# y = []
for a, b in zip(*sample_data):
	x.append(float(a))
	y.append(float(b))

# cycle(f, x, y)