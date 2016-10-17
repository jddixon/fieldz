# ~/dev/py/fieldz/littleBigTest.py

LITTLE_BIG_PROTO_SPEC = """
protocol org.xlattice.fieldz.test.littleBigProto

# This has been hacked down from bigTest.py by eliminating field types
# that we can't handle yet.

message bigTestMsg:
 # required fields, unnumbered
 vBoolReqField       vBool
 vEnumReqField       vEnum
 vuInt32ReqField     vuInt32
 vuInt64ReqField     vuInt64
 vsInt32ReqField     vsInt32
 vsInt64ReqField     vsInt64
 #vuInt32ReqField     vuInt32       # MAYBE NEVER
 #vuInt64ReqField     vuInt64       # --ditto--
 fsInt32ReqField     fsInt32
 fuInt32ReqField     fuInt32
 fFloatReqField      fFloat
 fsInt64ReqField     fsInt64
 fuInt64ReqField     fuInt64
 fDoubleReqField     fDouble
 lStringReqField     lString
 lBytesReqField      lBytes
 # lMsgReqField        lMsg         # NOT YET
 fBytes16ReqField    fBytes16
 fBytes20ReqField    fBytes20
 fBytes32ReqField    fBytes32

# Can't handle ANY optional (?), star (*), and plus (+) types.
"""
