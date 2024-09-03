# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from sphinx.util import logging


project = 'ypricemagic'
copyright = '2024, BobTheBuidler'
author = 'BobTheBuidler'

logger = logging.getLogger(__name__)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'a_sync.sphinx.ext',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Looks for objects in documentation of external libraries
intersphinx_mapping = {
    'a_sync': ('https://bobthebuidler.github.io/ez-a-sync', None),
    'brownie': ('https://eth-brownie.readthedocs.io/en/stable/', None),
    'checksum_dict': ('https://bobthebuidler.github.io/checksum_dict', None),
    'dank_mids': ('https://bobthebuidler.github.io/dank_mids', None),
    'eth_typing': ('https://eth-typing.readthedocs.io/en/stable/', None),
    'hexbytes': ('https://hexbytes.readthedocs.io/en/stable/', None),
    'pony': ('https://docs.ponyorm.org/', None),
    'python': ('https://docs.python.org/3', None),
    'typing_extensions': ('https://typing-extensions.readthedocs.io/en/latest/', None),
    'web3': ('https://web3py.readthedocs.io/en/stable/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {
    'undoc-members': True,
    'special-members': True,
    'inherited-members': True,
    'member-order': 'groupwise',
    # hide private methods that aren't relevant to us here
    'exclude-members': ','.join([
        '__new__',
        '__dict__',
        '__slots__',
        '__module__',
        '__hash__',
        '__repr__',
        '__setattr__',
        '__delattr__',
        '__init_from_abi__',
        '__method_names__',
        '__get_method_object__',
        '__annotations__',
        '__weakref__',
        '__reduce__',
        '__cause__',
        '__context__',
        '__suppress_context__',
        '__setstate__',
        '__traceback__',
        '_abc_impl',
        '__abstractmethods__',
        '__a_sync_default_mode__',
        '__a_sync_instance_will_be_sync__',
        '__a_sync_should_await__',
        '__a_sync_should_await_from_kwargs__',
        '__a_sync_flag_name__',
        '__a_sync_flag_value__',
        '__a_sync_instance_should_await__',
        '__a_sync_modifiers__',
        '__class_getitem__',
        '__init_subclass__',
        '__subclass_hook__',
    ]),
}
autodoc_typehints = "description"
# Don't show class signature with the class' name.
autodoc_class_signature = "separated"

automodule_generate_module_stub = True

sys.path.insert(0, os.path.abspath('./y'))


def skip_specific_members(app, what, name, obj, skip, options):
    """
    Function to exclude specific members for a particular module.
    """
    
    logger.info(f"module: {getattr(obj, '__module__', None)}  name: {name}  obj: {obj}")

    # Skip the __init__ and __call__ members of any NewType objects we defined.
    if type(getattr(obj, "__self__", None)).__qualname__ == "typing.NewType" and name in ["__init__", "__call__"]:
        return True
    
    # Skip the __init__, __str__, __getattribute__, args, and with_traceback members of all Exceptions
    if issubclass(getattr(obj, '__objclass__', type), BaseException) and name in ["__init__", "__str__", "__getattribute__", "args", "with_traceback"]:
        return True
    
    return skip

def setup(app):
    app.connect('autodoc-skip-member', skip_specific_members)