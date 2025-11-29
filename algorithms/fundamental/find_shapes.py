#
# algorithm for determining the closest match with the color group uses how far away the RGB value is from original
#
#
from libraries import pixel_functions, pixel_shapes_functions, btwn_amng_files_functions

from PIL import Image
import math
import os, sys
import pickle

from collections import OrderedDict
from libraries.cv_globals import top_shapes_dir, top_images_dir


image_filename = '8'
directory = "videos/street6/resized/min1/"

if len(sys.argv) >= 2:
   image_filename = sys.argv[0][0: len( sys.argv[0] ) - 4 ]

   directory = sys.argv[1]

   print("execute script find_shapes.py. filename " + image_filename + " directory " + directory )


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

if "min" in directory:
	min_clr = True
else:
	min_clr = False


original_image = Image.open(top_images_dir + directory + image_filename + ".png")
# [ (255,0,50), ... ]
all_pixel_rgbs = original_image.getdata()
image_size = original_image.size

# shapes[ pixel_index ] = [ pixel index1, pixel index2, .... ]
shapes = {}

already_done_pixels = set()

'''
def get_shape_pixels(pixel_index, done_nbrs):
	
	shape_pixels = set()
	
	nbr_pixels = pixel_functions.get_nbr_pixels(pixel_index, image_size )
	
	nbr_pixels = set(nbr_pixels).difference( done_nbrs )
	for nbr_pixel in nbr_pixels:
		done_nbrs.add(nbr_pixel)
		
		shape_pixel = False
		if min_clr:
			if all_pixel_rgbs[pixel_index] == all_pixel_rgbs[nbr_pixel]:
				shape_pixel = True
				
		else:
			color_change = pixel_functions.compute_appearance_difference(all_pixel_rgbs[pixel_index], all_pixel_rgbs[nbr_pixel] )
			if color_change is False:
				shape_pixel = True
		
		if shape_pixel:
			shape_pixels.add(nbr_pixel)
			already_done_pixels.add(nbr_pixel)
			shape_pixels |= get_shape_pixels(nbr_pixel, done_nbrs)
			
	return shape_pixels
'''


def get_shape_pixels_iterative(start_index):
	shape_pixels = set()
	stack = [start_index]
	done_nbrs = set()
	done_nbrs.add(start_index)

	while stack:
		pixel_index = stack.pop()

		nbr_pixels = pixel_functions.get_nbr_pixels(pixel_index, image_size)
		for nbr_pixel in nbr_pixels:
			if nbr_pixel in done_nbrs:
				continue

			done_nbrs.add(nbr_pixel)

			shape_pixel = False
			if min_clr:
				if all_pixel_rgbs[pixel_index] == all_pixel_rgbs[nbr_pixel]:
					shape_pixel = True
			else:
				if pixel_functions.compute_appearance_difference(all_pixel_rgbs[pixel_index], all_pixel_rgbs[nbr_pixel]) is False:
					shape_pixel = True

			if shape_pixel:
				shape_pixels.add(nbr_pixel)
				already_done_pixels.add(nbr_pixel)
				stack.append(nbr_pixel)

	return shape_pixels



#image_size[0] is width
for pixel_index in range( image_size[0] * image_size[1] ):

	if pixel_index in already_done_pixels:
		continue
	
	done_nbrs = set()
	#shape_pixels = get_shape_pixels(pixel_index, done_nbrs)
	
	#already_done_pixels |= shape_pixels
	
	#shapes[ pixel_index ] = list(shape_pixels)

				
	already_done_pixels.add(pixel_index)
	shape_pixels = get_shape_pixels_iterative(pixel_index)
	already_done_pixels |= shape_pixels
	shapes[pixel_index] = list(shape_pixels)
	shapes[pixel_index].append(pixel_index)




xy_shapes = {}
for shapeid in shapes:
	# shapeid is pixel index
	xy_shapeid = pixel_functions.convert_pindex_to_xy( shapeid, image_size[0] )
	
	shape_pixels = pixel_functions.convert_pindexes_to_xy( shapes[shapeid], image_size )
	xy_shapes[xy_shapeid] = shape_pixels			


target_im_shapes_dir = top_shapes_dir + directory + "shapes/"
if os.path.exists(target_im_shapes_dir ) == False:
   os.makedirs(target_im_shapes_dir)


with open(target_im_shapes_dir + image_filename + "shapes.data", 'wb') as fp:
   pickle.dump(shapes, fp)
fp.close()

with open(target_im_shapes_dir + image_filename + "xy_shapes.data", 'wb') as fp:
   pickle.dump(xy_shapes, fp)
fp.close()

btwn_amng_files_functions.create_shapeids_by_pindex( image_filename, directory, image_size )


xy_shapeids_by_xy = {}

for xy_shapeid in xy_shapes:
	
	for xy in xy_shapes[xy_shapeid]:
		if not xy_shapeids_by_xy.get(xy):
			xy_shapeids_by_xy[xy] = {xy_shapeid}
		else:
			xy_shapeids_by_xy[xy].add(xy_shapeid)

shapeids_by_pixel_dir = top_shapes_dir + directory + "shapes/shapeids_by_pixel/"
xy_shapeids_by_p_fpath = shapeids_by_pixel_dir + "xy" + image_filename + ".data"
with open(xy_shapeids_by_p_fpath, 'wb') as fp:
   pickle.dump(xy_shapeids_by_xy, fp)
fp.close()








