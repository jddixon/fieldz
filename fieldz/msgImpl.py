# ~/dev/py/fieldz/msgImpl.py

# DEBUG
import sys
# END
import fieldz.fieldTypes as F
from fieldz.raw         import lengthAsVarint, fieldHdrLen, readFieldHdr, \
                            writeRawVarint, readRawVarint, \
                            writeFieldHdr, LEN_PLUS_TYPE
from fieldz.typed       import *
from fieldz.msgSpec     import *

import fieldz.reg       as R

__all__ = ['makeMsgClass', 'makeFieldClass',
           'write',         'implLen',
          ]

# SERIALIZATION METHODS ---------------------------------------------
# This interface should be compatible with registry {put,get,len}Func but
# is NOT.  SHOULD REPLACE buf, pos WITH chan IN ALL PARAMETER LISTS


def implLen(msg, n):
    """
    msg is a reference to an instance of the MsgImpl class, n is its
    field number.  Returns the int length of the serialized object,
    including the lenght of the field header.
    """
    return msg.wireLen(n)

def _checkPosition(chan, end):
    if chan.position > end:
        errMsg = "read beyond end of buffer: position :=  %d, end is %d" % (
                chan.position, end)
        raise RuntimeError(errMsg) 

# -------------------------------------------------------------------
# METHODS USED AS COMPONENTS IN BUILDING CLASSES
# -------------------------------------------------------------------
def myName(self):               return self._name

def write(self):
    return notImpl
def myGetter(self):
    return notImpl
def myWireLen(self):
    print("DEBUG: myWireLen invoked")
    return notImpl
def myPWireLen(self, n):    # n is field number for nested msg, regID otherwise
    return notImpl

# specific to messages ----------------------------------------------
def myEnums(self):              return self._enums
def myMsgs(self):               return self._msgs
def myFieldClasses(self):       return self._fieldClasses

# specific to fields ------------------------------------------------
# FOR A GIVEN FIELD, THESE ARE CONSTANTS ASSIGNED BY makeFieldClass
def myFType(cls):               return cls._fType
def myQuantifier(cls):          return cls._quantifier
def myFieldNbr(cls):            return cls._fieldNbr
def myDefault(cls):             return cls._default

# these get and set the value attribute of the field instance; they
# have nothing to do with de/serialization to and from the channel
def myValueGetter(self):        return self._value
# XXX TYPE-SPECIFIC VALIDATION, COERCION:
def myValueSetter(self, value): self._value = value

# -------------------------------------------------------------------
# FIELD CLASS
# -------------------------------------------------------------------
class FieldImpl(object):
    """
    An abstract class intended to serve as parent to automatically
    generated classes whose purpose will be to ease user handling
    of data being sent or received across the wire.
    """

    __slots__ = [ '_value',]

    # should default precede value?  if a value is assigned, isn't that
    # a default?  In fact shouldn't the parameter list end with
    #   value=default?
    def __init__(self, value=None):
        # XXX NEED SOME VALIDATION
        self._value     = value

    def __eq__(self, other):
        if other is None:                           return False
        if self is other:                           return True
        if self._name != other._name:               return False
        if self._fType != other._fType:             return False
        if self._quantifier != other._quantifier:   return False
        if self._fieldNbr != other._fieldNbr:       return False
        # ignore defaults for now
        return True


