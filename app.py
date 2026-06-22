import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import datetime
import requests
import altair as alt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─────────────────────────────────────────
# 1. 페이지 설정 & 전역 CSS (초록/푸른색 톤 고도화, 붉은색 완전 제거)
# ─────────────────────────────────────────
st.set_page_config(
    page_title="김철수의 투자기록실",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif; }
:root {
    --green-50:  #EAF5E9; --green-100: #C8E6C9; --green-400: #66BB6A;
    --green-600: #388E3C; --green-800: #1B5E20;
    --blue-50:   #E1F5FE; --blue-100:  #B3E5FC; --blue-600:  #0288D1; --blue-800:  #01579B;
}
.app-header { padding: 1.2rem 0 0.8rem 0; border-bottom: 2px solid #0288D1; margin-bottom: 1.4rem; }
.app-title { font-size: 1.7rem; font-weight: 700; color: #01579B; letter-spacing: -0.5px; }
.app-subtitle { font-size: 0.85rem; color: #555; margin-top: 2px; }

/* 탭 스타일 */
div[data-baseweb="tab-list"] { gap: 4px; background: #E1F5FE; border-radius: 10px; padding: 4px 6px; }
button[data-baseweb="tab"] { border-radius: 8px !important; font-size: 0.85rem !important; font-weight: 500 !important; color: #0288D1 !important; background: transparent !important; border: none !important; padding: 6px 14px !important; transition: background 0.18s; }
button[data-baseweb="tab"][aria-selected="true"] { background: #0288D1 !important; color: #fff !important; }
button[data-baseweb="tab"]:hover:not([aria-selected="true"]) { background: #B3E5FC !important; }

/* 버튼 및 선택상자 푸른색/초록색 통일 */
.stButton > button { background-color: #0288D1 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 0.85rem !important; transition: background 0.18s; }
.stButton > button:hover { background-color: #01579B !important; }
div[data-baseweb="select"] > div { border-color: #0288D1 !important; border-radius: 8px !important; }
div[data-baseweb="tag"] { background-color: #B3E5FC !important; color: #01579B !important; }

/* 카드 스타일 */
.metric-card { background: #F1F8E9; border-left: 4px solid #388E3C; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
.metric-card h4 { margin: 0 0 4px 0; font-size: 0.75rem; color: #555; }
.metric-card .value { font-size: 1.4rem; font-weight: 700; color: #1B5E20; }
.section-divider { border: none; border-top: 1.5px solid #B3E5FC; margin: 1.2rem 0; }

/* 타임라인 스타일 */
.timeline-box { background: #F9FBFD; border-left: 3px solid #0288D1; padding: 8px 12px; margin-bottom: 6px; border-radius: 0 6px 6px 0; }
.timeline-date { font-size: 0.78rem; color: #666; font-weight: bold; }
.timeline-content { font-size: 0.9rem; color: #222; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 2. 전역 초기 데이터 세팅 (블로그 원문 전체 복원)
# ─────────────────────────────────────────
if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지': {'지역': '서울 마포구', '기본': '860세대, 2010년식', '매매가': '115000', '갭': '3억', '특징': '초품아, 마포 상암', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', '매매가': '82000', '갭': '2억', '특징': '신분당선 호매실 개통 예정', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
        '성복역롯데캐슬골드타운': {'지역': '경기 용인시', '기본': '2300세대, 2019년식', '매매가': '128000', '갭': '4억', '특징': '성복역 지하 통로 연결', 'history': [{'date': '2026-06-22', 'opinion': '신분당선 라인 대장급 입지.'}]}
    }

if 'geo_db' not in st.session_state:
    st.session_state['geo_db'] = {
        '상암월드컵파크10단지': [37.5843, 126.8821],
        '호반베르디움더센트럴': [37.2735, 126.9422],
        '성복역롯데캐슬골드타운': [37.3138, 127.0805]
    }

if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "1. 부동산 시장 접근과 매수 의미", "date": "2026-06", "content": """지난달 생각의 연장선에서. 유의미한 상승이 지속될까? 잘 모르겠음. 물음표. 이런 관점에서 투자대상으로서의 부동산은 유의미한가? 그럴 수도 아닐 수도. 거주대상으로서의 부동산은 유의미한가? 매우 그러함.\n\n이제 아파트 시장은 돈을 벌기 위함보다는 미래에 사지 못하게 되는 것을 경계하며 구매가 가능할 때 구매를 해둬야하는 리스크 헷지 상품이 되어버림. 없다면 무조건 매수를 해야하는 존재. 돈을 벌기 위함이라면 대체투자상품이 매우 많음. 그리고 현재 나라 상황상, 유주택자에게는 달러와 코인이 더 유의미해질 것 같음."""},
        {"category": "투자 마인드 & 철학", "title": "2. 임장의 의미 재정의", "date": "2026-06", "content": """임장도 이제 개념을 바꿔서 적용시켜야 하지 않을까. 많이 돌아다녀보는게 중요해짐. 가격을 비교하고 평가하는건 중요하지 않음. 동네의 특성, 분위기를 익혀야함. 도로 정비상태, 경사도, 혼잡도, 신호, 주변건물의 종류 등 현장에서만 알 수 있는 정보들이 무조건 있음.\n\n이런 정보들은 가격을 비교하기 위함이 아님. 나의 취향을 알고 선택하기 위해서 매우 중요. 과거처럼 거래를 자유롭게 할 수 없어짐. 돈의 문제가 아니라, 절차와 규제의 문제. 한번의 잘못된 선택으로 되돌리기가 힘들기 때문에 한번 할 때 최대한 나의 취향을 많이 반영시켜야함. 그걸 알기 위해서 임장을 많이 다녀야함. 가장 마음에 드는 동네를 찾기 위해서."""},
        {"category": "규제 & 정책 분석", "title": "3. 영끌금지와 생존 세팅값", "date": "2026-06", "content": """대한민국은 자유가 사라지는 중. 모든 분야 가리지 않고 규제, 제재가 생기고 있음. 부동산시장을 기준으로 대출규제 거래규제등을 통해 임차시장을 없애고 매매시장만 남겨놓으며 가격을 올림. 올라간 가격에 세금을 누진적으로 부과중.\n\n매수 가능한 사람을 없애버림. 매도를 할 수 밖에 없는 사람들을 만들어냄. 이런 시나리오 기준 주택 가격상승 = 세금증가, 대출규제 = 월 소득 외에 현금창출 불가, 확장재정 = 인플레, 고환율 = 생활비 부담 증가. 이미 정해진 경제상황. 영끌하다가 자칫하면 버티지 못하는 상황이 올 수도 있음. 조금 더 큰 수익을 얻기위해 과한 영끌을 하기 보다 장기간 더 버틸 수 있는 세팅값에 의미를 두는게 좋지 않을까. 1금융에서 해주는 정도의 대출만 실행. 40대 이후부터는 공격적인 대출 자제. 자산이 없는 30대라면 최대한 대출을 받는게 이득이긴 함."""},
        {"category": "투자 마인드 & 철학", "title": "4. 부동산 시장 관심의 경고", "date": "2026-06", "content": """관심이 없이 그냥 흘러가는대로 뒀더니 대출이 막히고 주택수 규제가 생기고 전월세 매물이 사라짐. 시간이 지나면 피해는 그대로 내게 다가옴. 실질 소득이 줄어들고 자산격차가 커지고 월세가 올라가는 문제는 전혀 중요하지 않을 정도. 전세 월세 매물이 없음. 외곽으로 점점 나가야함. 주거 자체가 불가능한 방향으로 가는 중. 부동산만큼은 관심을 빨리가지고 접근을 해야 준비를 할 수 있고 준비를 해둬야 5년 10년뒤에 피해자가 되는걸 막을 수 있음."""},
        {"category": "시장 전망 & 매크로", "title": "5. 과열 조짐과 공급 절벽의 미래", "date": "2026-04", "content": """매물기록 방법과 사이트를 바꿔보려고 새로운 기록을 시도 중. 매물숫자를 보니 어처구니가 없을 정도로 없다. 가격 Up, 거래량 Down, 매물 Down. 소량의 신고가가 전체 호가를 올리지만 거래량이 따라올 수 없는 상황. 개인적으론 흐름의 지속성에 대해서는 의문이 생김. 상승폭이 큰 곳들은 과열 느낌이며 신고가를 따라서 추격매수는 글쎄. 서울 중심부에서 가격이 안오른 물건보다 경기도 상대적으로 덜 오른 물건이 낫지 않을까."""},
        {"category": "규제 & 정책 분석", "title": "6. 전월세 공급과 수요 억제책의 역설", "date": "2025-10", "content": """24~25년 갱신이 만료되는 26~27년 사이 수요자 다수 발생. 28년까지 준공 물량 별로 없음. 대출규제는 수요가 줄어드는게 아니라 억누르고 있는 것뿐. 억눌린 수요는 매수가 가능한 시점이 오면 돈을 더 주더라도 억지로라도 매수를 하려고 함. 언제 못하게 될지 모르니까. 규제는 수요의 왜곡과 가격상승을 만듬. 전세가율로 매매가를 정하는 시대는 지남. 남들 얼마 벌었다 보지 말고 내가 가진 시드 기준(4~9억대)에서 기회를 찾아야 함."""},
        {"category": "규제 & 정책 분석", "title": "7. 대출 규제 포장과 사면 안되는 자산", "date": "2025-07", "content": """정부의 대출규제 요약해보면 실거주 1주택만 하라는 압박. 빌라, 오피스텔은 사망선고라 생각됨. 돈이 들어올 틈이 없어짐. 분양권도 실입주가 아니면 불가능한 구조. 가장 큰 이슈는 '소득증빙' 영역. 모든 항목이 국세청 소득이 잡혀있지 않으면 제한되는 방향으로 변함. 본업에 소홀하면 부동산 투자를 시작하는 것 조차 어려워짐. 소액으로 고수익을 쫓는건 부동산에서 할 수 있는 영역이 아님. 그만 찾고 시드 모아 한번에 좋은거 해야함."""},
        {"category": "자유 메모", "title": "8. 정권교체 시나리오와 대출 공부", "date": "2025-06", "content": """대출 상품과 조건이 너무 복잡함. 상환하고 다시 받는게 너무나도 무서운 상황. 대출 공부를 많이 한 사람과 안 한 사람의 차이가 벌어질 것. 규제가 생기면 매도 가능한 물건이 줄어들어 결국 정말 필요한 사람들만 눈물을 머금고 비싸게 사는 상황이 생길 수도 있음. 소상공인 입장에선 생활권이 서울이 아니라면 탈서울이 필수일 수도 있음. 신축 대단지 주변환경 조건값을 맞추면 적은 금액으로도 실거주 선택지가 많음."""},
        {"category": "투자 마인드 & 철학", "title": "9. 서민주거의 착각과 가치 정비", "code_date": "2025-05", "date":"2025-05", "content": """집값이 비싸다고 불만을 가진 사람, 무주택 서민을 보호해야 한다는 프레임에 갇힌 사람들과는 거리를 두어야 함. 부동산은 지역 이름보다 자신의 상황에 맞는 투자방법이 무엇일지 고민해야 함. 상급지 하급지 획일적 구분이 아니라 내 생활권 기준 접근성의 가성비를 봐야 함. 앞으로는 아파트 단지만 깨끗한 것보다 분당, 일산, 평촌처럼 주변 환경이 통째로 잘 정비된 곳의 가치가 훨씬 높아질 것임."""},
        {"category": "자유 메모", "title": "10. 실물 경기 체감과 소유의 기분", "date": "2025-02", "content": """체감경기가 상당히 안 좋음. 자영업자 소상공인이 힘든 구간이라 자산가격이 쉽게 상승할 여건은 아님. 결국 정치가 정리되면 경제 살리기를 위해 부동산 부양으로 시작할 수밖에 없음. 1주택자 기준에선 상급지 갈아타기를 위해 주택가격이 하락해야 부자가 될 가능성이 높아짐에도 대다수는 기분 때문에 오르기만 바람. 돈을 번 것 같은 '기분'과 '현실'을 철저히 구분해야 인생이 바뀜."""}
    ]

if 'board_view' not in st.session_state: st.session_state['board_view'] = 'list'
if 'current_post' not in st.session_state: st.session_state['current_post'] = None
if 'selected_cat' not in st.session_state: st.session_state['selected_cat'] = "전체글보기"

# ─────────────────────────────────────────
# 3. 탭 구성 (대출분석 매크로 탭으로 이동 완료)
# ─────────────────────────────────────────
tab_basic, tab_mind, tab_realestate, tab_finance = st.tabs([
    "📖 투자철학 요약", "🧠 기록 & 게시판", "🏢 특정지역별 관심단지 & 지도", "💰 계산기 & 자동 매크로"
])

# =================================================================
# 탭 1: 투자철학 요약
# =================================================================
with tab_basic:
    st.subheader("📖 흔들리지 않는 4가지 핵심 기준")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("💡 1. 부동산의 본질은 '리스크 헷지'", expanded=True):
            st.markdown("*\t돈을 벌기 위함이 아니라, 사지 못하게 되는 것을 막는 수단*\n* 알파 수익을 원한다면 달러, 미국 주식, 코인 등 대체재가 많습니다.\n* 현재 아파트는 무조건 매수해 두어야 하는 '주거 입장권'이자 생존 방어막입니다.")
        with st.expander("🔑 2. 영끌 금지와 개인의 상황"):
            st.markdown("*\t보편적인 정답은 없다. 오직 '나의 생애주기'만 있을 뿐.*\n* 자산이 없는 30대라면 최대한 대출을 당겨 자산을 선점하는 것이 맞습니다.\n* 하지만 소득 감소가 예상되는 40대 이상이라면 공격적인 대출은 독입니다.")
    with col2:
        with st.expander("🔇 3. 시장의 소음 구별법", expanded=True):
            st.markdown("*\t금액을 논하는 자는 멀리하고, 시대 흐름을 논하는 자를 곁에 두라.*\n* 하락장에선 비관론을, 상승장에선 무한 낙관론을 외치는 유튜버의 목적은 오직 '조회수'입니다.")
        with st.expander("💸 4. 세금을 계산하지 않은 투자는 허상"):
            st.markdown("*\t보유세와 거래세의 밸런스 게임*\n* 취득세, 양도세, 보유세 시뮬레이션 없이 무작정 주택 수만 늘리는 것은 빈 수레와 같습니다.")

# =================================================================
# 탭 2: 기록 & 게시판 (원문 포스트 독립 게시판 완성)
# =================================================================
with tab_mind:
    st.subheader("🧠 과거 기록실 (원문 전체 수록)")
    cat_list = ["전체글보기", "투자 마인드 & 철학", "규제 & 정책 분석", "시장 전망 & 매크로", "자유 메모"]
    col_menu, col_board = st.columns([2, 8])
    
    with col_menu:
        st.markdown("#### 📂 카테고리")
        selected_cat = st.radio("목록", cat_list, key="board_cat_radio", label_visibility="collapsed")
        if selected_cat != st.session_state['selected_cat']:
            st.session_state['selected_cat'] = selected_cat
            st.session_state['board_view'] = 'list'
            st.rerun()
        if st.button("✍️ 생각 작성하기", use_container_width=True):
            st.session_state['board_view'] = 'write'
            st.rerun()

    with col_board:
        if st.session_state['selected_cat'] == "전체글보기":
            display_posts = list(st.session_state['blog_db'])
        else:
            display_posts = [p for p in st.session_state['blog_db'] if p['category'] == st.session_state['selected_cat']]

        if st.session_state['board_view'] == 'write':
            st.markdown("#### ✏️ 새 글 작성")
            with st.form("write_form"):
                new_cat = st.selectbox("카테고리", cat_list[1:])
                new_title = st.text_input("제목")
                new_content = st.text_area("내용", height=300)
                if st.form_submit_button("등록"):
                    if new_title and new_content:
                        ym = datetime.datetime.now().strftime("%Y-%m")
                        st.session_state['blog_db'].insert(0, {"category": new_cat, "title": new_title, "content": new_content, "date": ym})
                        st.session_state['board_view'] = 'list'
                        st.rerun()
        elif st.session_state['board_view'] == 'read':
            post = st.session_state['current_post']
            if st.button("⬅️ 목록으로"):
                st.session_state['board_view'] = 'list'
                st.rerun()
            st.markdown(f"### {post['title']}")
            st.caption(f"분류: {post['category']} | 작성연월: {post['date']}")
            st.markdown('<hr style="border-top:1px solid #B3E5FC;">', unsafe_allow_html=True)
            st.write(post['content'].replace("\n", "<br>"), unsafe_allow_html=True)
        else:
            st.markdown(f"#### 📜 {st.session_state['selected_cat']}")
            for idx, post in enumerate(display_posts):
                with st.container():
                    c1, c2, c3 = st.columns([5, 3, 2])
                    with c1:
                        if st.button(post['title'], key=f"post_btn_{idx}_{post['title'][:3]}"):
                            st.session_state['current_post'] = post
                            st.session_state['board_view'] = 'read'
                            st.rerun()
                    with c2: st.caption(f"🔹 {post['category']}")
                    with c3: st.caption(f"📅 {post['date']}")
                    st.markdown("<hr style='margin:0px; padding:0px; border-top: 1px solid #E1F5FE;'>", unsafe_allow_html=True)

# =================================================================
# 탭 3: 특정지역별 관심단지 & 지도 (UX 대공사 + 주소 검색 + 수정/타임라인 연동)
# =================================================================
with tab_realestate:
    st.subheader("🏢 지역별 관심 단지 레이더 & 통합 임장노트")
    
    # 데이터 생성을 위한 백데이터 함수
    def get_mock_trends(apt_name):
        months = ['2025-01', '2025-04', '2025-07', '2025-10', '2026-01', '2026-04']
        base_prices = {'상암월드컵파크10단지': 11.2, '호반베르디움더센트럴': 8.1, '성복역롯데캐슬골드타운': 12.8}
        bp = base_prices.get(apt_name, 9.0)
        random.seed(len(apt_name))
        return pd.DataFrame([{'계약월': m, '아파트명': apt_name, '거래금액(억)': round(bp + random.uniform(-0.3, 0.3), 2)} for m in months])

    # 1/3 좌측 컨트롤 타워 (지역 카테고리 선선택 구조)
    col_panel, col_main_view = st.columns([3, 7])
    
    with col_panel:
        st.markdown("##### 📍 1단계: 지역 카테고리 선택")
        region_options = ["서울 마포구", "경기 수원시", "경기 용인시", "직접 추가"]
        selected_region = st.selectbox("조회할 지역구", region_options)
        
        # 해당 지역 단지 매칭
        apts_in_region = [name for name, info in st.session_state['memo_db'].items() if info.get('지역') == selected_region]
        
        st.markdown("##### 🏢 2단계: 관심 단지 목록")
        if not apts_in_region:
            st.caption("해당 지역에 등록된 관심 단지가 없습니다. 아래에서 새로 등록해 주세요.")
            chosen_apt = None
        else:
            chosen_apt = st.radio("상세 정보를 보실 단지를 선택하세요", apts_in_region)

        st.markdown('<hr style="border-top:1px solid #B3E5FC;">', unsafe_allow_html=True)
        st.markdown("##### ➕ 신규 단지 등록 및 위치 핀셋 검색")
        
        with st.form("new_apt_geo_form"):
            new_reg = st.text_input("지역명", value=selected_region if selected_region != "직접 추가" else "서울 ")
            new_name = st.text_input("단지명", placeholder="예: 녹번역e편한세상캐슬")
            search_addr = st.text_input("실제 주소 입력 (지도 매핑용)", placeholder="예: 서울 은평구 은평로 220")
            new_hh = st.text_input("세대수/연식", placeholder="2569세대, 2020년식")
            new_price = st.text_input("매매 호가 (억원)", placeholder="13.2억")
            new_gap = st.text_input("갭/전세가율", placeholder="5.5억 / 58%")
            new_feat = st.text_input("단지 주요 호재", placeholder="3호선 역세권, 초품아")
            new_op = st.text_area("첫 투자 의견", placeholder="주변 전세가 상승 추이 모니터링 필요")
            
            if st.form_submit_button("📍 주소 검색 및 대시보드 등록"):
                if new_name and search_addr:
                    try:
                        geolocator = Nominatim(user_agent="kimtaro_invest_app")
                        location = geolocator.geocode(search_addr, timeout=10)
                        if location:
                            st.session_state['geo_db'][new_name] = [location.latitude, location.longitude]
                            st.session_state['memo_db'][new_name] = {
                                '지역': new_reg, '기본': new_hh, '매매가': new_price, '갭': new_gap, '특징': new_feat,
                                'history': [{'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': new_op}]
                            }
                            st.success(f"🎯 위치 좌표 확인 완료 및 관심 리스트 등록 성공!")
                            st.rerun()
                        else:
                            st.error("주소를 찾지 못했습니다. 정확한 도로명 주소로 입력해 주세요.")
                    except Exception as e:
                        st.error("네트워크 허용 허들로 인해 기본 기본 좌표값으로 임시 매핑합니다.")
                        st.session_state['geo_db'][new_name] = [37.5665, 126.9780]
                        st.session_state['memo_db'][new_name] = {
                            '지역': new_reg, '기본': new_hh, '매매가': new_price, '갭': new_gap, '특징': new_feat,
                            'history': [{'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': new_op}]
                        }
                        st.rerun()

    # 2/3 우측 대형 뷰어 (지도 + 시세 가로 가독성 완성 + 타임라인식 업데이트 수정창)
    with col_main_view:
        if chosen_apt:
            apt_info = st.session_state['memo_db'][chosen_apt]
            coords = st.session_state['geo_db'].get(chosen_apt, [37.5665, 126.9780])
            
            # 메인 상단: 네이버형 인터랙티브 위경도 맵
            st.markdown(f"##### 🎯 {chosen_apt} 입지 레이더")
            m = folium.Map(location=coords, zoom_start=14)
            popup_html = f"<b>{chosen_apt}</b><br>호가: {apt_info.get('매매가','-')}억<br>갭: {apt_info.get('갭','-')}"
            folium.Marker(location=coords, popup=folium.Popup(popup_html, max_width=200), icon=folium.Icon(color='blue', icon='home')).add_to(m)
            st_folium(m, width=850, height=350, key=f"map_{chosen_apt}")
            
            # 메인 중단: 고개 돌리지 않는 시세 그래프 (X축 레이블 회전값 0도 고정)
            st.markdown("##### 📈 월별 실거래 평단가 트렌드")
            df_trend = get_mock_trends(chosen_apt)
            
            chart = alt.Chart(df_trend).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('계약월:O', title='계약월', axis=alt.Axis(labelAngle=0, labelFontSize=11)), # 0도 고정으로 가로 정렬 완성
                y=alt.Y('거래금액(억):Q', title='금액 (억원)', scale=alt.Scale(zero=False)),
                color=alt.Color('아파트명:N', scale=alt.Scale(range=['#0288D1']), legend=alt.Legend(title="단지명(동일 색상 매칭)")),
                tooltip=['계약월', '거래금액(억)']
            ).properties(height=220)
            st.altair_chart(chart, use_container_width=True)
            
            # 메인 하단: 데이터 정보 패널 및 연속 의견 업데이트 시스템 (날짜 무조건 누적 표시)
            st.markdown("##### 🗂️ 핵심 판단 지표 & 누적 코멘트 타임라인")
            
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1: st.metric("연식 및 세대수", apt_info.get('기본','-'))
            with col_d2: st.metric("현재 매매 호가", f"{apt_info.get('매매가','-')} 억")
            with col_d3: st.metric("현재 갭 / 전세가율", apt_info.get('갭','-'))
            
            # 타임라인식 연속 댓글/의견 표출 구조
            st.markdown("**📄 투자 의견 히스토리 (기록 날짜 의무 표기)**")
            for h in apt_info.get('history', []):
                st.markdown(f"""
                <div class="timeline-box">
                    <div class="timeline-date">📅 {h['date']} 작성</div>
                    <div class="timeline-content">{h['opinion']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # 수정 및 누적 추가 폼
            with st.form(f"append_comment_{chosen_apt}"):
                st.markdown("**✏️ 기존 정보 수정 및 추가 의견 업데이트**")
                up_price = st.text_input("매매 호가 수정", value=apt_info.get('매매가', ''))
                up_gap = st.text_input("갭 수정", value=apt_info.get('갭', ''))
                append_op = st.text_area("✍️ 새로운 임장 판단 추가 기록", placeholder="시간이 지나면서 바뀐 생각을 연이어 적어두세요.")
                
                if st.form_submit_button("💾 정보 업데이트 및 타임라인 누적"):
                    st.session_state['memo_db'][chosen_apt]['매매가'] = up_price
                    st.session_state['memo_db'][chosen_apt]['갭'] = up_gap
                    if append_op:
                        st.session_state['memo_db'][chosen_apt]['history'].append({
                            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
                            'opinion': append_op
                        })
                    st.success("데이터가 성공적으로 업데이트 및 누적 기록되었습니다.")
                    st.rerun()
        else:
            st.info("👈 왼쪽에서 분석 타겟 단지를 선택하시거나 신규 주소를 입력해 주세요.")

# =================================================================
# 탭 4: 계산기 & 자동 매크로 (대출 한도 계산기 이관 완료 + 실시간 환율 자동 갱신)
# =================================================================
with tab_finance:
    st.subheader("💰 고정 수식형 계산기 및 매크로 지표실")
    
    col_c1, col_c2 = st.columns([1, 1])
    
    with col_c1:
        st.markdown("#### 🔢 1. 적립식 복리 자산 계산기")
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            principal = st.number_input("초기 원금 (만원)", min_value=0, value=3000, step=100, key="tab4_p")
            rate_type = st.radio("수익률 기준", ["연 수익률(%)", "월 수익률(%)"], horizontal=True, key="tab4_rt")
            rate_val = st.number_input("수익률 입력", value=8.0, step=1.0, key="tab4_rv")
        with c_p2:
            monthly_addition = st.number_input("매월 추가 적립액 (만원)", min_value=0, value=100, step=10, key="tab4_ma")
            dur_type = st.radio("투자 기간 기준", ["년(Years)", "개월(Months)"], horizontal=True, key="tab4_dt")
            dur_val = st.number_input("투자 기간 입력", min_value=1, value=10, step=1, key="tab4_dv")

        total_months = dur_val if dur_type == "개월(Months)" else dur_val * 12
        monthly_rate = (rate_val / 100) if rate_type == "월 수익률(%)" else (rate_val / 100) / 12
        balance, invested_total, history = principal, principal, []
        for m in range(1, total_months + 1):
            balance += monthly_addition
            invested_total += monthly_addition
            balance += balance * monthly_rate
            history.append({"기간(월)": m, "총자산": balance, "누적원금": invested_total})
        df_calc = pd.DataFrame(history)
        final_amount = df_calc["총자산"].iloc[-1]
        gain = final_amount - invested_total

        st.markdown(f"""
        <div class="metric-card"><h4>최종 자산 결과</h4><div class="value">{final_amount/10000:,.2f} 억 원</div></div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("#### 🏦 2. 규제식 대출 한도 계산기 (이관 완료)")
        with st.container(border=True):
            st.markdown("**DSR 비율 시뮬레이션**")
            d_income = st.number_input("소득 증빙 연봉 (만원)", min_value=100, value=7000, step=500, key="tab4_income")
            d_debt = st.number_input("기존 포함 연간 원리금 상환총액 (만원)", min_value=0, value=2500, step=100, key="tab4_debt")
            if d_income > 0:
                dsr = (d_debt / d_income) * 100
                st.markdown(f"👉 **현재 산출 DSR:** **{dsr:.1f}%** (40% 초과 여부 확인 필수)")
        with st.container(border=True):
            st.markdown("**LTV 한도 시뮬레이션**")
            l_price = st.number_input("주택 기준 담보가 (만원)", min_value=1000, value=100000, step=1000, key="tab4_lprice")
            l_loan = st.number_input("신청 주담대 원금 (만원)", min_value=0, value=40000, step=1000, key="tab4_lloan")
            if l_price > 0:
                st.markdown(f"👉 **현재 산출 LTV:** **{(l_loan/l_price)*100:.1f}%**")

    # 하단 레이아웃: 10년치 최저임금 및 봇 기반 라이브 환율 갱신 시스템
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📊 3. 최근 10개년 최저시급 트렌드 및 실시간 환율 자동 매크로")
    
    # 무료 오픈 외부 API를 활용해, 사용자가 직접 수동으로 환율을 치지 않아도 시스템이 구동될 때 백그라운드에서 실시간 원달러 환율을 자동 스크래핑해오는 로직 탑재
    @st.cache_data(ttl=3600) # 1시간 단위 캐싱으로 서버 속도 유지
    def get_live_usd_exchange_rate():
        try:
            res = requests.get("https://open.er-api.com/v6/latest/USD").json()
            return round(res['rates']['KRW'], 1)
        except:
            return 1450.0 # 외부 통신 에러 발생 시 최신 백업 환율값 방어선 구축

    live_rate = get_live_usd_exchange_rate()
    st.caption(f"📢 현재 기준 실시간 원/달러 환율 매크로 수집 정보: **1 USD = {live_rate} 원** (자동 실시간 업데이트 중)")

    # 10개년 전수 데이터 셋
    wage_data = {
        '연도': ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026'],
        '최저시급(원)': [6470, 7530, 8350, 8590, 8720, 9160, 9620, 9860, 10030, 10320]
    }
    df_10y = pd.DataFrame(wage_data)
    # 실시간 가져온 라이브 환율을 10개년 데이터에 실시간 나누기 연산하여 달러 가치 변환 매크로 완성
    df_10y['달러환산(USD)'] = round(df_10y['최저시급(원)'] / live_rate, 2)

    base = alt.Chart(df_10y).encode(x=alt.X('연도:O', axis=alt.Axis(labelAngle=0)))
    bars = base.mark_bar(opacity=0.35, color='#66BB6A', width=25).encode(y=alt.Y('최저시급(원):Q', title='최저시급 (원)'))
    lines = base.mark_line(color='#0288D1', strokeWidth=3, point=True).encode(y=alt.Y('달러환산(USD):Q', title='달러 가치 (USD)'))
    
    st.altair_chart(alt.layer(bars, lines).resolve_scale(y='independent'), use_container_width=True)
    st.dataframe(df_10y.T, use_container_width=True)
