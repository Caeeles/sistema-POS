#!/usr/bin/python3

import os
import sys
import optparse

parser = optparse.OptionParser()
parser.add_option("-k", "--kivymd", action="store_true", dest="md", default=False, help="Create KivyMD Project")
parser.add_option("-p", "--package", dest="package_name", help="Create a new package with given name")

(options, args) = parser.parse_args()

main = """
from os.path import dirname, join

from kivy.garden.iconfonts import register

from app import MainApp

MainApp().run()
"""

init = """
from kivy.app import App

from .view import MainWindow

class MainApp(App):
    def build(self):
        return MainWindow()
"""

md_init = """
from kivymd.app import MDApp

from .view import MainWindow

class MainApp(MDApp):
    def build(self):
        return MainWindow()
"""

view = """
from kivy.uix.boxlayout import BoxLayout

class MainWindow(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
"""

kv = """
<MainWindow>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: rgba('#ffffff')
        Rectangle:
            pos: self.pos
            size: self.size
"""

package_init = """
from .{name} import {Name}
"""

package_py = """
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

Builder.load_file('{name}.kv')

class {Name}(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self.render, .1)

    def render(self, _):
        pass
"""

package_kv = """
<{Name}>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: rgba('#ffffff')
        Rectangle:
            pos: self.pos
            size: self.size
"""

def create_project(path, md=False):
    print(f"[!] Setting up kivy project: {path}")

    if not os.path.exists(path):
        os.mkdir(path)
    else:
        sys.exit('[!] Project Path Already Exists')

    os.mkdir(os.path.join(path, 'app'))

    with open(os.path.join(path, 'main.py'), 'w') as f:
        f.write(main)

    with open(os.path.join(path, 'app', '__init__.py'), 'w') as f:
        f.write(md_init if md else init)

    with open(os.path.join(path, 'app', 'view.py'), 'w') as f:
        f.write(view)

    with open(os.path.join(path, 'app', 'main.kv'), 'w') as f:
        f.write(kv)

    print('[!] Project Ready, Happy Coding :]')

def create_package(name):
    if not name:
        sys.exit('[!] Package name is required')

    package_path = name
    if not os.path.exists(package_path):
        os.mkdir(package_path)
    else:
        sys.exit('[!] Package Path Already Exists')

    with open(os.path.join(package_path, '__init__.py'), 'w') as f:
        f.write(package_init.format(name=name, Name=name.capitalize()))

    with open(os.path.join(package_path, f'{name}.py'), 'w') as f:
        f.write(package_py.format(name=name, Name=name.capitalize()))

    with open(os.path.join(package_path, f'{name}.kv'), 'w') as f:
        f.write(package_kv.format(Name=name.capitalize()))

    print(f'[!] Package {name} created successfully.')

if options.package_name:
    create_package(options.package_name)
elif len(args) < 1:
    sys.exit('[!] Project path is required')
else:
    create_project(args[0], md=options.md)