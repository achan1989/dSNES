# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import pytest

from dsnes import State, StateDelta

def test_add_1():
    state = State()
    for var in ("m", "x", "c", "e", "b", "d"):
        assert getattr(state, var) is None

    s = "Δ+C"
    delta = StateDelta.parse(s)
    state = delta.apply(state)
    assert state.c is True
    for var in ("m", "x", "e", "b", "d"):
        assert getattr(state, var) is None

    assert delta.encode() == s

def test_add_2():
    state = State(x=True, b=0xff)

    s = "Δ+m b=03 d=a2"
    delta = StateDelta.parse(s)
    state = delta.apply(state)
    assert state.x is True
    assert state.m is False
    assert state.b == 0x03
    assert state.d == 0xa2

    assert delta.encode() == s

def test_add_3():
    state = State(c=False)

    s = "Δd=60"
    delta = StateDelta.parse(s)
    state = delta.apply(state)
    assert state.c is False
    assert state.d == 0x60

    assert delta.encode() == s

def test_clear():
    state = State(e=True, m=False, x=True, c=False, b=1, d=2)

    s = "Δ-ecd"
    delta = StateDelta.parse(s)
    state = delta.apply(state)
    assert state.e is None
    assert state.m is False
    assert state.x is True
    assert state.c is None
    assert state.b == 1
    assert state.d is None

    assert delta.encode() == s

def test_combined():
    state = State(e=True, b=0x13, d=0x66)

    s = "Δ-ed +X"
    delta = StateDelta.parse(s)
    state = delta.apply(state)
    assert state.e is None
    assert state.b == 0x13
    assert state.d is None
    assert state.x is True

    assert delta.encode() == "Δ+X -ed"

def test_bad():
    with pytest.raises(ValueError):
        StateDelta.parse("Δ+k")
    with pytest.raises(ValueError):
        StateDelta.parse("Δ+x x")
    with pytest.raises(ValueError):
        StateDelta.parse("Δ-p")
    with pytest.raises(ValueError):
        StateDelta.parse("Δb=100")
    with pytest.raises(ValueError):
        StateDelta.parse("b=12")


# for var in ("m", "x", "c", "e", "dbr", "dp"):
#     assert getattr(state, var) is None
