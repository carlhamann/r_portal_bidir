import sys
import json
import numpy as np
import imageio
from argparse import Namespace

def load(config_path):
    """Load configuration file of Lightmetrica environment"""

    # Open config file
    with open(config_path) as f:
        config = json.load(f)

    # Add root directory and binary directory to sys.path
    if config['path'] not in sys.path:
        sys.path.insert(0, config['path'])
    if config['bin_path'] not in sys.path:
        sys.path.insert(0, config['bin_path'])

    return Namespace(**config)
