import numpy as np
import wave
import os
from pprint import pprint

files = map(lambda x: os.path.join('data', x), os.listdir('data'))

pprint(files)
