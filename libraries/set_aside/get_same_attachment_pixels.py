# this algorithm returns same attachment pixels from pixels2. see documentation Documentations/libraries/same_shapes_functions/get_same_attachments_by_nbrs.docx

# movement is to move attached_pixels1 to attached pixels in pixels2.
# all pixels are xy pixels
def get_same_attachment_pixels( attached_pixels1, movement, pixels2boundary, im_size ):
    
    same_attached_pixels = []
    
    pixels2boundary_in_order = pixel_functions.put_pixels_in_order(pixels2boundary)
    
    print("attached_pixels1")
    print(attached_pixels1)
    attached_pixels1_at_2 = pixel_functions.move_pixels( attached_pixels1, movement[0], movement[1], input_xy=True, im_size=im_size )
    
    print("attached_pixels1_at_2")
    print(attached_pixels1_at_2)
    
    image_functions.cr_im_from_pixels( "26", "videos/street3/resized/min1/", attached_pixels1_at_2, pixels_rgb=(255,255,0) )
    image_functions.cr_im_from_pixels( "26", "videos/street3/resized/min1/", pixels2boundary_in_order, pixels_rgb=(255,255,0) )
    
    def get_same_attached_pixels( pixels2boundary_in_order, attached_pixels1_at_2, check_distance=None ):
    
        # [((44, 84), (44, 84)), ((18, 83), (18, 83)), ... ]
        # [ ( closest attached_pixels1_at_2 pixel, closest pixels2boundary pixel ), ... ]
        distance, closest_bnd_pixels_at_2 = get_closest_pixels( attached_pixels1_at_2, pixels2boundary_in_order, im_size=im_size, return_both=True )
        if check_distance is not None and distance > check_distance:
            # no close boundaries exist from attached_pixels1_at_2
            return
        
        pre_cur_attached_pixels2 = { temp_pixels[1] for temp_pixels in closest_bnd_pixels_at_2 } 
        
        # get rest of the current attached pixels from pixels2boundary
        # [(8, 1), (2, 2), (3, 2), (4, 2), (3, 5), (4, 5) ... ]
        pre_cur_attached_pixels2 = pixel_functions.put_pixels_in_order( pre_cur_attached_pixels2 )
        
        # get in between pixels from pixels2boundary
        first_index = pixels2boundary_in_order.index( pre_cur_attached_pixels2[0] )
        last_index = pixels2boundary_in_order.index( pre_cur_attached_pixels2[-1] )
        
        cur_attached_pixels2 = []
        for cur_index in range(first_index, last_index + 1 ):
            cur_attached_pixels2.append( pixels2boundary_in_order[cur_index] )
        
        remaining_len = len(attached_pixels1_at_2) - len(cur_attached_pixels2)
        remaining_len_at_one_end = math.ceil( remaining_len / 2 )
        # get remaining pixels from both ends of the cur_attached_pixels2

        for cur_value in range(1, remaining_len_at_one_end + 1):
            ordered_boundary_index = first_index - cur_value
            if ordered_boundary_index < 0:
                break
            cur_attached_pixels2.insert(0, pixels2boundary_in_order[ordered_boundary_index] )
            remaining_len -= 1
        
        for cur_value in range(1, remaining_len + 1):
            ordered_boundary_index = last_index + cur_value
            if ordered_boundary_index >= len(pixels2boundary_in_order):
                break
            cur_attached_pixels2.insert( len(cur_attached_pixels2) - 1, pixels2boundary_in_order[ordered_boundary_index] )
        
        return cur_attached_pixels2   


    
    cur_attached_pixels2 = get_same_attached_pixels( pixels2boundary_in_order, attached_pixels1_at_2 )
    same_attached_pixels.append(cur_attached_pixels2)
    
    # take one more closest attached pixels if there is one
    # remove already taken attached pixels from pixels2boundary_in_order.
    # additionally, remove 3pixels from both ends of the cur_attached_pixels2 from pixels2boundary_in_order
    first_index = pixels2boundary_in_order.index( cur_attached_pixels2[0] ) - 3
    
    pixels2boundary_in_order = set(pixels2boundary_in_order).difference( set(cur_attached_pixels2) )
    pixels2boundary_in_order = pixel_functions.put_pixels_in_order( pixels2boundary_in_order )
    
    # remove 3pixels from both ends of the cur_attached_pixels2 from pixels2boundary_in_order
    # first 3 is to remove front 3. second 3 is to remove 3 pixels from end.
    for cur_value in range(3 + 3):
        if first_index < 0:
            break
        pixels2boundary_in_order.pop(first_index)
    
    get_same_attached_pixels( pixels2boundary_in_order, attached_pixels1_at_2, check_distance=3 )
    
    for attached_pixels in same_attached_pixels:
        image_functions.cr_im_from_pixels( "26", "videos/street3/resized/min1/", attached_pixels, pixels_rgb=(255,255,0) )
    
    sys.exit()
    




