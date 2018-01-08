# ~/dev/py/fieldz/msgImpl.py

# import sys      # for debugging


from wireops.enum import FieldTypes, PrimTypes

from wireops.raw import(length_as_varint, field_hdr_len, read_field_hdr,
                        write_raw_varint, read_raw_varint,
                        write_field_hdr)

from wireops.typed import T_GET_FUNCS, T_LEN_FUNCS, T_PUT_FUNCS

from fieldz import FieldzError
from fieldz.enum import Quants
from fieldz.field_impl import make_field_class

__all__ = ['make_msg_class', 'make_field_class', 'write', 'impl_len', ]

# SERIALIZATION METHODS ---------------------------------------------
# This interface should be compatible with registry {put,get,len}Func but
# is NOT.  SHOULD REPLACE buf, pos WITH chan IN ALL PARAMETER LISTS


def impl_len(msg, nnn):
    """
    msg is a reference to an instance of the MsgImpl class, n is its
    field number.  Returns the int length of the serialized object,
    including the lenght of the field header.
    """
    return msg.wire_len(nnn)


def _check_position(chan, end):
    if chan.position > end:
        err_msg = "read beyond end of buffer: position :=  %d, end is %d" % (
            chan.position, end)
        raise RuntimeError(err_msg)

# -------------------------------------------------------------------
# CODE FRAGMENTS: METHODS USED AS COMPONENTS IN BUILDING CLASSES
# -------------------------------------------------------------------

# pylint: disable=unused-argument


def write(self):
    raise NotImplementedError


def my_getter(self):
    raise NotImplementedError


def my_wire_len(self):
    print("DEBUG: myWireLen invoked")
    raise NotImplementedError


def my_p_wire_len(self, nnn):    # field number for nested msg, regID otherwise
    raise NotImplementedError

# specific to messages ----------------------------------------------


def my_enums(self):
    #pylint: disable=protected-access
    return self._enums


def my_msgs(self):
    #pylint: disable=protected-access
    return self._msgs


def my_field_classes(self):
    #pylint: disable=protected-access
    return self._field_classes

# specific to fields ------------------------------------------------
# FOR A GIVEN FIELD, THESE ARE CONSTANTS ASSIGNED BY make_field_class
#
#
# def myFType(cls): return cls._fType
#
#
# def myQuantifier(cls): return cls._quantifier
#
#
# def myFieldNbr(cls): return cls._fieldNbr
#
#
# def myDefault(cls): return cls._default
#
# these get and set the value attribute of the field instance; they
# have nothing to do with de/serialization to and from the channel
#
#
# def myValueGetter(self): return self._value
# XXX TYPE-SPECIFIC VALIDATION, COERCION:
#
#
# def myValueSetter(self, value): self._value = value     # GEEP

# -------------------------------------------------------------------
# MESSAGE CLASS
# -------------------------------------------------------------------


# WAS OF TYPE 'type' 2016-08-02

class MsgImpl(object):
    """
    An abstract class intended to serve as parent to automatically
    generated classes whose purpose will be to ease user handling
    of data being sent or received across the wire.
    """

    # DISABLE __slots__ until better understood
#   __slots__ = ['_field_classes', # list of field instances
#                #                 '_fields_by_name',
#                '_enums',         # nested enums
#                '_msgs',          # nested messages
#                ]

    def __init__(self, mname, field_classes=None, enums=None, msgs=None):
        self._mname = mname
        self._field_classes = field_classes
        self._enums = enums
        self._msgs = msgs
        self._parent_spec = None

    # EXPERIMENT 2018-01-05
    @property
    def mname(self):
        return self._mname
    # END EXPERIMENT

    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        if self._mname != other.mname:
            return False

#       print "MESSAGE NAMES THE SAME"              # DEBUG

        # -- compare fields -------------------------------
        if self._field_classes is None or other.field_classes is None:
            return False
#       print "SAME NUMBER OF FIELDS"               # DEBUG
        if len(self._field_classes) != len(other.field_classes):
            return False
        for i in range(len(self._field_classes)):
            if self._field_classes[i] != other.field_classes[i]:
                # DEBUG
                print("MESSAGE FIELDS %d DIFFER" % i)
                # END
                return False

