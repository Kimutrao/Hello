import streamlit as st

# 1. 페이지 기본 설정 (가장 위에 있어야 함)
st.set_page_config(page_title="김철수의 투자기록실", layout="wide")

# 2. 공통 CSS 및 헤더 세팅
st.markdown("""
<style>
/* 여기에 이전에 쓰던 CSS 복사 */
</style>
""", unsafe_allow_html=True)

st.title("홈 화면: 🗺️ 전체 관심단지 지도")

# 3. 임시 DB 세팅 (구글 시트 연결 전까지 사용)
if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = { ... }

# 4. 홈 화면에 보여줄 내용 (예: 지도 코드)
st.write("여기에 홈 화면용 대형 지도가 들어갑니다.")
