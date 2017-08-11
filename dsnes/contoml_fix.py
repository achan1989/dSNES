"""Fixes for contoml."""

# We use contoml's high-level API unchanged.
from contoml import loads, load, dumps, dump

# This is broken, let's fix it.
from contoml.file import TOMLFile

# Fixed version of TOMLFile.items()
def items(self):
    items = self._navigable.items()

    def has_anonymous_entry():
        return any(key == '' for (key, _) in items)

    if has_anonymous_entry():
        return items
    else:
        temp = dict(items)
        temp[''] = self['']
        return temp.items()
TOMLFile.items = items
