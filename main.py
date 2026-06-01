import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="1980년 전후 기온 상승 비교",
    layout="wide"
)

st.title("🌍 1980년 전후 기온 상승 속도 비교")

st.markdown("""
서울 기상관측 자료를 이용하여

- 특정 연도 이전
- 특정 연도 이후

기온 상승 추세가 달라졌는지 확인합니다.

가설 예시:

> 1980년 이후 온난화 속도가 이전보다 빨라졌을 것이다.
""")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ta_20260601093156.csv")

    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str).str.strip(),
        errors="coerce"
    )

    df["연도"] = df["날짜"].dt.year

    annual = (
        df.groupby("연도")["평균기온(℃)"]
        .mean()
        .reset_index()
    )

    annual = annual.dropna()

    return annual

annual = load_data()

# -----------------------------
# 기준 연도 선택
# -----------------------------
st.sidebar.header("분석 설정")

split_year = st.sidebar.slider(
    "기준 연도",
    min_value=int(annual["연도"].min()) + 10,
    max_value=int(annual["연도"].max()) - 10,
    value=1980
)

before = annual[annual["연도"] < split_year]
after = annual[annual["연도"] >= split_year]

# -----------------------------
# 회귀분석
# -----------------------------
slope_before, intercept_before, r_before, p_before, _ = linregress(
    before["연도"],
    before["평균기온(℃)"]
)

slope_after, intercept_after, r_after, p_after, _ = linregress(
    after["연도"],
    after["평균기온(℃)"]
)

before_rate = slope_before * 10
after_rate = slope_after * 10

# -----------------------------
# 요약 지표
# -----------------------------
st.subheader("📊 상승률 비교")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        f"{split_year}년 이전",
        f"{before_rate:.2f} ℃ / 10년"
    )

with col2:
    st.metric(
        f"{split_year}년 이후",
        f"{after_rate:.2f} ℃ / 10년"
    )

with col3:
    st.metric(
        "차이",
        f"{(after_rate-before_rate):.2f} ℃ / 10년"
    )

# -----------------------------
# 그래프
# -----------------------------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=annual["연도"],
        y=annual["평균기온(℃)"],
        mode="lines",
        name="연평균 기온"
    )
)

fig.add_trace(
    go.Scatter(
        x=before["연도"],
        y=intercept_before + slope_before * before["연도"],
        mode="lines",
        name=f"{split_year} 이전 추세선"
    )
)

fig.add_trace(
    go.Scatter(
        x=after["연도"],
        y=intercept_after + slope_after * after["연도"],
        mode="lines",
        name=f"{split_year} 이후 추세선"
    )
)

fig.add_vline(
    x=split_year,
    line_dash="dash"
)

fig.update_layout(
    title="연평균 기온 변화와 추세선",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# 통계 결과
# -----------------------------
st.subheader("📈 회귀분석 결과")

result_df = pd.DataFrame(
    {
        "구간": [
            f"{split_year} 이전",
            f"{split_year} 이후"
        ],
        "상승률(℃/10년)": [
            round(before_rate, 3),
            round(after_rate, 3)
        ],
        "R²": [
            round(r_before**2, 3),
            round(r_after**2, 3)
        ],
        "p-value": [
            round(p_before, 5),
            round(p_after, 5)
        ]
    }
)

st.dataframe(
    result_df,
    use_container_width=True
)

# -----------------------------
# 자동 해석
# -----------------------------
st.subheader("🔍 자동 해석")

difference = after_rate - before_rate

if difference > 0:
    st.success(
        f"""
        {split_year}년 이후의 기온 상승 속도가
        이전보다 약 {difference:.2f} ℃/10년 더 빠르게 나타났습니다.
        """
    )
else:
    st.warning(
        f"""
        {split_year}년 이후의 기온 상승 속도가
        이전보다 약 {abs(difference):.2f} ℃/10년 더 느리게 나타났습니다.
        """
    )

# -----------------------------
# 원자료 보기
# -----------------------------
with st.expander("연평균 데이터 보기"):
    st.dataframe(
        annual,
        use_container_width=True
    )
