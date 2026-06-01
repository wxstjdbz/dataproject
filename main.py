import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import linregress

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="서울 기온 변화 탐구",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ta_20260601093156.csv")

    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    df["연도"] = df["날짜"].dt.year

    annual = (
        df.groupby("연도")["평균기온(℃)"]
        .mean()
        .reset_index()
    )

    return annual.dropna()

annual = load_data()

# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🌍 서울의 기온 상승은 1980년 이후 가속화되었을까?")

st.markdown("""
서울은 지난 100년 이상 꾸준히 기온이 관측된 지역입니다.

전 세계적으로는 1970~1980년대 이후 온난화가 뚜렷해졌다는 연구 결과가 많이 보고되고 있습니다.

그렇다면 **서울 역시 특정 시점을 기준으로 기온 상승 속도가 빨라졌을까요?**

이 웹앱은 서울의 장기 기온 자료를 이용하여
특정 연도 전후의 기온 상승 추세를 비교합니다.
""")

st.divider()

# --------------------------------------------------
# 분석 설정
# --------------------------------------------------
st.sidebar.header("분석 설정")

split_year = st.sidebar.slider(
    "비교 기준 연도",
    min_value=int(annual["연도"].min()) + 10,
    max_value=int(annual["연도"].max()) - 10,
    value=1980
)

before = annual[annual["연도"] < split_year]
after = annual[annual["연도"] >= split_year]

# --------------------------------------------------
# 회귀 분석
# --------------------------------------------------
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
difference = after_rate - before_rate

# --------------------------------------------------
# 분석 방법
# --------------------------------------------------
st.subheader("🔬 분석 방법")

st.markdown(f"""
1. 일별 평균기온을 이용하여 **연평균 기온**을 계산했습니다.
2. 데이터를 **{split_year}년 이전**과 **{split_year}년 이후**로 나누었습니다.
3. 각 구간에 선형회귀를 적용하여 기온 상승 추세를 계산했습니다.
4. 회귀선의 기울기를 이용해 **10년당 기온 상승량**을 비교했습니다.
""")

# --------------------------------------------------
# 핵심 결과
# --------------------------------------------------
st.subheader("📊 핵심 결과")

c1, c2, c3 = st.columns(3)

c1.metric(
    f"{split_year}년 이전",
    f"{before_rate:.2f} ℃",
    "10년당 상승"
)

c2.metric(
    f"{split_year}년 이후",
    f"{after_rate:.2f} ℃",
    "10년당 상승"
)

c3.metric(
    "상승 속도 차이",
    f"{difference:.2f} ℃"
)

# --------------------------------------------------
# 그래프
# --------------------------------------------------
st.subheader("📈 연평균 기온 변화")

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
        name=f"{split_year}년 이전 추세",
        line=dict(width=4)
    )
)

fig.add_trace(
    go.Scatter(
        x=after["연도"],
        y=intercept_after + slope_after * after["연도"],
        name=f"{split_year}년 이후 추세",
        line=dict(width=4)
    )
)

fig.add_vline(
    x=split_year,
    line_dash="dash"
)

fig.update_layout(
    height=650,
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    legend_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 결론
# --------------------------------------------------
st.subheader("🧠 결론")

if difference > 0:
    st.success(
        f"""
### 가설 지지

{split_year}년 이후의 기온 상승 속도는
이전보다 **{difference:.2f}℃/10년** 더 크게 나타났습니다.

- 이전 구간: {before_rate:.2f}℃/10년 상승
- 이후 구간: {after_rate:.2f}℃/10년 상승

따라서 서울의 장기 기온 자료는

> "{split_year}년 이후 온난화가 가속화되었다"

라는 가설을 뒷받침하는 경향을 보여줍니다.
"""
    )

else:
    st.warning(
        f"""
### 가설 미지지

이번 분석에서는 {split_year}년 이후의 상승 속도가
이전보다 크지 않은 것으로 나타났습니다.

- 이전 구간: {before_rate:.2f}℃/10년 상승
- 이후 구간: {after_rate:.2f}℃/10년 상승

즉, 현재 선택된 기준 연도에서는
온난화 가속 현상이 뚜렷하게 나타나지 않았습니다.
"""
    )

# --------------------------------------------------
# 통계 정보
# --------------------------------------------------
with st.expander("📋 통계 세부 결과 보기"):

    result = pd.DataFrame({
        "구간": [
            f"{split_year}년 이전",
            f"{split_year}년 이후"
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
    })

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# 데이터
# --------------------------------------------------
with st.expander("📁 연평균 데이터 보기"):
    st.dataframe(
        annual,
        use_container_width=True
    )