#       print "FIELDS ARE THE SAME"                 # DEBUG

        # -- compare nested enums -------------------------
        if self._enums is None or other.enums is None:
            return False
        if len(self._enums) != len(other.enums):
            return False
        for i in range(len(self._enums)):
            if self._enums[i] != other.enums[i]:
                return False

        # -- compare nested msgs --------------------------
        if self._msgs is None or other.msgs is None:
            return False
        if len(self._msgs) != len(other.msgs):
            return False
        for i in range(len(self._msgs)):
            if self._msgs[i] != other.msgs[i]:
                return False

        return True

    def __len__(self):
        return len(self._field_classes)

    def __getitem__(self, nnn):
        # 2016-08-02, same fix
        # return self._fields[n]
        return self._field_classes[nnn]

    # -- INSTANCE SERIALIZATION -------------------------------------

    # INSTANCE PUT ----------------------------------------
    def write_stand_alone(self, chan):
        """
        Write the message stand-alone, as the topmost message on the
        channel.  Returns the message index as a convenience in testing.
        """
        mname = self._mname
        ndx = self._parent_spec.msg_name_index(mname)
        # DEBUG
        print("WRITE_STAND_ALONE: MSG %s INDEX IS %d" % (mname, ndx))
        # END

        self.write(chan, ndx)
        return ndx

    def write(self, chan, nnn):
        """
        n is the msg's field number OR regID
        """
        write_field_hdr(
            chan,
            nnn,
            PrimTypes.LEN_PLUS)   # write the field header
        msg_len = self._wire_len()         # then the unprefixed length
        write_raw_varint(chan, msg_len)

        # XXX DEBUG
        print("ENTERING MsgImpl.write FIELD NBR " +
              "%u, MSG LEN IS %u; AFTER WRITING HDR OFFSET  %u" % (
                  nnn, msg_len, chan.position))

        # XXX This only makes sense for simple messages all of whose
        # fields are required and so have only a single instance
        for field in self._field_classes:      # instances with a value attr

            # CLASS-LEVEL SLOTS are '_name', '_fType', '_quantifier',
            #                       '_fieldNbr', '_default',]
            # INSTANCE-LEVEL SLOT is '_value'

            #pylint: disable=protected-access
            f_name = field._name
            f_nbr = field.field_nbr
            f_quant = field.quantifier          # NEXT HURDLE
            field_type = field.field_type
            value = field.value
            # default = field.default

            # pylint: disable=no-member
            if f_quant == Quants.REQUIRED or f_quant == Quants.OPTIONAL:
                if field_type > 23:
                    # DEBUG
                    reg = self.msg_spec.reg
                    print("RECURSING TO WRITE FIELD %u TYPE %s" % (
                        f_nbr, reg.reg_id2name(field_type)))
                    # END
                    value.write(chan, f_nbr)
                else:
                    # DEBUG
                    display_val = value
                    if field_type == FieldTypes.L_STRING and len(
                            display_val) > 16:
                        display_val = display_val[:16] + '...'
                    print("WRITING FIELD %u TYPE %u VALUE %s" % (
                        f_nbr, field_type, display_val))
                    # END
                    T_PUT_FUNCS[field_type](chan, value, f_nbr)
            elif f_quant == Quants.PLUS or f_quant == Quants.STAR:
                v_list = value
                for varint_ in v_list:
                    # WORKING HERE
                    if field_type > 23:
                        # DEBUG
                        reg = self.msg_spec.reg
                        print("RECURSING TO WRITE FIELD %u TYPE %s" % (
                            f_nbr, reg.reg_id2name(field_type)))
                        # END
                        # this function recursing
                        varint_.write(chan, f_nbr)
                    else:
                        T_PUT_FUNCS[field_type](chan, varint_, f_nbr)
            else:
                raise RuntimeError(
                    "field '%s' has unknown quantifier '%s'" % (
                        f_name, f_quant))  # GEEP