class MetaField(type):

    # gets: valueError: "'_name' in __slots__ confliects with class variable"

    def __new__(meta, name, bases, dct):
        # DEBUG
        print("MetaField NEW, meta='%s', name='%s', bases='%s', dct='%s'" % (
                meta, name, bases, dct))
        sys.stdout.flush()
        # END
        return super(MetaField, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        # DEBUG
        super(MetaField, cls).__init__(name, bases, dct)
        print("MetaField INIT, meta='%s', name='%s', bases='%s', dct='%s'" % (
                meta, name, bases, d))
        sys.stdout.flush()
        # END

    def __call__(cls, *args, **kwargs):
        # DEBUG
        print("MetaField CALL with args = '%s'" % str(args))
        sys.stdout.flush()
        # END
        return type.__call__(cls, *args, **kwargs)

# -------------------------------------------------------------------
# MESSAGE CLASS
# -------------------------------------------------------------------
class MsgImpl(object):
    """
    An abstract class intended to serve as parent to automatically
    generated classes whose purpose will be to ease user handling
    of data being sent or received across the wire.
    """

    __slots__ = [ '_fields' ,       # list of field instances
#                 '_fieldsByName',  # that list indexed by Name
                  '_enums',         # nested enums
                  '_msgs',          # nested messages
                ]

    def __eq__(self, other):
        if other is None:                           return False
        if self is other:                           return True
        if self._name != other._name:               return False

#       print "MESSAGE NAMES THE SAME"              # DEBUG

        # -- compare fields -------------------------------
        if self._fields is None or other._fields is None:
            return False
#       print "SAME NUMBER OF FIELDS"               # DEBUG
        if len(self._fields) != len(other._fields): return False
        for i in range(len(self._fields)):
            if self._fields[i] != other._fields[i]:
                # DEBUG
                print("MESSAGE FIELDS %d DIFFER" % i)
                # END
                return False

#       print "FIELDS ARE THE SAME"                 # DEBUG

        # -- compare nested enums -------------------------
        if self._enums is None or other._enums is None:
            return False
        if len(self._enums) != len(other._enums): return False
        for i in range(len(self._enums)):
            if self._enums[i] != other._enums[i]: return False

        # -- compare nested msgs --------------------------
        if self._msgs is None or other._msgs is None:
            return False
        if len(self._msgs) != len(other._msgs): return False
        for i in range(len(self._msgs)):
            if self._msgs[i] != other._msgs[i]: return False

        return True

    def __len__(self):              return len(self._fields)
    def __getitem__(self, n):       return self._fields[n]

    # -- INSTANCE SERIALIZATION -------------------------------------

    # INSTANCE PUT ----------------------------------------
    def writeStandAlone(self, chan):
        """ 
        Write the message stand-alone, as the topmost message on the
        channel.  Returns the message index as a convenience in testing.
        """
        name    = self._name
        ndx     = self.parentSpec.msgNameIndex(name)
        # DEBUG
        print("WRITE_STAND_ALONE: MSG %s INDEX IS %d" % (name, ndx))
        # END
    
        self.write(chan, ndx)
        return ndx

    def write(self, chan, n):
        """
        n is the msg's field number OR regID
        """
        writeFieldHdr(chan, n, LEN_PLUS_TYPE)   # write the field header
        msgLen        = self._wireLen()         # then the unprefixed length
        writeRawVarint(chan, msgLen)

        # XXX DEBUG
        print("ENTERING MsgImpl.write FIELD NBR %u, MSG LEN IS %u; AFTER WRITING HDR OFFSET  %u" % (
                                                    n, msgLen, chan.position))

        # XXX This only makes sense for simple messages all of whose
        # fields are required and so have only a single instance
        for field in self._fields:      # these are instances with a value attr

            # CLASS-LEVEL SLOTS are '_name', '_fType', '_quantifier',
            #                       '_fieldNbr', '_default',]
            # INSTANCE-LEVEL SLOT is '_value'

            fName   = field.name
            fNbr    = field.fieldNbr
            fQuant  = field.quantifier          # NEXT HURDLE
            fType   = field.fType
            value   = field.value
            default = field.default

            if fQuant == Q_REQUIRED or fQuant == Q_OPTIONAL:
                if fType > 23:
                    # DEBUG
                    reg = self.msgSpec.reg
                    print("RECURSING TO WRITE FIELD %u TYPE %s" % (
                                               fNbr, reg.regID2Name(fType)))
                    # END
                    value.write(chan, fNbr)
                else:
                    # DEBUG
                    displayVal = value
                    if fType == F._L_STRING and len(displayVal) > 16:
                        displayVal = displayVal[:16] + '...'
                    print("WRITING FIELD %u TYPE %u VALUE %s" % (
                                        fNbr,   fType,   displayVal))
                    # END
                    tPutFuncs[fType](chan, value, fNbr)
            elif fQuant == Q_PLUS or fQuant == Q_STAR:
                vList = value
                for v in vList:
                    # WORKING HERE
                    if fType > 23:
                        # DEBUG
                        reg = self.msgSpec.reg
                        print("RECURSING TO WRITE FIELD %u TYPE %s" % (
                                                fNbr, reg.regID2Name(fType)))
                        # END
                        v.write(chan, fNbr)         # this function recursing
                    else:
                        tPutFuncs[fType](chan, v, fNbr)
            else:
                raise RuntimeError(
                    "field '%s' has unknown quantifier '%s'" % (
                           fName,                Q_NAMES[fQuant]))  # GEEP
#       # DEBUG
#       print "AFTER WRITING ENTIRE MESSAGE OFFSET IS %d" % chan.position
#       # END

    # -- INSTANCE GET -------------------------------------
    @classmethod
    def read(cls, chan, parentSpec):
        """msg refers to the msg, n is field number; returns msg, n"""
        (pType, n)  = readFieldHdr(chan)
        if n < 0 or n >= len(parentSpec._msgs):
            raise RuntimeError("msg ID '%s' out of range" % n)

        msgSpec     = parentSpec._msgs[n]

        msgLen = readRawVarint(chan)
        # DEBUG
        print("IMPL_GETTER, P_TYPE %d, MSG/FIELD NBR %d, MSG_LEN %d" % (
                pType, n, msgLen))
        # END

        end = chan.position + msgLen
        clz = _makeMsgClass(parentSpec, msgSpec)      # generated class

        fields = []                     # ???
        values = []                     # ???

        # XXX THIS IS NOT GOING TO WORK, BECAUSE WE NEED TO PEEK XXX
        for fClass in clz._fieldClasses:

            fType   = fClass._fType       # a number
            fQuant  = fClass._quantifier
            fieldNbr= fClass._fieldNbr

            # read the field header
            (pType, nbr)  = readFieldHdr(chan)
            # DEBUG
            print("    GET_FROM_CHAN, FIELD %u, TYPE %u" % (fieldNbr, fType))
            # END
            if fieldNbr != nbr:
                raise RuntimeError(" EXPECTED FIELD_NBR %d, GOT %d" % (
                                                    fieldNbr, nbr))
            if fQuant == Q_REQUIRED or fQuant == Q_OPTIONAL:
                if fType > 23:
                    reg = self.msgSpec.reg
                    # BEGIN JUNK ------------------------------------
                    # DEBUG
                    print("READING: FIELD TYPE IS %s" % reg.regID2Name(fType))
                    # END
                    entry = reg.regID2Entry(fType)
                    print("READING: FIELD TYPE bis IS %s" % entry.name)
                    # END JUNK --------------------------------------
                    childSpec  = entry.msgSpec

                    childClass = _makeMsgClass(msgSpec, CHILD_SPEC)

                    # RECURSE: read(childCls, chan, msgSpec)
                    # msgSpec is parentSpec here
                    value = tGetFuncs[fType](chan)  # XXX WRONG
                else:
                    value = tGetFuncs[fType](chan)
                _checkPosition(chan, end)
                values.append(value)

            elif fQuant == Q_PLUS or fQuant == Q_STAR:
                vList = []              # we are reading a list of values

                # WORKING HERE

            else:
                raise RunTimeError("unknown quantifier, index '%u'" % fQuant)
        # DEBUG
        print("AFTER COLLECTING %u FIELDS, OFFSET IS %u" % (
                                            len(fields), chan.position))
        # END

        # XXX BLOWS UP: can't handle Q_PLUS or Q_STAR (about line 407)
        return (clz(values), n)                                 # GEEP

    # -- INSTANCE SERIALIZED LENGTH -----------------------
    def _wireLen(self):
        """
        Returns the length of the body of a serialized message, excluding
        the header.
        """
        msgLen = 0
        n = 0 # DEBUG
        for field in self._fields:
            fName   = field.name
            fNbr    = field.fieldNbr
            fQuant  = field.quantifier          # NEXT HURDLE
            fType   = field.fType
            value   = field.value

            # XXX What follows doesn't quite make sense.  If a REQUIRED
            # message is missing, we simply won't find it.  Likewise
            # for Q_STAR
            if fQuant == Q_REQUIRED or fQuant == Q_OPTIONAL:
                contrib = tLenFuncs[ fType ] (value, fNbr)

                # DEBUG
                if fType > 23:
                    # XXX is the registry for the protocol? msgSpec?
                    print("    F_TYPE %u IS MSG %s" % (fType,
                            XXX.regID2Name(fType)))
                    print("    LEN: FIELD %u (%s), TYPE %u, CONTRIBUTION %d" % (
                                            n, fName, fType, contrib))
                n += 1
                # END
                msgLen += contrib

            elif fQuant == Q_PLUS or fQuant == Q_STAR:
                # value will be a non-empty list; handle each individual
                # member like Q_REQUIRED
                vList = value
                for v in vList:
                    # HACKING ABOUT
                    if fType > 23:
                        reg = self.msgSpec.reg
                        # DEBUG
                        print("    LEN: FIELD TYPE IS %s" % \
                                                        reg.regID2Name(fType))
#                       entry = reg.regID2Entry(fType)
#                       print "    LEN: FIELD TYPE bis IS %s" % entry.name
                        # END

                        contrib = v.wireLen(fNbr)

                    else:
                    # END HACKING

                        # -----------------------------------------------
                        # XXX FAILS with list index error, fType == 24 XXX
                        # -----------------------------------------------
                        print("DEBUG FIELD '%s' Q_PLUS MEMBER TYPE IS %s" % (
                                fName, fType))
                        contrib = tLenFuncs[ fType ] (v, fNbr)

                        # DEBUG
                        print("    LEN: FIELD %u (%s), TYPE %u, CONTRIB %d" % (
                                                    n, fName, fType, contrib))
                        # END
                    n += 1
                    msgLen += contrib


            else:
                raise RuntimeError(
                    "field '%s' has unknown quantifier '%s'" % (
                           fName,                Q_NAMES[fQuant]))  # GEEP

        return msgLen

    def wireLen(self, n):
        """
        Return the length of a serialized message including the field
        header, where n is the field number of a nested message or the
        regID if the message is not nested.
        """
        h       = lengthAsVarint(fieldHdrLen(n, LEN_PLUS_TYPE))
        count   = self._wireLen()
        return h + lengthAsVarint(count) + count

# META_MSG ======================================================
class MetaMsg(type):

    def __new__(meta, name, bases, dct):
        # DEBUG
#       print "METACLASS NEW gets called once"
        # END
        return super(MetaMsg, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        # definitely works:
        # setattr(cls, 'baz', '__init__ added to dictionary before super call')

        super(MetaMsg, cls).__init__(name, bases, dct)
#       print "METACLASS INIT gets called once"

    def __call__(cls, *args, **kwargs):
        """
        XXX At this time the only argument expected is a list of field
        values.  This is the INSTANCE.  kwargs is empty.
        """
        cls._fields         = []
#       cls._fieldsByName   = {}
        values = args[0]
        for idx,val in enumerate(values):
            thisField       = cls._fieldClasses[idx](val) 
            cls._fields.append(thisField)
#           cls._fieldsByName[thisField.name] = thisField
            setattr(cls, thisField.name, val)

#           # DEBUG
#           print "META_MSG.__call__: idx   = %u" % idx
#           print "                   name  = %s" % cls._fields[idx].name
#           print "                   value = %s" % cls._fields[idx].value
#           # END

#       print "  THERE ARE %u FIELDS SET" % len(cls._fields)    # DEBUG
        return type.__call__(cls, *args, **kwargs)

    # don't permit any new attributes to be added
    # XXX why do we need to do this given __slots__ list?
    def __setattr__(cls, attr, value):
        """ make the class more or less immutable """
        if attr not in dir(cls):
            raise AttributeError('cannot create attribute by assignment')
        return type.__setattr__(cls, attr, value)

# ===================================================================
# MAKERS
# ===================================================================

# EXPERIMENT: IMPLEMENTATION OF MESSAGE CLASS __init__
def msgInitter(cls, *args, **attrs):
    # We want to create instances of the respective fields and
    # assign 'arg' to field 'idx'.  This means that field instances
    # need to have been created before we get here

#   # DEBUG
#   print 'INITTER:'
#   if args:
#       for idx,arg in enumerate(args):
#           print "  arg %u is '%s'" % (idx, str(arg))
#   if attrs:
#       for key,val in attrs.iteritems:
#           print "  kwarg attr is '%s', value is '%s'" % (key, str(val))

#   # END

    # XXX if msgInitter is dropped from the dictionary, I get an error at
    # line 249 in __call__,
    #    return type.__call__(cls, *args, **kwargs)
    #  TypeError: object.__new__() takes no parameters
    #
    pass

msgClsByQName   = {}    # PROTO_NAME . MSG_NAME => class
fieldClsByQName = {}    # PROTO_NAME . MSG_NAME . FIELD_NAME => class

def makeMsgClass(parent, name):
    """ construct a MsgClass given a msg name known to the parent """
    msgSpec = parent.getMsgSpec(name)
    return _makeMsgClass(parent, msgSpec)

def _makeMsgClass(parent, msgSpec):
    """ construct a MsgClass given a MsgSpec """
    if parent is None:
        raise ValueError('parent must be specified')
    protoName = parent.name

    if msgSpec is None:
        raise ValueError('msgSpec be specified')

    # XXX single-dot name and so NO NESTED MSG_CLASSes
    qualName = '%s.%s' % (protoName, msgSpec.name)

    # DEBUG
    print('MAKE_MSG_CLASS for %s' % qualName)
    # END
    if qualName in msgClsByQName:
        return msgClsByQName[qualName]

    # build list of field classes -----------------------------------
    fieldClasses        = []
    fieldClassesByName  = {}
    fieldClassesByNbr   = {}        # by field nbr, not index
    # XXX implicit assumption is that fields are ordered by ascending
    # XXX field number
    for fieldSpec in msgSpec:
        # XXX NO ALLOWANCE FOR NESTED MSG_SPEC
        clz = makeFieldClass(qualName, fieldSpec)
        fieldClasses.append(clz)
        fieldClassesByName[ '%s.%s' % (qualName, fieldSpec.name)] = clz
        fieldClassesByNbr[fieldSpec.fieldNbr] = clz

    # class is not in cache, so construct ---------------------------
    d = {}
    d['__init__']   = msgInitter
    d['__slots__']  = [ '_name', '_enums', '_msgs', '_fieldClasses', 
                        '_fieldsClassesByName',     '_fieldsClassesByNbr',
                      ]
    # WORKING HERE ==============================
    for f in fieldClasses:
        # need uniquifier; cannot be just underscore
        d['__slots__'].append(str(f._name))
        d[f._name] = None
    # END HERE ==================================

    # we want a property for each item in the slots list
    d['_name']      = msgSpec.name
    d['name']       = msgSpec.name
    
    d['_enums']     = []      # enums visible at all levels; shd be immutable
    d['enums']      = property(myEnums)
    d['_msgs']      = []      # nested msgs, visible at all levels
    d['msgs']       = property(myMsgs)
    d['_fieldClasses'] = fieldClasses
    d['fieldClasses']  = property(myFieldClasses)

    # EXPERIMENT 12-12-15
    d['parentSpec']     = parent
    d['msgSpec']        = msgSpec
    # END EXPERIMENT

    # DEBUG =====================================
    print("MSG_IMPL DICTIONARY:")
    for key in d:
        print("  %-16s => %s" % (key, d[key]))
    # END =======================================

    C = MetaMsg( str(msgSpec.name), # name  MUST NOT BE UNICODE
                     (MsgImpl,),        # bases
                     d)                 # dictionry

    #----------------------------
    # possibly some more fiddling ...
    #----------------------------

    msgClsByQName[qualName] = C
    return C                        # GEEPGEEP

# -------------------------------------------------------------------
def makeFieldClass(dottedMsgName, fieldSpec):
    if dottedMsgName is None:   raise ValueError('null message name')
    if fieldSpec is None:       raise ValueError('null field spec')
    qualName = '%s.%s' % (dottedMsgName, fieldSpec.name)
    # DEBUG
    print('MAKE_FIELD_CLASS for %s' % qualName)
    # END
    if qualName in fieldClsByQName:   return fieldClsByQName[qualName]

    # DEBUG
    # won't work if FieldSpec has __slots__
    if '__dict__' in dir(FieldSpec):
        print("FieldSpec CLASS DICTIONARY excluding __doc__")
        for key in list(FieldSpec.__dict__.keys()):
            if key != '__doc__':
                print("    %-20s %s" % ( key, FieldSpec.__dict__[key]))
        print("fieldSpec INSTANCE DICTIONARY excluding __doc__")

    if '__dict__' in dir(fieldSpec):
        for key in list(fieldSpec.__dict__.keys()):
            if key != '__doc__':
                print("    %-20s %s" % ( key, fieldSpec.__dict__[key]))
    # END

    d = {}

    # XXX DISABLE __slots__ FOR DEBUGGING
    d['__slots__'] = ['_name', '_fType', '_quantifier',
                      '_fieldNbr', '_default',]

    # we want an attribute and a property for each fieldSpec attr
    d['_name']      = fieldSpec.name
    d['name']       = property(myName)
    d['_fType']     = fieldSpec.fTypeNdx
    d['fType']      = property(myFType)
    d['_quantifier']= fieldSpec.quantifier
    d['quantifier'] = property(myQuantifier)
    d['_fieldNbr']  = fieldSpec.fieldNbr
    d['fieldNbr']   = property(myFieldNbr)
    d['_default']   = fieldSpec.default
    d['default']    = property(myDefault)

    # this needs to be elaborated as appropriate to deal with the
    # 18 or so field types
    d['value']      = property(myValueGetter, myValueSetter)

    # 2016-02-19 adding '_' prefix caused small explosion of 
    #   '_name ... conflicts' errors
    # 2016-02-20 changing the prefix from '_' to '_QQQ_' had no effect
    #   on ValueErrors:
    #     "'_name' in __slots__ conficts with class variable"
    M = MetaField( '_QQQ_' + str(fieldSpec.name),   # name
                     (FieldImpl,),              # bases
                     d)                         # dictionry

    #----------------------------
    # possibly some more fiddling ...
    #----------------------------

    fieldClsByQName[qualName] = M
    return M

