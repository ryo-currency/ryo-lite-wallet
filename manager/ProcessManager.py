#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017-2018, The Sumokoin Project (www.sumokoin.org)

'''
Process managers for sumokoind, sumo-wallet-cli and sumo-wallet-rpc
'''

from __future__ import print_function

import sys, os
import re
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from multiprocessing import Process, Event
from time import sleep
from uuid import uuid4

from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO
from settings import REMOTE_DAEMON_ADDRESS, REMOTE_DAEMON_SSL_ADDRESS, WALLET_RPC_PORT, WALLET_RPC_PORT_SSL, CA_CERTS_PATH

from rpc import WalletRPCRequest

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # disable creating the window
DETACHED_PROCESS = 0x00000008  # forcing the child to have no console at all

class ProcessManager(Thread):
    def __init__(self, proc_args, proc_name=""):
        Thread.__init__(self)
        args_array = proc_args.encode( sys.getfilesystemencoding() ).split(u' ')
        self.proc = Popen(args_array,
                          shell=False, 
                          stdout=PIPE, stderr=STDOUT, stdin=PIPE, 
                          creationflags=CREATE_NO_WINDOW)
        self.proc_name = proc_name
        self.daemon = True
        log("[%s] started" % proc_name, LEVEL_INFO, self.proc_name)
    
    def run(self):
        for line in iter(self.proc.stdout.readline, b''):
            log(">>> " + line.rstrip(), LEVEL_DEBUG, self.proc_name)
        
        if not self.proc.stdout.closed:
            self.proc.stdout.close()
            
    def send_command(self, cmd):
        self.proc.stdin.write( (cmd + u"\n").encode("utf-8") )
        sleep(0.1)
    
        
    def stop(self):
        if self.is_proc_running():
            self.send_command('exit')
            counter = 0
            while True:
                if self.is_proc_running():
                    if counter < 60:
                        if counter == 2:
                            try:
                                self.send_command('exit')
                            except:
                                pass
                        sleep(1)
                        counter += 1
                    else:
                        self.proc.kill()
                        log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                        break
                else:
                    break
        log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)
    
    def is_proc_running(self):
        return (self.proc.poll() is None)
    

class WalletCliManager(ProcessManager):
    fail_to_connect_str = "wallet failed to connect to daemon"
    
    def __init__(self, resources_path, wallet_file_path, wallet_log_path, restore_wallet=False, restore_height=0):
        if not restore_wallet:
            wallet_args = u'%s/bin/ryo-wallet-cli --daemon-address %s --generate-new-wallet=%s --log-file=%s ' \
                                                % (resources_path, REMOTE_DAEMON_ADDRESS, wallet_file_path, wallet_log_path)
        else:
            wallet_args = u'%s/bin/ryo-wallet-cli --daemon-address %s --log-file=%s --restore-deterministic-wallet --restore-height %d' \
                                                % (resources_path, "fakehost", wallet_log_path, restore_height)
        ProcessManager.__init__(self, wallet_args, "ryo-wallet-cli")
        self.ready = Event()
        self.last_error = ""
        
    def run(self):
        is_ready_str = "Background refresh thread started"
        err_str = "Error:"
        for line in iter(self.proc.stdout.readline, b''):
            if not self.ready.is_set() and is_ready_str in line:
                self.ready.set()
                log("Wallet ready!", LEVEL_INFO, self.proc_name)
            elif err_str in line:
                self.last_error = line.rstrip()
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_ERROR, self.proc_name)
            else:
                log("[%s]>>> %s" % (self.proc_name, line.rstrip()), LEVEL_DEBUG, self.proc_name)
        
        if not self.proc.stdout.closed:
            self.proc.stdout.close()
    
    def is_ready(self):
        return self.ready.is_set()
            
    
    def is_connected(self):
        self.send_command("refresh")
        if self.fail_to_connect_str in self.last_error:
            return False
        return True
    
    def stop(self):
        if self.is_proc_running():
            self.send_command('exit')
            #self.proc.stdin.close()
            counter = 0
            while True:
                if self.is_proc_running():
                    if counter < 10:
                        if counter == 2:
                            try:
                                self.send_command('exit')
                            except:
                                pass
                        sleep(1)
                        counter += 1
                    else:
                        self.proc.kill()
                        log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                        break
                else:
                    break
        log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)


