.. ypricemagic documentation master file, created by
   sphinx-quickstart on Thu Feb  1 21:29:06 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ypricemagic's documentation!
=============================================

Time to price some shitcoins!

.. module:: y

   There is a lot of stuff in ypricemagic's docs that you probably won't need as a typical user.
   I've collected the most interesting components of the library here for your convenience.

   The main use case for this library is the pricing of shitcoins. `y.get_price` handles that for you.

   .. autofunction:: y.get_price

   
   If you do not know the block number but you know the timestamp at which you need your price, you first need to calculate it using this function:

   .. autofunction:: y.get_block_at_timestamp

   
   Usually, if you need one price you need more than one. The next two functions enable you to price multiple tokens in a streamlined, concurrent manner.

   .. autofunction:: y.get_prices

   .. autofunction:: y.map_prices


There are some powerful tools for interacting with deployed contracts in the `contracts` module.

.. automodule:: y.contracts


To learn about the rest of ypricemagic's capabilities, navigate the library structure below.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/modules.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