#       # DEBUG
#       print "AFTER WRITING ENTIRE MESSAGE OFFSET IS %d" % chan.position
#       # END

    # -- INSTANCE GET -------------------------------------
    @classmethod
    def read(cls, chan, parent_spec):
        """msg refers to the msg, n is field number; returns msg, n"""
        (p_type, nnn) = read_field_hdr(chan)
        if nnn < 0 or nnn >= len(parent_spec.msgs):
            raise RuntimeError("msg ID '%s' out of range" % nnn)

        msg_spec = parent_spec.msgs[nnn]

        msg_len = read_raw_varint(chan)
        # DEBUG
        print("IMPL_GETTER, P_TYPE %d, MSG/FIELD NBR %d, MSG_LEN %d" % (
            p_type, nnn, msg_len))
        # END

        end = chan.position + msg_len
        cls = _make_msg_class(parent_spec, msg_spec)      # generated class

        field_classes = []                     # ???
        values = []                     # ???

        # XXX THIS IS NOT GOING TO WORK, BECAUSE WE NEED TO PEEK XXX
        # pylint: disable=no-member
        for f_class in cls._field_classes:

            #pylint: disable=protected-access
            f_quant = f_class._quantifier
            field_type = f_class._field_type       # a number
            #pylint: disable=protected-access
            f_quant = f_class._quantifier
            field_nbr = f_class._field_nbr

            # read the field header
            (p_type, nbr) = read_field_hdr(chan)
            # DEBUG
            print(
                "    GET_FROM_CHAN, FIELD %u, TYPE %u" %
                (field_nbr, field_type))
            # END
            if field_nbr != nbr:
                raise RuntimeError(" EXPECTED FIELD_NBR %d, GOT %d" % (
                    field_nbr, nbr))
            # pylint: disable=no-member
            if f_quant == Quants.REQUIRED or f_quant == Quants.OPTIONAL:
                if field_type > 23:
                    reg = cls.msg_spec.reg
                    # BEGIN JUNK ------------------------------------
                    # DEBUG
                    print(
                        "READING: FIELD TYPE IS %s" %
                        reg.reg_id2name(field_type))
                    # END
                    entry = reg.reg_id2entry(field_type)
                    print("READING: FIELD TYPE bis IS %s" % entry.name)
                    # END JUNK --------------------------------------
                    # child_spec = entry.msg_spec

                    # child_class = _make_msg_class(msg_spec, child_spec)

                    # RECURSE: read(childCls, chan, msgSpec)
                    # msgSpec is parentSpec here
                    value = T_GET_FUNCS[field_type](chan)  # XXX WRONG
                else:
                    value = T_GET_FUNCS[field_type](chan)
                _check_position(chan, end)
                values.append(value)

            elif f_quant == Quants.PLUS or f_quant == Quants.STAR:
                # v_list = []              # we are reading a list of values

                # WORKING HERE
                pass

            else:
                raise RuntimeError("unknown quantifier, index '%u'" % f_quant)
        # DEBUG
        print("AFTER COLLECTING %u FIELDS, OFFSET IS %u" % (
            len(field_classes), chan.position))
        # END

        # XXX BLOWS UP: can't handle Quants.PLUS or Quants.STAR (about line
        # 407)
        return (cls(values), nnn)                                 # GEEP

    # -- INSTANCE SERIALIZED LENGTH -----------------------
    def _wire_len(self):
        """
        Returns the length of the body of a serialized message, excluding
        the header.
        """
        msg_len = 0
        nnn = 0  # DEBUG
        for field in self._field_classes:
            f_name = field.fname
            f_nbr = field.field_nbr
            f_quant = field.quantifier          # NEXT HURDLE
            field_type = field.field_type
            value = field.value

            # XXX What follows doesn't quite make sense.  If a REQUIRED
            # message is missing, we simply won't find it.  Likewise
            # for Quants.STAR

            # pylint: disable=no-member
            if f_quant == Quants.REQUIRED or f_quant == Quants.OPTIONAL:
                contrib = T_LEN_FUNCS[field_type](value, f_nbr)

                # DEBUG
                if field_type > 23:
                    reg = self.msg_spec.reg     # or protocol reg?
                    # XXX is the registry for the protocol? msgSpec?
                    print("    F_TYPE %u IS MSG %s" %
                          (field_type, reg.reg_id2name(field_type)))
                    print("    LEN: FIELD %u (%s), TYPE %u, CONTRIBUTION %d" %
                          (nnn, f_name, field_type, contrib))
                nnn += 1
                # END
                msg_len += contrib

            elif f_quant == Quants.PLUS or f_quant == Quants.STAR:
                # value will be a non-empty list; handle each individual
                # member like Quants.REQUIRED
                v_list = value
                for varint_ in v_list:
                    # HACKING ABOUT
                    if field_type > 23:
                        # pylint: disable=no-member
                        reg = self.msg_spec.reg
                        # DEBUG
                        print("    LEN: FIELD TYPE IS %s" %
                              reg.reg_id2name(field_type))
