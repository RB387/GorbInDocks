from werkzeug_utils_rus import secure_filename
from zipfile import ZipFile
import os
import shutil
import gorbin_tools2


class file_tools():
	'''Class with functions for work with files

		arguments:
		settings -- data from json config
		gt -- gorbin_tools class object

	'''
	def __init__(self, settings, gt):
		from config import UPLOAD_FOLDER, ZIP_FOLDER
		self.gt = gt
		self.UPLOAD_FOLDER = UPLOAD_FOLDER
		self.ZIP_FOLDER = ZIP_FOLDER
		self.settings = settings

	def sort_files(self, files):
		'''Sort files

			arguments:
			files -- files to sort

		returns sorted files
		'''
		if files:
			# sort by name
			files.sort(key = lambda x: x['name'].lower())
			# move folders to upper
			files.sort(key = lambda x: x['type'], reverse = True)
		return files

	def get_file_paths(self, dirName):
	  '''Get paths of all files in directory

	  	arguments:
		dirName -- directory path

		returns list of paths of all files inside
	  '''
	  # initialize file paths variable
	  filePaths = []
	   
	  # Read all directory, subdirectories and file lists
	  for root, _, files in os.walk(dirName):
	    for filename in files:
	        # Create the full filepath by using os module.
	        filePath = os.path.join(root, filename)
	        filePaths.append(filePath)
	         
	  # return all paths
	  return filePaths

	def get_dir_tree(self, login, dirId):
		'''Get list of user's file directory tree

			arguments:
			login -- user unique login
			dirId -- id of current directory

			returns list of directories of None (if got error)
		'''
		dir_names, directory = [], {'dir': dirId}
		#Walk up to home directory
		while directory['dir'] != '/':
			directory = self.gt.get_file(directory['dir'])
			#if directory exists
			if directory:
				#check permission
				if directory['owner'] != login:
					return dir_names[::-1]
				dir_names.append((directory['_id'], directory['name']))
			else:
				#else return error
				return None
		#return list of directories (id, name)		
		return dir_names[::-1]

	def file_upload(self, file, login, directory):
		'''Method to upload new file

			arguments:
				file -- object with file
				login -- current user's login
				directory -- where to save file
		
			ERROR CODES:
				1: File was uploaded succesfully
				0: No selected file
				-1: Such file already exists
				-2: File size exceeds limit
			
			returns tuple like (error code, file name)
		'''


		if file.filename == '':
			return (0, None)
		elif file:
			# get file size
			file_bytes = file.read()
			# get file name
			filename = secure_filename(file.filename)
			# "reset" fd to the beginning of the file
			file.seek(0)
			if len(file_bytes) > self.settings['max_file_size']:
				return (-2, filename)
			
			# get path where file will be saved
			if directory != '/':
				file_path = self.gt.get_file(directory)['location']
			else:
				file_path = os.path.join(self.UPLOAD_FOLDER, login)
				
			if not os.path.exists(file_path):
				# check temp path
				os.makedirs(file_path)
			# gen file path	
			file_path = os.path.join(file_path, filename)
			
			#if file with same name already exists
			if os.path.exists(file_path):
				#return error
				return (-1, filename)

			file.save(file_path)
			
			file.close()
			#add information about file in to database
			self.gt.add_file(owner=login, name=filename, 
							size=len(file_bytes)/1024/1024, 
							location = file_path, directory = str(directory))
			return (1, filename)

	def download_file(self, file_data, login, directory):
		'''Method to let user download his file.

			arguments:
			file_data -- info about file
			login -- current user login
			directory -- dir where file is stored

			ERROR CODES:
				1: File is ready to download
				0: Such file doesnt exist
				-1: Permission denied

			return tuple like (error code, path to file or None)
		'''
		if file_data:
			if login != file_data['owner']:
				# if user doesnt have access for this file
				return (-1, None)

			#if file disappeared
			if not os.path.exists(file_data['location']):
				# delete file and return error
				self.gt.del_file(file_id = file_data['_id'])
				return (0, None)
			# else
			if file_data['type'] == 'folder':
				# zip folder
				if not os.path.exists(self.ZIP_FOLDER):
					# check temp path
					os.makedirs(self.ZIP_FOLDER)

				# generate temp zip file name
				temp_path = os.path.join(self.ZIP_FOLDER, gorbin_tools2.str_now().replace(' ', '_').replace(':', '-')) + '_' + login + '.zip'

				with ZipFile(temp_path,'w') as zip: 
					# get basename for file
					basename = os.path.dirname(file_data['location'])

					# get info about files location on hard drive
					files_location = self.get_file_paths(os.path.join(basename, file_data['name']))
					
					# writing each file one by one 
					for file_loc in files_location:
						zip.write(file_loc, os.path.relpath(file_loc, basename))

				
				# send zip file
				return (1, temp_path)

			else:
				# download file
				return (1, file_data['location'])

	def get_download_list(self, values, login, directory):
		'''Method to download list of files in zip

			arguments:
				values -- file ids (from HTML, so first 2 values is trash)
				login -- current user login
				directory -- where file is stored

			ERROR CODES:
				1: zip is ready for download
				0: such doesnt exist
				-1: permission denied
				-2: no file
				-3: no file selected

			returns tuple like (error_code, path to zip or None)
		'''
		if len(values) <= 1:
			return (-3, None)
		# get only file ids
		values = values[2::]
		# initialize list with files locations
		files_location = []

		for file_id in values:
			# read file info one by one
			file_data = self.gt.get_file(file_id = file_id)

			if file_data:
				if login != file_data['owner']:
					# if user doesnt have access for this file
					return (-1, None)
				# if file disappeared
				if not os.path.exists(file_data['location']):
					# delete file and return error
					self.gt.del_file(file_id = file_data['_id'])
					return (0, None)
				# else
				if file_data['type']=='folder':
					# if folder then get info about all files in it
					files_location += self.get_file_paths(file_data['location'])
				else:
					# else just append
					files_location.append(file_data['location'])

			else:
				return (-2, None)
		

		if not os.path.exists(self.ZIP_FOLDER):
			# check temp path
			os.makedirs(self.ZIP_FOLDER)

		# generate temp zip file name
		temp_path = os.path.join(self.ZIP_FOLDER, gorbin_tools2.str_now().replace(' ', '_').replace(':', '-')) + '_' + login + '.zip'
		
		with ZipFile(temp_path,'w') as zip: 
			# get basename for file
			if directory == '/':
				basename = os.path.join(self.UPLOAD_FOLDER, login)
			else:
				basename = os.path.dirname(self.gt.get_file(values[0])['location'])

			# writing each file one by one 
			for file_loc in files_location:
				zip.write(file_loc, os.path.relpath(file_loc, basename))

		#send zip file
		return (1, temp_path)

	def delete_file(self, file_data, login, directory):
		'''Method to delete file

			arguments:
				file_data -- info about file
				login -- current user login
				directory -- where file is stored

			ERROR CODES:
				1: File was deleted succesfully
				0: File was not found
				-1: Permission denied

			returns error code
		'''
		if file_data:
			if login == file_data['owner']:
				#if such file exists
				if os.path.exists(file_data['location']):
					#delete file from database
					self.gt.del_file(file_id = file_data['_id'])
					#delete file from system
					'''
					if file_data['type'] == 'folder':
						shutil.rmtree(file_data['location'])
					else:
						os.remove(file_data['location'])
					'''
					return 1
				else:
					#delete from database
					self.gt.del_file(file_id = file_data['_id'])
					return 0
			else:
				return -1

	def delete_file_list(self, values, login, directory):
		'''Method to delete list of files

			arguments:
				values -- file ids (from HTML, so first 2 values is trash)
				login -- current user login
				directory -- where file is stored

			ERROR CODES:
				1: Files were deleted succesfully
				0: File not found
				-1: Permission denied
				-2: No File data
				-3: No File selected

			returns error code
		'''
		if len(values) <= 1:
			return -3

		#get only file ids
		values = values[2::]
		for file_id in values:
			#read file info one by one
			file_data = self.gt.get_file(file_id = file_id)
			if file_data:
				if login == file_data['owner']:
					#if such file exists
					if os.path.exists(file_data['location']):
						#delete file from database
						self.gt.del_file(file_id = file_id)
						#delete file from system
						'''
						if file_data['type'] == 'folder':
							shutil.rmtree(file_data['location'])
						else:
							os.remove(file_data['location'])
						'''
					else:
						#delete from database
						self.gt.del_file(file_id = file_id)
						return 0
				else:
					#if user doesnt have access for this file
					return -1
			else:
				return -2

		return 1

	def create_folder(self, folder_name, login, directory):
		'''Method to create folder

			arguments:
				folder_name -- name of new folder
				login -- current user login
				directory -- where to create folder

			ERROR CODES:
				1: Folder was created succesfully
				0: Such folder already exists

			returns error code
		'''
		if directory != '/':
			path = os.path.join(self.gt.get_file(directory)['location'], folder_name)
		else:
			path = os.path.join(self.UPLOAD_FOLDER, login, folder_name)

		if not os.path.exists(path):
			#create folder on hard drive
			os.makedirs(path)
			#add information about it to MongoDB
			self.gt.add_folder(owner  = login, name = folder_name, size = None, location = path, directory = directory)
			return 1
		else:
			return 0
