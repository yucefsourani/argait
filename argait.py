#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  argait.py
#  
#  Copyright 2017 youcef sourani <youssef.m.sourani@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from bs4 import BeautifulSoup
import urllib
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
import threading
import os

def get_icons_theme_and_catogery(force=False):
    file_ = GLib.get_user_config_dir()+"/freedesktop_iconstheme"
    if force:
        try:
            url = urllib.request.Request("http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html",headers={"User-Agent":"Mozilla/5.0"})
            htmldoc=urllib.request.urlopen(url,timeout=10)
            with open(file_,"wb") as mf:
                mf.write(htmldoc.read())
        except Exception as e:
            print(e)
            return False
    else:
        if not os.path.isfile(file_):
            try:
                url = urllib.request.Request("http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html",headers={"User-Agent":"Mozilla/5.0"})
                htmldoc=urllib.request.urlopen(url,timeout=10)
                with open(file_,"wb") as mf:
                    mf.write(htmldoc.read())
            except Exception as e:
                print(e)
                return False
    try:
        with open(file_,"rb") as mf:
            soup = BeautifulSoup(mf,"html.parser")
    except Exception as e:
        print(e)
        return False
                
    result = {}
    for table in soup.findAll("div",{"class":"table"}):
        name = table.a.attrs["name"]
        if name != "idm140470199740784":
            ll = []
            for tr in table.div.table.tbody:
                for t in tr.td:
                    ll.append(t)
            result[name]=ll.copy()
            ll.clear()
    return result
    
class MW(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.resize(800, 600)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.icons_catogerys = get_icons_theme_and_catogery()
        
        
        self.vb = Gtk.VBox(spacing=10)
        self.add(self.vb)
        update_button = Gtk.Button("Refresh")
        update_button.connect("clicked",self.on_update_button_clicked,False)
        update_button_internet = Gtk.Button("Update Info From Internet")
        update_button_internet.connect("clicked",self.on_update_button_clicked,True)
        aboutbutton = Gtk.Button("About")
        aboutbutton.connect("clicked",self.on_aboutbutton_clicked)
        self.spinner = Gtk.Spinner()
        self.vb.pack_end(aboutbutton,False,False,0)
        self.vb.pack_end(update_button_internet,False,False,0)
        self.vb.pack_end(update_button,False,False,0)
        self.vb.pack_end(self.spinner,False,False,0)
        self.gui()
        
    def gui(self):
        self.grid = Gtk.Grid()
        self.vb.pack_start(self.grid,True,True,0)
        if not self.icons_catogerys:
            return
        
        stack = Gtk.Stack()
        stack.set_hexpand(True)
        stack.set_vexpand(True)
        self.grid.attach(stack, 0, 1, 1, 1)
        stackswitcher = Gtk.StackSwitcher()
        stackswitcher.set_stack(stack)
        self.grid.attach(stackswitcher, 0, 0, 1, 1)
        
        for name,icons in self.icons_catogerys.items():
            sw = Gtk.ScrolledWindow()
            flowbox = Gtk.FlowBox(homogeneous=True)
            flowbox.set_valign(Gtk.Align.START)
            flowbox.set_max_children_per_line(6)
            flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
            sw.add(flowbox)
            stack.add_titled(sw, name,name)
            for icon in icons:
                try:
                    button  = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
                    button.connect("clicked",self.on_button_clicked,icon)
                    vbutton = Gtk.VBox(spacing=3) 
                    pixbuf  = Gtk.IconTheme.get_default().load_icon(icon, 64, 0)
                    image   = Gtk.Image.new_from_pixbuf(pixbuf)
                    label   = Gtk.Label(icon,selectable=True)
                    vbutton.pack_start(image,False,False,0)
                    vbutton.pack_start(label,False,False,0)
                    button.add(vbutton)
                    flowbox.add(button)
                except Exception as e:
                    print(e)
        

        self.show_all()

    def on_button_clicked(self,button,iconname):
        self.clipboard.set_text(iconname, -1)
        
    def on_update_button_clicked(self,button,force):
        self.vb.remove(self.grid)
        self.grid.destroy()
        threading.Thread(target=self.refresh_gui,args=(force,)).start()

    def refresh_gui(self,force):
        GLib.idle_add(self.spinner.start)
        self.icons_catogerys.clear()
        self.icons_catogerys = get_icons_theme_and_catogery(force)
        GLib.idle_add(self.spinner.stop)
        GLib.idle_add(self.gui)
        
    def on_aboutbutton_clicked(self,button):
        about = Gtk.AboutDialog(parent=self,transient_for=self, modal=True)
        about.set_program_name("ArGAIT")
        about.set_version("0.1")
        about.set_copyright("Copyright © 2017 Youssef Sourani")
        about.set_comments("Arfedora Get All IconTheme")
        about.set_website("https://arfedora.blogspot.com")
        logo_  = Gtk.IconTheme.get_default().load_icon("applications-games", 64, 0)
        about.set_logo(logo_)
        about.set_authors(["Youssef Sourani <youssef.m.sourani@gmail.com>"])
        about.set_license_type(Gtk.License.GPL_3_0)
        translators_ = ("translator-credit")
        if translators_ != "translator-credits":
            about.set_translator_credits(translators_)
        about.run()
        about.destroy()

mw = MW()
mw.connect("delete-event", Gtk.main_quit)
mw.show_all()
Gtk.main()


