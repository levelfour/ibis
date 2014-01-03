#!/usr/bin/env python
# -*- coding: utf-8 -*-

def render(html):
	_html = """Content-Type: text/html

<html>
	<head>
		<title>Python CGI framework</title>
	</head>
	<body>
		%s
	</body>
</html>""" % html
	print _html

render('<span style="color: red; font-size: x-large;">hello</span><br /><input type="text" placeHolder="input your name"/>')
