moosekettle
===========

python/gtk interface to the iKettle
http://www.firebox.com/product/6068/iKettle

run it with
  python moosekettle.py --ip 192.168.0.128

it currently doesn't scan the network

protocol write up
http://www.awe.com/mark/blog/20140223.html

running this on windows
=======================

You can run this app on Windows too if you install python and pygtk first.

* Grab Python "2.7.6 Windows Installer" from http://python.org/download/
and install it

* Grab "pygtk all in one 2.22.6 msi" from 
http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.22/ and install it

* You can then grab moosekettle.py
https://github.com/iamamoose/moosekettle/archive/master.zip
and run it as   c:\moosekettle.py -i 192.168.0.128
