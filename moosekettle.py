#!/usr/bin/python -t
# Simple attempt at a gui for my ikettle
#
# I'm a perl guy, but they'll laugh at me at work if I wrote this in perl/tk
#
# protocol: http://www.awe.com/mark/blog/20140223.html
#
# things to do: 
#    nice interface with shiny buttons and circles
#    sound sample when boiled
#    scan for IP (look for 2000 open, then HELLOAPP stuff)
#    remember last working IP to save above
#    get rid of connect button, just try to connect every so often
#                               or rescan or something else
#
# Mark J Cox 2014

import gtk
import pango
import gobject, socket

cnf = "moosekettle.cfg"

class MooseKettle(gtk.Window):

    def __init__(self, configip, argip):
        super(MooseKettle, self).__init__()

        self.kettleconnected = 0
        self.configip = configip
        self.ip = configip
        if (argip):
            self.ip = argip
#        self.set_decorated(False)
        self.resize(400,34)
        self.connect("destroy", self.gotofail)

        box = gtk.HBox()
        self.add(box)

        self.bconnect = gtk.Button("connect")
        self.bconnect.connect("clicked", self.clickbconnect)
        box.pack_start(self.bconnect)
        self.bconnect.show()

        self.bboil = gtk.ToggleButton("boil")
        self.bboil.connect("clicked", self.clickboil)
        self.bboil.show()
        box.pack_start(self.bboil)
        self.b100 = gtk.ToggleButton("100")
        self.b100.connect("clicked", self.clicksend, "set sys output 0x80")
        box.pack_start(self.b100)
        self.b100.show()
        self.b95 = gtk.ToggleButton("95")
        self.b95.connect("clicked", self.clicksend, "set sys output 0x2")
        box.pack_start(self.b95)
        self.b95.show()
        self.b80 = gtk.ToggleButton("80")
        self.b80.connect("clicked", self.clicksend, "set sys output 0x4000")
        box.pack_start(self.b80)
        self.b80.show()
        self.b65 = gtk.ToggleButton("65")
        self.b65.connect("clicked", self.clicksend, "set sys output 0x200")
        box.pack_start(self.b65)
        self.b65.show()
        self.bwarm = gtk.ToggleButton("warm")
        self.bwarm.connect("clicked", self.clicksend, "set sys output 0x8")
        box.pack_start(self.bwarm)
        self.bwarm.show()
        self.setbuttons(False) # initially not connected

        button = gtk.Button("quit")
        button.connect("clicked", self.gotofail)
        box.pack_start(button)
        button.show()

        box.show()

        self.show_all()
        self.kconnect()

    def setbuttons(self, status):
        self.bboil.set_sensitive(status)
        self.b100.set_sensitive(status)
        self.b95.set_sensitive(status)
        self.b80.set_sensitive(status)
        self.b65.set_sensitive(status)
        self.bwarm.set_sensitive(status)

    def clickboil(self, widget, data=None):
        if widget.get_active():
            self.kettlesend("set sys output 0x4")
        else:
            self.kettlesend("set sys output 0x0")

    def clicksend(self, widget, data=None):
        widget.handler_block_by_func(self.clicksend)
        if widget.get_active():
            self.kettlesend(data)
            widget.set_active(False)
        else:
            widget.set_active(True)
        widget.handler_unblock_by_func(self.clicksend)

    def kettlesend(self, data):
#        print data
        self.sock.send(data+"\n")

    def clickbconnect(self, widget):
#        print "Connecting...."
        self.kconnect()

    def gotofail(self, widget):
#        print "Closing"
        try:
            self.sock.close()
        except:
            pass
        gtk.main_quit()
    
    def expose(self, widget, event):
        # redundant function to draw a nice circle for the GUI
        w, h = widget.window.get_size()
        xgc = widget.window.new_gc()

        xgc.set_rgb_fg_color(gtk.gdk.color_parse("green"))
        xgc.line_width = 3
        widget.window.draw_arc(xgc, False, 5, 5, 80, 80, 0*64, 360*64)

        context = self.create_pango_context()
        self.layout = self.create_pango_layout("moose")
        desc = pango.FontDescription('Sans 14')
        self.layout.set_font_description(desc) 

        widget.window.draw_layout(xgc, 20, 35, layout=self.layout)

    def kconnect(self):
        if (not self.ip):
            self.ip = self.get_ip("Enter IP Address of Kettle","127.0.0.1")
            if (not self.ip):
                return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip,2000))
            self.sock.send("HELLOKETTLE\n")
            gobject.io_add_watch(self.sock, gobject.IO_IN, self.handler)
            gobject.timeout_add(5000, self.check_connected)
        except:
            message = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,
                                        buttons=gtk.BUTTONS_NONE,message_format=None);
            message.set_markup("Failed to connect to kettle")
            message.show()
            self.ip=""  # the one given didnt work

    def get_ip(self, text, default=''):
        msgd = gtk.MessageDialog(self, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                              gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, text)
        entry = gtk.Entry()
        entry.set_text(default)
        entry.show()
        msgd.vbox.pack_end(entry)
        entry.connect('activate', lambda _: msgd.response(gtk.RESPONSE_OK))
        msgd.set_default_response(gtk.RESPONSE_OK)

        msgr = msgd.run()
        text = entry.get_text().decode('utf8')
        msgd.destroy()
        if (msgr == gtk.RESPONSE_OK):
            return text
        else:
            return None

    def check_connected(self):
        if (self.kettleconnected == 0):
            try:
                self.sock.close()
            except:
                pass
            message = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,
                                        buttons=gtk.BUTTONS_NONE,message_format=None);
            message.set_markup("Failed to connect to kettle")
            message.show()

    def setbutton(self, button, status):
        button.handler_block_by_func(self.clicksend)
        button.set_active(status)
        button.handler_unblock_by_func(self.clicksend)

    def handler(self, conn, *args):
        line = conn.recv(4096)
        if not len(line):  # "Connection closed."
            self.bconnect.set_sensitive(True)
            self.setbuttons(False) # not connected
            self.kconnect()
            return False
        else:
            for myline in line.splitlines():
