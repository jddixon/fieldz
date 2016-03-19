# ~/dev/py/fieldz/bigTest.py

BIG_TEST = u"""
protocol org.xlattice.fieldz.test.bigProto

# This should exercise all combinations of the 20 field types, with
# the four quantifiers.  The first category (required fields) have no
# explicit field numbers.  In the other categories field numbers are
# specified.

message bigTestMsg:
 # required fields, unnumbered
 vBoolReqField      vBool          # @0 implied
 vEnumReqField      vEnum          # @1 implied
 vuInt32ReqField    vuInt32        # and so forth
 vuInt64ReqField    vuInt64
 vsInt32ReqField    vsInt32
 vsInt64ReqField    vsInt64
 #vuInt32ReqField   vuInt32
 #vuInt64ReqField   vuInt64
 fsInt32ReqField    fsInt32
 fuInt32ReqField    fuInt32
 fFloatReqField     fFloat
 fsInt64ReqField    fsInt64
 fuInt64ReqField    fuInt64
 fDoubleReqField    fDouble
 lStringReqField    lString
 lBytesReqField     lBytes
 lMsgReqField       lMsg
 fBytes16ReqField   fBytes16
 fBytes20ReqField   fBytes20
 fBytes32ReqField   fBytes32

 # optional fields, numbered
 # XXX FAILS (can't handle space(s) before quantifier
 #vBoolOptField       vBool ?   @ 100
 vBoolOptField      vBool?    @100
 vEnumOptField      vEnum?    @101
 vuInt32OptField    vuInt32?  @102
 vuInt64OptField    vuInt64?  @103
 vsInt32OptField    vsInt32?  @104
 vsInt64OptField    vsInt64?  @105
 #vuInt32OptField   vuInt32?  @106
 #vuInt64OptField   vuInt64?  @107
 fsInt32OptField    fsInt32?  @108
 fuInt32OptField    fuInt32?  @109
 fFloatOptField     fFloat?   @110
 fsInt64OptField    fsInt64?  @111
 fuInt64OptField    fuInt64?  @112
 fDoubleOptField    fDouble?  @113
 lStringOptField    lString?  @114
 lBytesOptField     lBytes?   @115
 lMsgOptField       lMsg?     @116
 fBytes16OptField   fBytes16? @117
 fBytes20OptField   fBytes20? @118
 fBytes32OptField   fBytes32? @119

 # optional/repeated (*) fields, numbered
 vBoolStarField     vBool*    @200
 vEnumStarField     vEnum*    @201
 vuInt32StarField   vuInt32*  @202
 vuInt64StarField   vuInt64*  @203
 vsInt32StarField   vsInt32*  @204
 vsInt64StarField   vsInt64*  @205
 #vuInt32StarField  vuInt32*  @206
 #vuInt64StarField  vuInt64*  @207
 fsInt32StarField   fsInt32*  @208
 fuInt32StarField   fuInt32*  @209
 fFloatStarField    fFloat*   @210
 fsInt64StarField   fsInt64*  @211
 fuInt64StarField   fuInt64*  @212
 fDoubleStarField   fDouble*  @213
 lStringStarField   lString*  @214
 lBytesStarField    lBytes*   @215
 lMsgStarField      lMsg*     @216
 fBytes16StarField  fBytes16* @217
 fBytes20StarField  fBytes20* @218
 fBytes32StarField  fBytes32* @219

 # required/repeated (+) fields, numbered
 vBoolPlusField     vBool+    @300
 vEnumPlusField     vEnum+    @301
 vuInt32PlusField   vuInt32+  @302
 vuInt64PlusField   vuInt64+  @303
 vsInt32PlusField   vsInt32+  @304
 vsInt64PlusField   vsInt64+  @305
 #vuInt32PlusField  vuInt32+  @306
 #vuInt64PlusField  vuInt64+  @307
 fsInt32PlusField   fsInt32+  @308
 fuInt32PlusField   fuInt32+  @309
 fFloatPlusField    fFloat+   @310
 fsInt64PlusField   fsInt64+  @311
 fuInt64PlusField   fuInt64+  @312
 fDoublePlusField   fDouble+  @313
 lStringPlusField   lString+  @314
 lBytesPlusField    lBytes+   @315
 lMsgPlusField      lMsg+     @316
 fBytes16PlusField  fBytes16+ @317
 fBytes20PlusField  fBytes20+ @318
 fBytes32PlusField  fBytes32+ @319

"""
