import sys, os, copy, logging
from libraries.cv_globals import top_images_dir, top_tests_dir, top_shapes_dir
import pickle
from PIL import ImageTk, Image
from libraries import btwn_amng_files_functions, pixel_shapes_functions, cv_globals, image_functions, pixel_functions





# deleting shapeids.
# delete from image shapes, image boundaries and image neighbors.
def delete_shapeids( shapeids, image_shapes, im_shapes_boundaries, im_shapes_nbrs, im_xy_shapeids_by_p, im_shapes_colors ):

	for shapeid in shapeids:
		for pixel in image_shapes[shapeid]:
			im_xy_shapeids_by_p[pixel].remove(shapeid)

	# deleting from image shapes, image shapes boundaries and im shapes colors is straight forward.
	for shapeid in shapeids:
		image_shapes.pop(shapeid)
		im_shapes_boundaries.pop(shapeid)
		im_shapes_colors.pop(shapeid)

	# deleting target_shapeid from shapes neighbors is a little bit tricky. it affects target_shapeid's neighbors.
	# process goes like this
	# get neighbors from target_shapeid. delete target_shapeid from all its neighbors. then delete target_shapeid from shapes neighbors.

	for shapeid in shapeids:
		t_shape_nbrs = im_shapes_nbrs[shapeid]

		for t_shape_nbr in t_shape_nbrs:
			im_shapes_nbrs[t_shape_nbr].remove(shapeid)
		im_shapes_nbrs.pop(shapeid)



# all_shapes_pixels:  [ { (x,y), ... }, ... ]
def create_shapeids( all_shapes_pixels, image_shapes, im_shapes_boundaries, im_shapes_nbrs, im_xy_shapeids_by_p, im_shapes_colors, im_rgb_data, image_size, min_colors ):

	new_shapeids = set()  # target_shapeid can not be used. if shapeid is used by other newly added shape, that shapeid can not be assigned to any other shape.
	for shape_pixels in all_shapes_pixels:
		
		it = iter(shape_pixels)
		shapeid_to_create = next(it) # get aribtrary pixel to use as shapeid.
		while shapeid_to_create in new_shapeids: # get unique shapeid
			shapeid_to_create = next(it)

		image_shapes[shapeid_to_create] = shape_pixels
		new_shapeids.add(shapeid_to_create)
		
		im_shapes_colors[shapeid_to_create] = pixel_shapes_functions.get_shape_color( shape_pixels, im_rgb_data, min_colors )
		
		im_shapes_boundaries[shapeid_to_create] = pixel_shapes_functions.get_boundary_pixels(shape_pixels)
		im_shapes_nbrs[shapeid_to_create] = set()
		
		for shape_pixel in shape_pixels:
			if im_xy_shapeids_by_p.get(shape_pixel) is None:
				im_xy_shapeids_by_p[shape_pixel] = {shapeid_to_create}
			else:
				im_xy_shapeids_by_p[shape_pixel].add(shapeid_to_create)

	# add newly created shapes to im_shapes_nbrs
	for new_shapeid in new_shapeids:
		
		outside_nbr_pixels = set()
		for boundary_p in im_shapes_boundaries[new_shapeid]:
			outside_nbr_pixels |= pixel_functions.get_nbr_pixels( boundary_p, image_size, input_xy=True)

		outside_nbr_pixels = outside_nbr_pixels.difference( image_shapes[new_shapeid] )
		
		for shapeid in im_shapes_boundaries:
			if shapeid == new_shapeid:
				continue
			
			pixel_overlap = outside_nbr_pixels.intersection( im_shapes_boundaries[shapeid] )
			if len(pixel_overlap) >= 1:
				im_shapes_nbrs[new_shapeid].add(shapeid)
				im_shapes_nbrs[shapeid].add(new_shapeid)

	return new_shapeids








































