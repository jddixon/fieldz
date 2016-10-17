# ~/dev/py/fieldz/zoggeryProtoSpec.py

ZOGGERY_PROTO_SPEC = """
protocol org.xlattice.zoggery

message logEntry:
 timestamp  fuInt32
 nodeID     fBytes20
 key        fBytes20
 length     vuInt32
 by         lString
 path       lString
"""
