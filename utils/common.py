#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
Misc utility classes/functions for application
'''

import os, sys, string

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    

class DummyStream:
    ''' dummyStream behaves like a stream but does nothing. '''
    def __init__(self): pass
    def write(self,data): pass
    def read(self,data): pass
    def flush(self): pass
    def close(self): pass
    
def getAppPath():
    '''Get the path to this script no matter how it's run.'''
    #Determine if the application is a py/pyw or a frozen exe.
    if hasattr(sys, 'frozen'):
        # If run from exe
        dir_path = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
    elif '__file__' in locals():
        # If run from py
        dir_path = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
    else:
        # If run from command line
        #dir_path = sys.path[0]
        dir_path = os.getcwdu()
    return dir_path

    
def getHomeDir():
    if sys.platform == 'win32':
        import winpaths
        homedir = winpaths.get_common_appdata() # = e.g 'C:\ProgramData'
    else:
        homedir = os.path.expanduser("~")
    return homedir

def getSockDir():
    if sys.platform == 'win32':
        import winpaths
        homedir = winpaths.get_appdata() # = e.g 'C:\ProgramData'
    else:
        homedir = os.path.expanduser("~")
    return homedir
    
def makeDir(d):
    if not os.path.exists(d):
        os.makedirs(d)
    return d

def ensureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    return f

def _xorData(data):
    """Xor Method, Take a data Xor all bytes and return"""
    data = [chr(ord(c) ^ 10) for c in data]
    return string.join(data, '')

def readFile(path, offset=0, size=-1, xor_data=False):
    """Read specified block from file, using the given size and offset"""
    fd = open(path, 'rb')
    fd.seek(offset)
    data = fd.read(size)
    fd.close()
    return _xorData(data) if xor_data else data
    
def writeFile(path, buf, offset=0, xor_data=False):
    """Write specified block on file at the given offset"""
    if xor_data:
        buf = _xorData(buf)
    fd = open(path, 'wb')
    fd.seek(offset)
    fd.write(buf)
    fd.close()
    return len(buf)

def print_money(amount):
    try:
        amount = int(amount)
    except:
        raise Exception("Error parsing amount. Money amount must be an integer.")
    return "%s <small>RYO</small>" % ("{:,.9f}".format(amount/1000000000.))

def print_money2(amount):
    try:
        amount = int(amount)
    except:
        raise Exception("Error parsing amount. Money amount must be an integer.")
    return "%s" % ("{:,.9f}".format(amount/1000000000.))

"""
https://stackoverflow.com/a/13790289
"""
def tail( f, lines=20 ):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return all_read_text.splitlines()[-total_lines_wanted:]
    
