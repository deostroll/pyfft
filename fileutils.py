import csv
import json
import shutil

class Expando(object):
	pass

def get_csv_writer(file, *headers):
  f = open(file, 'w')
  writer = csv.writer(f, lineterminator='\n')
  writer.writerow(headers)
  o = Expando()
  # set_attr(o, 'writer', writer)
  setattr(o, 'writer', writer)
  o.fd = f
  return o

def dump_json(file, data):
  json.dump(data , open(file, 'w'))


def copy(src, dst):
	shutil.copy(src,dst)  

def get_csv_reader(file):
	f = open(file)
	reader = csv.reader(f, lineterminator='\n')

	o = Expando()
	o.reader = reader
	o.fd = f
	return o

def get_from_csv(file):
	o = get_csv_reader(file)
	r = o.reader
	next(r)
	x = []
	y = []

	for a,b in r:
		x.append(float(a))
		y.append(float(b))

	return (x, y)	