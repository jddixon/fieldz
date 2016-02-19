#!/usr/bin/python3

# ~/dev/py/fieldz/testProtoSpec.py

##############################################
# XXX WARNING: ACTUAL ROUND TRIPS ARE DISABLED
##############################################

import time, unittest
from io import StringIO

# from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
import fieldz.fieldTypes    as F
import fieldz.msgSpec       as M
import fieldz.typed         as T
import fieldz.reg           as R

from fieldz import reg

# PROTOCOLS ---------------------------------------------------------
from simpleProtocol         import SIMPLE_PROTOCOL
from zoggeryProtoSpec       import ZOGGERY_PROTO_SPEC
from nestedEnumProtoSpec    import NESTED_ENUM_PROTO_SPEC
from nestedMsgsProtoSpec    import NESTED_MSGS_PROTO_SPEC

# rng = SimpleRNG( time.time() )

# TESTS -------------------------------------------------------------
class TestProtoSpec (unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    # actual unit tests #############################################

    def testMaps(self):
        maxNdx  = F.maxNdx
        maxName = F.asStr(maxNdx)
        self.assertEqual('fBytes32', maxName)

    def testEnum(self):
        """
        A not very useful enum, limited to mapping a fixed list of
        names into a zero-based sequence of integers.
        """

        # XXX should test null or empty lists, ill-formed names
        name  = 'george'
        pairs = [('abc', 3), ('def', 5), ('ghi', 7)]
        enum  = M.EnumSpec.create(name, pairs)
        # self.assertEqual( ','.join(pairs), enum.__repr__())
        self.assertEqual( 3, enum.value('abc'))
        self.assertEqual( 5, enum.value('def'))
        self.assertEqual( 7, enum.value('ghi'))

    def doFieldTest(self, msgReg, name, fType, quantifier=M.Q_REQUIRED,
                                                fieldNbr=0, default=None):
        # XXX Defaults are ignore for now.
        f = M.FieldSpec(msgReg, name, fType, quantifier, fieldNbr, default)

        self.assertEqual(name,         f.name)
        self.assertEqual(fType,        f.fTypeNdx)
        self.assertEqual(quantifier,   f.quantifier)
        self.assertEqual(fieldNbr,     f.fieldNbr)
        if default is not None:
            self.assertEqual(default,  f.default)

        expectedRepr = "%s %s%s @%d \n" % (
                            name, f.fTypeName, M.qName(quantifier), fieldNbr)
        # DEFAULTS NOT SUPPORTED
        self.assertEqual(expectedRepr, f.__repr__())

    def testsQuantifiers(self):
        qName = M.qName
        self.assertEqual('',  qName(M.Q_REQUIRED))
        self.assertEqual('?', qName(M.Q_OPTIONAL))
        self.assertEqual('*', qName(M.Q_STAR))
        self.assertEqual('+', qName(M.Q_PLUS))

    def testFieldSpec(self):
        protoName = 'org.xlattice.upax'
        nodeReg   = R.NodeReg()
        protoReg  = R.ProtoReg(protoName, nodeReg)
        msgReg    = R.MsgReg(protoReg)

        # default is not implemented yet
        self.doFieldTest(msgReg,  'foo',    F._V_UINT32,  M.Q_REQUIRED,   9)
        self.doFieldTest(msgReg,  'bar',    F._V_SINT32,  M.Q_STAR,      17)
        self.doFieldTest(msgReg,  'nodeID', F._F_BYTES20, M.Q_OPTIONAL,  92)
        self.doFieldTest(msgReg,  'tix',    F._V_BOOL,    M.Q_PLUS,     147)

    def testProtoSpec(self):
        """ this is in fact the current spec for a log entry """
        protoName = 'org.xlattice.upax'
        nodeReg   = R.NodeReg()
        protoReg  = R.ProtoReg(protoName, nodeReg)
        msgReg    = R.MsgReg(protoReg)
        protoSpec = M.ProtoSpec(protoName, protoReg)
        self.assertEqual(protoName, protoSpec.name)

        msgName    = 'logEntry'
        # the enum is not used
        enum    = M.EnumSpec.create('Joe', [ \
                        ('oh', 92), ('hello', 47), ('there', 322) ,])
        fields  = [ \
                M.FieldSpec(msgReg,'timestamp', F._F_UINT32,  M.Q_REQUIRED, 0),
                M.FieldSpec(msgReg,'nodeID',    F._F_BYTES20, M.Q_REQUIRED, 1),
                M.FieldSpec(msgReg,'key',       F._F_BYTES20, M.Q_REQUIRED, 2),
                M.FieldSpec(msgReg,'length',    F._V_UINT32,  M.Q_REQUIRED, 3),
                M.FieldSpec(msgReg,'by',        F._L_STRING,  M.Q_REQUIRED, 4),
                M.FieldSpec(msgReg,'path',      F._L_STRING,  M.Q_REQUIRED, 5),
        ]
        msgSpec = M.MsgSpec(msgName, protoSpec, msgReg)
        self.assertEqual(msgName, msgSpec.name)
        for f in fields:
            msgSpec.addField(f)

        # protoSpec.addMsg(msgSpec)     # ALREADY DONE in __init__
        self.roundTripProtoSpecViaString(protoSpec)             # GEEP

    def roundTripProtoSpecViaString(self, m):
        """
        Convert a MsgSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        equal.
        """
        canonicalSpec = str(m.__repr__())
        # DEBUG
        print("### roundTrip: SPEC IN CANONICAL FORM:\n" + canonicalSpec)
        print("### END SPEC IN CANONICAL FORM #######")
        # END
        p = StringProtoSpecParser( StringIO(canonicalSpec) )
        clonedSpec   = p.parse()
        self.assertIsNone(clonedSpec.parent)    # created by default
        self.assertIsNotNone(clonedSpec.reg)

        # DEBUG
        cloneRepr = clonedSpec.__repr__()
        print("### CLONED SPEC IN CANONICAL FORM:\n" + cloneRepr)
        print("### END CLONED SPEC ##############")
        # END

        # crude tests of __eq__ AKA ==
        self.assertFalse( m == None        )
        self.assertTrue ( m == m           )

        # one way of saying it ------------------
        # XXX NEXT LINE FAILS
        self.assertTrue ( m.__eq__(clonedSpec)  )

        self.assertTrue ( clonedSpec.__eq__(m)  )
        # this is the same test -----------------
        self.assertTrue ( m == clonedSpec  )
        self.assertTrue ( clonedSpec == m  )

    def testParseAndWriteProtoSpec(self):
        data = StringIO(ZOGGERY_PROTO_SPEC)
        p    = StringProtoSpecParser(data)   # data should be file-like
        sOM  = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.ProtoSpec))
        self.assertEqual( 'org.xlattice.zoggery', sOM.name )
        self.assertEqual(0, len(sOM.enums) )
        self.assertEqual(1, len(sOM.msgs) )
        self.assertEqual(0, len(sOM.seqs) )

        msgSpec = sOM.msgs[0]
        # XXX THIS SHOULD BE A LOOP, with no magic numbers
        self.assertEqual(msgSpec.fName(0),     'timestamp')
        self.assertEqual(msgSpec.fTypeName(0), 'fuInt32')
        self.assertEqual(msgSpec.fName(1),     'nodeID')
        self.assertEqual(msgSpec.fTypeName(1), 'fBytes20')
        self.assertEqual(msgSpec.fName(2),     'key')
        self.assertEqual(msgSpec.fTypeName(2), 'fBytes20')
        self.assertEqual(msgSpec.fName(3),     'length')
        self.assertEqual(msgSpec.fTypeName(3), 'vuInt32')
        self.assertEqual(msgSpec.fName(4),     'by')
        self.assertEqual(msgSpec.fTypeName(4), 'lString')
        self.assertEqual(msgSpec.fName(5),     'path')
        self.assertEqual(msgSpec.fTypeName(5), 'lString')      # GEEP

    def testNestedEnum(self):
        data = StringIO(NESTED_ENUM_PROTO_SPEC)
        p    = StringProtoSpecParser(data)   # data should be file-like
        sOM  = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.ProtoSpec))

        self.assertEqual( 'org.xlattice.zoggery.ne', sOM.name )
        self.assertEqual(1, len(sOM.msgs))
        msg = sOM.msgs[0]

        self.assertEqual( 'nestedEnums', msg.name )
        enums = msg.enums
        self.assertIsNotNone(enums)
        self.assertEqual(2, len(enums))

        fooEnum = enums[0]
        barEnum = enums[1]
        self.assertEqual( 'Foo', fooEnum.name)
        self.assertEqual( 'Bar', barEnum.name )

        self.assertEqual(2, len(fooEnum) )
        self.assertEqual(3, len(barEnum) )

        aPair = fooEnum[0]
        self.assertEqual('a',  aPair.symbol)
        self.assertEqual(1,    aPair.value)

        bPair = fooEnum[1]
        self.assertEqual('b',  bPair.symbol)
        self.assertEqual(2,    bPair.value)

        cPair = barEnum[0]
        self.assertEqual('c',  cPair.symbol)
        self.assertEqual(3,    cPair.value)

        dPair = barEnum[1]
        self.assertEqual('d',  dPair.symbol)
        self.assertEqual(4,    dPair.value)

        ePair = barEnum[2]
        self.assertEqual('e',  ePair.symbol)
        self.assertEqual(5,    ePair.value)

