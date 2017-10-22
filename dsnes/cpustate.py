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
            if not (value >= 0 and value <= 0xff):
                raise ValueError("Value for b reg out of range")
            self._b = int(value)

    @property
    def d(self):
        return self._d
    @d.setter
    def d(self, value):
        if value is None:
            self._d = None
        else:
            if not (value >= 0 and value <= 0xff):
                raise ValueError("Value for d reg out of range")
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
            return "unknown"

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

        if s == "unknown":
            return cls()

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
                        "{!r} is not a valid CPU flags encoding".format(data))

            elif kind == "b=":
                b = int(data, base=16)
                kwargs["b"] = b

            elif kind == "d=":
                d = int(data, base=16)
                kwargs["d"] = d

            elif kind == "":
                continue

            else:
                raise ValueError(
                    "{!r} is not a valid CPU state encoding".format(s))

        if kwargs:
            return cls(**kwargs)
        else:
            raise ValueError(
                "{!r} is not a valid CPU state encoding".format(s))

    def __repr__(self):
        code = self.encode()
        if code:
            return "<{cls} {code}>".format(
                cls=self.__class__.__name__,
                code=code)
        else:
            return "<{cls}>".format(cls=self.__class__.__name__)


class StateDelta:
    def __init__(self, to_add, to_clear):
        for var, value in to_add:
            if var not in State.VALID_VARS:
                raise ValueError(
                    "{!r} is not a valid to_add item".format((var, value)))
            if var in ("b", "d"):
                if not (value >= 0 and value <= 0xff):
                    raise ValueError(
                        "Value for {} reg out of range".format(var))
        for var in to_clear:
            if var not in State.VALID_VARS:
                raise ValueError(
                    "{!r} is not a valid to_clear item".format(var))
        self.to_add = to_add
        self.to_clear = to_clear

    def clone(self):
        cls = self.__class__
        return cls(
            to_add=self.to_add[:], to_clear=self.to_clear[:])

    def apply(self, state):
        state = state.clone()
        for var, value in self.to_add:
            assert hasattr(state, var)
            setattr(state, var, value)
        for var in self.to_clear:
            assert hasattr(state, var)
            setattr(state, var, None)
        return state

    def encode(self):
        add = ""
        clear = ""
        b_str = ""
        d_str = ""

        add_lookup = {
            ("e", False): "e",
            ("e", True): "E",
            ("m", False): "m",
            ("m", True): "M",
            ("x", False): "x",
            ("x", True): "X",
            ("c", False): "c",
            ("c", True): "C"
        }

        for var, value in self.to_add:
            flag = add_lookup.get((var, value), None)
            if flag:
                add += flag
            elif var == "b":
                b_str = "b={:02x}".format(value)
            elif var == "d":
                d_str = "d={:02x}".format(value)
            else:
                raise ValueError(
                    "Invalid item in to_add: {!r}".format((var, value)))
        if add:
            add = "+{}".format(add)

        for var in self.to_clear:
            clear += var
        if clear:
            clear = "-{}".format(clear)

        parts = [part for part in (add, clear, b_str, d_str) if part]
        if any(parts):
            return " ".join(parts)
        else:
            return None

    @classmethod
    def parse(cls, s):
        add_lookup = {
            "e": ("e", False),
            "E": ("e", True),
            "m": ("m", False),
            "M": ("m", True),
            "x": ("x", False),
            "X": ("x", True),
            "c": ("c", False),
            "C": ("c", True)
        }
        to_add = []
        to_clear = []

        parts = s.split(" ")
        for part in parts:
            mod = part[:1]
            kind = part[:2]
            if mod == "+":
                data = part[1:]
                try:
                    for letter in data:
                        kvp = add_lookup[letter]
                        to_add.append(kvp)
                except LookupError:
                    raise ValueError(
                        "'{}' is not a valid delta state encoding".format(s))

            elif mod == "-":
                data = part[1:]
                for letter in data:
                    to_clear.append(letter)

            elif kind == "b=":
                data = part[2:]
                b = int(data, base=16)
                to_add.append(("b", b))

            elif kind == "d=":
                data = part[2:]
                d = int(data, base=16)
                to_add.append(("d", d))

            else:
                raise ValueError(
                    "'{}' is not a valid delta state encoding".format(s))

        return cls(to_add, to_clear)
