<h1 class="libTop">fieldz</h1>

**fieldz** is a Python3 implementation of a protocol meant to be
generally compatible with Google's
[Protocol Buffers](https://developers.google.com/protocol-buffers).

## Field Types

There are currently 20 defined field types.  These fall into several
categories distinguished by the first one or two characters of the
type name:

* `f` for fixed-length
* `fs` for fixed-length, signed
* `fu` for fixed-length, unsigned
* `v` for variable-length
* `vs` for variable-length, signed
* `vu` for variable-length, unsigned
* `l` for length-encoded, meaning that the field begins with its
  length encoded as a variable length integer, a **varint**

Varints are used to efficiently store integer values in the smallest
possible number of bytes.

The actual field types are

* `vBool`, a boolean
* `vEnum`, an enum
* `vInt32`, a 32-bit integer
* `vInt64`, a 64-bit integer
* `vuInt32`, a 32-bit unsigned integer
* `vsInt32`, a 32-bit signed integer
* `vuInt64`, a 64-bit unsigned integer
* `vsInt64`, a 64-bit signed integer
* `fuInt32`, an unsigned 32-bit floating point value
* `fsInt32`, a signed 32-bit floating point value
* `fFloat`, a floating point number, a 32-bit value
* `fuInt64`, a fixed length unsigned integer
* `fsInt64`, a fixed lenth signed integer
* `fDouble`, a fixed length double, a 64-bit value
* `lString`, a varint L followed by a UTF-encoded string of that length
* `lBytes`, a varint L followed by L bytes
* `lMsg`, a varint L followed by a message declaration of that length
* `fBytes16`, a field of 16 bytes
* `fBytes20`, a string of 20 bytes, such as an SHA1 hash
* `fBytes32`, a string of 32 bytes, such as an SHA256 hash

## Acceptable Names

Acceptable field, message, and enum names consist of an alphabetic character
(which may be an underscore, '_')
followed by zero or more alphabetic characters, underscores, or digits.

So the following are acceptable names:

* `_abc123`

but the following are not acceptable:

* `5_abc123` (begins with a digit)
* `$abc123`  (contains a dollar sign)
* `a.b`      (contains a dot)

## Acceptable Protocol Names

Acceptable protocol names are like field and message names except that
they may be **dotted**.  That is, an acceptable protocol name consists of
one or more otherwise acceptable names; where there is more than one such
component name, the component names are separated by single dots ('.').
So any
name which is an acceptable message or field name is also an acceptable
protocol name.

Examples of acceptable protocol names:

* `a`
* `a_b.cd.ef`

Invalid protocol names:

* `a..b` (sequence of more than one dot)
* `.ab`  (leading dot)
* `ab.`  (trailing dot)

## Message Declarations

A message declaration describes the possibly recursive structure of a
message to be passed over the wire or stored compressed on disk.

A typical message looks like:

    message logEntry {
         timestamp  fuInt32
         nodeID     fBytes20
         key        fBytes20
         length     vuInt32
         by         lString
         path       lString
    }

Message names consist of an alphabetic character (which may be an underscore,
'_')
followed by zero or more alphabetic characters, underscores, or digits.  The
name must be followed in the declaration line by a colon (':').

Field declarations are usually indented below the `message`
line.

This particular message is called `logEntry`.  The message has six fields
but no constituent messages enums

## Protocol Declaration

A protocol declaration consists of a header line like

    protocol org.xlattice.zoggery

followed by zero or more enum and/or message declarations.


## Implementation Notes

*  [api](https://jddixon.github.io/fieldz//api.html)
*  [channels](https://jddixon.github.io/fieldz//channels.html)
*  [goals](https://jddixon.github.io/fieldz//goals.html)


## Project Status

Pre-alpha.  Code and unit tests exist, but some tests fail.

