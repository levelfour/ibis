Ibis
====

Light Web Framework written with Python

## About
Why am I developing web framework?
There are already many web framework even written with Python.
For instance, [Django](http://www.djangoproject.jp), [Flask](http://flask.pocoo.org), [Bottle](http://bottlepy.org/), [Pyramid](http://www.pylonsproject.org/projects/pyramid/) and so on.
I have to develop web system for a certain reason, and I do not prefer to writing PHP, so I decided to try to develop with Python.

But there is a problem.

The server I have to use is **Light Plan** of [Sakura Rental Server](http://www.sakura.ne.jp/plans.html).
Look at above web site.
**In Light Plan, we cannot use SSH!**
So, we cannot use relatively big framework such as Django (because we cannot install framework in server).
Fortunately, original CGI script by Python (Perl, Ruby as like) is allowed.
Therefore, I decided first to develop original web framework wrapping CGI.

(Later, I was told that Flask consists of only 1 file, so maybe I could use Flask to develop web system)

By the way, the original mean of word "ibis" is Japanese famous, but almost extinct bird like cranes, which called "toki" in Japanese.

## Feature
Ibis has below features.
* running on CGI and SQLite3
* consists of only 1 file (at least at present)
* easy replacement of variable in view
* automatically create model files from XML schema (like [Propel](http://propelorm.org))

## Usage
### import module
When you use Ibis web framework (after now I simply call this "Ibis"), all you have to do is import ibis module (given as ibis.py).
In fact, ibis.py has 2 modes such as module mode and script mode.
Script mode is described later.
```python
import ibis
```
Then, ibis module is available.
Look at index.cgi.

####index.cgi
```python
#!/usr/bin/env python
# coding: utf-8
import ibis

if __name__ == "__main__":
        app = ibis.ibis()
        app.layout('view/layout.html')
        app.render('view/content.html')

        for v in app.request.post:
                print "post[{}] = {}<br />".format(v, app.request.post[v])

        print "<br />"
        
        print "This request is {}GET<br />".format("" if app.request.isGet() else "not ")
        print "This request is {}POST<br />".format("" if app.request.isPost() else "not ")
        print "This request is {}Ajax<br />".format("" if app.request.isAjax() else "not ")
```
Line 1 is shebang. (I recommend using `#!/usr/bin/env python` instead `#!/usr/bin/python` because in not all machine python is installed in /usr/bin/)
Line 2 is the config of character code.
At line 3, this script import ibis module.

### render view
```python
        app = ibis.ibis()
        app.layout('view/layout.html')
        app.render('view/content.html')
```
In this part, this CGI script rendering view.
`ibis.ibis` is the root class of ibis module.
This class has following functions:
* rendering view
* retain HTTP request data
* logger

Now, I describe first function.
View consists of two parts. "Layout" and "Element".
In general, header and footer are shared in one site, so it is absurd to write these section in all HTML files.
To avoid this, we need a templete file. This is layout.
Element is the rest parts.

All you have to do is **first set layout** then **render elements**.
The former responds to `app.layout` and the latter to `app.render`.

Let's look at layout.html.

####layout.html
```html
<html lang="ja">
<head>
        <title>PythonでCGI framework</title>
        <meta charset="utf-8" />
        <script src="/view/jquery.js"></script>
        <style>
                body {
                        font-family: "Lucida Grande", "segoe UI", "ヒラギノ丸ゴ ProN W4", "Hiragino Maru Gothic ProN", Meiryo, Arial, sans-serif;
                }
        </style>
</head>
<body>
        $$__CONTENT__$$
</body>
</html>
```

In this file, jQuery is imported, and font and character code is set.
Using this layout, you need not write these code in each HTML file.

You may notice there is `$$__CONTENT__$$`.
The token such as `$$/.*/$$` will replace by ibis rendering engine.
You can add replacement variable as you wish, and you have to set variable in controller.
To set variable, you can call this method in Python script.
```python
app.set(REPLACEMENT_VARIABLE_NAME, VALUE)
```
For example, if you call `app.set("VALUE1", "hello, world!")`,
`$$VALUE1$$` in view will be replaced with "hello, world!".

`$$__CONTENT__$$` is a special replacement variable.
This will be replaced with the content of file which given as `app.render` argument.
So, layout must have one `$$_CONTENT__$$`.
(if layout does not have `$$__CONTENT__$$`, there is no error, but there is also no change after `app.render`.)

## access to request data

(Now writing...)
