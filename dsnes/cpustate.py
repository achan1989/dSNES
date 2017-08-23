# Copyright 2017 Adrian Chan
# Licensed under GPLv3

class State:
    def __init__(self, e=None, m=None, x=None, c=None):
        self.e = None
        if e is not None:
            self.e = bool(e)

        self.m = None
        if m is not None:
            self.m = bool(m)

        self.x = None
        if x is not None:
            self.x = bool(x)

        self.c = None
        if c is not None:
            self.c = bool(c)

    def clone(self):
        cls = self.__class__
        return cls(e=self.e, m=self.m, x=self.x, c=self.c)

    def encode(self):
        s = ""
        for flag in ("m", "x", "c", "e"):
            value = getattr(self, flag)
            if value is not None:
                value = bool(value)
                s += flag.upper() if value else flag
        return s or None

    @classmethod
    def parse(cls, s):
        lookup = {
            "e": {"e": False},
            "E": {"e": True},
            "m": {"m": False},
            "M": {"m": True},
            "x": {"x": False},
            "X": {"x": True},
            "c": {"c": False},
            "C": {"c": True}
        }
        kwargs = {}
        try:
            for letter in s:
                kwargs.update(lookup[letter])
        except LookupError:
            raise ValueError("'{}' is not a valid State encoding".format(s))
        if kwargs:
            return cls(**kwargs)
        else:
            return None

    def __repr__(self):
        flags = self.encode()
        if flags:
            return "<{cls} {flags}>".format(
                cls=self.__class__.__name__,
                flags=flags)
        else:
            return "<{cls}>".format(cls=self.__class__.__name__)
