from .base import Property, Component, ObjectWithProperties, Register, HTMLComp, TemplateProcessor, init, render, initialize_comps_classes, BrowserDOMRender

# TODO Future: To load a precompiled version of components.base (See ticket #222 in Brython repo)
"""
import sys
# Ensure that VFS path finder is installed
from _importlib import VFSPathFinder
if VFSPathFinder not in sys.path_hooks:
    sys.path_hooks.insert(0, VFSPathFinder)
    print('WARNING: VFS path hook installed')
else:
    print('INFO: VFS path finder already installed')

orig_path = list(sys.path)
# Override VFS entry in sys.path
vfs_pyc_url =  'http://localhost:8000/demo/components/base.vfs.js'
sys.path[0] = vfs_pyc_url
from base_pyc import  Property, Component, ObjectWithProperties, Register, HTMLComp, TemplateProcessor, init, BrowserDOMRender

#Restore
sys.path = orig_path
"""
