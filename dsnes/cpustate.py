# Copyright 2017 Adrian Chan
# Licensed under GPLv3

class State:
    def __init__(self, e=None, m=None, x=None, c=None, dbr=None):
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

        self.dbr = None
        if dbr is not None:
            assert dbr >= 0 and dbr <= 0xff
            self.dbr = int(dbr)

    def clone(self):
        cls = self.__class__
        return cls(e=self.e, m=self.m, x=self.x, c=self.c, dbr=self.dbr)

    def encode(self):
        p = ""
        for flag in ("m", "x", "c", "e"):
            value = getattr(self, flag)
            if value is not None:
                value = bool(value)
                p += flag.upper() if value else flag
        if p:
            p = "p={}".format(p)

        b = ""
        if self.dbr is not None:
            b = "b={:x}".format(self.dbr)

        if any((p, b)):
            return " ".join((p, b))
        else:
            return None

    @classmethod
    def parse(cls, s):
        kwargs = {}
        p_lookup = {
            "e": {"e": False},
            "E": {"e": True},
            "m": {"m": False},
            "M": {"m": True},
            "x": {"x": False},
            "X": {"x": True},
            "c": {"c": False},
            "C": {"c": True}
        }

        parts = s.split(" ")
        for part in parts:
            kind = part[:2]
            data = part[2:]
            if kind == "p=":
                try:
                    for letter in data:
                        kwargs.update(p_lookup[letter])
                except LookupError:
                    raise ValueError(
                        "'{}' is not a valid CPU flags encoding".format(data))

            elif kind == "b=":
                dbr = int(data, base=16)
                kwargs["dbr"] = dbr

        if kwargs:
            return cls(**kwargs)
        else:
            if s:
                raise ValueError(
                    "'{}' is not a valid CPU state encoding".format(s))
            return None

    def __repr__(self):
        code = self.encode()
        if s:
            return "<{cls} {code}>".format(
                cls=self.__class__.__name__,
                code=code)
        else:
            return "<{cls}>".format(cls=self.__class__.__name__)
