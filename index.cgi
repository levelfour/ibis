#!/usr/bin/env python
# coding: utf-8
import os
import re
import logging

LOG_FILE_PATH = "tmp/log/debug.log"

print "Content-Type: text/html\n\n"

class View:
	def __init__(self):
		self.__set_var__ = {}
		self.layout('lib/default/layout.html')
		try:
			if os.path.exists(LOG_FILE_PATH):
				self.__log_file__ = open(LOG_FILE_PATH, "a")
			else:
				self.__log_file__ = open(LOG_FILE_PATH, "w")
				os.chmod(LOG_FILE_PATH, 0666)
			logging.basicConfig(filename=LOG_FILE_PATH,
					            level=logging.DEBUG)
		except Exception, (msg):
			self.set('__ERROR_MESSAGE__', str(msg))
			self.render('lib/error/error.html')
			quit()

	def __del(self):
		self.__logfile__.close()

	def layout(self, filename):
		try:
			with open(filename, "r") as lf:
				self.__layout__ = lf.read()
		except IOError, (msg):
			self.error_log(msg)

	def render(self, filename):
		try:
			with open(filename, "r") as f:
				content = f.read()
		except IOError, (msg):
			self.error_log(msg)

		self.set("__CONTENT__", content)
		self.__layout__ = self.__layout__.replace("%%__CONTENT__%%", content)
		for var in re.findall("%%(.*)%%", self.__layout__):
			try:
				self.__layout__ = self.__layout__.replace("%%"+var+"%%", self.__set_var__[var])
			except:
				pass
		print self.__layout__

	def set(self, var_name, value):
		if isinstance(value, str):
			self.__set_var__[var_name] = value
		else:
			self.error_log("ERROR: set method need str value")

	def log(self, msg=""):
		logging.debug(msg)

	def error_log(self, msg=""):
		logging.error(msg)
		self.set('__ERROR_MESSAGE__', str(msg))
		self.render('lib/error/error.html')
		quit()

############################################

if __name__ == "__main__":
	v = View()
	v.layout('layout.html')
	v.render('content.html')
