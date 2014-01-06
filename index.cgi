#!/usr/bin/env python
# coding: utf-8
import os, sys, traceback
import re
import logging

LOG_FILE_PATH = "tmp/log/debug.log"
DATE_FORMAT = '%Y/%m/%d %p %I:%M:%S'

print "Content-Type: text/html\n\n"

class View:
	def __init__(self):
		self.__set_var = {}
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
		for var in re.findall("%%(.*)%%", self.__layout):
			try:
				self.__layout = self.__replace_set_value(self.__layout)
			except:
				pass
		print self.__layout

	def __replace_set_value(self, string):
		for var in re.findall("%%(.*)%%", string):
			try:
				string = string.replace("%%"+var+"%%", self.__replace_set_value(self.__set_var[var]))
			except:
				pass
		return string

	def set(self, var_name, value):
		if isinstance(value, str):
			self.__set_var[var_name] = value
		else:
			self.error_log("ERROR: set method need str value")

	def log(self, msg=""):
		self.__logger.debug(msg)

	def error_log(self, msg=""):
		info = sys.exc_info()
		tb_info = traceback.extract_tb(info[2])[0]
		self.__logger.error(msg)
		self.set('__ERROR_FILE__', str(tb_info[0]))
		self.set('__ERROR_LINE__', str(tb_info[1]))
		self.set('__ERROR_FUNC__', str(tb_info[2]))
		self.set('__ERROR_TEXT__', str(tb_info[3]))
		self.set('__ERROR_MESSAGE__', str(msg))
		self.render('lib/error/error.html')
		quit()

############################################

if __name__ == "__main__":
	v = View()
	v.layout('layout.html')
	v.render('content.html')
