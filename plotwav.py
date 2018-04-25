#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
import struct

file = sys.argv[1]
bit_depth = sys.argv[2]

f = wave.open(file,'rb')
signal = f.readframes(-1)
data = np.fromstring(signal, bit_depth)

rate = f.getframerate()
channels = f.getnchannels()

show = True
if channels == 1:
    x = np.linspace(0, len(data)/rate, num=len(data))    
    plt.plot(x, data)    
elif channels == 2:
    x = np.linspace(
        0, 
        len(data)/channels/rate, 
        num=len(data)/channels
    )
    # left channel
    ldata = data[::2]
    
    # right channel
    rdata = data[1::2]
    
    plt.plot(x, ldata)
    plt.plot(x, rdata)
    
else:
    show = False

if show : 
    plt.title('Wave form: %s' % file)
    plt.show()