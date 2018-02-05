# fieldz/fieldz/parser.py

from wireops.enum import FieldTypes
from fieldz import FieldzError, reg, msg_spec as M
from fieldz.enum import Quants
from fieldz.msg_spec import(
    validate_simple_name, validate_dotted_name,
    EnumPairSpec, EnumSpec, FieldSpec,
    MsgSpec, ProtoSpec,  # SeqSpec,
)

__all__ = [
    'StringSpecParser',
    'StringMsgSpecParser',
    'ParseError',
]

MAX_INDENT = 16


class ParseError(RuntimeError):
    pass


class QuantificationError(ParseError):
    pass


class StringSpecParser(object):

    __slots__ = ['_fd', '_node_reg', '_reg', ]

    def __init__(self, fd, node_reg=None):

        # DEBUG
        print('entering StringSpecParser')
        # END

        # XXX should die if fd not open
        self._fd = fd
        if node_reg is None:
            node_reg = reg.NodeReg()
        self._node_reg = node_reg
        self._reg = reg.ProtoReg(node_reg)

    @property
    def node_reg(self):
        return self._node_reg

    @property
    def reg(self):
        return self._reg

    def get_line(self):
        while True:
            line = self._fd.readline()
            # DEBUG
            print("get_line: '%s'" % line)
            # END

            # The first condition never fails if fd is a file-like object
            # (from StringIO)
            if line is None or line == '':
                return None

            # strip off any comments
            string = line.partition('#')[0]

            # get rid of any trailing blanks
            line = string.rstrip()
            if line != '':
                return line

    def expect_token_count(self, tokens, whatever, nnn):
        if len(tokens) != nnn:
            raise ParseError(
                "too many tokens in %s '%s'" %
                (whatever, tokens))

    # -- MsgSpec ----------------------------------------------------
    def expect_msg_spec_name(self, line, indent='', step=' '):
        """ on a line beginning 'message ' """
        starter = indent + 'message '

        _ = step                # suppress warning

        if not line or not line.startswith(starter):
            raise ParseError("badly formatted message name line '%s'" % line)

        line = line[len(starter):]
        words = line.split()
        self.expect_token_count(words, 'message name', 1)
        name = words[0]
        if name[-1] == ':':
            name = name[:-1]
        validate_simple_name(name)
        # print "DEBUG: msgSpec name is '%s'" % str(name)
        return name

    def expect_msg_spec(self, parent, line, indent='', step=' '):
        name = self.expect_msg_spec_name(line, indent, step)
        msg_reg = reg.MsgReg(parent.reg)
        print("expect_msg_spec: NAME = %s" % name)            # DEBUG
        this_msg = MsgSpec(name, msg_reg, parent)

        line = self.get_line()

        print("expect_msg_spec: COLLECTING ENUMS; line is '%s'" % line)
        line = self.accept_enum_specs(this_msg, line, indent + step, step)

        # accept any MsgSpecs at the next indent level
        print("expect_msg_spec: COLLECTING NESTED MSGS; line is '%s'" % line)
        line = self.acept_msg_specs(this_msg, line, indent + step, step)

        print("expect_msg_spec: COLLECTING FIELDS; line is '%s'" % line)
        line = self.expect_fields(this_msg, line, indent + step, indent)

        parent.reg.add_msg(this_msg)  # NOT done in MsgSpec.__init__
        return line

    def expect_msg_specs(self, parent, line, indent='', step=' '):
        """
        Expect one or more msgSpecs, hanging them off the parent.

        Must return the first line found which does not begin a
        msgSpec
        """
        line = self.expect_msg_spec(parent, line, indent, step)
        print("BACK FROM expect_msg_spec: line is '%s'" % line)

        # collect any other MsgSpec declarations present
        if line:
            line = line.strip()
        if not line:
            line = self.acept_msg_specs(parent, line, indent, step)
        # DEBUG
        print("EXITING expect_msg_specs, returning line = '%s'" % line)
        # END
        return line

    def acept_msg_specs(self, parent, line, indent='', step=' '):
        """
        Accept zero or more msgSpecs, hanging them off the parent
        and creating a registry for each.

        Must return the first line found which does not begin a
        msgSpec
        """
        print("ENTERING accept_msg_specs: line is '%s'" % line)

        if line:
            msg_starter = indent + 'message'
            while line.startswith(msg_starter):
                line = self.expect_msg_spec(parent, line, indent, step)
                if line:
                    line = line.rstrip()
                if not line:
                    break
        print("LEAVING accept_msg_specs: line is '%s'" % line)
        return line

    # -- EnumPairSpec -----------------------------------------------
    def accept_enum_pair(self, line, indent='', step=' '):
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
        if not parts[1]:
            raise ParseError("expected = in enum pair: '%s'" % line)
        sym = parts[0].strip()
        val = parts[2].strip()

        _ = step    # suppress warning

        return EnumPairSpec(sym, val)

    def expect_enum(self, parent, line, indent, step):
        # we know the line begins with INDENT + 'enum'.  This
        # should be followed by the enum's name, and then a sequence
        # of pairs at a deeper indent
        from_ = len(indent) + len('enum')
        string = line[from_:]
        # s should begin with one or more spaces, followed by one
        # simple name
        if string[0] != ' ':
            raise ParseError("can't find enum name in '%s'" % line)
        name = string.strip()
        validate_simple_name(name)
        pairs = []
        line = self.get_line()          # we require at least one pair
        pair = self.accept_enum_pair(line, indent + step, step)
        if pair is None:
            raise ParseError("expected enum pair, found '%s'" % line)
        pairs.append(pair)

        # we have one pair, let's see if there are any more
        line = self.get_line()
        pair = self.accept_enum_pair(line, indent + step, step)
        while pair is not None:
            pairs.append(pair)
            line = self.get_line()
            pair = self.accept_enum_pair(line, indent + step, step)
        e_spec = EnumSpec(name, pairs)

        # XXX we need to verify that the enum's name is not already
        # in us; simplest thing to do is to have addEnum() verify
        # this,
        parent.add_enum(e_spec)           # parent is ProtoSpec or MsgSpec
        print("DEBUG expectEnum: adding %s to parent registry" % e_spec.name)
        parent.reg.add_enum(e_spec)
        return line

    def accept_enum_specs(self, parent, line, indent='', step=' '):
        """
        Accept and return any enums at the specified indent.  Return
        the first line at the wrong indent or not matching the enum
        syntax.
        """
        enum_start = indent + 'enum'

        while line and line.startswith(enum_start):
            line = self.expect_enum(parent, line, indent, step)

        # DEBUG
