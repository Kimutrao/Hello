import streamlit as st
import datetime

# 페이지 기본 설정 (멀티 페이지 앱에서는 각 파일 최상단에 고유 타이틀 지정 가능)
st.set_page_config(page_title="김철수의 투자기록실", layout="wide", initial_sidebar_state="expanded")

# 공통 스타일 정의 (사이드바 메뉴 및 전역 폰트)
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif; }
.app-header { padding: 1rem 0 0.7rem 0; border-bottom: 2px solid #0288D1; margin-bottom: 1.2rem; }
.app-title { font-size: 1.6rem; font-weight: 700; color: #01579B; letter-spacing: -0.5px; }
.app-subtitle { font-size: 0.82rem; color: #777; margin-top: 2px; }
.result-box { background: #E8F5E9; border: 1.5px solid #66BB6A; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.result-box .r-label { font-size: 0.8rem; color: #555; margin-bottom: 2px; }
.result-box .r-value { font-size: 1.5rem; font-weight: 700; color: #1B5E20; }
.danger-box { background: #FFEBEE; border: 1.5px solid #E53935; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.timeline-box { background: #F9FBFD; border-left: 3px solid #0288D1; padding: 7px 11px; margin-bottom: 5px; border-radius: 0 5px 5px 0; }
.timeline-date { font-size: 0.74rem; color: #888; font-weight: 600; }
.timeline-content { font-size: 0.88rem; color: #222; margin-top: 2px; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <div class="app-title">📗 김철수의 투자기록실 포털</div>
  <div class="app-subtitle">부동산 입지 레이더 · 실전 투자 철학 아카이브 · 금융 금융 매크로</div>
</div>
""", unsafe_allow_html=True)

# ── 프로젝트 전역 공유 데이터베이스(Session State) 초기화 ──
if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지 (33평)': {'지역': '서울 마포구', '기본': '860세대, 2010년식', 'kb시세': 11.2, '호가_매매': 11.5, '호가_전세': 6.5, '전월거래량': 5, '특징': '초품아, 마포 상암', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴 (25평)': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', 'kb시세': 8.0, '호가_매매': 8.2, '호가_전세': 5.2, '전월거래량': 12, '특징': '신분당선 호매실 호재', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
    }
if 'geo_db' not in st.session_state:
    st.session_state['geo_db'] = {'상암월드컵파크10단지 (33평)': [37.5843, 126.8821], '호반베르디움더센트럴 (25평)': [37.2735, 126.9422]}

if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "1. 부동산 시장 접근과 매수 의미", "date": "2026-06", "content": "유의미한 상승이 지속될까? 잘 모르겠음. 이제 아파트 시장은 리스크 헷지 상품이 되어버림."},
        {"category": "규제 & 정책 분석", "title": "2. 영끌금지와 생존 세팅값", "date": "2026-06", "content": "장기간 더 버틸 수 있는 세팅값에 의미를 두는게 좋지 않을까."},
    ]
if 'dsr_loans' not in st.session_state: st.session_state['dsr_loans'] = []

# 홈 화면 대문 콘텐츠
st.subheader("👋 방문을 환영합니다")
st.write("왼쪽 사이드바 메뉴를 클릭하시면 각 탭별로 특화된 독립된 시스템 화면으로 이동하실 수 있습니다.")
st.markdown("""
- **🏢 관심단지 상세 분석**: 개별 아파트의 대형 입지 지도와 실거래 빨간 점 트렌드, 취득세 시뮬레이션을 모니터링합니다.
- **🧠 기록 & 게시판**: 월별 투자 철학 원문을 온전하게 보관하고 수정하는 네이버 카페형 인덱스 공간입니다.
- **💰 계산기 & 매크로**: DSR 계산기 및 자산 성장 복리 시뮬레이터, 실시간 환율 연동 지표를 제공합니다.
""")
