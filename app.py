import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import altair as alt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─────────────────────────────────────────
# 1. 페이지 설정 & 전역 CSS (붉은색 제거, 푸른색/초록색 톤앤매너)
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
    --blue-600:  #0288D1; --blue-800:  #01579B;
}
.app-header { padding: 1.2rem 0 0.8rem 0; border-bottom: 2px solid #388E3C; margin-bottom: 1.4rem; }
.app-title { font-size: 1.7rem; font-weight: 700; color: #1B5E20; letter-spacing: -0.5px; }
.app-subtitle { font-size: 0.85rem; color: #555; margin-top: 2px; }

/* 탭 스타일 */
div[data-baseweb="tab-list"] { gap: 4px; background: #F1F8E9; border-radius: 10px; padding: 4px 6px; }
button[data-baseweb="tab"] { border-radius: 8px !important; font-size: 0.85rem !important; font-weight: 500 !important; color: #388E3C !important; background: transparent !important; border: none !important; padding: 6px 14px !important; transition: background 0.18s; }
button[data-baseweb="tab"][aria-selected="true"] { background: #388E3C !important; color: #fff !important; }
button[data-baseweb="tab"]:hover:not([aria-selected="true"]) { background: #C8E6C9 !important; }

/* 공통 버튼 */
.stButton > button { background-color: #388E3C !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 0.85rem !important; transition: background 0.18s, transform 0.1s; }
.stButton > button:hover { background-color: #2E7D32 !important; transform: translateY(-1px); }

/* 카드 스타일 */
.metric-card { background: #F1F8E9; border-left: 4px solid #388E3C; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
.metric-card h4 { margin: 0 0 4px 0; font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 0.4px; }
.metric-card .value { font-size: 1.4rem; font-weight: 700; color: #1B5E20; }
.section-divider { border: none; border-top: 1.5px solid #C8E6C9; margin: 1.2rem 0; }

/* 데이터프레임 헤더 컬러 수정 */
div[data-testid="stDataFrame"] thead tr th { background-color: #E8F5E9 !important; color: #2E7D32 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 2. 헤더 & 세션 초기화 및 과거 기록 연동
# ─────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-title">📗 김철수의 투자기록실</div>
    <div class="app-subtitle">부동산 시세 분석 · 투자 철학 · 금융 기록</div>
</div>
""", unsafe_allow_html=True)

if 'memo_db' not in st.session_state: 
    # 부동산 탭과 시세비교 탭 연동을 위한 초기 데이터 바인딩
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지': {'기본': '860세대', '갭': '3억', '특징': '초품아, 마포 상암', '의견': 'DMC 직주근접 유효'},
        '호반베르디움더센트럴': {'기본': '1100세대', '갭': '2억', '특징': '신분당선 호매실 호재', '의견': '수원 권선구 중심선점'},
        '성복역롯데캐슬골드타운': {'기본': '2300세대', '갭': '4억', '특징': '성복역 지하 통로 연결', '의견': '신분당선 역세권 핵심단지'}
    }

# 과거 전달해주신 10편의 블로그 기록 데이터 피딩 (게시판 포맷 자동 안착)
if 'blog_db' not in st.session_state: 
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "26년 4월 부동산 생각기록", "date": "2026-04", "content": "매물숫자를 보니 어처구니가 없을 정도로 없다. 가격 Up, 거래량 Down, 매물 Down. 소량의 신고가가 전체 호가를 올리지만 거래량이 따라올 수 없는 상황이다. 개인적으론 흐름의 지속성에 대해서는 의문이 생김. 소유를 위한 것이라면 무조건 매수, 투자를 위한 것이라면 깊은 고민이 필요하다."},
        {"category": "규제 & 정책 분석", "title": "25년 10월 전월세 공급과 수요", "date": "2025-10", "content": "24~25년 갱신이 만료되는 26~27년 사이 수요자 다수 발생 예정. 28년까지 준공 물량 부족. 대출규제는 수요억제책일 뿐 수요의 왜곡과 가격상승을 만든다. 규제가 심해질수록 시장은 더욱 이상해진다. 내 시드 기준에서 살만한 4~9억대 기회를 찾아야 한다."},
        {"category": "규제 & 정책 분석", "title": "25년 7월 규제의 여파와 사면 안되는 물건", "date": "2025-07", "content": "정부 대출규제는 사실상 전세규제. 빌라와 오피스텔은 사망선고 수준으로 수요층 제한됨. 가장 큰 핵심 이슈는 '소득증빙' 영역이다. 국세청 소득이 잡히지 않으면 투자가 제한되는 방향으로 변하고 있다. 소액투자보다 시드를 모아 한번에 아파트 안전자산으로 가야 한다."},
        {"category": "시장 전망 & 매크로", "title": "25년 6월 대출 조건값과 정권교체 파급력", "date": "2025-06", "content": "DSR, 스트레스 DSR 등 대출 조건이 너무 복잡해짐. 공부한 자만이 살아남는다. 입법 행정 사법 모두 규제 강화 기조 유지 시 매도 물량이 줄어 호가 잔치가 벌어질 수 있음. 소상공인 입장에선 굳이 서울에 집착할 필요 없이 수도권 신축 대단지 가성비 선택지도 훌륭한 대안이다."},
        {"category": "투자 마인드 & 철학", "title": "25년 5월 서민주거 개념과 상황별 투자", "date": "2025-05", "content": "서민과 비서민을 유무주택으로 나누는 이분법을 경계하라. 부동산 투자는 지역 이름보다 자신의 상황(소득, 자녀, 맞벌이 등)에 집중해야 정답이 보인다. 앞으로는 단지만 깨끗한 곳보다 주변 인프라와 주거 정비가 통째로 잘 된 환경(분당, 일산 평촌 등)의 중요성이 커질 것이다."},
        {"category": "자유 메모", "title": "25년 3월 경기 체감과 부동산 부양 시나리오", "date": "2025-03", "content": "체감경기가 매우 안 좋고 소비가 줄어 자산가격 폭등은 어렵다. 하지만 내수 진작을 위해 결국 정부는 건설/토목업 등 부동산 경기 살리기 카드를 꺼낼 수밖에 없다. 큰 구역별 매크로 분석보다 내가 사고 싶은 단지 위주의 마이크로 접근이 유효한 케바케 시장이다."},
        {"category": "투자 마인드 & 철학", "title": "25년 2월 전문가 의견 차단과 다주택 전략", "date": "2025-02", "content": "Next(대안)가 없는 공포/희망회로 유튜버는 멀리하라. 1주택자 관점에선 상급지 이동을 위해 집값이 떨어지는 게 절대적으로 유리하지만 자본주의 특성상 하락은 제한적이다. 진짜 유의미한 투자 수익률 싸움을 하려면 철저한 세법 학습을 바탕으로 한 다주택 세팅 전략으로 가야 한다."},
        {"category": "자유 메모", "title": "25년 1월 타이밍과 폭망한 부동산 시장의 틈새", "date": "2025-01", "content": "신축 아파트를 제외한 상가, 빌라, 오피, 지방/구축은 멸망한 상태. 규제가 꼬여있어 상급지 똘똘한 한채 쏠림이 지속되나 이 실타래가 풀릴 때 천대받던 물건들이 기회를 줄 수 있다. 지금 25년도에 20년도 가격으로 살 수 있는 낙폭 과대 구축들은 인플레 저장 수단으로 훌륭하다."},
        {"category": "시장 전망 & 매크로", "title": "24년 12월 환율, 미국주식 그리고 국내 자본이동", "date": "2024-12", "content": "계엄/탄핵 정국 이후 시장 급랭. 급매를 잡기 가장 좋은 시기다. 미국 주식과 비트코인이 신이 되어 돈이 몰려있지만, 자산시장은 영원히 한쪽만 오르지 않는다. 가성비 영역에 도달한 국내 부동산 시장으로 돈이 되돌아오는 사이클이 분명히 오니 체력과 멘탈을 유지하며 세팅을 기다려라."},
        {"category": "투자 마인드 & 철학", "title": "24년 11월 대출규제 효과와 주택 소유욕의 본질", "date": "2024-11", "content": "대출규제로 거래량이 급감한 것을 가격 안정이란 착시로 보면 안 됨. 주택은 인스타형 인정욕구와 공간 소유욕이 결합한 자산이기에 가치가 쉽게 소멸하지 않는다. 내 인생을 바꾸기 위해 필요한 하나의 든든한 실물 디딤돌 자산으로 부동산을 정의하고 접근해야 상급지 집착에서 자유롭다."}
    ]

if 'board_view' not in st.session_state: st.session_state['board_view'] = 'list'
if 'current_post' not in st.session_state: st.session_state['current_post'] = None
if 'selected_cat' not in st.session_state: st.session_state['selected_cat'] = "전체글보기"

# ─────────────────────────────────────────
# 3. 탭 레이아웃
# ─────────────────────────────────────────
tab_basic, tab_mind, tab_realestate, tab_finance, tab_price = st.tabs([
    "📖 투자철학 요약", "🧠 기록 & 게시판", "🏢 부동산 & 대출", "💰 복리 계산기 & 매크로", "📊 시세비교 & 지도"
])

# ═══════════════════════════════════════════
# 탭 1: 투자철학 요약
# ═══════════════════════════════════════════
with tab_basic:
    st.subheader("📖 흔들리지 않는 4가지 핵심 기준")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("💡 1. 부동산의 본질은 '리스크 헷지'", expanded=True):
            st.markdown("*\t돈을 벌기 위함이 아니라, 사지 못하게 되는 것을 막는 수단*\n* 알파 수익을 원한다면 달러, 미국 주식, 코인 등 대체재가 많습니다.\n* 현재 아파트는 무조건 매수해 두어야 하는 '주거 입장권'이자 생존 방어막입니다.")
        with st.expander("🔑 2. 영끌 금지와 개인의 상황"):
            st.markdown("*\t보평적인 정답은 없다. 오직 '나의 생애주기'만 있을 뿐.*\n* 자산이 없는 30대라면 최대한 대출을 당겨 자산을 선점하는 것이 맞습니다.\n* 하지만 소득 감소가 예상되는 40대 이상이라면 공격적인 대출은 독입니다.")
    with col2:
        with st.expander("🔇 3. 시장의 소음 구별법", expanded=True):
            st.markdown("*\t금액을 논하는 자는 멀리하고, 시대 흐름을 논하는 자를 곁에 두라.*\n* 하락장에선 비관론을, 상승장에선 무한 낙관론을 외치는 유튜버의 목적은 오직 '조회수'입니다.")
        with st.expander("💸 4. 세금을 계산하지 않은 투자는 허상"):
            st.markdown("*\t보유세와 거래세의 밸런스 게임*\n* 취득세, 양도세, 보유세 시뮬레이션 없이 무작정 주택 수만 늘리는 것은 빈 수레와 같습니다.")

# ═══════════════════════════════════════════
# 탭 2: 기록 & 게시판 (네이버 카페 연월 표기형 게시판 완성)
# ═══════════════════════════════════════════
with tab_mind:
    st.subheader("🧠 과거 기록실 & 게시판")
    cat_list = ["전체글보기", "투자 마인드 & 철학", "규제 & 정책 분석", "시장 전망 & 매크로", "자유 메모"]
    col_menu, col_board = st.columns([2, 8])
    
    with col_menu:
        st.markdown("#### 📂 카테고리")
        selected_cat = st.radio("목록", cat_list, label_visibility="collapsed")
        if selected_cat != st.session_state['selected_cat']:
            st.session_state['selected_cat'] = selected_cat
            st.session_state['board_view'] = 'list'
            st.rerun()
        st.write("")
        if st.button("✍️ 글쓰기", use_container_width=True):
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
                        import datetime
                        ym = datetime.datetime.now().strftime("%Y-%m")
                        st.session_state['blog_db'].insert(0, {"category": new_cat, "title": new_title, "content": new_content, "date": ym})
                        st.session_state['board_view'] = 'list'
                        st.rerun()
        elif st.session_state['board_view'] == 'read':
            post = st.session_state['current_post']
            if st.button("목록으로 돌아가기"):
                st.session_state['board_view'] = 'list'
                st.rerun()
            st.markdown(f"### {post['title']}")
            st.caption(f"분류: {post['category']} | 작성연월: {post['date']}")
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.write(post['content'])
        else:
            st.markdown(f"#### 📜 {st.session_state['selected_cat']} ({len(display_posts)}편)")
            for idx, post in enumerate(display_posts):
                with st.container():
                    c1, c2, c3 = st.columns([5, 3, 2])
                    with c1:
                        if st.button(post['title'], key=f"p_{idx}"):
                            st.session_state['current_post'] = post
                            st.session_state['board_view'] = 'read'
                            st.rerun()
                    with c2: st.caption(f"🔹 {post['category']}")
                    with c3: st.caption(f"📅 {post['date']}")
                    st.markdown("<hr style='margin:0px; padding:0px; border-top: 1px solid #EAF5E9;'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 탭 3: 부동산 & 대출 (DSR 경고 색상 푸른색/초록색 변경 완료)
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 부동산 임장 노트 및 대출 계산기")
    col_memo, col_loan = st.columns([1, 1])
    
    with col_memo:
        st.markdown("#### 📝 단지별 임장 메모 관리")
        with st.form("realestate_memo_form"):
            apt_name = st.text_input("단지명", placeholder="예: 상암월드컵파크10단지")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                apt_hh = st.text_input("세대수/연식", placeholder="예: 860세대, 2010년식")
                apt_gap = st.text_input("현재 갭/전세가율", placeholder="예: 갭 3억, 65%")
            with c_m2:
                apt_feat = st.text_input("주요 특징/호재", placeholder="예: 초품아, DMC 인접")
                apt_opinion = st.text_input("💡 투자의견", placeholder="예: 11억 이하 진입 검토")
            if st.form_submit_button("단지 메모 저장"):
                st.session_state['memo_db'][apt_name] = {'기본': apt_hh, '갭': apt_gap, '특징': apt_feat, '의견': apt_opinion}
                st.success("데이터베이스에 임장 노트가 연동·저장되었습니다!")
                st.rerun()
                
        if st.session_state['memo_db']:
            for name, info in st.session_state['memo_db'].items():
                with st.expander(f"🏠 {name}"):
                    st.write(f"- **기본정보**: {info.get('기본', '-')} | **특징**: {info.get('특징', '-')}")
                    st.write(f"- **갭/전세**: {info.get('갭', '-')} | **의견**: {info.get('의견', '-')}")

    with col_loan:
        st.markdown("#### 🏦 대출 한도 분석")
        with st.container(border=True):
            st.markdown("**1. DSR 계산**")
            dsr_income = st.number_input("연소득 (만원)", min_value=100, value=7000, step=500)
            dsr_debt = st.number_input("연간 원리금 상환액 (만원)", min_value=0, value=2500, step=100)
            if dsr_income > 0:
                dsr_result = (dsr_debt / dsr_income) * 100
                # 붉은색 필터 제거 후 진한 네이비(블루 계열) 지표로 교체
                color = "#01579B" if dsr_result > 40 else "#1B5E20" 
                st.markdown(f"👉 **나의 DSR:** <span style='color:{color}; font-weight:bold; font-size:1.2rem;'>{dsr_result:.1f}%</span> (기준점 40%)", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("**2. LTV 계산**")
            ltv_price = st.number_input("주택 기준가격 (만원)", min_value=1000, value=100000, step=1000)
            ltv_loan = st.number_input("주택담보대출 신청액 (만원)", min_value=0, value=40000, step=1000)
            if ltv_price > 0:
                ltv_result = (ltv_loan / ltv_price) * 100
                st.markdown(f"👉 **나의 LTV:** <span style='color:#1B5E20; font-weight:bold; font-size:1.2rem;'>{ltv_result:.1f}%</span>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 탭 4: 복리 계산기 & 매크로
# ═══════════════════════════════════════════
with tab_finance:
    st.subheader("💰 적립식 복리 계산기 & 성장 그래프")
    col_calc1, col_calc2 = st.columns([1, 1])
    with col_calc1:
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            principal = st.number_input("초기 원금 (만원)", min_value=0, value=3000, step=100)
            rate_type = st.radio("수익률 기준", ["연 수익률(%)", "월 수익률(%)"], horizontal=True)
            rate_val = st.number_input("수익률 입력", value=8.0, step=1.0)
        with c_p2:
            monthly_addition = st.number_input("매월 추가 적립액 (만원)", min_value=0, value=100, step=10)
            dur_type = st.radio("투자 기간 기준", ["년(Years)", "개월(Months)"], horizontal=True)
            dur_val = st.number_input("투자 기간 입력", min_value=1, value=10, step=1)

    with col_calc2:
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
        return_rate = (gain / invested_total) * 100 if invested_total > 0 else 0

        st.markdown(f"""
        <div class="metric-card"><h4>최종 자산 (예상)</h4><div class="value">{final_amount/10000:,.2f} 억 원</div></div>
        <div class="metric-card"><h4>순수익금 (이자)</h4><div class="value" style="color:#01579B;">+{gain:,.0f} 만원</div></div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📈 자산 성장 그래프 (원금 vs 총자산)")
    base_chart = alt.Chart(df_calc).encode(x=alt.X('기간(월):Q', title='투자기간 (개월수)'))
    area_principal = base_chart.mark_area(opacity=0.4, color='#9E9E9E').encode(y=alt.Y('누적원금:Q', title='금액 (만원)'))
    line_total = base_chart.mark_line(color='#388E3C', strokeWidth=3).encode(y='총자산:Q')
    st.altair_chart((area_principal + line_total).interactive(), use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📉 [매크로 지표] 원화 가치 하락과 실질 최저시급(USD)의 역설")
    data = {
        '연도': ['2020', '2021', '2022', '2023', '2024', '2025', '2026'],
        '최저시급(원)': [8590, 8720, 9160, 9620, 9860, 10030, 10320],
        '달러환산(USD)': [7.91, 7.34, 7.24, 7.47, 6.70, 6.97, 6.78]
    }
    df_wage = pd.DataFrame(data)
    base = alt.Chart(df_wage).encode(x=alt.X('연도:O'))
    bar = base.mark_bar(opacity=0.4, color='#C8E6C9', width=30).encode(y=alt.Y('최저시급(원):Q'))
    line = base.mark_line(color='#0288D1', strokeWidth=3).encode(y=alt.Y('달러환산(USD):Q', scale=alt.Scale(domain=[6.0, 8.5])))
    st.altair_chart(alt.layer(bar, line).resolve_scale(y='independent'), use_container_width=True)

# ═══════════════════════════════════════════
# 탭 5: 시세비교 & 지도 (2/3 지도 레이아웃 + 복수 지역 선택 로직 완성)
# ═══════════════════════════════════════════
with tab_price:
    st.subheader("📊 부동산 대시보드 (위치 기반 시세 흐름)")
    
    # 가상의 거래 백데이터 세팅
    @st.cache_data
    def load_map_transaction_data():
        complexes_info = [
            ('서울 마포구', '상암월드컵파크10단지', 11.0, 37.5843, 126.8821),
            ('경기 수원시', '호반베르디움더센트럴', 8.0, 37.2735, 126.9422),
            ('경기 용인시', '성복역롯데캐슬골드타운', 13.0, 37.3138, 127.0805),
            ('서울 은평구', '녹번역e편한세상캐슬', 13.0, 37.6015, 126.9362),
            ('경기 용인시', '보원아파트', 7.0, 37.3325, 127.0952),
        ]
        months = ['2025-01', '2025-07', '2026-01', '2026-04']
        rows = []
        random.seed(42)
        for region, apt, base_p, lat, lon in complexes_info:
            for m in months:
                for _ in range(2):
                    price = round(base_p + np.random.uniform(-0.4, 0.4), 2)
                    rows.append({'지역': region, '아파트명': apt, '계약월': m, '거래금액(억)': price, '위도': lat, '경도': lon})
        return pd.DataFrame(rows)

    df_map_all = load_map_transaction_data()

    # 📌 좌측 2/3 메인화면(지도·그래프) 및 우측 1/3 필터단 분할
    col_main_view, col_filter_view = st.columns([7, 3])

    with col_filter_view:
        st.markdown("#### 🔍 지역 및 단지 필터")
        all_regions = sorted(df_map_all['지역'].unique().tolist())
        
        # 1. 기준 지역 필수 선택 (단일 선택)
        primary_region = st.selectbox("📌 기준 지역 선택 (필수 1개)", all_regions, index=0)
        
        # 2. 추가 지역 복수 선택 기능
        remain_regions = [r for r in all_regions if r != primary_region]
        additional_regions = st.multiselect("➕ 추가 비교지역 선택 (복수 가능)", remain_regions)
        
        # 최종 결합 선택지역
        total_selected_regions = [primary_region] + additional_regions
        
        # 지역 기준 필터링 데이터
        filtered_by_region = df_map_all[df_map_all['지역'].isin(total_selected_regions)]
        available_apts = sorted(filtered_by_region['아파트명'].unique().tolist())
        
        selected_apts = st.multiselect("🏢 비교 분석할 단지 선택", available_apts, default=available_apts[:1])

    with col_main_view:
        if selected_apts:
            final_display_df = filtered_by_region[filtered_by_region['아파트명'].isin(selected_apts)]
            
            # 🗺️ 지도 연동 모듈 (Folia 지도 활용 기본 구조 세팅)
            st.markdown("##### 📍 관심 단지 위치 레이더")
            # 네이버 지도 API 연동 전, 가장 가볍고 강력하게 지도를 그려주는 Folium 객체입니다.
            center_lat = final_display_df['위도'].mean()
            center_lon = final_display_df['경도'].mean()
            m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
            marker_cluster = MarkerCluster().add_to(m)
            
            for apt in selected_apts:
                apt_data = final_display_df[final_display_df['아파트명'] == apt].iloc[0]
                # 🏢 부동산&대출 탭에 수집된 선생님의 임장 데이터 자동 실시간 동기화
                saved_memo = st.session_state['memo_db'].get(apt, {})
                popup_txt = f"""
                <div style='width:220px; font-family:sans-serif;'>
                    <h5 style='margin:0 0 5px 0; color:#1B5E20;'>{apt}</h5>
                    <b>특징:</b> {saved_memo.get('특징', '기록 없음')}<br>
                    <b>현재 갭:</b> {saved_memo.get('갭', '-')}<br>
                    <b>💡 판단노트:</b> {saved_memo.get('의견', '-')}
                </div>
                """
                folium.Marker(
                    location=[apt_data['위도'], apt_data['경도']],
                    popup=folium.Popup(popup_txt, max_width=260),
                    tooltip=apt,
                    icon=folium.Icon(color='green', icon='home')
                ).add_to(marker_cluster)
            
            st_folium(m, width=800, height=350, key="naver_folium_map")
            
            # 시세 실거래 변화 차트
            st.markdown("##### 📈 선택 단지 시세 트렌드")
            chart_data = final_display_df.groupby(['계약월', '아파트명'])['거래금액(억)'].mean().reset_index().pivot(index='계약월', columns='아파트명', values='거래금액(억)')
            st.line_chart(chart_data, height=240)
            
            # 하단 연동 정보 표시 패널
            st.markdown("##### 🗂️ 임장 판단 정보 패널 (부동산 탭 연동)")
            for apt in selected_apts:
                memo = st.session_state['memo_db'].get(apt, {})
                if memo:
                    st.info(f"🏠 **{apt}** ➔ **[특징]** {memo.get('특징', '-')} | **[갭수준]** {memo.get('갭', '-')} | **[나의 최종 투자판단]** {memo.get('의견', '-')}")
        else:
            st.warning("분석할 단지를 우측 필터에서 선택해 주세요.")
