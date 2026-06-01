import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import linregress

# ---------------------------------
# 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="서울 기온 변화 분석",
    page_icon="🌍",
    layout="wide"
)

# ---------------------------------
# 데이터 로드
# ---------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ta_20260601093156.csv")

    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
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

# ---------------------------------
# 헤더
# ---------------------------------
st.title("🌍 서울의 기온 상승은 언제부터 빨라졌을까?")

st.markdown("""
서울의 장기 기온 자료를 이용하여

**'1980년 이후 기온 상승 속도가 이전보다 빨라졌는가?'**

라는 가설을 확인해봅니다.

그래프와 회귀분석을 통해 특정 시점을 기준으로
기온 상승 추세가 얼마나 달라졌는지 비교할 수 있습니다.
""")

st.divider()

# ---------------------------------
# 사이드바
# ---------------------------------
st.sidebar.header("⚙️ 분석 설정")

split_year = st.sidebar.slider(
    "기준 연도",
    min_value=int(annual["연도"].min()) + 10,
    max_value=int(annual["연도"].max()) - 10,
    value=1980
)

# ---------------------------------
# 데이터 분리
# ---------------------------------
before = annual[annual["연도"] < split_year]
after = annual[annual["연도"] >= split_year]

# ---------------------------------
# 회귀분석
# ---------------------------------
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

# ---------------------------------
# 핵심 결과
# ---------------------------------
st.subheader("📊 핵심 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "이전 상승률",
        f"{before_rate:.2f} ℃",
        help="10년당 평균 상승 기온"
    )

with col2:
    st.metric(
        "이후 상승률",
        f"{after_rate:.2f} ℃",
        help="10년당 평균 상승 기온"
    )

with col3:
    st.metric(
        "증가폭",
        f"{difference:.2f} ℃"
    )

# ---------------------------------
# 그래프
# ---------------------------------
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
        name=f"{split_year} 이전 추세",
        line=dict(width=4)
    )
)

fig.add_trace(
    go.Scatter(
        x=after["연도"],
        y=intercept_after + slope_after * after["연도"],
        name=f"{split_year} 이후 추세",
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

# ---------------------------------
# 결과 해석
# ---------------------------------
st.subheader("🔍 결과 해석")

if difference > 0:
    st.success(
        f"""
        **{split_year}년 이후의 기온 상승 속도가 더 빠르게 나타났습니다.**

        - {split_year}년 이전: {before_rate:.2f} ℃ / 10년
        - {split_year}년 이후: {after_rate:.2f} ℃ / 10년

        즉, 이후 시기의 온난화 경향이 더 강하게 나타난다고 볼 수 있습니다.
        """
    )
else:
    st.info(
        f"""
        {split_year}년 이후 상승 속도가 이전보다 크지 않은 것으로 나타났습니다.

        기준 연도를 바꾸어 결과를 비교해보세요.
        """
    )

# ---------------------------------
# 통계 정보
# ---------------------------------
st.subheader("📋 통계 요약")

summary = pd.DataFrame({
    "구간": [f"{split_year} 이전", f"{split_year} 이후"],
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
    summary,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------
# 원자료
# ---------------------------------
with st.expander("📁 연평균 데이터 보기"):
    st.dataframe(
        annual,
        use_container_width=True
    )
