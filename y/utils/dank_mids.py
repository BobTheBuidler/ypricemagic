import logging

logger = logging.getLogger(__name__)
logger.warning(
    "y.utils.dank_mids.dank_w3 has been deprecated and will be removed soon. Please import and use `dank_web3` from `dank_mids` directly."
)
from dank_mids import dank_web3 as dank_w3

"""
This module provides a deprecation warning for the `dank_w3` import and guides users to use `dank_web3` directly from `dank_mids`.

The `dank_w3` alias is deprecated and will be removed soon. Users are strongly encouraged to update their imports to use `dank_web3` directly. Transitioning to the new import path is recommended to ensure future compatibility.

Examples:
    Importing `dank_web3` directly from `dank_mids`:

    >>> from dank_mids import dank_web3
    >>> # Use dank_web3 as needed
    >>> web3_instance = dank_web3

    Using the deprecated `dank_w3` alias (not recommended):

    >>> from y.utils.dank_mids import dank_w3
    >>> # This will trigger a warning
    >>> web3_instance = dank_w3

See Also:
    - :mod:`dank_mids`: The module where `dank_web3` is defined.
    - :class:`dank_mids.brownie_patch.DankWeb3`: The class providing the `dank_web3` instance.
"""
