# ~/dev/py/fieldz/nestedEnumProtoSpec.py

""" Nested enum protocol spec, to be used in testing. """

NESTED_ENUM_PROTO_SPEC = """
protocol org.xlattice.zoggery.ne

enum Baz                    # goes into ProtoSpec dictionary
 x = 42
 y = 43

message nestedEnums
 enum Foo                   # goes into MsgSpec dictionary
  a = 1
  b = 2

 enum Bar
  c = 3
  d = 4
  e = 5

 whatever    vuint32?
 cantImagine vsint32+
 # these symbols implemented as varints
 zzz         Baz                        # protoSpec level
 xxx         Foo                        # msgSpec level
 yyy         Bar                        # ditto
"""
