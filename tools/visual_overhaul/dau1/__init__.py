"""DAU1 - Opal universal donor asset unlock.

Reusable, dependency-light (stdlib + Pillow) discovery / decode / render / catalog tooling for donor
animation assets.  Every parser is bounds-checked and raises ``DecodeError`` with a stable machine code
instead of guessing: a unit is only reported ``DECODED`` when real pixels were produced and validated.
"""
