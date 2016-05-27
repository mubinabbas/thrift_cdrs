#!/usr/bin/env python2

import time
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import sys

sys.path.append("./thrift_stub_dir")
from ssp import ttypes


fd = file("calls-thrift.bin")
t = TTransport.TFileObjectTransport(fd)
p = TBinaryProtocol.TBinaryProtocolAccelerated(t)
while True:
    obj = ttypes.Calls()
    try:
        obj.read(p)
        print("%s, %s, %s, %s, %s" % (obj.i_call, obj.cli, obj.cld, time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(obj.setup_time)), obj.call_id))
    except EOFError:
        break

