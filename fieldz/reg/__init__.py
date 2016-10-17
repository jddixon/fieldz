# ~/dev/py/fieldz/reg/__init__.py

__all__ = ['RegEntry',                      # abstract type
           'FieldTypeEntry',                # msgSpec constituents
           'CoreTypeEntry',                 # ill-conceived?
           'NodeReg', 'ProtoEntry',
           'ProtoReg', 'MsgReg',            # either may contain ...
           'MsgEntry', 'EnumEntry',         # either of these
           ]

from fieldz.msg_spec import validateDottedName
import fieldz.typed as T
from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.core_types as C
import fieldz.msg_spec as M

# BEGIN NEW CLASSES =================================================


class UniqueNameRegistry(object):
    """
    An abstract class which can be used with both the NodeReg and the
    ProtoReg, because both control regID generation, but not in this
    form with the MsgReg, which needs to obtain regIDs from the parent
    registry.
    """

    def __init__(self):
        self._entries = {}    # regID -> name XXX WAS A LIST
        self._name2RegID = {}    # name  -> regID, must be unique
        self._nextRegID = 0

    @property
    def nextRegID(self):
        return self._nextRegID

    def regID2Name(self, regID):
        if regID in self._entries:
            # return self._entries[regID].name # ELSEWHERE
            return self._entries[regID]     # HERE
        print("no name found in registry for regID %s" % str(regID))
        return None

    def getRegID(self):
        """
        Reserve the next free regID, step _nextRegID, and return the
        reserved value.
        """
        freeID = self._nextRegID
        # DEBUG
        print("GET_REG_ID: ASSIGNING ID %u" % freeID)
        # END
        self._nextRegID += 1
        return freeID

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, i):
        """ returns the actual entry, which is not immutable """
        return self._entries[i]

    def name2RegID(self, name):
        try:
            regID = self._name2RegID[name]
        except KeyError:
            regID = None
        return regID

    def register(self, whatever):
        """ subclasses must override """
        raise NotImplementedError()


class NodeReg(UniqueNameRegistry):
    """
    Maintains the list of protocols known to the XLattice node.
    """

    def __init__(self):
        super(NodeReg, self).__init__()

        # if newer versions of protocols have the same name, newer
        # replace older (but older may still be present and reachable
        # by hash)

        self._protosByHash = {}    # hash  -> regID: must be unique
        self._regID2Hash = {}    # regID -> content key

        # these are associated with fieldTypes and core classes
        self._putter = []   # methods, write instance field type to buffer
        self._getter = []   # methods, get instance field type from buffer
        self._lenFunc = []
        self._pLenFunc = []

        # initialize the lists above
        self.bootstrap()

    def register(self, protoSpec):
        """
        We convert the protoSpec to canonical form, then hash that
        to get the content key that uniquely identifies the protocol.
        """
        if protoSpec is None:
            raise ValueError('protoSpec cannot be None')

        # reduce the spec to canonical form
        canonical = None                # XXX STUB

        # ....

        # create a ProtoEntry
        protoEntry = None               # XXX STUB

        # register it
        regID = None
        if protoEntry is not None:
            regID = self._register(protoEntry)
        return regID

    def _register(self, entry):
        """ used to register both protoSpecs and basic types """

        # XXX CLEAN THIS UP
        # creation of the entry has used the next free regID
        self._nextRegID += 1            # so we step it

        self._entries[entry.regID] = entry

        name = entry.qualName

        # we maintain a list of type names
        self._name2RegID[name] = entry.regID

#       # DEBUG
#       print "%-20s => regiID %d" % (name, entry.regID)
#       # END

    def _registerBasicType(self, entry):
        # THIS IS A HACK, to make things compile
        self._register(entry)

    def bootstrap(self):
        # register the names of the core elements: field types and the
        # core classes

        # -- add fieldTypes -----------------------------------------
        for i in range(F.MAX_NDX + 1):
            entry = FieldTypeEntry(
                self,               # reg
                FS().asStr(i),        # qualName,
                T.tPutFuncs[i],     # putter,
                T.tGetFuncs[i])     # getter,
            self._registerBasicType(entry)

        cTypes = C.CoreTypes()
        for i in range(cTypes.maxNdx + 1):
            entry = CoreTypeEntry(
                self,               # reg
                cTypes.asStr(i),    # qualName,
                M.cPutFuncs[i],     # putter,
                M.cGetFuncs[i],     # getter,
                M.cLenFuncs[i],     # getter,
                M.cPLenFuncs[i])    # getter,
            self._registerBasicType(entry)


