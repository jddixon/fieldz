# ~/dev/py/fieldz/nestedMsgsProtoSpec.py

NESTED_MSGS_PROTO_SPEC = """
protocol org.xlattice.zoggery.nm

enum Baz                    # goes into ProtoSpec dictionary
 x = 42
 y = 43

message nestedMsgs
 enum Foo                   # goes into MsgSpec dictionary
  a = 1
  b = 2

 enum Bar
  c = 3
  d = 4
  e = 5

 message A
  message B
   message C
    cField1 vuint32
    cField2 vuint32
   bField1   Baz
   bField2   Foo
   bField3   C
  aField1    Bar            # at parent msg level enum
  aField2    Baz            # the proto level enum
  aField3    B              # the embedded msg
 whatever    vuint32?
 cantImagine vsint32+
 # these symbols implemented as varints
 zzz         Baz                        # protoSpec level
 xxx         Foo                        # msgSpec level
 yyy         Bar                        # ditto
"""
