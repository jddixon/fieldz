# ~/dev/py/fieldz/reg/__init__.py

__all__ = ['RegEntry',                      # abstract type
           'FieldTypeEntry',                # msgSpec constituents
           'CoreTypeEntry',                 # ill-conceived?
           'NodeReg', 'ProtoEntry',
           'ProtoReg', 'MsgReg',            # either may contain ...
           'MsgEntry', 'EnumEntry',         # either of these
           ]

from fieldz.msg_spec import validate_dotted_name
from fieldz.typed import T_GET_FUNCS, T_PUT_FUNCS
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
        self._name2reg_id = {}    # name  -> regID, must be unique
        self._next_reg_id = 0

    @property
    def next_reg_id(self):
        return self._next_reg_id

    def reg_id2name(self, reg_id):
        if reg_id in self._entries:
            # return self._entries[regID].name # ELSEWHERE
            return self._entries[reg_id]     # HERE
        print("no name found in registry for regID %s" % str(reg_id))
        return None

    def get_reg_id(self):
        """
        Reserve the next free regID, step _nextRegID, and return the
        reserved value.
        """
        free_id = self._next_reg_id
        # DEBUG
        print("GET_REG_ID: ASSIGNING ID %u" % free_id)
        # END
        self._next_reg_id += 1
        return free_id

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, i):
        """ returns the actual entry, which is not immutable """
        return self._entries[i]

    def name2reg_id(self, name):
        try:
            reg_id = self._name2reg_id[name]
        except KeyError:
            reg_id = None
        return reg_id

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

        self._protos_by_hash = {}    # hash  -> regID: must be unique
        self._reg_id2hash = {}    # regID -> content key

        # these are associated with fieldTypes and core classes
        self._putter = []   # methods, write instance field type to buffer
        self._getter = []   # methods, get instance field type from buffer
        self._len_func = []
        self._p_len_func = []

        # initialize the lists above
        self.bootstrap()

    @property
    def putter(self):
        return self._putter

    @property
    def getter(self):
        return self._getter

    @property
    def len_func(self):
        return self._len_func

    @property
    def p_len_func(self):
        return self._p_len_func

    def register(self, proto_spec):
        """
        We convert the protoSpec to canonical form, then hash that
        to get the content key that uniquely identifies the protocol.
        """
        if proto_spec is None:
            raise ValueError('protoSpec cannot be None')

        # reduce the spec to canonical form
        canonical = None                # XXX STUB

        # ....

        # create a ProtoEntry
        proto_entry = None               # XXX STUB

        # register it
        reg_id = None
        if proto_entry is not None:
            reg_id = self._register(proto_entry)
        return reg_id

    def _register(self, entry):
        """ used to register both protoSpecs and basic types """

        # XXX CLEAN THIS UP
        # creation of the entry has used the next free regID
        self._next_reg_id += 1            # so we step it

        self._entries[entry.reg_id] = entry

        name = entry.qual_name

        # we maintain a list of type names
        self._name2reg_id[name] = entry.reg_id

#       # DEBUG
#       print "%-20s => regiID %d" % (name, entry.regID)
#       # END

    def _register_basic_type(self, entry):
        # THIS IS A HACK, to make things compile
        self._register(entry)

    def bootstrap(self):
        # register the names of the core elements: field types and the
        # core classes

        # -- add fieldTypes -----------------------------------------
        for ndx in range(F.MAX_NDX + 1):
            entry = FieldTypeEntry(
                self,               # reg
                FS().as_str(ndx),        # qualName,
                T_PUT_FUNCS[ndx],     # putter,
                T_GET_FUNCS[ndx])     # getter,
            self._register_basic_type(entry)

        c_types = C.CoreTypes()
        for ndx in range(c_types.max_ndx + 1):
            entry = CoreTypeEntry(
                self,               # reg
                c_types.as_str(ndx),    # qualName,
                M.C_PUT_FUNCS[ndx],     # putter,
                M.C_GET_FUNCS[ndx],     # getter,
                M.C_LEN_FUNCS[ndx],     # getter,
                M.C_P_LEN_FUNCS[ndx])    # getter,
            self._register_basic_type(entry)


# -- MERGE INTO ABOVE, POSSIBLY ABSTRACTING SOME OF IT --------------
class XXXRegistry(object):

    def __init__(self):
        self._entries = []

        self._qual_names = []   # unique qualified (dotted) name list
        self._q_name2reg_id = {}   # qualified name to content key
        # content key is hash of canonical string version of object
        self._q_name2hash = {}   # qualified name to content key
        self._hash2reg_id = {}   # content key to unique ID

    def register(self, q_name, r_canonical, putter,
                 getter, len_func, p_len_func):
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
            q_name,
            r_canonical,
            putter,
            getter,
            len_func,
            p_len_func)
        self._register(entry)       # _uses_ the next free regID
        return entry.reg_id

    def _register(self, entry):
        # creation of the entry has used the next free regID
        self._next_reg_id += 1            # so we step it
        self._entries.append(entry)
        name = entry.qual_name

        # we maintain a list of type names
        self._qual_names.append(name)
        self._q_name2reg_id[name] = entry.reg_id