#       print "acceptEnumSpecs returning '%s'" % line
        # END

        return line

    # -- FieldSpec --------------------------------------------------
    # def expectField(self, nextFieldNbr, line, indent, step):
    def expect_field(self, msg_spec, line, indent, step):

        # DEBUG #######################
        def leading_spaces(line):
            count = 0
            for char in line:
                if char != ' ':
                    break
                count += 1
            return count

        l_count = leading_spaces(line)
        if l_count != len(indent):
            print("expect_field: LINE: '%s'" % line)
            print("expect_field: expected %d leading spaces, got %d" % (
                  len(indent), l_count))
        # END #########################

        if not line.startswith(indent):
            raise ParseError(
                "wrong indent for field declaration: '%s'" %
                line)

        # DEBUG
        print("expectField: line = '%s'" % line)
        # END

        line = line[len(indent):]

        _ = step    # suppress warning

        # from here we are very sloppy about the indent

        # accept NAME FTYPE(Q)? (@N)? (=DEFAULT)?

        words = line.split()
        word_count = len(words)

        # DEBUG
        print("             found %d tokens: %s" % (word_count, words))
        # END

        if word_count < 2:
            raise ParseError("too few tokens in field def '%s'" % line)
        if word_count > 5:
            raise ParseError("too many tokens in field def '%s'" % line)

        # -- field name -------------------------
        f_name = words[0]
        validate_simple_name(f_name)

        # -- quantifier -------------------------
        quant = words[1][-1]
        if quant == '?' or quant == '*' or quant == '+':
            words[1] = words[1][:-1]
            if quant == '?':
                # pylint: disable=no-member
                quantifier = Quants.OPTIONAL
            elif quant == '*':
                # pylint: disable=no-member
                quantifier = Quants.STAR
            else:
                # pylint: disable=no-member
                quantifier = Quants.PLUS
        else:
            # pylint: disable=no-member
            quantifier = Quants.REQUIRED

        # -- field type --------------------------
        type_name = words[1]
        validate_dotted_name(type_name)
        field_type = None

        # DEBUG ###
        print("             field '%s' type '%s' quant %d (%s)" % (
            f_name, type_name, quantifier.value, quantifier.sym))
        # END #####

        # first check against list of names of field types
        try:
            field_type = FieldTypes.from_sym(type_name)
            # DEBUG
            print(
                "LIST type_name is '%s', index is '%s'" %
                (type_name, field_type))
            # END
        except KeyError:
            # DEBUG
            print("NOT IN LIST type_name '%s'" % type_name)
            # END
            field_type = None

        if field_type is None:
            # check at the message level
            field_type = msg_spec.reg.name2reg_id(type_name)
            # DEBUG
            print(
                "MSG type_name is '%s', index is '%s'" %
                (type_name, field_type))
            # END

        if field_type is None:
            # ask the parent to resolve
            field_type = msg_spec.parent.reg.name2reg_id(type_name)
            # DEBUG
            print(
                "PARENT type_name is '%s', index is '%s'" %
                (type_name, field_type))
            # END

        if field_type is None:
            err_msg = "'%s'; can't determine field type in line: '%s'" % (
                type_name, line)
            raise ParseError(err_msg)

        # -- field number -----------------------
        field_nbr = -1
        if word_count > 2:
            if words[2].startswith('@'):
                field_nbr = int(words[2][1:])    # could use some validation
