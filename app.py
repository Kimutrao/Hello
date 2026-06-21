import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="나만의 투자 대시보드", layout="wide")
st.title("🚀 통합 투자 분석 & 개인 임장 노트")
st.write("나만의 부동산 대시보드 정식 오픈을 축하합니다!")

tab_market, tab_book = st.tabs(["📊 지역별 시세 흐름", "📖 투자 철학 전자책"])

with tab_market:
    st.subheader("임시 데이터 그래프 (구글 DB 연동 전)")
    
    # 임시 샘플 데이터 (화면이 잘 나오는지 확인용)
    chart_data = pd.DataFrame(
        np.random.randn(20, 3) * 0.5 + [10, 12, 14],
        columns=['단지A', '단지B', '단지C']
    )
    st.line_chart(chart_data)

with tab_book:
    st.header("제 1장. 맹신 금지의 법칙")
    st.markdown("대부분의 경우는 조회수와 광고를 위해 어그로를 끄는 것뿐입니다. 나의 상황에 맞는 투자를 해야 합니다.")