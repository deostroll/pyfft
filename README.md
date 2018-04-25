This is a small set of python scripts which will analyze an audio file and detect some specific sound...(like a snap, clap, etc)

## Software Requirements

Python 3+ should be installed

Pythonic packages

- matplotlib
- numpy
- scipy
- pyaudio

> Note: These packages should be installed for python 3

## General workflow

1. Record a sample
2. Do some preliminary analysis on sample audio
3. Record test audio which contains 'sample' sounds
4. Split test into small audio clips (which "may" contain the sound we want to detect)
5. Analyze above audio clips; identify if it contains the sound we are expecting

>Note: These scripts don't have anything specific for recording. You may try audacity if you want to quickly get started. However, most operating systems would probably already have a sound recorder installed. You can use that too.

## Theory

When analyzing the sample we make note of the following:

1. Peak or dominant frequencies in the frequency spectogram (using FFT and some interpolation)
2. We study the sample's wave form graph to find a spike in the audio output. (This is later used for splitting the test audio into smaller clips)
3. We analyze the spectrograms of the test audio clips and compare it with our sample's spectrogram. This helps in identifying if the test clip has the desired sound.

### Strategy for identification

1. Peak Extraction:

The spectrogram is a XY scatter plot. For filtering peak amplitudes, we find the pairs (`x` and `y` values) whose `y`-value is greater than 50% of its maximum.

2. Normalization:

In the dataset obtained above, we normalize both `x` and `y` values, relatively. Hence all `x` values are subtracted with its minimum. Similar process is done for `y` values. 

Now we have a simpler discrete dataset where the values start from `x=0`. The "width" of this dataset (`x` range) is the maximum `x` value.

3. Comparision:

We simply do a ratio comparision of the widths, with the constraint that the larger is always the numerator, and the other quantity is the denominator.

This ratio should approx be in the interval `[1, 2)`

> Note: We are only comparing "widths". This approximately let us detect desired sound. A more rigorous approximation might require comparing the y-values via some approach. 

## Important Scripts

For **step 2** in the workflow above use the following scripts:

### 1. plotwav.py

Plots the wave form graph of a wav file.

Usage:

```
./plotwav.py <wav_file> Int16
```

### 2. fftplotwav.py

Plots the frequency spectrogram

Usage:

```
./fftplot.py <wav_file> Int16
```

### 3. fftanalyze.py

Creates the frequency spectrogram discrete dataset as a CSV file. It gets stored in the `samples` folder

Usage:

```
./fftanalyze.py <wav_file> Int16
```

---

For **step 4** in the workflow use the following scripts:

### 4. split_wav2.py

This script is usually run against a test audio file. 

It splits the file into short audio clips which may contain our desired sound. They are stored in the `processed` folder

Usage:

```
./split_wav2.py <wav_file> Int16
```

**Important:** For each experiment you may want to edit this file to match the parameters you noted down in step 2. Manually change the values for the following variables: `THRESHOLD` and `SAMPLE_LENGTH`

---

For **step 5** use the following scripts:

### 5. batch_generate_wav_fft.py

This will process wav files in the `processed` folder and generate fft datasets (in csv format). Output gets stored in the same folder.

Usage:

```
./batch_generate_wav_fft.py
```

### 6. batch_analyze.py

Compare the fft datasets in the `processed` folder against a sample-fft dataset, and report the width ratio.

Usage:

```
./batch_analyze.py <sample_fft_csv_dataset_file>
```

---

The other scripts are here for any further diagnosis you may require. The ones that start with `batch_` will mainly work with files in the `processed` folder.

## Conventions

Not mandatory to follow, but helps if you want to rigorously experiment.

1. All sample audio files affix the word `sample` in the filename
E.g

```
data/clap_sample_472ms_16bit_mono.wav
```
2. All test audio files affix the word `test` in the filename
3. All audio files must be wav format with 16 bit data, mono channel. It is also good to incorporate the length of the audio clip, and, bit-depth for easily being able to distinguish.