#       # DEBUG
#       print "%-20s => regiID %d" % (name, entry.regID)
#       # END

        # we map names to the rCanonical hash  (which may be null)
        self._q_name2hash[name] = entry.r_canonical

        # and we main a reverse map
        if entry.r_canonical is not None:
            self._hash2reg_id[entry.r_canonical] = entry.reg_id


# FOO

# -- BASIC TYPES, ALSO IN NODE REGISTRY -----------------------------

class RegEntry(object):
    __slots__ = ['_id', '_qual_name', '_putter', '_getter',
                 '_len_func', '_p_len_func', ]

    def __init__(self, reg, qual_name, putter, getter,
                 len_func=None, p_len_func=None):
        # XXX CURRENTLY NOT USED
        if reg is None:
            raise ValueError('reg may not be None')
        # END NOT USED

        if qual_name is None:
            raise ValueError('qualName may not be None')
        if putter is None:
            raise ValueError('putter may not be None')
        if getter is None:
            raise ValueError('getter may not be None')
        # lenFunc and pLenFunc may be None

        M.validate_dotted_name(qual_name)
        # XXX if the name is dotted the protocol must be defined.
        self._qual_name = qual_name

        # XXX these must be methods with the right signature :-)
        self._putter = putter
        self._getter = getter
        self._len_func = len_func
        self._p_len_func = p_len_func

        # XXX THIS IS A BAD IDEA.  If the entry cannot be created, we don't
        # want to have allocated an ID.  So create the entry and then
        # register it, allocating an ID at registration time
        self._id = reg.next_reg_id             # MOVE ME XXX

    @property
    def reg_id(self): return self._id

    @property
    def qual_name(self): return self._qual_name

    @property
    def putter(self): return self._putter

    @property
    def getter(self): return self._getter

    @property
    def len_func(self): return self._len_func

    @property
    def p_len_func(self): return self._p_len_func               # GEEP


class FieldTypeEntry(RegEntry):

    def __init__(self, reg, qual_name, putter, getter):
        super(FieldTypeEntry, self).__init__(reg, qual_name, putter, getter)

    @property
    def r_canonical(self): return None


class CoreTypeEntry(RegEntry):
    __slots__ = ['_rCanonical', ]

    def __init__(self, reg, qual_name, putter, getter, len_func, p_len_func):
        super(CoreTypeEntry, self).__init__(
            reg, qual_name, putter, getter, len_func, p_len_func)

        # XXX STUB

    @property
    def r_canonical(self): return None                         # FOO

# -- PROTOCOLS ------------------------------------------------------


class ProtoEntry(object):
    """
    Used in NodeReg, contains information about specific protocol.
    """

    def __init__(self, node_reg, proto_spec):
        self._node_reg = node_reg
        self._proto_spec = proto_spec
        self._reg = ProtoReg(node_reg)  # nodeReg is parent


class ProtoReg(UniqueNameRegistry):
    """
    Contains information related to a specific protocol.
    """

    def __init__(self, name, node_reg=None):
        super(ProtoReg, self).__init__()

        # FOR DEBUG ONLY
        self._name = name
        # END

        if node_reg is None:
            node_reg = NodeReg()
        self._node_reg = node_reg   # where to resolve protocol names

        self._putter = []   # methods, write instance field type to buffer
        self._getter = []   # methods, get instance field type from buffer
        self._len_func = []
        self._p_len_func = []

        # populate the above four lists from the nodeReg
        for i in range(len(node_reg.putter)):
            self._putter[i] = node_reg.putter[i]
            self._getter[i] = node_reg.getter[i]
            self._len_func[i] = node_reg.len_func[i]
            self._p_len_func[i] = node_reg.p_len_func[i]

    @property
    def node_reg(self): return self._node_reg

    def get_reg_id(self):
        """ get the next free regID from the parent """
        return self._node_reg.get_reg_id()

    def _check_name(self, name):
        if self._node_reg.name2reg_id(name) is not None:
            raise RuntimeError(
                "name '%s' is already in the node registry" % name)
        if name in self._name2reg_id:
            raise RuntimeError(
                "name '%s' is already in the protocol registry" % name)

    def add_enum(self, enum_obj):
        name = enum_obj.name
        print("DEBUG ADDING enum %s to ProtoReg" % name)
        self._check_name(name)
        reg_id = self.get_reg_id()   # reserve the next free regID and increment
        entry = EnumEntry(name, reg_id)

        # register
        self._entries[reg_id] = entry
        self._name2reg_id[name] = reg_id
        return reg_id

    def add_msg(self, msg_spec):
        name = msg_spec.name
        self._check_name(name)
        reg_id = self.get_reg_id()   # reserve the next free regID and increment
        # DEBUG
        print(
            "    fielzd.reg.__init__.ProtoReg.addMsg: adding %d, '%s', to ProtoReg" % (
                reg_id, name))
        # END
        entry = MsgEntry(name, reg_id, self, msg_spec)

        # register
        self._entries[reg_id] = entry
        self._name2reg_id[name] = reg_id
        return reg_id                        # GEEP

