import sys, struct, json
from PIL import Image

color_index = [
	(  0,   0,   0, 255), # black
	(  0,  67, 133, 255), # darkblue
	(150,   0,  64, 255), # purple
	(  0, 139,  80, 255), # green
	(207, 142,  68, 255), # brown
	( 84,  77,  67, 255), # darkgray
	(168, 153, 135, 255), # gray
	(255, 255, 255, 255), # white
	(219,  29,  35, 255), # red
	(255, 168,  17, 255), # orange
	(245, 231,   0, 255), # yellow
	(133, 207,  68, 255), # lightgreen
	(125, 187, 255, 255), # lightblue
	( 68, 133, 207, 255), # blue
	(207,  68, 133, 255), # pink / magenta
	(255, 214, 144, 255), # beige
]

ROOT = sys.argv[1]

def convertColor(c):
	r = ((c >> 8) & 0xF8) & 0xFF
	r |= r >> 5
	
	g = ((c >> 3) & 0xFC) & 0xFF
	g |= g >> 6
	
	b = (c << 3) & 0xFF
	b |= b >> 5
	return (r, g, b, 255)

with open(ROOT+'/in.gmv', 'rb') as f:
	b1 = f.read(1)
	b2 = f.read(1)
	if b1 != b'G' or b2 != b'V':
		print('not a GMV file')
		sys.exit(-1)
	header_size = struct.unpack('H', f.read(2))[0]
	version = struct.unpack('B', f.read(1))[0]
	width = struct.unpack('H', f.read(2))[0]
	height = struct.unpack('H', f.read(2))[0]
	frames = struct.unpack('H', f.read(2))[0]
	flags = struct.unpack('B', f.read(1))[0]
	
	img_index = flags & 0x01
	
	print('Width:', width)
	print('Height:', height)
	print('Frames:', frames)
	print('Image mode:', 'Index' if img_index else 'RGB565')
	with open(ROOT+'/metadata.json', 'w+') as md:
		md.write(json.dumps({
			'width': width,
			'height': height,
			'frames': frames,
		}))
	
	if img_index:
		transparent_color = struct.unpack('B', f.read(1))[0]
		use_transparent_color = struct.unpack('B', f.read(1))[0] != 0
	else:
		transparent_color = struct.unpack('H', f.read(2))[0]
		use_transparent_color = transparent_color != 0
	print('Transparency:', 'yes' if use_transparent_color else 'no')
	f.seek(header_size)
	img = Image.new('RGBA' if use_transparent_color else 'RGB', (width, height*frames))
	pixels = img.load()
	
	x_cursor = 0
	y_cursor = 0
	if img_index:
		while True:
			s = f.read(1)
			if not s:
				break
			count = struct.unpack('B', s)[0]
			s = f.read(1)
			byte = struct.unpack('B', s)[0]
			c1 = byte >> 4
			c2 = byte & 0x0F
			i = 0
			while i < count:
				i += 1
				pixels[x_cursor, y_cursor] = color_index[c1]
				x_cursor += 1
				if x_cursor >= width:
					x_cursor = 0
					y_cursor += 1
				pixels[x_cursor, y_cursor] = color_index[c2]
				x_cursor += 1
				if x_cursor >= width:
					x_cursor = 0
					y_cursor += 1
	else:
		while True:
			s = f.read(1)
			if not s:
				break
			count = struct.unpack('B', s)[0]
			if count == 0x80:
				color = struct.unpack('H', f.read(2))[0]
				pixels[x_cursor, y_cursor] = convertColor(color)
				x_cursor += 1
				if x_cursor >= width:
					x_cursor = 0
					y_cursor += 1
				continue
			if not (count & 0x80):
				if count == 0x7F:
					pixels[x_cursor, y_cursor] = (0, 0, 0, 0)
				else:
					if count >= 16:
						count = 15
					pixels[x_cursor, y_cursor] = color_index[count]
				x_cursor += 1
				if x_cursor >= width:
					x_cursor = 0
					y_cursor += 1
				continue
			count &= 0x7F
			i = struct.unpack('B', f.read(1))[0]
			if i == 0x80:
				color = convertColor(struct.unpack('H', f.read(2))[0])
			elif i == 0x7F:
				color = (0, 0, 0, 0)
			else:
				if i >= 16:
					i = 15
				color = color_index[i]
			for i in range(count):
				pixels[x_cursor, y_cursor] = color
				x_cursor += 1
				if x_cursor >= width:
					x_cursor = 0
					y_cursor += 1
	img.save(ROOT+'/in.bmp')
sys.exit(0)
