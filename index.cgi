#!/usr/bin/env python
# coding: utf-8
import ibis

if __name__ == "__main__":
	v = ibis.View()
	v.layout('view/layout.html')
	v.render('view/content.html')
	for v in ibis.request.post:
		print "form[{}]: {}<br />".format(v, ibis.request.post[v])
	
	for v in ibis.request.get:
		print "qs[{}]: {}<br />".format(v, ibis.request.get[v])