# -- MESSAGES -------------------------------------------------------


class MsgEntry(object):
    """
    Used in ProtoReg OR MsgReg; contains information about a MsgSpec (which
    might be nested).
    """
    __slots__ = ['_name', '_reg_id', '_parent', '_msg_spec', ]

    def __init__(self, name, reg_id, parent, msg_spec):
        self._name = name
        self._reg_id = reg_id
        self._parent = parent        # VALUE?
        self._msg_spec = msg_spec

    @property
    def name(self): return self._name

    @property
    def reg_id(self): return self._reg_id

    @property
    def parent(self): return self._parent

    @property
    def msg_spec(self): return self._msg_spec


class MsgReg(object):
    """
    Like a UniqueNameRegistry, but gets regIDs and name uniqueness
    guarantees from its ultimate parent, the protoReg.
    """

    def __init__(self, parent_reg):
        if parent_reg is None:
            raise ValueError('parentReg must not be None')
        self._parent_reg = parent_reg  # where to look if we can't resolve a name

        # The registry exists to allow us to distinguish these types
        # by name and to map regIDs back to types.
        self._enum_entries = {}    # enum specs nested within this msg spec
        self._msg_entries = {}    # message specs nested within this one
        self._name2reg_id = {}    # names local to this message spec

        # XXX field names must also be distinct and MIGHT be tracked here
        self._field_entries = []    # this message's fields

    @property
    def parent(self): return self._parent_reg

    def reg_id2name(self, reg_id):
        if reg_id in self._enum_entries:
            return self._enum_entries[reg_id].name
        if reg_id in self._msg_entries:
            return self._msg_entries[reg_id].name
        return self._parent_reg.reg_id2name(reg_id)

    def __len_(self):
        return len(self._name2reg_id)

    def get_reg_id(self):
        """ Get the next free regID from the parent registry. """
        return self._parent_reg.get_reg_id()

    def name2reg_id(self, name):
        if name in self._name2reg_id:
            return self._name2reg_id[name]
        else:
            return self._parent_reg.name2reg_id(name)

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

    def _check_name(self, name):
        if self._parent_reg.name2reg_id(name) is not None:
            raise RuntimeError(
                "name '%s' is already in the parent registry" % name)
        if name in self._name2reg_id:
            raise RuntimeError(
                "name '%s' is already in the message registry" % name)

    def add_enum(self, enum_obj):
        name = enum_obj.name
        print("DEBUG ADDING enum %s to ProtoReg" % name)
        self._check_name(name)
        reg_id = self.get_reg_id()   # reserve the next free regID and increment
        entry = EnumEntry(name, reg_id)

        # register
        self._enum_entries[reg_id] = entry
        self._name2reg_id[name] = reg_id
        return reg_id

    def reg_id2entry(self, reg_id):
        return self._msg_entries[reg_id]

    def add_msg(self, msg_spec):
        name = msg_spec.name
        self._check_name(name)
        reg_id = self.get_reg_id()   # reserve the next free regID and increment
        # DEBUG
        print(
            "    fielzd.reg.__init__.MsgReg.addMsg: adding %d, '%s', to ProtoReg" % (
                reg_id, name))
        # END
        entry = MsgEntry(name, reg_id, self, msg_spec)   # third arg is reg

        # register
        self._msg_entries[reg_id] = entry
        self._name2reg_id[name] = reg_id
        return reg_id                        # GEEP

# -- ENUMS ----------------------------------------------------------


class EnumEntry(object):
    __slots__ = ['_name', '_reg_id', ]

    def __init__(self, name, reg_id):
        self._name = name
        self._reg_id = reg_id

    @property
    def name(self): return self._name

    @property
    def reg_id(self): return self._reg_id

    # XXX JUST A HACK

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
