import pytest

def summa(a,b):
    return a + b

def test_summa():
    assert summa(2,3) == 5
    assert summa(4, 4) == 8