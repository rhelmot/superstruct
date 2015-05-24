SuperStruct
===========

Python's `struct` module doesn't have enough data types. This should fix
that.

Right now the only additional formats it defines are the 128/256/512 bit
integers, signed and unsigned, but support should be coming soon for defining
arbitrary field types with bitfields.

Use `x`, `y`, or `z` to pack or unpack a 128/256/512 bit value, and the capital
versions to unpack an unsigned value.

Installing
----------

`$ python setup.py install`

Usage
-----

`>>> import superstruct as struct`

And consult Python's documentation on `struct`.

TODO
----

- Support the `pack_into` and similar methods from `struct`
- Support arbitrary bitfield creation
