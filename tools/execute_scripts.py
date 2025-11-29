import  os, sys
from libraries.cv_globals import proj_dir, top_images_dir, top_shapes_dir
import winsound


print("run execute_scripts.py")

execute_script = sys.argv[0]
directory = sys.argv[1]

if "putpix_into_clrgrp.py" in execute_script:
   clrgrp_type = sys.argv[2]


if directory != "" and directory[-1] != '/':
   directory +='/'



execute_filepath = None

skip_files_by_num = []

def create_skip_files( filepath, skip_filename=None ):
   global skip_files_by_num
   
   
   if not os.path.exists(filepath ):
      return

   # getting already executed files
   for file in os.listdir(filepath):
      if skip_filename is None:
         break
      # file is a filename in the directory. not the filepath.
      if os.path.isdir(file) or skip_filename not in file:
         continue
   
      temp_num = [x for x in list(file) if x.isdigit()] 

      num = ""
      for i in range( 0, len( temp_num ) ):
         num += temp_num[i]
      
      skip_files_by_num.append( num )




if  "putpix_into_clrgrp.py" in execute_script:

   execute_filenames = "png"
   
   create_skip_files( top_images_dir + directory + clrgrp_type , ".png" )
   
   execute_filepath = top_images_dir + directory

      

if  "find_shapes.py" in execute_script or \
    "crud_shape" in execute_script:

   execute_filenames = "png"
   
   if "find_shapes.py" in execute_script:
      create_skip_files( top_shapes_dir + directory + "shapes", "shapes.data" )
   elif "crud_shape_neighbors.py" in execute_script:
      create_skip_files( top_shapes_dir + directory + "shapes/shape_nbrs/", "_shape_nbrs.data" )
   elif "crud_shape_boundaries.py" in execute_script:
      create_skip_files( top_shapes_dir + directory + "shapes/boundary/", ".data" )
   
   execute_filepath = top_images_dir + directory


elif "create_globals.py" in execute_script or "evaluate_images.py" in execute_script:
	sys.argv = [ execute_script , directory ]
	exec(open(proj_dir + execute_script).read())


skipped_files = []
for file in os.listdir(execute_filepath):
   
   if execute_filenames not in file:
      continue   

   if "putpix_into_clrgrp.py" not in execute_script:
      sys.argv = [ file , directory ]
   else:
      sys.argv = [ file , directory, clrgrp_type ]
   
   print("file " + file )
   
   temp_num = [x for x in list(file) if x.isdigit()] 

   num = ""
   for i in range( 0, len( temp_num ) ):
      num += temp_num[i]
   
   if num in skip_files_by_num:
      skipped_files.append( file )
      continue
   
   
   exec(open(proj_dir + execute_script).read())
   print()

print("skipped_files")
print( skipped_files )
print()


















