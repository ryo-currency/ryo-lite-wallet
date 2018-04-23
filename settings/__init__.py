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

USER_AGENT = "Sumo LITE Wallet"
APP_NAME = "Sumo LITE Wallet"
VERSION = [0, 1, 0]


_data_dir = makeDir(os.path.join(getHomeDir(), 'SumoLITEWallet'))
DATA_DIR = _data_dir

log_file  = os.path.join(DATA_DIR, 'logs', 'app.log') # default logging file
log_level = logging.DEBUG # logging level

seed_languages = [("0", "English"), 
                  ("1", "Spanish"), 
                  ("2", "German"), 
                  ("3", "Italian"), 
                  ("4", "Portuguese"),
                  ("5", "Russian"),
                  ("6", "Japanese"),
                ]

# COIN - number of smallest units in one coin
COIN = 1000000000.0

WALLET_RPC_PORT = 19736
WALLET_RPC_PORT_SSL = 19737

REMOTE_DAEMON_HOST = "wallet-node.sumokoin.com"
REMOTE_DAEMON_PORT = 4444
REMOTE_DAEMON_SSL_PORT = 4446
REMOTE_DAEMON_ADDRESS = "%s:%s" % (REMOTE_DAEMON_HOST, REMOTE_DAEMON_PORT)
REMOTE_DAEMON_SSL_ADDRESS = "%s:%s" % (REMOTE_DAEMON_HOST, REMOTE_DAEMON_SSL_PORT)

RESOURCES_PATH = "../Resources" if sys.platform == 'darwin' and hasattr(sys, 'frozen') else "./Resources"
CA_CERTS_PATH = RESOURCES_PATH + "/certs/cacert-2018-03-07.pem"