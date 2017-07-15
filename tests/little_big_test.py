# ~/dev/py/fieldz/littleBigTest.py

"""
This has been hacked down from bigTest.py by eliminating field types
that we can't handle yet.
"""

LITTLE_BIG_PROTO_SPEC = """
protocol org.xlattice.fieldz.test.littleBigProto

message bigTestMsg:
 # required fields, unnumbered
 vBoolReqField       vbool
 vEnumReqField       venum
 vuInt32ReqField     vuint32
 vuInt64ReqField     vuint64
 vsInt32ReqField     vsint32
 vsInt64ReqField     vsint64
 #vuInt32ReqField     vuint32       # MAYBE NEVER
 #vuInt64ReqField     vuint64       # --ditto--
 fsInt32ReqField     fsint32
 fuInt32ReqField     fuint32
 fFloatReqField      ffloat
 fsInt64ReqField     fsint64
 fuInt64ReqField     fuint64
 fDoubleReqField     fdouble
 lStringReqField     lstring
 lBytesReqField      lbytes
 #lMsgReqField        lmsg         # NOT YET
 fBytes16ReqField    fbytes16
 fBytes20ReqField    fbytes20
 fBytes32ReqField    fbytes32

# Can't handle ANY optional (?), star (*), and plus (+) types.
"""
