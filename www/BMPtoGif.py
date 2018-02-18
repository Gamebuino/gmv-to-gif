import math, subprocess, os, sys
from PIL import Image

ROOT = sys.argv[1]

fps = 25

width = 80.0
height = 64.0

scale = math.ceil(1080.0 / height)
scale = 3
output_width = width*scale
output_height = height*scale

img_in = Image.open(ROOT+'/in.bmp').convert('RGB')
frames = img_in.size[1] / height
print('Frames: ', frames)

data = list(img_in.getdata())

try:
	os.mkdir(ROOT+'/tmp')
except:
	pass

for i in range(int(frames)):
	img = Image.new('RGB', (int(width), int(height)))
	start = int(width*height*i)
	stop = int(width*height*(i + 1))
	img.putdata(data[start:stop])
	img.resize((int(output_width), int(output_height))).save(ROOT+'/tmp/'+str(i).zfill(4)+'.png')

try:
	os.unlink(ROOT+'/out.gif')
except:
	pass

subprocess.call(['ffmpeg', '-r', str(fps), '-i', ROOT+'/tmp/%04d.png', '-vf', 'palettegen', '-y', ROOT+'/tmp/palette.png'])
subprocess.call(['ffmpeg', '-r', str(fps), '-i', ROOT+'/tmp/%04d.png', '-i', ROOT+'/tmp/palette.png', '-lavfi', 'paletteuse', '-y',  ROOT+'/out.gif'])

for i in range(int(frames)):
	os.unlink(ROOT+'/tmp/'+str(i).zfill(4)+'.png')
sys.exit(0)