#               if fieldNbr < nextFieldNbr:
#                   raise FieldzError('field number <= last field number')

        # -- default ----------------------------
        # XXX STUB - NOT IMPLEMENTED YET

        msg_spec.add_field(
            FieldSpec(msg_spec.reg, f_name, field_type, quantifier, field_nbr))

    def expect_fields(self, msg_spec, line, indent='', step=' '):
        # DEBUG
        print("expect_fields: line is '%s'" % line)
        # END
        # they get appended to fields; there must be at least one
        if line is None or line == '':
            raise ParseError('no fields found')

        # get the required first field declaration
        print("BRANCH TO expectField(0)")
        self.expect_field(msg_spec, line, indent, step)
        # DEBUG
        print("BACK FROM expectField(0)")
        k = 1
        # END

        # DROPPING THIS: let MsgSpec constructor handle automatic
        # assignment of field numbers
        # nextFieldNbr = fields[0].fieldNbr + 1

        # get any other field declarations
        line = self.get_line()
        while line is not None and line != '':
            if not line.startswith(indent):
                print("DEBUG: NOT A FIELD DECL: '%s'" % line)
                break
            print("BRANCH TO expectField(%u)" % k)
            # fields.append(self.expectField(nextFieldNbr, line, indent, step))
            self.expect_field(msg_spec, line, indent, step)
            print("BACK FROM expectField(%u)" % k)
            k = k + 1
            # nextFieldNbr = fields[0].fieldNbr + 1
            line = self.get_line()
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

    def __init__(self, fd, node_reg=None):
        super(StringMsgSpecParser, self).__init__(fd, node_reg)
        protocol = 'org.xlattice.fieldz.test'

        # these are dummies
        self.parent_reg = reg.ProtoReg(protocol, self._node_reg)
        self.parent = M.ProtoSpec(protocol, self.parent_reg)

    def parse(self):
        # DEBUG
        print("entering StringMsgSpecParser.parse()")
        # END
        line = self.get_line()
        # msg_reg = reg.MsgReg(self.parent_reg)
        line = self.expect_msg_spec(self.parent, line)

        # DEBUG
        for reg_id in self.parent_reg.entries:  # .keys():
            print("ENTRY: regID %u, name %s" % (
                reg_id, self.parent_reg.entries[reg_id]))
        # END

        ppp = self.parent

        # the parent is a dummy ProtoSpec
        # DEBUG
        print("parse(): parent is a ", type(self.parent))
        if ppp is None:
            print("    parent field is None")
        elif ppp.msgs is None:
            print("    parent.msgs is None")                   # SEEN
        else:
            print("    parent has %d msgs" % len(ppp.msgs))
        # END

        return ppp.msgs[0]


class StringProtoSpecParser(StringSpecParser):
    """
    Reads a human-readable ProtoSpec (a *.xlgo file) to produce a
    ProtoSpec object model, which is a ProtoSpec with FieldSpecs and EnumSpecs
    dangling off of it.
    """

    def __init__(self, fd, node_reg=None):
        super(StringProtoSpecParser, self).__init__(fd, node_reg)
        # DEBUG
        print("entering StringProtoSpecParser.__init__")
        # END
        self._proto_name = None
        self._seqs = []

    # -- protocol line ----------------------------------------------
    def expect_proto_name(self, indent='', step=' '):
        line = self.get_line()
        if indent != '' and not line.startswith(indent):
            raise ParseError("missing indent on protocol line '%s'" % line)

        _ = step    # suppress warning

        # from here we ignore any indentation
        words = line.split()
        self.expect_token_count(words, 'protocol', 2)
        if words[0] == 'protocol':
            # print("DEBUG: protocol is '%s'" % str(self._protocol))
            print("DEBUG: protocol is '%s'" % str(words[1]))
            validate_dotted_name(words[1])
            return words[1]
        raise ParseError("expected protocol line, found '%s'" % line)

    # -- seqSpecs ---------------------------------------------------
    def accept_seq_specs(self, proto_spec, line, indent='', step=' '):
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

        proto_name = self.expect_proto_name()
        proto_spec = ProtoSpec(proto_name, self._reg)

        line = self.get_line()

        # accept zero or more EnumSpec declarations at zero indentation
        line = self.accept_enum_specs(
            proto_spec, line)  # default indent and step

        # DEBUG
        print("  line returned by acceptEnumSpecs: '%s'" % line)
        # END

        # expect one or more MsgSpec declaration at zero indentation; these
        # may include nested EnumSpec declations at 'step' indentation and
        # nested MsgSpecs at 'step' indentation; the MsgSpecs may include
        # nested EnumSpecs and MsgSpecs at progressively greater indentations,
        # possibly limited to a maximum indentation of MAX_INDENT

        # WORKING HERE NEXT
        if line:
            # DEBUG
            print("BRANCH to expect_msg_spec: line = '%s'" % line)
            # END
            line = self.expect_msg_specs(
                proto_spec, line)  # default indent and step

        # expect zero or more SeqSpecs
        # XXX NO SUCH METHOD and seqs is not defined
        # self.acceptSeqSpecs(seqs, line)    # as usual, default indent & step

        return proto_spec


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

    def __init__(self, m_spec, wb):
        if m_spec is None:
            raise FieldzError('no MsgSpec identified')
        self._msg_spec = m_spec

        if wb is None:
            raise FieldzError('no WireBuffer specified')
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
