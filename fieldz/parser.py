# fieldz/fieldz/parser.py

from fieldz.fieldTypes import FieldTypes as F, FieldStr as FS
import fieldz.reg as R
import fieldz.msgSpec as M

from fieldz.msgSpec import *

__all__ = [
    'StringSpecParser',
    'StringMsgSpecParser',
    'ParserError',
]

MAX_INDENT = 16


class ParserError(RuntimeError):
    pass


class QuantificationError(ParserError):
    pass


class StringSpecParser(object):

    __slots__ = ['_fd', '_nodeReg', '_reg', ]

    def __init__(self, fd, nodeReg=None):

        # DEBUG
        print('entering StringSpecParser')
        # END

        # XXX should die if fd not open
        self._fd = fd
        if nodeReg is None:
            nodeReg = R.NodeReg()
        self._nodeReg = nodeReg
        self._reg = R.ProtoReg(nodeReg)

    @property
    def nodeReg(self): return self._nodeReg

    @property
    def reg(self): return self._reg

    def getLine(self):
        while True:
            line = self._fd.readline()

            # The first condition never fails if fd is a file-like object
            # (from StringIO)
            if line is None or line == '':
                return None

            # strip off any comments
            s = line.partition('#')[0]

            # get rid of any trailing blanks
            line = s.rstrip()
            if line != '':
                return line

    def expectTokenCount(self, tokens, whatever, n):
        if len(tokens) != n:
            raise ParserError(
                "too many tokens in %s '%s'" %
                (whatever, tokens))

    # -- MsgSpec ----------------------------------------------------
    def expectMsgSpecName(self, line, indent='', step=' '):
        """ on a line beginning 'message ' """
        starter = indent + 'message '
        if not line or not line.startswith(starter):
            raise ParserError("badly formatted message name line '%s'" % line)

        line = line[len(starter):]
        words = line.split()
        self.expectTokenCount(words, 'message name', 1)
        name = words[0]
        if name[-1] == ':':
            name = name[:-1]
        validateSimpleName(name)
        # print "DEBUG: msgSpec name is '%s'" % str(name)
        return name

    def expectMsgSpec(self, parent, line, indent='', step=' '):
        name = self.expectMsgSpecName(line, indent, step)
        msgReg = R.MsgReg(parent.reg)
        print("EXPECT_MSG_SPEC: NAME = %s" % name)            # DEBUG
        thisMsg = MsgSpec(name, msgReg, parent)

        line = self.getLine()

        print("expectMsgSpec: COLLECTING ENUMS; line is '%s'" % line)
        line = self.acceptEnumSpecs(thisMsg, line, indent + step, step)

        # accept any MsgSpecs at the next indent level
        print("expectMsgSpec: COLLECTING NESTED MSGS; line is '%s'" % line)
        line = self.acceptMsgSpecs(thisMsg, line, indent + step, step)

        print("expectMsgSpec: COLLECTING FIELDS; line is '%s'" % line)
        line = self.expectFields(thisMsg, line, indent + step, indent)

        parent.reg.addMsg(thisMsg)  # NOT done in MsgSpec.__init__
        return line

    def expectMsgSpecs(self, parent, line, indent='', step=' '):
        """
        Expect one or more msgSpecs, hanging them off the parent.

        Must return the first line found which does not begin a
        msgSpec
        """
        line = self.expectMsgSpec(parent, line, indent, step)
        print("BACK FROM expectMsgSpec: line is '%s'" % line)

        # collect any other MsgSpec declarations present
        if line is not None and len(line.strip()) > 0:
            line = self.acceptMsgSpecs(parent, line, indent, step)
        return line

    def acceptMsgSpecs(self, parent, line, indent='', step=' '):
        """
        Accept zero or more msgSpecs, hanging them off the parent
        and creating a registry for each.

        Must return the first line found which does not begin a
        msgSpec
        """
        print("ENTERING acceptMsgSpecs: line is '%s'" % line)
        msgStarter = indent + 'message'
        while line.startswith(msgStarter):
            line = self.expectMsgSpec(parent, line, indent, step)
            if line is None or len(line.strip()) == 0:
                break
        print("LEAVING acceptMsgSpecs: line is '%s'" % line)
        return line

    # -- EnumPairSpec -----------------------------------------------
    def acceptEnumPair(self, line, indent='', step=' '):
        if not line.startswith(indent):
            # DEBUG
            # print "acceptEnumPair: line not correctly indented: %s" % line
            # END
            return None
        line = line[len(indent):]

        # XXX we are not strict about the indent
        line = line.strip()
        # syntax is simply A = N
        parts = line.partition('=')
        if (parts[1] is None):
            raise ParserError("expected = in enum pair: '%s'" % line)
        sym = parts[0].strip()
        val = parts[2].strip()
        return EnumPairSpec(sym, val)

    def expectEnum(self, parent, line, indent, step):
        # we know the line begins with INDENT + 'enum'.  This
        # should be followed by the enum's name, and then a sequence
        # of pairs at a deeper indent
        from_ = len(indent) + len('enum')
        s = line[from_:]
        # s should begin with one or more spaces, followed by one
        # simple name
        if s[0] != ' ':
            raise ParserError("can't find enum name in '%s'" % line)
        name = s.strip()
        validateSimpleName(name)
        pairs = []
        line = self.getLine()          # we require at least one pair
        pair = self.acceptEnumPair(line, indent + step, step)
        if pair is None:
            raise ParserError("expected enum pair, found '%s'" % line)
        pairs.append(pair)

        # we have one pair, let's see if there are any more
        line = self.getLine()
        pair = self.acceptEnumPair(line, indent + step, step)
        while pair is not None:
            pairs.append(pair)
            line = self.getLine()
            pair = self.acceptEnumPair(line, indent + step, step)
        eSpec = EnumSpec(name, pairs)

        # XXX we need to verify that the enum's name is not already
        # in us; simplest thing to do is to have addEnum() verify
        # this,
        parent.addEnum(eSpec)           # parent is ProtoSpec or MsgSpec
        print("DEBUG expectEnum: adding %s to parent registry" % eSpec.name)
        parent.reg.addEnum(eSpec)
        return line

    def acceptEnumSpecs(self, parent, line, indent='', step=' '):
        """
        Accept and return any enums at the specified indent.  Return
        the first line at the wrong indent or not matching the enum
        syntax.
        """
        enumStart = indent + 'enum'

        while line and line.startswith(enumStart):
            line = self.expectEnum(parent, line, indent, step)

        # DEBUG
