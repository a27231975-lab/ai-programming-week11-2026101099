import pytest
from load_scores import load_scores
from helpers import 쓰기



def test_정상_파일을_읽는다():
    kept, skipped = load_scores("scores.csv")
    assert len(kept) == 5

def test_빈_줄은_건너뛴다(tmp_path):
    파일 = tmp_path / "blank_lines.csv"
    파일.write_text(
        "name,score\n"
        "\n"
        "김하나,88\n"
        "\n"
        "윤보람,64\n"
        "\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(파일))

    assert len(kept) == 2
    assert skipped == []

def test_이름에_쉼표가_있어도_읽는다(tmp_path):
    파일 = tmp_path / "comma_name.csv"
    파일.write_text(
        'name,score\n'
        '"김, 하나",88\n',
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(파일))

    assert kept == [("김, 하나", 88)]
    assert skipped == []

def test_없는_파일이면_오류가_난다():
    with pytest.raises(FileNotFoundError):
        load_scores("없는파일.csv")

def test_헤더만_있으면_빈_결과가_나온다():
    kept, skipped = load_scores("empty.csv")
    assert kept == []
    assert skipped == []

def test_경계1_0점은_유효하다():
    쓰기("경계0.csv", 0)

    kept, skipped = load_scores("경계0.csv")

    assert len(kept) == 1
    assert kept[0][1] == 0
    assert skipped == []

def test_경계2_100점은_유효하다():
    쓰기("경계100.csv", 100)

    kept, skipped = load_scores("경계100.csv")

    assert len(kept) == 1
    assert kept[0][1] == 100
    assert skipped == []

def test_경계3_101점은_무효하다():
    쓰기("경계101.csv", 101)

    kept, skipped = load_scores("경계101.csv")

    assert kept == []
    assert len(skipped) == 1

@pytest.mark.parametrize("점수, 유효한가", [
    (-1, False),
    (0, True),
    (1, True),
    (99, True),
    (100, True),
    (101, False),
])
def test_점수_경계값(점수, 유효한가):
    쓰기(f"임시.csv", 점수)
    kept, skipped = load_scores("임시.csv")
    assert (len(kept) == 1) == 유효한가

def test_이름이_비어_있으면_건너뛴다(tmp_path):
    파일 = tmp_path / "no_name.csv"
    파일.write_text("name,score\n,88\n", encoding="utf-8")

    kept, skipped = load_scores(str(파일))

    assert kept == []
    assert skipped == [(2, ",88", "이름이 비어 있음")]