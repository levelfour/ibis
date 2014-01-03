#!/usr/bin/env python
# coding: utf-8

class View:
	__layout = ""

	def __init__(self):
		pass

	def __del(self):
		pass

	def layout(self, filename):
		try:
			with open(filename, "r") as lf:
				self.__layout = lf.read()
		except IOError, (msg):
			print msg
			quit()

	def render(self, filename):
		try:
			with open(filename, "r") as f:
				content = f.read()
		except IOError, (msg):
			print msg
			quit()
		html = "Content-Type: text/html\n\n" + self.__layout
		print html

v = View()
v.layout('layout.html')
v.render('content.html')
