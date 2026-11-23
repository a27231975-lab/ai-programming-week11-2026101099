import pytest

from bug3_logic import find_max


def test_일반적인_목록의_최댓값():
    assert find_max([70, 85, 60, 95]) == 95


def test_첫번째_값이_최댓값():
    assert find_max([95, 85, 70, 60]) == 95


def test_원소가_하나인_목록():
    assert find_max([70]) == 70


def test_원소가_두개이고_마지막이_더_크다():
    assert find_max([60, 95]) == 95


def test_음수_목록의_최댓값():
    assert find_max([-30, -10, -20]) == -10


def test_빈_목록의_현재_예외():
    # 빈 목록의 명세는 별도로 없으므로 현재 구현의 예외를 확인한다.
    with pytest.raises(IndexError):
        find_max([])
        