#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017-2018, The Sumokoin Project (www.sumokoin.org)
'''
App top-level settings
'''

__doc__ = 'default application wide settings'

import sys
import os
import logging

from utils.common import getHomeDir, makeDir

USER_AGENT = "Ryo LITE Wallet"
APP_NAME = "Ryo LITE Wallet"
VERSION = [0, 2, 0, 3]


_data_dir = makeDir(os.path.join(getHomeDir(), 'RyoLITEWallet'))
DATA_DIR = _data_dir

log_file  = os.path.join(DATA_DIR, 'logs', 'app.log') # default logging file
log_level = logging.DEBUG # logging level

seed_languages = [
    ("0", "German"),
    ("1", "English"),
    ("2", "Spanish"),
    ("3", "French"),
    ("4", "Italian"),
    ("5", "Dutch"),
    ("6", "Portuguese"),
    ("7", "Russian"),
    ("8", "Japanese"),
    ("9", "Chinese (simplified)"),
    ("10", "Esperanto"),
    ("11", "Lojban"),
                ]

# COIN - number of smallest units in one coin
COIN = 1000000000.0

WALLET_RPC_PORT = 19836
WALLET_RPC_PORT_SSL = 19836

REMOTE_DAEMON_HOST = "178.63.69.7"
REMOTE_DAEMON_PORT = 12211
REMOTE_DAEMON_SSL_PORT = 12211
REMOTE_DAEMON_ADDRESS = "%s:%s" % (REMOTE_DAEMON_HOST, REMOTE_DAEMON_PORT)
REMOTE_DAEMON_SSL_ADDRESS = "%s:%s" % (REMOTE_DAEMON_HOST, REMOTE_DAEMON_SSL_PORT)

RESOURCES_PATH = "../Resources" if sys.platform == 'darwin' and hasattr(sys, 'frozen') else "./Resources"
CA_CERTS_PATH = RESOURCES_PATH + "/certs/cacert-2018-03-07.pem"
