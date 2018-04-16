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
		params = f.getparams()
		cb = self.callback

		while True:			
			cb(*q.get(), params, fname)
			q.task_done()

	def wait(self):

		self._event.wait()
		self._q.join()

	
def main(file, bit_depth):

	def write_wav(file, raw_data):
		ws = wave.open(file, 'w')
		ws.setnchannels(1)
		ws.setframerate(44100)
		ws.setsampwidth(2)
		ws.writeframes(raw_data)
		ws.close()	

	def process_raw(count, raw, params, fname):
		data = np.fromstring(raw, bit_depth)
		data_length = len(data)

		max_freq_range = data_length if data_length > params.framerate else params.framerate

		x = np.linspace(0, params.framerate, data_length)
		y = np.abs(fft(data))

		csvobj = fs.get_csv_writer('processed/data_fft_%s_%s.csv' % (fname, pad(count)), 'f', 'a')
		writer = csvobj.writer
		half = int(data_length/2)
		[ 
			writer.writerow([f, a]) 
				for f,a in 
					zip(
						x[: half], 
						y[: half]
					)
		]

		csvobj.fd.close()

		wav_file = 'processed/audio_%s_%s.wav' % (fname, pad(count))
		write_wav(wav_file, raw)

	player = AsyncPlayer(
		file=file,
		bit_depth=bit_depth,
		sample_length=0.5,
		callback=process_raw
	)

	player.play()
	time.sleep(3)
	player.wait()


if __name__ == '__main__':
	file, bit_depth = sys.argv[1:]

	main(file, bit_depth)