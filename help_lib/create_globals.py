from libraries import pixel_functions, btwn_amng_files_functions, pixel_shapes_functions

from PIL import Image
import shutil
import os, sys, json, pickle, logging
from libraries.cv_globals import top_shapes_dir

directory = "videos/street6/resized/min1"
if len( sys.argv ) >= 2:
	directory = sys.argv[1]

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
	directory +='/'

if "min" in directory:
	min_colors = True
else:
	min_colors = False


shapes_dir = top_shapes_dir + directory + "shapes/"
low_high_filenums = btwn_amng_files_functions.get_low_highest_filenums( directory )


# create image rgb xy data
im_rgb_xy_data_dir = shapes_dir + "im_rgb_xy_data/"
if os.path.exists(im_rgb_xy_data_dir):
	shutil.rmtree(im_rgb_xy_data_dir)
os.makedirs(im_rgb_xy_data_dir)

for filenum in range( low_high_filenums[0], low_high_filenums[1] + 1 ):
	
	original_image = Image.open("images/" + directory + str(filenum) + ".png")
	im_rgb_data = original_image.getdata()
	
	# now image rgb data are stored in pixel indexes. convert them to data like this
	# { (x,y): (24,255,0), ... }
	
	im_rgb_xy_data = {}
	for pindex, rgb in enumerate(im_rgb_data):
		xy = pixel_functions.convert_pindex_to_xy( pindex, original_image.size[0] )
		
		im_rgb_xy_data[xy] = rgb
	
	save_fpath = im_rgb_xy_data_dir + str(filenum) + ".data"
	with open(save_fpath, 'wb') as fp:
		pickle.dump(im_rgb_xy_data, fp)
	fp.close()
	


shapes_colors_dir = shapes_dir + "shapes_colors/"
if os.path.exists(shapes_colors_dir):
	shutil.rmtree(shapes_colors_dir)
os.makedirs(shapes_colors_dir)



all_largest_shp_sizes = []
for filenum in range( low_high_filenums[0], low_high_filenums[1] + 1 ):
	
	xy_shapes_dfile = shapes_dir + str(filenum) + "xy_shapes.data"
	with open (xy_shapes_dfile, 'rb') as fp:
		# { 79999: [79999, ... ], ... }
		# { shapeid: [ pixel indexes ], ... }
		cur_im_xy_shapes = pickle.load(fp)
	fp.close()

	largest_shape_size = max( [ len(temp_shape) for temp_shape in cur_im_xy_shapes.values() ] )	   
	all_largest_shp_sizes.append(largest_shape_size)
	
	# create xy shapes colors
	# { shapeid: (r,g,b), ... }
	shapes_colors = pixel_shapes_functions.get_all_shapes_colors( str(filenum), directory, min_colors=min_colors, xy_shape=True )
	
	save_fpath = shapes_colors_dir + str(filenum) + "xy.data"
	with open(save_fpath, 'wb') as fp:
		pickle.dump(shapes_colors, fp)
	fp.close()



json_data = {
	"all_largest_shp_sizes": all_largest_shp_sizes
}

global_filename = shapes_dir + "global_data.json"
with open(global_filename, 'w') as json_file:
	json.dump(json_data, json_file, indent=4)


















