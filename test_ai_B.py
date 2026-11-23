import pytest

from load_scores import load_scores


def test_정상_데이터를_순서대로_반환한다(tmp_path):
    path = tmp_path / "normal.csv"
    path.write_text(
        "name,score\n김하나,88\n이두리,75\n박세찬,90\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("이두리", 75), ("박세찬", 90)]
    assert skipped == []


def test_빈_줄은_오류로_기록하지_않는다(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text(
        "name,score\n\n김하나,88\n\n이두리,75\n\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("이두리", 75)]
    assert skipped == []


def test_이름_속_쉼표를_보존한다(tmp_path):
    path = tmp_path / "comma.csv"
    path.write_text(
        'name,score\n"김, 하나",88\n',
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김, 하나", 88)]
    assert skipped == []


def test_없는_파일은_FileNotFoundError를_발생시킨다(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(str(path))


def test_헤더만_있으면_두_목록이_빈다(tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text("name,score\n", encoding="utf-8")

    assert load_scores(str(path)) == ([], [])


@pytest.mark.parametrize(
    "잘못된행",
    [
        "이두리",
        "이두리,75,추가",
        ",75",
        "이두리,",
        "이두리,abc",
    ],
)
def test_잘못된_행을_기록하고_다음_행을_계속_읽는다(
    tmp_path, 잘못된행
):
    path = tmp_path / "invalid.csv"
    내용 = (
        "name,score\n"
        "김하나,88\n"
        f"{잘못된행}\n"
        "박세찬,90\n"
    )
    path.write_text(내용, encoding="utf-8")

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("박세찬", 90)]
    assert len(skipped) == 1

    줄번호, 원본행, 이유 = skipped[0]
    assert 줄번호 == 3
    assert 원본행 == 잘못된행
    assert isinstance(이유, str)
    assert 이유.strip() != ""

    # 입력 파일을 수정하지 않아야 한다.
    assert path.read_text(encoding="utf-8") == 내용


def test_동명이인을_임의로_제외하지_않는다(tmp_path):
    path = tmp_path / "same_name.csv"
    path.write_text(
        "name,score\n김하나,88\n김하나,91\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    assert kept == [("김하나", 88), ("김하나", 91)]
    assert skipped == []


@pytest.mark.parametrize(
    "점수, 유효한가",
    [
        (-1, False),
        (0, True),
        (1, True),
        (99, True),
        (100, True),
        (101, False),
    ],
)
def test_점수_허용_범위의_경계(tmp_path, 점수, 유효한가):
    path = tmp_path / "boundary.csv"
    path.write_text(
        f"name,score\n김하나,{점수}\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path))

    if 유효한가:
        assert kept == [("김하나", 점수)]
        assert skipped == []
    else:
        assert kept == []
        assert len(skipped) == 1
        assert skipped[0][0] == 2
        assert skipped[0][1] == f"김하나,{점수}"
        assert skipped[0][2].strip() != ""