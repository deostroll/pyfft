#!/usr/bin/python3
import numpy as np
import wave
from pprint import pprint as pp
import sys
from scipy.fftpack import fft
import fileutils as fs
from threading import Thread, Event
import pyaudio
import queue
from os import path
import time
import math
from functools import reduce

Expando = fs.Expando

def pad(n, len=2):
	return (('0' * 2) + str(n))[-2:]

class AsyncPlayer:

	def __init__(self, file, sample_length, callback, bit_depth='Int16'):
		
		self.file = file

		if bit_depth == 'Int16':
			self.format = pyaudio.paInt16
		else:
			raise 'Unknown format:'

		self.sample_length = sample_length
		self.bit_depth = bit_depth
		self.callback = callback

	def play(self):

		# channels = self.channels
		# rate = self.rate
		format = self.format

		self.CHUNK = 1024

		self._pyaudio = pyaudio.PyAudio()

		self._wfile = wave.open(self.file)
		params = self._wfile.getparams()
		print("WAV parameters:")
		print(params)

		self._p = p = pyaudio.PyAudio()

		self.stream = p.open(
			format=format,
			channels=params.nchannels,
			rate=params.framerate,
			output=True
		)

		self._q = queue.Queue()

		t1 = Thread(target=self._process, name='fft')

		t2 = Thread(target=self._play, name='player')
		# t1.start()

		t1.daemon = t2.daemon = True

		t1.start()
		t2.start()

		self._event = Event()

	def _play(self):

		f = self._wfile
		stream = self.stream
		q = self._q
		params = f.getparams()
		self.params = params
		# Assuming a frame rate of 44100 samples per second.
		# Therefore time for one sample = 1/44100 seconds.
		# Therefore, number of samples in say 4 seconds,
		# 	= 1/44100 * 4

		frame_length = int(params.framerate * self.sample_length)
		
		self.frame_length = frame_length

		print('Frame Length:', frame_length)
		counter = 0

		while True:
			raw = f.readframes(frame_length)
			counter = counter + 1
			if len(raw):
				q.put((counter, raw))
				stream.write(raw)
			else:
				break

		stream.close()
		self._p.terminate()

		self._event.set()

	def _process(self):
		
		bit_depth = self.bit_depth
		q = self._q
		file = self.file
		fname, ext = path.splitext(path.basename(file))
		f = self._wfile
		cb = self.callback
		self.fname = fname
		while True:			
			cb(*q.get())
			q.task_done()

	def wait(self):

		self._event.wait()
		self._q.join()

def find_first_index(fn, data):
	counter = 0
	broken = False
	for x in data:
		if fn(x):
			broken = True
			break;
		counter = counter + 1
	return counter if broken == True else -1

def main(file, bit_depth):

	THRESHOLD = 10880 # This is the lowest value observed for a snap
	CACHE_SIZE = 2
	SAMPLE_LENGTH = .540 / 2

	def write_wav(file, cache):
		accumulator = lambda acc, item: acc + item[1]
		
		raw_data = reduce(
			accumulator,
			filter(lambda x: x[0], cache),
			b''
		)
		
		framerate = player.params.framerate
		sample_length = player.sample_length
		total_length = sample_length * 2

		data = np.fromstring(raw_data, bit_depth)

		indexes, = np.nonzero(np.abs(data) > THRESHOLD)

		start = indexes[0] - int(framerate * sample_length)
		end = start + int(framerate * total_length)

		sub_sliced = data[start:end]

		ws = wave.open(file, 'w')
		ws.setnchannels(1)
		ws.setframerate(44100)
		ws.setsampwidth(2)
		# ws.writeframes(raw_data[desired_byte_start: desired_bytes_length])
		ws.writeframes(sub_sliced.tobytes())

		print('Saved:', file)
		ws.close()	

	def write_wav_index(file, raw_data, index, length):
		
		print('with index:', file, index, length)
		
		data = np.fromstring(raw_data, bit_depth)
		new_data = data[index : length]
		raw = bytes(new_data)

		ws = wave.open(file, 'w')
		ws.setnchannels(1)
		ws.setframerate(44100)
		ws.setsampwidth(2)
		ws.writeframes(raw)
		ws.close()	

	cache = []
	flags = Expando()
	flags.capturing = False
	flags.clip_count = 0
	flags.cache = cache
	flags.ready = False
	flags.winding = False

	def process_raw(count, raw):
		data = np.fromstring(raw, bit_depth)
		data_length = len(data)
		cache = flags.cache
		cache.append([False, raw])
		# begin - processing
		if not flags.ready and len(cache) == CACHE_SIZE:
			flags.ready = True
		elif flags.ready and not flags.capturing:
			# begin - when not capturing

			if len(cache) > CACHE_SIZE:
				while len(cache) > CACHE_SIZE : cache.pop(0)
			# analyze
			data = np.fromstring(raw, bit_depth)

			index = find_first_index(lambda x: math.fabs(x) > THRESHOLD, data)

			if index > -1:

				cache[-1][0] = True
				cache[-2][0] = True

				flags.capturing = True

			# end - when not capturing
		elif flags.ready and flags.capturing and not flags.winding:
			# begin - when capturing, not winding
			data = np.fromstring(raw, bit_depth)

			index = find_first_index(lambda x: math.fabs(x) < THRESHOLD, data)

			if index > -1:
				cache[-1][0] = True
				flags.winding = True
			# end - when capturing, not winding
		elif flags.ready and flags.capturing and flags.winding: 

			# when ready, capturing, and winding!
			
			# begin - else block
			cache[-1][0] = True

			flags.capturing = False
			flags.winding = False
			fname = player.fname
			flags.clip_count = flags.clip_count + 1
			wave_file = 'processed/audio_%s_%s_%s.wav' % (fname, pad(count), pad(flags.clip_count))
			write_wav(wave_file, cache)
			# end - else block
		# end - processing
		

	player = AsyncPlayer(
		file=file,
		bit_depth=bit_depth,
		sample_length=SAMPLE_LENGTH, # observed duration of snap is about 350 ms
		callback=process_raw
	)
	player.play()
	time.sleep(3)
	player.wait()


if __name__ == '__main__':
	file, bit_depth = sys.argv[1:]

	main(file, bit_depth)