# this program expects a file plots.json
import json
import numpy as np
import math
from pprint import pprint as pp
import csv

f = open('plots.json')

data = json.load(f)

x = np.array(data['x'])
y = np.array(data['y'])

assert len(x) == len(y)

prev = None
state = 0
farr = []
s = 0
  #  1 - high jump
  #  0 - normal
  # -1 - low jump

data_file = open('plot_data.csv', 'w')
data_writer  = csv.writer(data_file, lineterminator='\n')
data_writer.writerow(['Freq', 'Amplitude'])

for freq, amp in zip(x, y):
  if prev is None:
    prev = amp
    continue
  data_writer.writerow([freq, amp])  
  change = (amp - prev)/prev * 100.0
  abs_change = math.fabs(change)

  # begin - comparing absolute change
  if abs_change > 30:
    if s == 0 and change >= 0:
      s = 1 # positive jump
    elif s == 0 and change < 0:
      s = -1 # negative jump
    elif s == 1 and change < 0:
      s = 0 # back to normal
    elif s == -1 and change >= 0:
      s = 0 # back to normal
    else:
      # skip this reading
      prev = amp
      continue 
    farr.append(
      (freq, 
        amp, 
        abs_change, 
        'jump' if s == 1 else 'drop' if s == -1 else 'normal', 
        prev)
    )    
  # end - comparing absolute change
  prev = amp

output = open('spikes.csv', 'w')
writer = csv.writer(output, lineterminator='\n')
writer.writerow(['Frequency', "Amplitude", "% Change", "Change Type", "Previous Amplitude"])
[ writer.writerow(item) for item in farr]


