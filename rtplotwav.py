#!/usr/bin/python
import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import time
import wave
import sys
from threading import Thread
import Queue as queue

from pprint import pprint as pp, pformat as fmt
from colors import *
from Tkinter import TclError

class Expando(object):
	pass

class AsyncPlotter(Thread):
	
	def __init__(self, line, chunk, bit_width, sample_width):
		
		Thread.__init__(self)
		
		self._line = line
		self._chunk = chunk
		self._bit_width = bit_width
		self._sample_width = sample_width

		self._q = queue.Queue()
		self._out_queue = queue.Queue()
		self._is_active = False
		self.daemon = True

	def run(self):

		print 'thread started'
		BYTES_PER_CHUNK = self._chunk * self._sample_width
		while self._is_active:
			try:
				raw = self._q.get(0)
			except queue.Empty:
				continue

			if len(raw) == BYTES_PER_CHUNK:
				data = np.fromstring(raw, self._bit_width)
			else:
				data = np.zeros(self._chunk)
				last = np.fromstring(raw, self._bit_width)
				data[:len(last)] = last
				# self._is_active = False
			self._out_queue.put(data)
		print 'thread stopped'

	def plot(self, raw_data):

		self._q.put(raw_data)

	def start(self):
		
		self._is_active = True
		Thread.start(self)

	def get_data(self):

		try:
			return self._out_queue.get(0)
		except queue.Empty:
			return None

	def stop(self):
		self._is_active = False

	def is_done(self):
		return self._is_active and (self._q.qsize() > 0)


class AsyncPlayer(Thread):

	def __init__(self, stream):

		Thread.__init__(self)
		self._stream = stream
		self._is_busy = False
		self._is_active = False
		self._q = queue.Queue()
		self.daemon = True

	def run(self):
	
		print 'player thread started'
		while self._is_active:
			try:
				raw = self._q.get(0)
			except queue.Empty:
				continue

			self._write(raw)

		print 'player thread stopped'

	def _write(self, raw):
		self._is_busy = True
		self._stream.write(raw)
		self._is_busy = False

	def stop(self):
		self._is_active = False

	def start(self):
		self._is_active = True
		Thread.start(self)

	def writeAsync(self, raw_data):
		self._q.put(raw_data)

params = ['nchannels', 'sampwidth', 'framerate', 'nframes', "comptype", 'compname']

def dbg(*args, **kwargs):
	
	result = ''
	f = lambda x: fmt(x, indent=2)
	if len(args):
		result = result + ('%s ' * len(args)) % (tuple(map(f, args)))

	if len(kwargs):
		plug = ''
		dat = []
		for k,v in kwargs:
			plug = plug + '%s:%s,'
			dat.append(k)
			dat.append(f(v))

		result = result + plug % (tuple(dat))

	# print '::dbg'
	print color(result, fg='yellow')
	# print '::dbg::'


CHUNK = 1024             # samples per frame

def main(file, bit_width):
	f = wave.open(file, 'rb')
	p = pyaudio.PyAudio()
	
	WIDTH = f.getsampwidth()
	FORMAT = p.get_format_from_width(WIDTH)
	CHANNELS = f.getnchannels()
	RATE = f.getframerate()

	prms = f.getparams()
	d={}
	d.update(zip(params, prms))
	dbg('Params:', d)
	
	stream = p.open(
		format = FORMAT, 
		channels = CHANNELS, 
		rate = RATE, 
		output = True
	)
	
	fig, ax = plt.subplots(1, figsize=(15,7))

	plt.show(block=False)	
	
	x = np.arange(CHUNK)
	# creating line with random data
	rnd_rng = np.random.rand(CHUNK)
	rnd_rng[1] = -32767
	rnd_rng[2] = 32767
	
	line, = ax.plot(x, rnd_rng, '-', lw=2)

	plotter = AsyncPlotter(line, CHUNK, bit_width, WIDTH)
	plotter.start()

	player = AsyncPlayer(stream)
	player.start()

	while True:
		raw = f.readframes(CHUNK)
		if raw:			
			# start = time.time()
			# player.writeAsync(raw)
			player.writeAsync(raw)
			plotter.plot(raw)
			data = plotter.get_data()
			if not data is None:
				line.set_ydata(data)
				try:
					fig.canvas.draw()
					fig.canvas.flush_events()
				except TclError:
					plotter.stop()
					break
			
		else:						
			break

	player.stop()
	while not plotter.is_done():
		data = plotter.get_data()
		if not data is None:
			line.set_ydata(data)
			try:
				fig.canvas.draw()
				fig.canvas.flush_events()
			except TclError:
				plotter.stop()
				break
		else:
			break

	plotter.stop()
	print 'waiting for workers to stop...'
	plotter.join()
	player.join()
	stream.stop_stream()
	stream.close()
	p.terminate()

if __name__ == '__main__':
	file = sys.argv[1]
	width = sys.argv[2]
	main(file, width)