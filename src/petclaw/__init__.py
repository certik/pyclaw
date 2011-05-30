#  =====================================================================
#  Package:     petclaw
#  File:        __init__.py
#  Authors:     Amal Alghamdi
#               David Ketcheson
#               Aron Ahmadia
#  ======================================================================
"""Main petclaw package"""

import os
import logging, logging.config

# Default logging configuration file
_DEFAULT_LOG_CONFIG_PATH = os.path.join(os.path.dirname(__file__),'log.config')
del os

# Setup loggers
logging.config.fileConfig(_DEFAULT_LOG_CONFIG_PATH)

__all__ = []

# Module imports
__all__.extend(['Controller','Data','Dimension','Grid','Solution','riemann'])
from controller import Controller
from grid import Dimension, Grid 
from pyclaw.data import Data
from pyclaw.solution import Solution

# Sub-packages
import evolve
from evolve import *
__all__.extend(evolve.__all__)

import plot
__all__.append('plot')