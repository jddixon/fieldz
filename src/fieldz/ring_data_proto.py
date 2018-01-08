# ~/dev/py/pzog/ringDataProto.py

"""
This represents the contents of a file containing data on several
(well, one or more) ring hosts.
"""

RING_DATA_PROTO_SPEC = """
protocol org.xlattice.pzog.ringData

message ringData:
 message hostInfo:
  hostName      lstring     # @0: alphanumeric only
  ipAddr        lstring     # @1: dotted quad; could be fuint32
  nodeID        fbytes32    # @2: so binary
  pubKey        lstring     # @3: or could be lbytes
  privateKey    lstring     # @4: ditto
 hosts          hostInfo+
"""