#       self.roundTripProtoSpecViaString(sOM)       # GEEP

    def testNestedMsgs(self):
        """ XXX so far this is just testNestedEnum XXX """
        data = StringIO(NESTED_MSGS_PROTO_SPEC)
        p    = StringProtoSpecParser(data)   # data should be file-like
        sOM  = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.ProtoSpec))

        self.assertEqual( 'org.xlattice.zoggery.nm', sOM.name )
        self.assertEqual(1, len(sOM.msgs))
        msg = sOM.msgs[0]

        self.assertEqual( 'nestedMsgs', msg.name )
        enums = msg.enums
        self.assertIsNotNone(enums)
        self.assertEqual(2, len(enums))

        fooEnum = enums[0]
        barEnum = enums[1]
        self.assertEqual( 'Foo', fooEnum.name)
        self.assertEqual( 'Bar', barEnum.name )

        self.assertEqual(2, len(fooEnum) )
        self.assertEqual(3, len(barEnum) )

        aPair = fooEnum[0]
        self.assertEqual('a',  aPair.symbol)
        self.assertEqual(1,    aPair.value)

        bPair = fooEnum[1]
        self.assertEqual('b',  bPair.symbol)
        self.assertEqual(2,    bPair.value)

        cPair = barEnum[0]
        self.assertEqual('c',  cPair.symbol)
        self.assertEqual(3,    cPair.value)

        dPair = barEnum[1]
        self.assertEqual('d',  dPair.symbol)
        self.assertEqual(4,    dPair.value)

        ePair = barEnum[2]
        self.assertEqual('e',  ePair.symbol)
        self.assertEqual(5,    ePair.value)

        self.roundTripProtoSpecViaString(sOM) 

if __name__ == '__main__':
    unittest.main()