#       print "acceptEnumSpecs returning '%s'" % line
        # END

        return line

    # -- FieldSpec --------------------------------------------------
    # def expectField(self, nextFieldNbr, line, indent, step):
    def expectField(self, msgSpec, line, indent, step):
        if not line.startswith(indent):
            raise ParseError("wrong indent for field declaration: '%s'" % line)

        # DEBUG
        print("expectField: line = '%s'" % line)
        # END

        line = line[len(indent):]

        # from here we are very sloppy about the indent

        # accept NAME FTYPE(Q)? (@N)? (=DEFAULT)?

        words = line.split()
        wordCount = len(words)

        # DEBUG
        print("             found %d tokens: %s" % (wordCount, words))
        # END

        if wordCount < 2:
            raise ParserError("too few tokens in field def '%s'" % line)
        if wordCount > 5:
            raise ParserError("too many tokens in field def '%s'" % line)

        # -- field name -------------------------
        fName = words[0]
        validateSimpleName(fName)

        # -- quantifier -------------------------
        q = words[1][-1]
        if q == '?' or q == '*' or q == '+':
            words[1] = words[1][:-1]
            if q == '?':
                quantifier = Q_OPTIONAL
            elif q == '*':
                quantifier = Q_STAR
            else:
                quantifier = Q_PLUS
        else:
            quantifier = Q_REQUIRED

        # -- field type --------------------------
        typeName = words[1]
        validateDottedName(typeName)
        fType = None

        # DEBUG ###
        print("             field '%s' type '%s' quant %d" % (
            fName, typeName, quantifier))
        # END #####

        # first check against list of names of basic field types
        if FS().ndx(typeName):
            fType = FS().ndx(typeName)

        if fType is None:
            # check at the message level
            fType = msgSpec.reg.name2RegID(typeName)

        if fType is None:
            print("DEBUG fType for '%s' not found at message level" % typeName)
            # ask the parent to resolve
            fType = msgSpec.parent.reg.name2RegID(typeName)

        if fType is None:
            print("DEBUG fType for '%s' not found in parent" % typeName)
            raise ParserError("can't identify type name in '%s'" % line)

        # -- field number -----------------------
        fieldNbr = -1
        if wordCount > 2:
            if words[2].startswith('@'):
                fieldNbr = int(words[2][1:])    # could use some validation
