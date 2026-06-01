import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

st.set_page_config(
    page_title="기온 상승 전후 비교",
    layout="wide"
)

st.title("🌍 1980년 전후 기온 상승 속도 비교")
st.markdown("""
이 앱은 연평균 기온을 기반으로

- 특정 기준연도 이전
- 특정 기준연도 이후

의 기온 상승 추세를 비교합니다.
""")

uploaded_file = st.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

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

    st.subheader("기준 연도 설정")

    split_year = st.slider(
        "전후 비교 기준",
        min_value=int(annual["연도"].min()) + 10,
        max_value=int(annual["연도"].max()) - 10,
        value=1980
    )

    before = annual[annual["연도"] < split_year]
    after = annual[annual["연도"] >= split_year]

    slope_before, intercept_before, r_before, p_before, _ = linregress(
        before["연도"],
        before["평균기온(℃)"]
    )

    slope_after, intercept_after, r_after, p_after, _ = linregress(
        after["연도"],
        after["평균기온(℃)"]
    )

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
        title="연평균 기온 변화",
        xaxis_title="연도",
        yaxis_title="평균기온(℃)",
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📈 추세 비교")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            f"{split_year} 이전 상승률",
            f"{slope_before * 10:.2f} ℃ / 10년"
        )

        st.write(f"p-value: {p_before:.4f}")
        st.write(f"R²: {r_before**2:.3f}")

    with col2:
        st.metric(
            f"{split_year} 이후 상승률",
            f"{slope_after * 10:.2f} ℃ / 10년"
        )

        st.write(f"p-value: {p_after:.4f}")
        st.write(f"R²: {r_after**2:.3f}")

    st.subheader("🔍 해석")

    diff = (slope_after - slope_before) * 10

    if diff > 0:
        st.success(
            f"{split_year}년 이후 기온 상승 속도가 "
            f"약 {diff:.2f} ℃/10년 더 빠릅니다."
        )
    else:
        st.warning(
            f"{split_year}년 이후 기온 상승 속도가 "
            f"약 {abs(diff):.2f} ℃/10년 더 느립니다."
        )

    st.dataframe(annual)

else:
    st.info("CSV 파일을 업로드하세요.")
