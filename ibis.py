#!/usr/bin/env python
# coding: utf-8
import os, sys, traceback
import re
import logging

LOG_FILE_PATH = "tmp/log/debug.log"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

print "Content-Type: text/html\n\n"

class View:
	def __init__(self):
		self.__set_var = {}
		self.__set_arr = {}
		self.__logger = logging.getLogger(self.__class__.__name__)
		self.__log_format = '%(asctime)s - %(levelname)s(%(name)s) # %(message)s'
		self.layout('lib/default/layout.html')
		try:
			if os.path.exists(LOG_FILE_PATH):
				self.__log_file = open(LOG_FILE_PATH, "a")
			else:
				self.__log_file = open(LOG_FILE_PATH, "w")
				os.chmod(LOG_FILE_PATH, 0666)
			logging.basicConfig(filename=LOG_FILE_PATH,
					            level=logging.DEBUG,
								format=self.__log_format,
								datefmt=DATE_FORMAT,)
		except Exception, (msg):
			self.set('__ERROR_MESSAGE__', str(msg))
			self.render('lib/error/error.html')
			quit()

	def __del(self):
		self.__logfile.close()

	def layout(self, filename):
		try:
			with open(filename, "r") as lf:
				self.__layout = lf.read()
		except Exception, (msg):
			self.error_log(msg)

	def render(self, filename):
		try:
			with open(filename, "r") as f:
				content = f.read()
		except Exception, (msg):
			self.error_log(msg)

		self.set("__CONTENT__", content)
		self.__layout = self.__expand(self.__layout)
		print self.__layout

	def set(self, var_name, value):
		if isinstance(value, str):
			self.__set_var[var_name] = value
		else:
			self.error_log("ERROR: set method need str value")

	def push(self, array_name, value):
		if isinstance(value, str):
			if not array_name in self.__set_arr:
				self.__set_arr[array_name] = []
			self.__set_arr[array_name].append(value)
		else:
			self.error_log("ERROR: push method need str array")

	# expand set variable ($$***$$) and set array (@@ $@***$@ @@)
	def __expand(self, string):
		# expand set array
		for arr in re.findall("@@(.*)@@", string, re.DOTALL):
			string = string.replace("@@"+arr+"@@", self.__expand_array(arr))
		# expand set variable
		for var in re.findall("\$\$(.*)\$\$", string):
			if var in self.__set_var:
				string = string.replace("$$"+var+"$$", self.__expand(self.__set_var[var]))
			else:
				string = string.replace("$$"+var+"$$", "")
		return string

	# expand set array (@@ ... @@) in `string`
	def __expand_array(self, string):
		try:
			array_names = []	# array names included in `string`
			array_len = 0		# max length of arrays
			for array_name in re.findall("\$@(.*)\$@", string):
				array_names.append(array_name)
				# find longest array length
				if array_name in self.__set_arr \
						and len(self.__set_arr[array_name]) > array_len:
					array_len = len(self.__set_arr[array_name])
			# output element by `array_len` times
			expanded_str = ""
			for i in range(array_len):
				element = string
				for array_name in array_names:
					if len(self.__set_arr[array_name]) > i:
						value = self.__set_arr[array_name][i]
						element = element.replace("$@"+array_name+"$@", value)
					else:
						element = element.replace("$@"+array_name+"$@", "")
				expanded_str += element
			return expanded_str
		except Exception, (msg):
			self.error_log(msg)

	def log(self, msg=""):
		self.__logger.debug(msg)

	def error_log(self, msg=""):
		self.__logger.error(msg)
		info = sys.exc_info()
		tb_info = traceback.extract_tb(info[2])[0]
		# push stack info
		for st_info in traceback.extract_stack():
			self.push('__ERROR_FILE__', str(st_info[0]))
			self.push('__ERROR_LINE__', str(st_info[1]))
			self.push('__ERROR_FUNC__', str(st_info[2]))
			self.push('__ERROR_TEXT__', str(st_info[3]))
		# push current stack info
		self.push('__ERROR_FILE__', str(tb_info[0]))
		self.push('__ERROR_LINE__', str(tb_info[1]))
		self.push('__ERROR_FUNC__', str(tb_info[2]))
		self.push('__ERROR_TEXT__', str(tb_info[3]))
		self.set('__ERROR_MESSAGE__', str(msg))
		self.render('lib/error/error.html')
		quit()