#               if fieldNbr < nextFieldNbr:
#                   raise ValueError('field number <= last field number')

        # -- default ----------------------------
        # XXX STUB - NOT IMPLEMENTED YET

        msgSpec.addField(
            FieldSpec(msgSpec.reg, fName, fType, quantifier, fieldNbr))

    def expectFields(self, msgSpec, line, indent='', step=' '):
        # they get appended to fields; there must be at least one
        if line is None or line == '':
            raise ParserError('no fields found')

        # get the required first field declaration
        print("BRANCH TO expectField(0)")
        self.expectField(msgSpec, line, indent, step)
        # DEBUG
        print("BACK FROM expectField(0)")
        k = 1
        # END

        # DROPPING THIS: let MsgSpec constructor handle automatic
        # assignment of field numbers
        # nextFieldNbr = fields[0].fieldNbr + 1

        # get any other field declarations
        line = self.getLine()
        while line is not None and line != '':
            if not line.startswith(indent):
                print("DEBUG: NOT A FIELD DECL: '%s'" % line)
                break
            print("BRANCH TO expectField(%u)" % k)
            #fields.append( self.expectField(nextFieldNbr, line, indent, step) )
            self.expectField(msgSpec, line, indent, step)
            print("BACK FROM expectField(%u)" % k)
            k = k + 1
            # nextFieldNbr = fields[0].fieldNbr + 1
            line = self.getLine()
        return line

    # OVERRIDE THIS to change fuctionality --------------------------
    def parse(self):
        raise NotImplementedError('StringSpecParser.parse()')


class StringMsgSpecParser(StringSpecParser):
    """
    Reads a human-readable MsgSpec (a *.msgSpec file) to produce a
    MsgSpec object model, which is a MsgSpec with FieldSpecs and EnumSpecs
    dangling off of it.
    """

    def __init__(self, fd, nodeReg=None):
        super(StringMsgSpecParser, self).__init__(fd, nodeReg)
        protocol = 'org.xlattice.fieldz.test'

        # these are dummies
        self.parentReg = R.ProtoReg(protocol, self._nodeReg)
        self.parent = M.ProtoSpec(protocol, self.parentReg)

    def parse(self):
        # DEBUG
        print("entering StringMsgSpecParser.parse()")
        # END
        line = self.getLine()
        msgReg = R.MsgReg(self.parentReg)
        line = self.expectMsgSpec(self.parent, line)

        # DEBUG
        for regID in self.parentReg._entries:  # .keys():
            print("ENTRY: regID %u, name %s" % (regID,
                                                self.parentReg._entries[regID]))
        # END

        p = self.parent

        # the parent is a dummy ProtoSpec
        # DEBUG
        print("parse(): parent is a ", type(self.parent))
        if p is None:
            print("    parent field is None")
        elif p._msgs is None:
            print("    parent._msgs is None")                   # SEEN`
        else:
            print("    parent has %d msgs" % len(p._msgs))
        # END

        return p._msgs[0]


