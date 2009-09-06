#!/usr/bin/python
"""
Wrapper around djape to allow it to be bound to a specific
IP address - in production, we want it to only accept 
requests from localhost.
"""

import sys, os
sys.path.append(
    os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        'djape'
    )
)
import cpserv

from djape.server.application import Application
import wsgiwapi

if __name__ == '__main__':
    import sys
    server = wsgiwapi.make_server(
        Application(), ('0.0.0.0', 9876)
    )
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