# -- MERGE INTO ABOVE, POSSIBLY ABSTRACTING SOME OF IT --------------
class xxxRegistry(object):

    def __init__(self):
        self._entries = []

        self._qualNames = []   # unique qualified (dotted) name list
        self._qName2regID = {}   # qualified name to content key
        # content key is hash of canonical string version of object
        self._qName2hash = {}   # qualified name to content key
        self._hash2regID = {}   # content key to unique ID

    def register(self, qName, rCanonical, putter, getter, lenFunc, pLenFunc):
        """
        Add a type to the registry's internal tables.  The canonical
        string serialization of the type is used to calculate a content
        key (160 bit SHA1 or 256 bit SHA3) for the type.  The caller
        must provide a putter, a method for serializing an instance of
        the type into a bytearray, and a getter, a method for deserializing
        an instance from a bytearray.
        """

        # XXX STUB - add some validation

        # THIS IS NOW JUST WRONG:
        entry = _DefinedRegEntry(
            qName,
            rCanonical,
            putter,
            getter,
            lenFunc,
            pLenFunc)
        self._register(entry)       # _uses_ the next free regID
        return entry._regID         # GEEP

    def _register(self, entry):
        # creation of the entry has used the next free regID
        self._nextRegID += 1            # so we step it
        self._entries.append(entry)
        name = entry.qualName

        # we maintain a list of type names
        self._qualNames.append(name)
        self._qName2regID[name] = entry.regID

#       # DEBUG
#       print "%-20s => regiID %d" % (name, entry.regID)
#       # END

        # we map names to the rCanonical hash  (which may be null)
        self._qName2hash[name] = entry.rCanonical

        # and we main a reverse map
        if entry.rCanonical is not None:
            self._hash2regID[entry.rCanonical] = entry.regID


# FOO

# -- BASIC TYPES, ALSO IN NODE REGISTRY -----------------------------

class RegEntry(object):
    __slots__ = ['_id', '_qualName', '_putter', '_getter',
                 '_lenFunc', '_pLenFunc', ]

    def __init__(self, reg, qualName, putter, getter,
                 lenFunc=None, pLenFunc=None):
        # XXX CURRENTLY NOT USED
        if reg is None:
            raise ValueError('reg may not be None')
        # END NOT USED

        if qualName is None:
            raise ValueError('qualName may not be None')
        if putter is None:
            raise ValueError('putter may not be None')
        if getter is None:
            raise ValueError('getter may not be None')
        # lenFunc and pLenFunc may be None

        M.validateDottedName(qualName)
        # XXX if the name is dotted the protocol must be defined.
        self._qualName = qualName

        # XXX these must be methods with the right signature :-)
        self._putter = putter
        self._getter = getter
        self._lenFunc = lenFunc
        self._pLenFunc = pLenFunc

        # XXX THIS IS A BAD IDEA.  If the entry cannot be created, we don't
        # want to have allocated an ID.  So create the entry and then
        # register it, allocating an ID at registration time
        self._id = reg.nextRegID             # MOVE ME XXX

    @property
    def regID(self): return self._id

    @property
    def qualName(self): return self._qualName

    @property
    def putter(self): return self._putter

    @property
    def getter(self): return self._getter

    @property
    def lenFunc(self): return self._lenFunc

    @property
    def pLenFunc(self): return self._pLenFunc               # GEEP


class FieldTypeEntry(RegEntry):

    def __init__(self, reg, qualName, putter, getter):
        super(FieldTypeEntry, self).__init__(reg, qualName, putter, getter)

    @property
    def rCanonical(self): return None


class CoreTypeEntry(RegEntry):
    __slots__ = ['_rCanonical', ]

    def __init__(self, reg, qualName, putter, getter, lenFunc, pLenFunc):
        super(
            CoreTypeEntry,
            self).__init__(
            reg,
            qualName,
            putter,
            getter,
            lenFunc,
            pLenFunc)

        # XXX STUB

    @property
    def rCanonical(self): return None                         # FOO

# -- PROTOCOLS ------------------------------------------------------


class ProtoEntry(object):
    """
    Used in NodeReg, contains information about specific protocol.
    """

    def __init__(self, nodeReg, protoSpec):
        self._nodeReg = nodeReg
        self._protoSpec = protoSpec
        self._reg = ProtoReg(nodeReg)  # nodeReg is parent


class ProtoReg(UniqueNameRegistry):
    """
    Contains information related to a specific protocol.
    """

    def __init__(self, name, nodeReg=None):
        super(ProtoReg, self).__init__()

        # FOR DEBUG ONLY
        self._name = name
        # END

        if nodeReg is None:
            nodeReg = NodeReg()
        self._nodeReg = nodeReg   # where to resolve protocol names

        self._putter = []   # methods, write instance field type to buffer
        self._getter = []   # methods, get instance field type from buffer
        self._lenFunc = []
        self._pLenFunc = []

        # populate the above four lists from the nodeReg
        for i in range(len(nodeReg._putter)):
            self._putter[i] = nodeReg._putter[i]
            self._getter[i] = nodeReg._getter[i]
            self._lenFunc[i] = nodeReg._lenFunc[i]
            self._pLenFunc[i] = nodeReg._pLenFunc[i]

    @property
    def nodeReg(self): return self._nodeReg

    def getRegID(self):
        """ get the next free regID from the parent """
        return self._nodeReg.getRegID()

    def _checkName(self, name):
        if self._nodeReg.name2RegID(name) is not None:
            raise RuntimeError(
                "name '%s' is already in the node registry" % name)
        if name in self._name2RegID:
            raise RuntimeError(
                "name '%s' is already in the protocol registry" % name)

    def addEnum(self, enumObj):
        name = enumObj.name
        print("DEBUG ADDING enum %s to ProtoReg" % name)
        self._checkName(name)
        regID = self.getRegID()   # reserve the next free regID and increment
        entry = EnumEntry(name, regID)

        # register
        self._entries[regID] = entry
        self._name2RegID[name] = regID
        return regID

    def addMsg(self, msgSpec):
        name = msgSpec.name
        self._checkName(name)
        regID = self.getRegID()   # reserve the next free regID and increment
        # DEBUG
        print(
            "    fielzd.reg.__init__.ProtoReg.addMsg: adding %d, '%s', to ProtoReg" % (
                regID, name))
        # END
        entry = MsgEntry(name, regID, self, msgSpec)

        # register
        self._entries[regID] = entry
        self._name2RegID[name] = regID
        return regID                        # GEEP

