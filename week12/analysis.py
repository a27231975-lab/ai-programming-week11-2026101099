import pandas as pd

def 정제(df):
    # 1단계: 점수 결측치 삭제
    df = df.dropna(subset=['점수'])
    print("1단계 - 점수 결측치 삭제:", len(df), "행")

    # 2단계: 중복 행 제거
    df = df.drop_duplicates()
    print("2단계 - 중복 행 제거:", len(df), "행")
# 3단계: 공백 제거
    df['반'] = df['반'].str.strip()
    df['과목'] = df['과목'].str.strip()
    print("3단계 - 공백 제거:", len(df), "행")
    # 4단계: 점수 범위 확인
    df = df[(df['점수'] >= 0) & (df['점수'] <= 100)]
    print("4단계 - 점수 범위 확인:", len(df), "행")

    return df


# 반별 평균 계산 함수
def 반별평균(df):
    return df.groupby("반")["점수"].mean()


# 파일을 직접 실행할 때만 정제 실행
if __name__ == "__main__":
    df = pd.read_csv('scores_2026.csv')
    df_clean = 정제(df)

    df_clean.to_csv(
        'scores_2026_clean.csv',
        index=False,
        encoding='utf-8-sig'
    )

    print("최종 정제 완료:", len(df_clean), "행")