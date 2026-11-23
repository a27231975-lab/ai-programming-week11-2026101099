import pytest

from load_scores import load_scores


def test_정상_학생_목록을_읽는다(tmp_path):
    path = tmp_path / "normal.csv"
    path.write_text(
        "name,score\n"
        "김하나,88\n"
        "이두리,75\n"
        "박세찬,90\n"
        "윤보람,64\n"
        "서한별,95\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [
        ("김하나", 88),
        ("이두리", 75),
        ("박세찬", 90),
        ("윤보람", 64),
        ("서한별", 95),
    ]
    assert skipped == []


def test_빈_줄은_기록하지_않는다(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text(
        "name,score\n"
        "\n"
        "김하나,88\n"
        "\n"
        "이두리,75\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("이두리", 75)]
    assert skipped == []


def test_이름에_쉼표가_있어도_읽는다(tmp_path):
    path = tmp_path / "comma.csv"
    path.write_text(
        'name,score\n"김, 하나",88\n',
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김, 하나", 88)]
    assert skipped == []


def test_앞뒤_공백을_제거한다(tmp_path):
    path = tmp_path / "spaces.csv"
    path.write_text(
        "name,score\n  김하나  , 88 \n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88)]
    assert skipped == []


def test_동명이인은_둘_다_남긴다(tmp_path):
    path = tmp_path / "duplicates.csv"
    path.write_text(
        "name,score\n김하나,88\n김하나,75\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("김하나", 75)]
    assert skipped == []


def test_없는_파일은_예외가_발생한다(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(str(path))


def test_헤더만_있으면_빈_결과를_반환한다(tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text("name,score\n", encoding="utf-8")

    kept, skipped = load_scores(str(path))

    assert kept == []
    assert skipped == []


@pytest.mark.parametrize(
    "row, reason",
    [
        ("김하나", "열 개수가 2가 아님"),
        ("김하나,88,추가", "열 개수가 2가 아님"),
        (",88", "이름이 비어 있음"),
        ("   ,88", "이름이 비어 있음"),
        ("김하나,", "점수가 비어 있음"),
        ("김하나,abc", "점수가 정수가 아님"),
        ("김하나,88.5", "점수가 정수가 아님"),
    ],
)
def test_잘못된_행을_이유와_함께_기록한다(tmp_path, row, reason):
    path = tmp_path / "invalid.csv"
    path.write_text(
        f"name,score\n{row}\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == []
    assert skipped == [(2, row, reason)]


@pytest.mark.parametrize(
    "score, valid",
    [
        (-1, False),
        (0, True),
        (1, True),
        (99, True),
        (100, True),
        (101, False),
    ],
)
def test_점수_경계값(tmp_path, score, valid):
    path = tmp_path / "boundary.csv"
    path.write_text(
        f"name,score\n김하나,{score}\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    if valid:
        assert kept == [("김하나", score)]
        assert skipped == []
    else:
        assert kept == []
        assert skipped == [
            (2, f"김하나,{score}", "점수가 0~100 밖")
        ]


def test_오류_행_뒤에도_정상_행을_읽는다(tmp_path):
    path = tmp_path / "mixed.csv"
    path.write_text(
        "name,score\n"
        "김하나,88\n"
        "이두리,abc\n"
        "박세찬,90\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("박세찬", 90)]
    assert skipped == [
        (3, "이두리,abc", "점수가 정수가 아님")
    ]