# -- MESSAGES -------------------------------------------------------


class MsgEntry(object):
    """
    Used in ProtoReg OR MsgReg; contains information about a MsgSpec (which
    might be nested).
    """
    __slots__ = ['_name', '_regID', '_parent', '_msgSpec', ]

    def __init__(self, name, regID, parent, msgSpec):
        self._name = name
        self._regID = regID
        self._parent = parent        # VALUE?
        self._msgSpec = msgSpec

    @property
    def name(self): return self._name

    @property
    def regID(self): return self._regID

    @property
    def parent(self): return self._parent

    @property
    def msgSpec(self): return self._msgSpec


class MsgReg(object):
    """
    Like a UniqueNameRegistry, but gets regIDs and name uniqueness
    guarantees from its ultimate parent, the protoReg.
    """

    def __init__(self, parentReg):
        if parentReg is None:
            raise ValueError('parentReg must not be None')
        self._parentReg = parentReg  # where to look if we can't resolve a name

        # The registry exists to allow us to distinguish these types
        # by name and to map regIDs back to types.
        self._enumEntries = {}    # enum specs nested within this msg spec
        self._msgEntries = {}    # message specs nested within this one
        self._name2RegID = {}    # names local to this message spec

        # XXX field names must also be distinct and MIGHT be tracked here
        self._fieldEntries = []    # this message's fields

    @property
    def parent(self): return self._parentReg

    def regID2Name(self, regID):
        if regID in self._enumEntries:
            return self._enumEntries[regID].name
        if regID in self._msgEntries:
            return self._msgEntries[regID].name
        return self._parentReg.regID2Name(regID)

    def __len_(self):
        return len(self._name2RegID)

    def getRegID(self):
        """ Get the next free regID from the parent registry. """
        return self._parentReg.getRegID()

    def name2RegID(self, name):
        if name in self._name2RegID:
            return self._name2RegID[name]
        else:
            return self._parentReg.name2RegID(name)

#   # XXX WRONG: what's added can be either a MsgSpec or an EnumSpec
#   def append(self, enum):
#       if enum is None:
#           raise ValueError('cannot add null enum')
#       name = enum.name
#       if name in self._name2RegID:
#           raise KeyError("we already have an enum '%s'" % name)

#       entry = EnumEntry( enum, len(self._enumEntries) )
#       self._name2RegID[name] = entry
#       self._enumEntries.append(entry)
#       # DEBUG
#       print "added '%s' to enumReg" % name
#       # END

#   def ndx(self, name):
#       if name in self._name2RegID:
#           return self._name2RegID[name].ndx
#       else:
#           return None                     # GEEP

    def _checkName(self, name):
        if self._parentReg.name2RegID(name) is not None:
            raise RuntimeError(
                "name '%s' is already in the parent registry" % name)
        if name in self._name2RegID:
            raise RuntimeError(
                "name '%s' is already in the message registry" % name)

    def addEnum(self, enumObj):
        name = enumObj.name
        print("DEBUG ADDING enum %s to ProtoReg" % name)
        self._checkName(name)
        regID = self.getRegID()   # reserve the next free regID and increment
        entry = EnumEntry(name, regID)

        # register
        self._enumEntries[regID] = entry
        self._name2RegID[name] = regID
        return regID

    def regID2Entry(self, regID):
        return self._msgEntries[regID]

    def addMsg(self, msgSpec):
        name = msgSpec.name
        self._checkName(name)
        regID = self.getRegID()   # reserve the next free regID and increment
        # DEBUG
        print(
            "    fielzd.reg.__init__.MsgReg.addMsg: adding %d, '%s', to ProtoReg" % (
                regID, name))
        # END
        entry = MsgEntry(name, regID, self, msgSpec)   # third arg is reg

        # register
        self._msgEntries[regID] = entry
        self._name2RegID[name] = regID
        return regID                        # GEEP

# -- ENUMS ----------------------------------------------------------


class EnumEntry(object):
    __slots__ = ['_name', '_regID', ]

    def __init__(self, name, regID):
        self._name = name
        self._regID = regID

    @property
    def name(self): return self._name

    @property
    def regID(self): return self._regID

    # XXX JUST A HACK

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