#                       entry = reg.regID2Entry(fType)
#                       print "    LEN: FIELD TYPE bis IS %s" % entry.name
                        # END

                        contrib = varint_.wire_len(f_nbr)

                    else:
                        # END HACKING

                        # -----------------------------------------------
                        # XXX FAILS with list index error, fType == 24 XXX
                        # -----------------------------------------------
                        # DEBUG
                        print("FIELD '%s' Quants.PLUS MEMBER TYPE IS %s" % (
                            f_name, field_type))
                        # END
                        contrib = T_LEN_FUNCS[field_type](varint_, f_nbr)

                        # DEBUG
                        print("    LEN: FIELD %u (%s), TYPE %u, CONTRIB %d" % (
                            nnn, f_name, field_type, contrib))
                        # END
                    nnn += 1
                    msg_len += contrib

            else:
                raise RuntimeError(
                    "field '%s' has unknown quantifier '%s'" % (
                        f_name, f_quant))

        return msg_len

    def wire_len(self, nnn):
        """
        Return the length of a serialized message including the field
        header, where n is the field number of a nested message or the
        regID if the message is not nested.
        """
        len_ = length_as_varint(field_hdr_len(nnn, PrimTypes.LEN_PLUS))
        count = self._wire_len()
        return len_ + length_as_varint(count) + count

# META_MSG ======================================================


class MetaMsg(type):

    def __new__(mcs, name, bases, namespace, **kwargs):
        # DEBUG
        print("MetaMsgNEW gets called once")
        # END
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):

        # definitely works:
        # setattr(cls, 'baz', '__init__ added to dictionary before super call')

        super().__init__(name, bases, namespace)
        print("MetaMsgINIT gets called once")

        return

        #############################################################
        # BEING IGNORED - belongs in a maker class
        #############################################################
#       cls._field_classes = []
#       cls._field_classes_by_name   = {}
#       values = args[0]
#       for idx, val in enumerate(values):
#           this_field = cls._field_classes[idx](val)
#           cls._field_classes.append(this_field)
#           cls._field_classes_by_name[thisField.fname] = thisField
#           setattr(cls, this_field.fname, val)

#           # DEBUG
#           print("META_MSG.__call__:")
#           print("   idx   = %u" % idx)
#           print("   name  = %s" % cls._field_classes[idx].fname)
#           print("   value = %s" % cls._field_classes[idx].value)
#           # END

#       print "  THERE ARE %u FIELDS SET" % len(cls._field_classes)    # DEBUG

#       return super().__init__(name, bases, namespace)

    #########################################################################
    # DISABLE FOR NOW; XXX SHOULD BE ADDED WHEN THE INSTANCE HAS BEEN CREATED
    #########################################################################
    # don't permit any new attributes to be added
    # XXX why do we need to do this given __slots__ list?
    def __setattr__(cls, attr, value):
        """ make the class more or less immutable """

        #############################
        # WHERE THE ERROR COMES FROM:
        #############################
        if attr not in dir(cls):
            raise AttributeError('cannot create attribute by assignment!')
        return type.__setattr__(cls, attr, value)

