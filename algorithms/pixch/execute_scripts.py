import sys, traceback, os, time, shutil
from libraries.cv_globals import top_shapes_dir
from libraries import btwn_amng_files_functions

directory = sys.argv[1]
if directory[-1] != "/":
   directory += "/"

exec_scriptnames = [   "findim_pixch.py", "find_pixch_shapes.py", "unm_G50_shapes.py", "confirm_unm_G50.py", "pixch_shapes2.py", "unm_pixch_shapes2.py", "match_unm_pixels3.py"
                      ]

# script names that need to be run for every each files.
eachf_scripts = { "find_pixch_shapes.py", "unm_G50_shapes.py", "confirm_unm_G50.py", "pixch_shapes2.py", "unm_pixch_shapes2.py", "match_unm_pixels3.py" }

pixch_dir = top_shapes_dir + directory + "pixch/"

pixch_shapes1_path = pixch_dir + "pixch_shapes1/data/" + "{}.{}G50.data"
unm_G50_shapes_path = pixch_dir + "unm_matched/data/" + "{}.{}" + "_1.data"
unm_G50_shapes_conf_path = pixch_dir + "unm_matched/data/" + "{}.{}" + "_1.confirmed"
pixch_shapes2_path = pixch_dir + "pixch_shapes2/data/" + "{}.{}.data"
unm_pixch_shapes_path = pixch_dir + "pixch_shapes2/data/" + "{}.{}unm_matched.data"
unm_pixels3_path = pixch_dir + "pixch_shapes3/data/" + "{}.{}unm_matched.data"


scripts_paths = {  "findim_pixch.py": "./always_execute/",  "find_pixch_shapes.py": pixch_shapes1_path,  "unm_G50_shapes.py": unm_G50_shapes_path,  "confirm_unm_G50.py": unm_G50_shapes_conf_path,
                    "pixch_shapes2.py": pixch_shapes2_path, "unm_pixch_shapes2.py": unm_pixch_shapes_path,  "match_unm_pixels3.py":  unm_pixels3_path      }
                            

lowest_fnum, highest_fnum =  btwn_amng_files_functions.get_low_highest_filenums(directory)
all_eachf = btwn_amng_files_functions.get_btwn_files_nums( lowest_fnum, highest_fnum )


def run_for_eachf( script_fpath, script_name ):

	for eachf in all_eachf:
		im1fnum = eachf.split('.')[0]
		im2fnum = eachf.split('.')[1]
		
		cur_script_path = scripts_paths[script_name].format( im1fnum, im2fnum )
		if os.path.exists(cur_script_path):
			print("skipping " + cur_script_path)
			continue		
		
		sys.argv = [ script_fpath, directory, eachf ]
		ns = {"__name__": "__main__", "__file__": script_fpath, "__builtins__": __builtins__}

		print("each files " + eachf )
		with open(script_fpath) as exec_script:
			exec(exec_script.read(), ns) 
              


for exec_scriptname in exec_scriptnames:
	cur_dirname = "algorithms/pixch/"
	cur_execute_script = cur_dirname + exec_scriptname
   
	try:
		start_time = time.time()
		
		print("executing " + cur_execute_script )
		if exec_scriptname in eachf_scripts:
			# running script for each files.
			run_for_eachf( cur_execute_script,  exec_scriptname )
		else:
			# check if this script is already executed
			if os.path.exists( scripts_paths[exec_scriptname] ):
				print("skipping " + cur_execute_script)
				continue

			with open(cur_execute_script) as exec_script:
				exec(exec_script.read())   
      
		end_time = time.time()
		elapsed_time = end_time - start_time
		elapsed_mins = int( elapsed_time / 60 )
		elapsed_secs = int( elapsed_time % 60 )
		print("it took " + str(elapsed_mins) + " minutes " + str(elapsed_secs) + " seconds")
      
	except Exception as e:
		print("error occurred in " + cur_execute_script )
		print( traceback.format_exc() )
		
		# delete directory
		shutil.rmtree(scripts_dirs[exec_scriptname])
         
		sys.exit(1)
         

































