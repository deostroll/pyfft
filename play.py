import sys
import pyaudio
import wave
from pprint import pprint
import time

def callback(data, framecount, time_info, status_flags):
	print 'in callback'
	return (data, pyaudio.paContinue)

def main(file):
	f = wave.open(file, 'rb')
	p = pyaudio.PyAudio()
	FORMAT = p.get_format_from_width(f.getsampwidth())
	CHANNELS = f.getnchannels()
	RATE = f.getframerate()
	
	stream = p.open(
		format = FORMAT, 
		channels = CHANNELS, 
		rate = RATE, 
		output = True,
		# stream_callback = callback
	)

	# CHUNK = 1024

	# while True:
	# 	data = f.readframes(CHUNK)
	# 	# print 'len:', len(data)
	# 	if data:
	# 		stream.write(data)
	# 	else:
	# 		break

	raw = f.readframes(-1)
	stream.write(raw)
	

	# p.terminate()
	# time.sleep(30)
	stream.stop_stream()
	stream.close()
	print 'done'

if __name__ == '__main__':
	file = sys.argv[1]
	main(file)
