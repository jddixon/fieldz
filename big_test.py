# ~/dev/py/fieldz/bigTest.py

"""
This should exercise all combinations of the 20 field types, with
the four quantifiers.  The first category (required fields) have no
explicit field numbers.  In the other categories field numbers are
specified.
"""

BIG_TEST = u"""
protocol org.xlattice.fieldz.test.bigProto

message bigTestMsg:
 # required fields, unnumbered
 vBoolReqField      vbool          # @0 implied
 vEnumReqField      venum          # @1 implied
 vuInt32ReqField    vuint32        # and so forth
 vuInt64ReqField    vuint64
 vsInt32ReqField    vsint32
 vsInt64ReqField    vsint64
 #vuInt32ReqField   vuint32
 #vuInt64ReqField   vuint64
 fsInt32ReqField    fsint32
 fuInt32ReqField    fuint32
 fFloatReqField     ffloat
 fsInt64ReqField    fsint64
 fuInt64ReqField    fuint64
 fDoubleReqField    fdouble
 lStringReqField    lstring
 lBytesReqField     lbytes
 lMsgReqField       lmsg
 fBytes16ReqField   fbytes16
 fBytes20ReqField   fbytes20
 fBytes32ReqField   fbytes32

 # optional fields, numbered
 # XXX FAILS (can't handle space(s) before quantifier)
 #vBoolOptField       vbool ?   @ 100
 vBoolOptField      vbool?    @100
 vEnumOptField      venum?    @101
 vuInt32OptField    vuint32?  @102
 vuInt64OptField    vuint64?  @103
 vsInt32OptField    vsint32?  @104
 vsInt64OptField    vsint64?  @105
 #vuInt32OptField   vuint32?  @106
 #vuInt64OptField   vuint64?  @107
 fsInt32OptField    fsint32?  @108
 fuInt32OptField    fuint32?  @109
 fFloatOptField     ffloat?   @110
 fsInt64OptField    fsint64?  @111
 fuInt64OptField    fuint64?  @112
 fDoubleOptField    fdouble?  @113
 lStringOptField    lstring?  @114
 lBytesOptField     lbytes?   @115
 lMsgOptField       lmsg?     @116
 fBytes16OptField   fbytes16? @117
 fBytes20OptField   fbytes20? @118
 fBytes32OptField   fbytes32? @119

 # optional/repeated (*) fields, numbered
 vBoolStarField     vbool*    @200
 vEnumStarField     venum*    @201
 vuInt32StarField   vuint32*  @202
 vuInt64StarField   vuint64*  @203
 vsInt32StarField   vsint32*  @204
 vsInt64StarField   vsint64*  @205
 #vuInt32StarField  vuint32*  @206
 #vuInt64StarField  vuint64*  @207
 fsInt32StarField   fsint32*  @208
 fuInt32StarField   fuint32*  @209
 fFloatStarField    ffloat*   @210
 fsInt64StarField   fsint64*  @211
 fuInt64StarField   fuint64*  @212
 fDoubleStarField   fdouble*  @213
 lStringStarField   lstring*  @214
 lBytesStarField    lbytes*   @215
 lMsgStarField      lmsg*     @216
 fBytes16StarField  fbytes16* @217
 fBytes20StarField  fbytes20* @218
 fBytes32StarField  fbytes32* @219

 # required/repeated (+) fields, numbered
 vBoolPlusField     vbool+    @300
 vEnumPlusField     venum+    @301
 vuInt32PlusField   vuint32+  @302
 vuInt64PlusField   vuint64+  @303
 vsInt32PlusField   vsint32+  @304
 vsInt64PlusField   vsint64+  @305
 #vuInt32PlusField  vuint32+  @306
 #vuInt64PlusField  vuint64+  @307
 fsInt32PlusField   fsint32+  @308
 fuInt32PlusField   fuint32+  @309
 fFloatPlusField    ffloat+   @310
 fsInt64PlusField   fsint64+  @311
 fuInt64PlusField   fuint64+  @312
 fDoublePlusField   fdouble+  @313
 lStringPlusField   lstring+  @314
 lBytesPlusField    lbytes+   @315
 lMsgPlusField      lmsg+     @316
 fBytes16PlusField  fbytes16+ @317
 fBytes20PlusField  fbytes20+ @318
 fBytes32PlusField  fbytes32+ @319

"""
