#!/usr/bin/env python
# coding: utf-8
import ibis

if __name__ == "__main__":
	app = ibis.ibis()
	v = ibis.View()
	v.layout('view/layout.html')
	v.render('view/content.html')

	for v in app.request.get:
		print "qs[{}] = {}<br />".format(v, app.request.get[v])

	app.request.get["invalid"]
