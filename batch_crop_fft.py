import os
from PIL import Image

def main(bit_depth='Int16'):
	files = os.listdir('processed')
	s = 'fig_fft_'

	for file in files:
		filename = os.path.basename(file)
		basename, ext = os.path.splitext(filename)
		actual_file_path = os.path.join('processed', file)
		if ext == ".png" and basename.startswith(s):
			im = Image.open(actual_file_path)
			box = (80, 58, 576, 427)
			region = im.crop(box)
			cropped_file = 'processed/crop_%s.png' % basename[len(s):]
			region.save(cropped_file)
			print('Saved:', cropped_file)

if __name__ == '__main__':
	main()