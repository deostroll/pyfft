from threading import Thread
import time

def main():
	active = True
	def foo():
		print 'begin thread'
		while active:
			print 'doing something...'
			time.sleep(1)
		print 'end thread'


	t = Thread(target=foo, name='foo')
	t.start()
	time.sleep(10)	
	active = False
main()
