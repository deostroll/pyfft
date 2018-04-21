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

	
def main(file, bit_depth):

	THRESHOLD = 5625 # This is the lowest value observed for a snap

	def write_wav(file, raw_data):
		ws = wave.open(file, 'w')
		ws.setnchannels(1)
		ws.setframerate(44100)
		ws.setsampwidth(2)
		ws.writeframes(raw_data)
		ws.close()	

	cache = []
	flags = Expando()
	flags.capturing = False
	flags.clip_count = 0
	flags.cache = cache

	def process_raw(count, raw):
		data = np.fromstring(raw, bit_depth)
		data_length = len(data)
		cache = flags.cache
		cache.append(raw)

		if not flags.capturing:

			if len(cache) > 2:
				cache.pop(0) 	# remove the item from the left of queue and 
								# maintain queue size = 2

			if any(map(lambda x: math.fabs(x) > THRESHOLD, data)):
				flags.capturing = True
		else:
			# write clip using the last two frames
			# new_raw = ''.join(cache[1:])
			new_raw = reduce(lambda acc, item: acc + item, cache[1:], b'')
			# clip_count = clip_count + 1
			flags.clip_count = flags.clip_count + 1
			fname = player.fname
			wav_file = 'processed/audio_%s_%s_%s.wav' % (fname, pad(count), pad(flags.clip_count))
			write_wav(wav_file, new_raw)
			flags.capturing = False
			cache = []

	player = AsyncPlayer(
		file=file,
		bit_depth=bit_depth,
		sample_length=0.240, # observed duration of snap is about 350 ms
		callback=process_raw
	)
	player.play()
	time.sleep(3)
	player.wait()


if __name__ == '__main__':
	file, bit_depth = sys.argv[1:]

	main(file, bit_depth)