class StringProtoSpecParser(StringSpecParser):
    """
    Reads a human-readable ProtoSpec (a *.xlgo file) to produce a
    ProtoSpec object model, which is a ProtoSpec with FieldSpecs and EnumSpecs
    dangling off of it.
    """

    def __init__(self, fd, nodeReg=None):
        super(StringProtoSpecParser, self).__init__(fd, nodeReg)
        # DEBUG
        print("entering StringProtoSpecParser.__init__")
        # END
        self._protoName = None
        self._seqs = []

    # -- protocol line ----------------------------------------------
    def expectProtoName(self, indent='', step=' '):
        line = self.getLine()
        if indent != '' and not line.startswith(indent):
            raise ParseException("missing indent on protocol line '%s'" % line)

        # from here we ignore any indentation
        words = line.split()
        self.expectTokenCount(words, 'protocol', 2)
        if words[0] == 'protocol':
            validateDottedName(words[1])
            return words[1]
            print("DEBUG: protocol is '%s'" % str(self._protocol))
        else:
            raise ParserError("expected protocol line, found '%s'" % line)

    # -- seqSpecs ---------------------------------------------------
    def acceptSeqSpecs(self, protoSpec, line, indent='', step=' '):
        # XXX STUB XXX
        pass

    def parse(self):
        # DEBUG
        print("entering StringProtoSpecParser.parse()")
        # END

        # EnumPairSpecs, EnumSpecs, and SeqSpecs contain no recursive
        # elements are so are used directly
        class MsgSpecObj(object):
            pass

        protoName = self.expectProtoName()
        protoSpec = ProtoSpec(protoName, self._reg)

        line = self.getLine()

        # accept zero or more EnumSpec declarations at zero indentation
        line = self.acceptEnumSpecs(protoSpec, line)  # default indent and step

        # DEBUG
        print("  line returned by acceptEnumSpecs: '%s'" % line)
        # END

        # expect one or more MsgSpec declaration at zero indentation; these
        # may include nested EnumSpec declations at 'step' indentation and
        # nested MsgSpecs at 'step' indentation; the MsgSpecs may include
        # nested EnumSpecs and MsgSpecs at progressively greater indentations,
        # possibly limited to a maximum indentation of MAX_INDENT

        # WORKING HERE NEXT
        line = self.expectMsgSpecs(protoSpec, line)  # default indent and step

        # expect zero or more SeqSpecs
        # XXX NO SUCH METHOD and seqs is not defined
        # self.acceptSeqSpecs(seqs, line)    # as usual, default indent & step

        return protoSpec


# == OLDER CODE, MAY BE OBSOLETE ====================================
# POSSIBLY SUPERCLASS IS TFReader
class WireMsgSpecParser(object):
    """
    Reads a MsgSpec fully serialized to wire form (and so a sequence of
    fieldz) produce a MsgSpec object model, which is a MsgSpec with
    FieldSpecs and EnumSpecs dangling off of it.
    """

    def __init__(self, w):
        pass

# POSSIBLY SUPERCLASS IS TFBuffer OR TFWriter


class WireMsgSpecWriter(object):
    """
    Given a MsgSpec (including attached FieldSpecs and optional EnumSpecs)
    produces a serialization using FieldTypes.
    """

    def __init__(self, mSpec, wb):
        if mSpec is None:
            raise ValueError('no MsgSpec identified')
        self._m = mSpec

        if wb is None:
            raise ValueError('no WireBuffer specified')
        self._wb = wb

    def write(self):

        # THIS SHOULD JUST USE TFWriter, OR ITS BITS AND PIECES.
        # To use TFWriter in its current form, we need a wired-in class
        # definition, say MsgSpecClz.
        # Alternatively, put the putNext methods into a dispatch table
        # and invoke them through that table.

        # protocol
        # name
        # enum
        # fields

        pass
# END OF PARSER
