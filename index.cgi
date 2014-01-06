#!/usr/bin/env python
# coding: utf-8
import ibis

if __name__ == "__main__":
	v = ibis.View()
	v.layout('layout.html')
	v.render('content.html')
