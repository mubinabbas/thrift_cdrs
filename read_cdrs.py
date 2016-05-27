#!/usr/bin/env python2

import time
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import sys

sys.path.append("./thrift_stub_dir")
from ssp import ttypes


fd = file("cdrs-thrift.bin")
t = TTransport.TFileObjectTransport(fd)
p = TBinaryProtocol.TBinaryProtocolAccelerated(t)
while True:
    obj = ttypes.Cdrs()
    try:
        obj.read(p)
        print("%s, %s, %s, %s, %s" % (obj.i_call, obj.cli_in, obj.cld_in, time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(obj.connect_time)), obj.remote_ip))
    except EOFError:
        break

