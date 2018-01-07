# ~/dev/py/fieldz/zoggeryProtoSpec.py

"""
Message spec for a simplifid log entry.
"""

ZOGGERY_PROTO_SPEC = """
protocol org.xlattice.zoggery

message logEntry:
 timestamp  fuint32
 nodeID     fbytes20
 key        fbytes20
 length     vuint32
 by         lstring
 path       lstring
"""