# ===================================================================
# MAKERS
# ===================================================================

# EXPERIMENT: IMPLEMENTATION OF MESSAGE CLASS __init__
# DROPPING THIS FOR NOW
# UN-DROPPED 2017-03-03


def msg_initter(cls, *args, **attrs):
    # We want to create instances of the respective fields and
    # assign 'arg' to field 'idx'.  This means that field instances
    # need to have been created before we get here

    # DEBUG
    print('INITTER:')
    if args:
        for idx, arg in enumerate(args):
            print("  arg %u is '%s'" % (idx, str(arg)))
    if attrs:
        # XXX REVIEW ME:
        for key, val in iter(attrs.items):
            print("  kwarg attr is '%s', value is '%s'" % (key, str(val)))

    # END

    # XXX if msg_initter is dropped from the dictionary, I get an error at
    # line 249 in __call__,
    #  return type.__call__(cls, *args, **kwargs)
    #  TypeError: object.__new__() takes no parameters
    #


# XXX A Strange Litle Device:
MSG_CLS_BY_Q_NAME = {}    # PROTO_NAME . MSG_NAME => class


def make_msg_class(parent, name):
    """ construct a MsgClass given a msg name known to the parent """
    # DEBUG
    print("\nMAKE_MSG_CLASS: parent '%s', name '%s'" % (parent, name))
    # END
    msg_spec = parent.get_msg_spec(name)
    return _make_msg_class(parent, msg_spec)


def _make_msg_class(parent, msg_spec):
    """ construct a MsgClass given a MsgSpec """
    if parent is None:
        raise FieldzError('parent must be specified')
    proto_name = parent.name

    if msg_spec is None:
        raise FieldzError('msgSpec be specified')

    # XXX single-dot name and so NO NESTED MSG_CLASSes
    qual_name = '%s.%s' % (proto_name, msg_spec.mname)

    # DEBUG
    print('_MAKE_MSG_CLASS for %s' % qual_name)
    # END
    if qual_name in MSG_CLS_BY_Q_NAME:
        # XXX BUT CACHING HAS BEEN DISABLED
        # DEBUG
        print("    USING CACHED CLASS for %s\n" % qual_name)
        # END
        return MSG_CLS_BY_Q_NAME[qual_name]

    # build list of field classes -----------------------------------
    field_classes = []
    field_classes_by_name = {}
    field_classes_by_nbr = {}        # by field nbr, not index
    # XXX implicit assumption is that fields are ordered by ascending
    # XXX field number
    for field_spec in msg_spec:
        # XXX NO ALLOWANCE FOR NESTED MSG_SPEC
        cls = make_field_class(qual_name, field_spec)
        field_classes.append(cls)
        field_classes_by_name['%s.%s' % (qual_name, field_spec.fname)] = cls
        field_classes_by_nbr[field_spec.field_nbr] = cls

    # class is not in cache, so construct ---------------------------

    # _enums = []
    # _msgs = []

    # DEBUG
    print("    _MAKE_MSG_CLASS: _name is %s" % msg_spec.mname)
    # END DEBUG

    class Msg(MsgImpl, metaclass=MetaMsg,
              # uncommented the next line 2017-02-03
              __init__=msg_initter,
              # 'name' already in use?
              mname=msg_spec.mname,
              enums=property(my_enums),
              msgs=property(my_msgs),
              field_classes=property(my_field_classes),

              # EXPERIMENT 2012-12-15
              parent_spec=parent,
              msg_spec=msg_spec
              # END EXPERIMENT
              ):
        pass

    # DEBUG =====================================
    print("MSG_IMPL DICTIONARY:")
    for key in Msg.__dict__:
        print("  %-16s => %s" % (key, Msg.__dict__[key]))
    # END =======================================

    # DEBUG
    print("\n_make_msg_class returning something of type %s\n" % type(Msg))
    # END

    # ----------------------------
    # possibly some more fiddling ...
    # ---------------------------

    # XXX DISABLING CACHINE
    # MSG_CLS_BY_Q_NAME[qual_name] = Msg
    return Msg
