# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from sphinx.util import logging


project = "ypricemagic"
copyright = "2024, BobTheBuidler"
author = "BobTheBuidler"

logger = logging.getLogger(__name__)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "a_sync.sphinx.ext",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "../y/interfaces/*",
]

# Looks for objects in documentation of external libraries
intersphinx_mapping = {
    "a_sync": ("https://bobthebuidler.github.io/ez-a-sync", None),
    "brownie": ("https://eth-brownie.readthedocs.io/en/stable/", None),
    "checksum_dict": ("https://bobthebuidler.github.io/checksum_dict", None),
    "dank_mids": ("https://bobthebuidler.github.io/dank_mids", None),
    "dictstruct": ("https://bobthebuidler.github.io/dictstruct", None),
    "eth_typing": ("https://eth-typing.readthedocs.io/en/stable/", None),
    "evmspec": ("https://bobthebuidler.github.io/evmspec", None),
    "hexbytes": ("https://hexbytes.readthedocs.io/en/stable/", None),
    "pony": ("https://docs.ponyorm.org/", None),
    "python": ("https://docs.python.org/3", None),
    "typed_envs": ("https://bobthebuidler.github.io/typed-envs/", None),
    "typing_extensions": ("https://typing-extensions.readthedocs.io/en/latest/", None),
    "web3": ("https://web3py.readthedocs.io/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

autodoc_default_options = {
    "undoc-members": True,
    "special-members": True,
    "inherited-members": True,
    "member-order": "groupwise",
    # hide private methods that aren't relevant to us here
    "exclude-members": ",".join(
        [
            "__new__",
            "__dict__",
            "__slots__",
            "__module__",
            "__hash__",
            "__repr__",
            "__del__",
            "__setattr__",
            "__delattr__",
            "__init_from_abi__",
            "__method_names__",
            "__get_method_object__",
            "__annotations__",
            "__weakref__",
            "__reduce__",
            "__cause__",
            "__context__",
            "__suppress_context__",
            "__setstate__",
            "__traceback__",
            "_abc_impl",
            "__abstractmethods__",
            "__a_sync_default_mode__",
            "__a_sync_instance_will_be_sync__",
            "__a_sync_should_await__",
            "__a_sync_should_await_from_kwargs__",
            "__a_sync_flag_name__",
            "__a_sync_flag_value__",
            "__a_sync_instance_should_await__",
            "__a_sync_modifiers__",
            "__class_getitem__",
            "__init_subclass__",
            "__subclasshook__",
            "__orig_bases__",
            "__parameters__",
            # cache dict for instances for async_property lib
            "__async_property__",
            # float stuff
            "bit_count",
            "bit_length",
            "as_integer_ratio",
            "conjugate",
            "is_integer",
            "imag",
            "real",
        ]
    ),
}
autodoc_typehints = "description"
# Don't show class signature with the class' name.
autodoc_class_signature = "separated"

automodule_generate_module_stub = True

sys.path.insert(0, os.path.abspath("./y"))


def skip_specific_members(app, what, name, obj, skip, options):
    """
    Function to exclude specific members for a particular module.

    Args:
        app: The Sphinx application object.
        what: The type of the object which the docstring belongs to (one of "module", "class", "exception", "function", "method", "attribute").
        name: The fully qualified name of the object.
        obj: The object itself.
        skip: A boolean indicating if autodoc will skip this member if True.
        options: The options given to the directive: an object with attributes inherited_members, undoc_members, show_inheritance and noindex that are true if the flag option of same name was given to the auto directive.

    Returns:
        True if the member should be skipped, False otherwise.
    """

    # Skip some dundermethods in all cases.
    if name in [
        "__abs__",
        "__ceil__",
        "__divmod__",
        "__float__",
        "__floor__",
        "__format__",
        "__getformat__",
        "__getnewargs__",
        "__int__",
        "__mod__",
        "__ne__",
        "__neg__",
        "__pos__",
        "__rdivmod__",
        "__rfloordiv__",
        "__rmod__",
        "__rmul__",
        "__round__",
        "__rpow__",
        "__rsub__",
        "__rtruediv__",
        "__setformat__",
        "__trunc__",
        # not a dunder but this can go here
        "_ChecksumAddressSingletonMeta__instances",
    ]:
        return True

    # Skip the __init__ and __call__ members of any NewType objects we defined.
    if type(
        getattr(obj, "__self__", None)
    ).__qualname__ == "typing.NewType" and name in ["__init__", "__call__"]:
        return True

    # Skip the __init__, __str__, __getattribute__, args, and with_traceback members of all Exceptions
    if issubclass(getattr(obj, "__objclass__", type), BaseException) and name in [
        "__init__",
        "__str__",
        "__getattribute__",
        "args",
        "with_traceback",
    ]:
        return True

    if not skip:
        logger.info(
            f"module: {getattr(obj, '__module__', None)}  name: {name}  obj: {obj}"
        )
    return skip


def setup(app):
    """
    Connect the skip_specific_members function to the autodoc-skip-member event.

    Args:
        app: The Sphinx application object.
    """
    app.connect("autodoc-skip-member", skip_specific_members)
