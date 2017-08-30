# Copyright 2017 Adrian Chan
# Licensed under GPLv3

class State:
    VALID_VARS = ("e", "m", "x", "c", "b", "d")
    VALID_FLAGS_VALUES = (None, True, False)

    def __init__(self, e=None, m=None, x=None, c=None, b=None, d=None):
        self.e = e
        self.m = m
        self.x = x
        self.c = c
        self.b = b
        self.d = d

    @property
    def e(self):
        return self._e
    @e.setter
    def e(self, value):
        assert value in self.VALID_FLAGS_VALUES
        self._e = value

    @property
    def m(self):
        return self._m
    @m.setter
    def m(self, value):
        assert value in self.VALID_FLAGS_VALUES
        self._m = value

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        assert value in self.VALID_FLAGS_VALUES
        self._x = value

    @property
    def c(self):
        return self._c
    @c.setter
    def c(self, value):
        assert value in self.VALID_FLAGS_VALUES
        self._c = value

    @property
    def b(self):
        return self._b
    @b.setter
    def b(self, value):
        if value is None:
            self._b = None
        else:
            assert value >= 0 and value <= 0xff
            self._b = int(value)

    @property
    def d(self):
        return self._d
    @d.setter
    def d(self, value):
        if value is None:
            self._d = None
        else:
            assert value >= 0 and value <= 0xff
            self._d = int(value)

    def clone(self):
        cls = self.__class__
        return cls(
            e=self.e, m=self.m, x=self.x, c=self.c, b=self.b, d=self.d)

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
        if self.b is not None:
            b = "b={:x}".format(self.b)

        d = ""
        if self.d is not None:
            d = "d={:x}".format(self.d)

        parts = [part for part in (p, b, d) if part]
        if any(parts):
            return " ".join(parts)
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
                b = int(data, base=16)
                kwargs["b"] = b

            elif kind == "d=":
                d = int(data, base=16)
                kwargs["d"] = d

            else:
                raise ValueError(
                    "'{}' is not a valid CPU state encoding".format(s))

        if kwargs:
            return cls(**kwargs)
        else:
            if s:
                raise ValueError(
                    "'{}' is not a valid CPU state encoding".format(s))
            return None

    def __repr__(self):
        code = self.encode()
        if code:
            return "<{cls} {code}>".format(
                cls=self.__class__.__name__,
                code=code)
        else:
            return "<{cls}>".format(cls=self.__class__.__name__)
