#!/usr/bin/python

# testMsgSpec.py
import time, unittest
from io     import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringMsgSpecParser

import fieldz.fieldTypes    as F
import fieldz.msgSpec       as M
import fieldz.typed         as T
import fieldz.reg           as R

LOG_ENTRY_MSG_SPEC = """
# protocol org.xlattice.zoggery
message logEntry:
 timestamp   fuInt32
 nodeID      fBytes20
 key         fBytes20
 length      vuInt32
 by          lString
 path        lString
"""

MULTI_ENUM_MSG_SPEC = """
# protocol org.xlattice.zoggery
message multiEnum
 enum Foo
  a = 1
  b = 2

 enum Bar
  c = 3
  d = 4
  e = 5

 whatever    vuInt32?
 cantImagine vsInt32+
 # NEXT LINES FAIL
 xxx         Foo
 yyy         Bar

"""

class TestMsgSpec (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################
    def makeRegistries(self, protocol):
        nodeReg = R.NodeReg()
        protoReg= R.ProtoReg(protocol, nodeReg)
        msgReg  = R.MsgReg(protoReg)
        return (nodeReg, protoReg, msgReg)
    
    # actual unit tests #############################################

    def testMaps(self):
        maxNdx  = F.maxNdx
        maxName = F.asStr(maxNdx)
        self.assertEquals('fBytes32', maxName)

    def testEnum(self):
        """ 
        A not very useful enum, limited to mapping a fixed list of
        names into a zero-based sequence of integers.
        """

        # XXX should test null or empty lists, ill-formed names
        name  = 'george'
        pairs = [('abc', 3), ('def', 5), ('ghi', 7)]
        enum  = M.EnumSpec.create(name, pairs)
        # self.assertEquals( ','.join(pairs), enum.__repr__())
        self.assertEquals( 3, enum.value('abc'))
        self.assertEquals( 5, enum.value('def'))
        self.assertEquals( 7, enum.value('ghi'))

    def doFieldTest(self, name, fType, quantifier=M.Q_REQUIRED, 
                                                fieldNbr=0, default=None):
        nodeReg, protoReg, msgReg = self.makeRegistries(
                                'org.xlattice.fieldz.tes.fieldSpec')
        
        # XXX Defaults are ignore for now.
        f = M.FieldSpec(msgReg, name, fType, quantifier, fieldNbr, default)

        self.assertEquals(name,         f.name)
        self.assertEquals(fType,        f.fTypeNdx)
        self.assertEquals(quantifier,   f.quantifier)
        self.assertEquals(fieldNbr,     f.fieldNbr)
        if default is not None:
            self.assertEquals(default,  f.default)

        expectedRepr = "%s %s%s @%d \n" % (
                            name, f.fTypeName, M.qName(quantifier), fieldNbr)
        # DEFAULTS NOT SUPPORTED
        self.assertEquals(expectedRepr, f.__repr__())

    def testsQuantifiers(self):
        qName = M.qName
        self.assertEquals('',  qName(M.Q_REQUIRED))
        self.assertEquals('?', qName(M.Q_OPTIONAL))
        self.assertEquals('*', qName(M.Q_STAR))
        self.assertEquals('+', qName(M.Q_PLUS))

    def testFieldSpec(self):
        nodeReg, protoReg, msgReg = self.makeRegistries(
                                'org.xlattice.fieldz.tes.fieldSpec')
        # default is not implemented yet
        self.doFieldTest('foo',    F._V_UINT32,  M.Q_REQUIRED,   9) 
        self.doFieldTest('bar',    F._V_SINT32,  M.Q_STAR,      17)    
        self.doFieldTest('nodeID', F._F_BYTES20, M.Q_OPTIONAL,  92)
        self.doFieldTest('tix',    F._V_BOOL,    M.Q_PLUS,     147)

    def roundTripMsgSpecViaString(self, m, protocol):
        """ 
        Convert a MsgSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        equal.
        """
        #canonicalSpec = m.__repr__()
        canonicalSpec = str(m.__repr__())
        # DEBUG
        print("CANONICAL SPEC:\n" + canonicalSpec)
        # END

        nodeReg     = R.NodeReg()
        protoReg    = R.ProtoReg(protocol, nodeReg)
        p = StringMsgSpecParser( StringIO(canonicalSpec) )
        
        # XXX FAILS: protoSpec has ill-formed protocol line
        clonedSpec  = p.parse()
        
        self.assertIsNotNone(clonedSpec)
        # DEBUG =======================
        print('CLONED SPEC:\n' + clonedSpec.__repr__())
        # END =========================
        # crude tests of __eq__ AKA ==
        self.assertFalse( m == None        )
        self.assertTrue ( m == m           )

        # one way of saying it ------------------
        self.assertTrue ( m.__eq__(clonedSpec)  )
        self.assertTrue ( clonedSpec.__eq__(m)  )
        # this is the same test -----------------
        self.assertTrue ( m == clonedSpec  )
        self.assertTrue ( clonedSpec == m  )                # FOO

    def testMsgSpec(self):
        """ this is in fact the current spec for a log entry """
        protocol    = 'org.xlattice.upax'
        nodeReg, protoReg, msgReg = self.makeRegistries(protocol)

        # the enum is not used 
        enum    = M.EnumSpec.create('Joe', [ \
                        ('oh', 92), ('hello', 47), ('there', 322) ,])
        fields  = [ \
                M.FieldSpec(msgReg,'timestamp',F._F_UINT32,   M.Q_REQUIRED, 0),
                M.FieldSpec(msgReg,'nodeID',   F._F_BYTES20,  M.Q_REQUIRED, 1),
                M.FieldSpec(msgReg,'key',      F._F_BYTES20,  M.Q_REQUIRED, 2),
                M.FieldSpec(msgReg,'by',       F._L_STRING,   M.Q_REQUIRED, 3),
                M.FieldSpec(msgReg,'path',     F._L_STRING,   M.Q_REQUIRED, 4),
        ]
        name    = 'logEntry'
        msgSpec = M.MsgSpec(name, protoReg, msgReg)
        for f in fields:
            msgSpec.addField(f)
        msgSpec.addEnum(enum)

        self.assertEquals(name, msgSpec.name)

        # XXX DEPRECATED
        self.assertEquals(len(fields), len(msgSpec)) 
        for i in range(len(msgSpec)):
            self.assertEquals(fields[i].name,       msgSpec.fName(i))
            self.assertEquals(fields[i].fTypeName,  msgSpec.fTypeName(i))
        # END DEPRECATED

        self.assertEquals(len(fields), len(msgSpec)) 
        i = 0
        for field in msgSpec:
            self.assertEquals(fields[i].name,       field.name)
            self.assertEquals(fields[i].fTypeNdx,   field.fTypeNdx)
            i += 1

        self.roundTripMsgSpecViaString(msgSpec, protocol)                 # BAZ

    def testParseAndWriteMsgSpec(self):
        data = StringIO(LOG_ENTRY_MSG_SPEC)
        p    = StringMsgSpecParser(data)   # data should be file-like
        sOM  = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.MsgSpec))

        self.assertEquals( 'logEntry', sOM.name )

        # XXX THIS SHOULD BE A LOOP, with no magic numbers
        self.assertEquals(sOM.fName(0),     'timestamp')   
        self.assertEquals(sOM.fTypeName(0), 'fuInt32')
        self.assertEquals(sOM.fName(1),     'nodeID')
        self.assertEquals(sOM.fTypeName(1), 'fBytes20')
        self.assertEquals(sOM.fName(2),     'key')
        self.assertEquals(sOM.fTypeName(2), 'fBytes20')
        self.assertEquals(sOM.fName(3),     'length')
        self.assertEquals(sOM.fTypeName(3), 'vuInt32')
        self.assertEquals(sOM.fName(4),     'by')
        self.assertEquals(sOM.fTypeName(4), 'lString')
        self.assertEquals(sOM.fName(5),     'path')
        self.assertEquals(sOM.fTypeName(5), 'lString')          # BAR

    def testMultiEnum(self):
        protocol = 'org.xlattice.fieldz.test.multiEnum'

        data = StringIO(MULTI_ENUM_MSG_SPEC)
        p    = StringMsgSpecParser(data)   # data should be file-like
        sOM  = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.MsgSpec))

        # self.assertEquals( 'org.xlattice.zoggery', sOM.protocol )
        self.assertEquals( 'multiEnum', sOM.name )

        enums = sOM.enums
        self.assertIsNotNone(enums)
        self.assertEquals(2, len(enums))

        fooEnum = enums[0] 
        barEnum = enums[1] 
        self.assertEquals( 'Foo', fooEnum.name)
        self.assertEquals( 'Bar', barEnum.name )
        
        self.assertEquals(2, len(fooEnum) )
        self.assertEquals(3, len(barEnum) )

        aPair = fooEnum[0]
        self.assertEquals('a',  aPair.symbol)
        self.assertEquals(1,    aPair.value)

        bPair = fooEnum[1]
        self.assertEquals('b',  bPair.symbol)
        self.assertEquals(2,    bPair.value)

        cPair = barEnum[0]
        self.assertEquals('c',  cPair.symbol)
        self.assertEquals(3,    cPair.value)

        dPair = barEnum[1]
        self.assertEquals('d',  dPair.symbol)
        self.assertEquals(4,    dPair.value)

        ePair = barEnum[2]
        self.assertEquals('e',  ePair.symbol)
        self.assertEquals(5,    ePair.value)

        self.roundTripMsgSpecViaString(sOM, protocol)             # GEEP

if __name__ == '__main__':
    unittest.main()
