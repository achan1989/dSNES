# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import pytest

from dsnes import State

def test_unknown():
    s = "unknown"
    state = State.parse(s)
    for var in ("e", "m", "x", "c", "b", "d"):
        assert getattr(state, var) is None
    assert state.encode() == s

def test_simple_1():
    s = "p=e"
    state = State.parse(s)
    assert state.e is False
    for var in ("m", "x", "c", "b", "d"):
        assert getattr(state, var) is None
    assert state.encode() == s

def test_simple_2():
    s = "b=12"
    state = State.parse(s)
    assert state.b == 0x12
    for var in ("m", "x", "c", "e", "d"):
        assert getattr(state, var) is None
    assert state.encode() == s

def test_simple_3():
    s = "d=80"
    state = State.parse(s)
    assert state.d == 0x80
    for var in ("m", "x", "c", "e", "b"):
        assert getattr(state, var) is None
    assert state.encode() == s

def test_combined_1():
    s = "p=MxE d=0"
    state = State.parse(s)
    assert state.m is True
    assert state.x is False
    assert state.c is None
    assert state.e is True
    assert state.b is None
    assert state.d == 0
    assert state.encode() == s

def test_combined_2():
    s = "d=10 b=f p=Cm"
    state = State.parse(s)
    assert state.m is False
    assert state.x is None
    assert state.c is True
    assert state.e is None
    assert state.b == 0xf
    assert state.d == 0x10
    assert state.encode() == "p=mC b=f d=10"

def test_bad():
    with pytest.raises(ValueError):
        State.parse("")
    with pytest.raises(ValueError):
        State.parse("p=Mx v")
    with pytest.raises(ValueError):
        State.parse("p=Mxq")
    with pytest.raises(ValueError):
        State.parse("d=potato")
    with pytest.raises(ValueError):
        State.parse("Δ+C")