class WalletRPCManager(ProcessManager):
    def __init__(self, resources_path, wallet_file_path, wallet_password, app, log_level=1, enable_ssl=False):
        self.user_agent = str(uuid4().hex)
        enable_ssl=False
        wallet_log_path = os.path.join(os.path.dirname(wallet_file_path), "ryo-wallet-rpc.log")
        if enable_ssl:
            wallet_rpc_args = u'%s/bin/ryo-wallet-rpc --daemon-address %s --wallet-file %s --log-file %s --rpc-bind-port %d --user-agent %s --log-level %d --enable-ssl --cacerts-path %s' \
                                            % (resources_path, REMOTE_DAEMON_SSL_ADDRESS, wallet_file_path, wallet_log_path, WALLET_RPC_PORT_SSL, self.user_agent, log_level, CA_CERTS_PATH)
        else:
            wallet_rpc_args = u'%s/bin/ryo-wallet-rpc --daemon-address %s --wallet-file %s --log-file %s --rpc-bind-port %d --user-agent %s --log-level %d' \
                                            % (resources_path, REMOTE_DAEMON_ADDRESS, wallet_file_path, wallet_log_path, WALLET_RPC_PORT, self.user_agent, log_level)
        ProcessManager.__init__(self, wallet_rpc_args, "ryo-wallet-rpc")
        sleep(0.2)
        self.send_command(wallet_password)
        
        self.rpc_request = WalletRPCRequest(app, self.user_agent, enable_ssl)
#         self.rpc_request.start()
        self._stopped = False
        self._ready = Event()
        self.block_height = 0
        self.is_password_invalid = Event()
        self.last_log_lines = []
        self.last_error = ""
    
    def run(self):
        rpc_ready_strs = ["Binding on 127.0.0.1:%d" % WALLET_RPC_PORT, "Starting wallet rpc server", "Run net_service loop", "Refresh done"]
        err_str = "ERROR"
        invalid_password_str = "invalid password"
        height_regex = re.compile(r"Processed block: \<([a-z0-9]+)\>, height (\d+)")
        height_regex2 = re.compile(r"Skipped block by height: (\d+)")
        height_regex3 = re.compile(r"Skipped block by timestamp, height: (\d+)")
        
        for line in iter(self.proc.stdout.readline, b''):
            if self._stopped: break
            
            m_height = height_regex.search(line)
            if m_height: self.block_height = m_height.group(2)
            if not m_height:
                m_height = height_regex2.search(line)
                if m_height: self.block_height = m_height.group(1)
            if not m_height:
                m_height = height_regex3.search(line)
                if m_height: self.block_height = m_height.group(1)
                
            if not self._ready.is_set() and any(s in line for s in rpc_ready_strs):
                self._ready.set()
                log("RPC server ready!", LEVEL_INFO, self.proc_name)
                
            if err_str in line:
                self.last_error = line.rstrip()
                if not self.is_password_invalid.is_set() and invalid_password_str in line:
                    self.is_password_invalid.set()
                    log("ERROR: Invalid wallet password", LEVEL_ERROR, self.proc_name)
                else:
                    log(self.last_error, LEVEL_ERROR, self.proc_name)
            elif m_height:
                log(line.rstrip(), LEVEL_INFO, self.proc_name)
            else:
                log(line.rstrip(), LEVEL_DEBUG, self.proc_name)
            
            if len(self.last_log_lines) > 1:
                self.last_log_lines.pop(0)
            self.last_log_lines.append(line[:120])
            
        if not self.proc.stdout.closed:
            self.proc.stdout.close()    

    def is_ready(self):
        return self._ready.is_set()
    
    def is_invalid_password(self):
        return self.is_password_invalid.is_set()
    
    def stop(self, force=False):
        if not force: self.rpc_request.stop_wallet()
        if self.is_proc_running():
            counter = 0
            while True:
                if self.is_proc_running():
                    if counter < 60:
                        sleep(1)
                        counter += 1
                    else:
                        self.proc.kill()
                        log("[%s] killed" % self.proc_name, LEVEL_INFO, self.proc_name)
                        break
                else:
                    break
        
        self._stopped = True
        self._ready = Event()
        self.block_height = 0
        self.is_password_invalid = Event()
        self.last_log_lines = []
        self.last_error = ""
        
        log("[%s] stopped" % self.proc_name, LEVEL_INFO, self.proc_name)        
        