#                print "got a line: "+myline
                if (myline.startswith("HELLOAPP")):
                    self.kettleconnected = 1
                    self.setbuttons(True) # connected
                    self.bconnect.set_sensitive(False)
                    self.writeconfig(self.ip)
                    conn.send("get sys status\n")
                if (myline.startswith("sys status key=")):
                    if (len(myline)<16):
                        key = 0
                    else:
                        key = ord(myline[15]) & 0x3f
                    self.setbutton(self.b100,key&0x20)
                    self.setbutton(self.b95,key&0x10)
                    self.setbutton(self.b80,key&0x8)
                    self.setbutton(self.b65,key&0x4)
                    self.setbutton(self.bwarm,key&0x2)
                    self.bboil.handler_block_by_func(self.clickboil)
                    self.bboil.set_active(key&0x1)
                    self.bboil.handler_unblock_by_func(self.clickboil)
                if (myline == "sys status 0x100"):
                    self.setbutton(self.b100,True)
                    self.setbutton(self.b95,False)
                    self.setbutton(self.b80,False)
                    self.setbutton(self.b65,False)
                elif (myline == "sys status 0x95"):
                    self.setbutton(self.b95,True)
                    self.setbutton(self.b100,False)
                    self.setbutton(self.b80,False)
                    self.setbutton(self.b65,False)
                elif (myline == "sys status 0x80"):
                    self.setbutton(self.b80,True)
                    self.setbutton(self.b100,False)
                    self.setbutton(self.b95,False)
                    self.setbutton(self.b65,False)
                elif (myline == "sys status 0x65"):
                    self.setbutton(self.b65,True)
                    self.setbutton(self.b100,False)
                    self.setbutton(self.b95,False)
                    self.setbutton(self.b80,False)
                elif (myline == "sys status 0x11"):
                    self.setbutton(self.bwarm,True)
                elif (myline == "sys status 0x10"):
                    self.setbutton(self.bwarm,False)
                elif (myline == "sys status 0x5"):
                    self.bboil.handler_block_by_func(self.clickboil)
                    self.bboil.set_active(True)
                    self.bboil.handler_unblock_by_func(self.clickboil)
                elif (myline == "sys status 0x0"):
                    self.setbutton(self.b100,False)
                    self.setbutton(self.b95,False)
                    self.setbutton(self.b80,False)
                    self.setbutton(self.b65,False)
                    self.setbutton(self.bwarm,False)
                    self.bboil.handler_block_by_func(self.clickboil)
                    self.bboil.set_active(False)
                    self.bboil.handler_unblock_by_func(self.clickboil)
                elif (myline == "sys status 0x3"):
                    message = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,
                                                buttons=gtk.BUTTONS_NONE,message_format=None);
                    message.set_markup("Your Kettle Has Boiled")
                    message.show()
                elif (myline == "sys status 0x1"):
                    message = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,
                                                buttons=gtk.BUTTONS_NONE,message_format=None);
                    message.set_markup("Your Kettle Was Removed")
                    message.show()

            return True

    def writeconfig(self,ip):
        if (ip == self.configip):
            return
        try:
            config.add_section('Main')
        except:
            pass
        config.set('Main','ip',ip)
        with open(cnf, 'wb') as configfile:
            config.write(configfile)

import argparse
import ConfigParser

config = ConfigParser.RawConfigParser()
configip = None
try:
    config.read(cnf)
    configip = config.get('Main','ip')
except:
    pass

parser = argparse.ArgumentParser(description="Simple GUI interface to the ikettle")
parser.add_argument('-i','--ip',help='IP address for kettle', required=False)
args = vars(parser.parse_args())

MooseKettle(configip,args['ip'])
gtk.main()
