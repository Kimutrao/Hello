import streamlit as st
import pandas as pd
import numpy as np
import io, random, datetime, requests
import altair as alt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─────────────────────────────────────────
# 1. 페이지 설정 & 전역 CSS (눈 편안한 푸른색/초록색)
# ─────────────────────────────────────────
st.set_page_config(page_title="김철수의 투자기록실", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif; }
div[data-baseweb="tab-list"] { gap: 3px; background: #E1F5FE; border-radius: 10px; padding: 4px 6px; }
button[data-baseweb="tab"] { border-radius: 8px !important; font-size: 0.82rem !important; font-weight: 500 !important; color: #0288D1 !important; background: transparent !important; border: none !important; padding: 5px 12px !important; }
button[data-baseweb="tab"][aria-selected="true"] { background: #0288D1 !important; color: #fff !important; }
button[data-baseweb="tab"]:hover:not([aria-selected="true"]) { background: #B3E5FC !important; }
.stButton > button { background-color: #0288D1 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 0.83rem !important; }
.stButton > button:hover { background-color: #01579B !important; }
.stFormSubmitButton > button { background-color: #388E3C !important; }
.stFormSubmitButton > button:hover { background-color: #2E7D32 !important; }
div[data-baseweb="select"] > div { border-color: #0288D1 !important; border-radius: 8px !important; }
.metric-card { background: #F1F8E9; border-left: 4px solid #388E3C; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }
.metric-card h4 { margin: 0 0 2px 0; font-size: 0.72rem; color: #666; }
.metric-card .value { font-size: 1.25rem; font-weight: 700; color: #1B5E20; }
.sec-div { border: none; border-top: 1.5px solid #B3E5FC; margin: 1rem 0; }
.timeline-box { background: #F9FBFD; border-left: 3px solid #0288D1; padding: 7px 11px; margin-bottom: 5px; border-radius: 0 5px 5px 0; }
.timeline-date { font-size: 0.74rem; color: #888; font-weight: 600; }
.timeline-content { font-size: 0.88rem; color: #222; margin-top: 2px; line-height: 1.5; }
.result-box { background: #E8F5E9; border: 1.5px solid #66BB6A; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.result-box .r-label { font-size: 0.8rem; color: #555; margin-bottom: 2px; }
.result-box .r-value { font-size: 1.5rem; font-weight: 700; color: #1B5E20; }
.warn-box { background: #FFF8E1; border: 1.5px solid #FFB300; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.danger-box { background: #FFEBEE; border: 1.5px solid #E53935; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.app-header { padding: 1rem 0 0.7rem 0; border-bottom: 2px solid #0288D1; margin-bottom: 1.2rem; }
.app-title { font-size: 1.6rem; font-weight: 700; color: #01579B; letter-spacing: -0.5px; }
.app-subtitle { font-size: 0.82rem; color: #777; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <div class="app-title">📗 김철수의 투자기록실</div>
  <div class="app-subtitle">부동산 시세 분석 · 투자 철학 · 금융 계산기</div>
</div>
""", unsafe_allow_html=True)

# ── Session State 초기화 ──
if 'board_view' not in st.session_state: st.session_state['board_view'] = 'list'
if 'current_post' not in st.session_state: st.session_state['current_post'] = None
if 'selected_cat' not in st.session_state: st.session_state['selected_cat'] = "전체글보기"
if 'dsr_loans' not in st.session_state: st.session_state['dsr_loans'] = []

if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지': {'지역': '서울 마포구', '기본': '860세대, 2010년식', 'kb시세': 11.2, '호가_매매': 11.5, '호가_전세': 6.5, '매물수': 12, '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', 'kb시세': 8.0, '호가_매매': 8.2, '호가_전세': 5.2, '매물수': 8, '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
        '성복역롯데캐슬골드타운': {'지역': '경기 용인시', '기본': '2300세대, 2019년식', 'kb시세': 12.5, '호가_매매': 12.8, '호가_전세': 7.5, '매물수': 25, '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': '신분당선 라인 대장급 입지.'}]},
    }

if 'geo_db' not in st.session_state:
    st.session_state['geo_db'] = {
        '상암월드컵파크10단지': [37.5843, 126.8821], '호반베르디움더센트럴': [37.2735, 126.9422], '성복역롯데캐슬골드타운': [37.3138, 127.0805]
    }

if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "1. 부동산 시장 접근과 매수 의미", "date": "2026-06", "content": "지난달 생각의 연장선에서. 유의미한 상승이 지속될까? 잘 모르겠음.\n\n이제 아파트 시장은 돈을 벌기 위함보다는 미래에 사지 못하게 되는 것을 경계하며 구매가 가능할 때 구매를 해둬야하는 리스크 헷지 상품이 되어버림. 없다면 무조건 매수를 해야하는 존재."},
        {"category": "규제 & 정책 분석", "title": "2. 영끌금지와 생존 세팅값", "date": "2026-06", "content": "대한민국은 자유가 사라지는 중. 조금 더 큰 수익을 얻기위해 과한 영끌을 하기 보다 장기간 더 버틸 수 있는 세팅값에 의미를 두는게 좋지 않을까."},
    ]

# ── 상단 탭 구성 ──
tab_basic, tab_mind, tab_realestate, tab_finance = st.tabs([
    "📖 투자철학 요약", "🧠 기록 & 게시판", "🏢 관심단지 & 비교 (지도)", "💰 매크로 & 계산기"
])

# ═══════════════════════════════════════════
# 탭 1: 투자철학 (생략 없이 유지)
# ═══════════════════════════════════════════
with tab_basic:
    st.subheader("📖 흔들리지 않는 4가지 핵심 기준")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("💡 1. 부동산의 본질은 리스크 헷지", expanded=True):
            st.markdown("- 돈을 벌기 위함이 아니라, 사지 못하게 되는 것을 막는 수단\n- 알파 수익을 원한다면 달러, 미국 주식, 코인 등 대체재가 많습니다.\n- 현재 아파트는 무조건 매수해 두어야 하는 주거 입장권이자 생존 방어막입니다.")
        with st.expander("🔑 2. 영끌 금지와 개인의 상황"):
            st.markdown("- 보편적인 정답은 없다. 오직 나의 생애주기만 있을 뿐.\n- 자산이 없는 30대라면 최대한 대출을 당겨 자산을 선점하는 것이 맞습니다.\n- 소득 감소가 예상되는 40대 이상이라면 공격적인 대출은 독입니다.")
    with col2:
        with st.expander("🔇 3. 시장의 소음 구별법", expanded=True):
            st.markdown("- 금액을 논하는 자는 멀리하고, 시대 흐름을 논하는 자를 곁에 두라.\n- 하락장엔 비관론, 상승장엔 낙관론을 외치는 유튜버의 목적은 오직 조회수입니다.")
        with st.expander("💸 4. 세금을 계산하지 않은 투자는 허상"):
            st.markdown("- 보유세와 거래세의 밸런스 게임\n- 취득세, 양도세, 보유세 시뮬레이션 없이 무작정 주택 수만 늘리는 것은 빈 수레입니다.")

# ═══════════════════════════════════════════
# 탭 2: 기록 & 게시판 (관리자 뱃지 제거)
# ═══════════════════════════════════════════
with tab_mind:
    cat_list = ["전체글보기", "투자 마인드 & 철학", "규제 & 정책 분석", "시장 전망 & 매크로", "자유 메모"]
    col_menu, col_board = st.columns([2, 8])

    with col_menu:
        st.markdown("#### 📂 카테고리")
        selected_cat = st.radio("카테고리", cat_list, key="board_cat_radio", label_visibility="collapsed")
        if selected_cat != st.session_state['selected_cat']:
            st.session_state['selected_cat'] = selected_cat
            st.session_state['board_view'] = 'list'
            st.rerun()
        if st.button("✍️ 새 글 작성", use_container_width=True):
            st.session_state['board_view'] = 'write'
            st.rerun()

    with col_board:
        display_posts = list(st.session_state['blog_db']) if st.session_state['selected_cat'] == "전체글보기" else [p for p in st.session_state['blog_db'] if p['category'] == st.session_state['selected_cat']]

        if st.session_state['board_view'] == 'write':
            st.markdown("#### ✏️ 새 글 작성")
            with st.form("write_form"):
                new_cat = st.selectbox("카테고리", cat_list[1:])
                new_title = st.text_input("제목")
                new_content = st.text_area("내용", height=280)
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
            st.caption(f"분류: {post['category']} | {post['date']}")
            st.markdown('<hr style="border-top:1px solid #B3E5FC; margin:6px 0;">', unsafe_allow_html=True)
            for line in post['content'].split('\n'):
                st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)

        else:
            st.markdown(f"#### 📜 {st.session_state['selected_cat']}")
            for idx, post in enumerate(display_posts):
                col_t, col_c, col_d = st.columns([5, 3, 2])
                with col_t:
                    if st.button(post['title'], key=f"p_{idx}_{post['title'][:6]}", use_container_width=True):
                        st.session_state['current_post'] = post
                        st.session_state['board_view'] = 'read'
                        st.rerun()
                with col_c: st.caption(f"🔹 {post['category']}")
                with col_d: st.caption(f"📅 {post['date']}")

# ═══════════════════════════════════════════
# 탭 3: 관심단지 & 비교 (지도 부활, 가로 축 수정, 동적 테이블)
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 관심단지 레이더 & 교차 비교")

    # 국토부 실거래가 데이터 생성기 (MOLIT Simulator)
    @st.cache_data
    def get_molit_mock_data(apt_name, years):
        months = pd.date_range(end=pd.Timestamp.today(), periods=years*12, freq='M').strftime('%Y-%m').tolist()
        bp = st.session_state['memo_db'].get(apt_name, {}).get('kb시세', 9.0)
        random.seed(len(apt_name))
        rows = []
        trend_sale, trend_jeonse = 0.0, 0.0
        for m in months:
            trend_sale += random.uniform(-0.05, 0.08)
            trend_jeonse += random.uniform(-0.03, 0.06)
            sale_price = round(bp + trend_sale + random.uniform(-0.2, 0.2), 1)
            jeonse_price = round((bp * 0.6) + trend_jeonse + random.uniform(-0.1, 0.1), 1)
            rows.append({'계약월': m, '아파트명': apt_name, '매매평균(억)': sale_price, '전세평균(억)': jeonse_price})
        return pd.DataFrame(rows)

    # ── 1/3 컨트롤 패널 ──
    col_panel, col_view = st.columns([3, 7])
    
    with col_panel:
        st.markdown("##### 📍 Step 1: 지역 선택")
        all_regions = sorted(set(v['지역'] for v in st.session_state['memo_db'].values()))
        sel_region = st.selectbox("지역구", all_regions, key="step1_region")
        
        st.markdown("##### 🏢 Step 2: 메인 단지 선택")
        region_apts = [k for k, v in st.session_state['memo_db'].items() if v.get('지역') == sel_region]
        main_apt = st.radio("상세보기 단지", region_apts, key="step2_apt") if region_apts else None
        
        st.markdown("##### 📊 Step 3: 비교할 단지 추가 (선택)")
        other_apts = [a for a in st.session_state['memo_db'].keys() if a != main_apt]
        compare_apts = st.multiselect("비교 단지 추가", other_apts, key="step3_compare")
        
        all_selected = [main_apt] + compare_apts if main_apt else compare_apts

        st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
        st.markdown("##### ✏️ 신규 단지 등록 및 수정")
        with st.form("apt_info_form"):
            f_name = st.text_input("단지명 (신규 등록 시 입력)", value=main_apt if main_apt else "")
            f_reg = st.text_input("지역명", value=sel_region)
            f_addr = st.text_input("도로명 주소 (지도 표시용)", placeholder="예: 서울 마포구 월드컵북로 332")
            f_hh = st.text_input("세대수/연식", placeholder="1000세대, 2015년식")
            
            st.markdown("**현재 호가 및 시세 (수동 입력)**")
            c_f1, c_f2 = st.columns(2)
            with c_f1: f_sale = st.number_input("매매 호가(억)", value=0.0, step=0.1)
            with c_f2: f_jeonse = st.number_input("전세 호가(억)", value=0.0, step=0.1)
            c_f3, c_f4 = st.columns(2)
            with c_f3: f_kb = st.number_input("KB시세(억)", value=0.0, step=0.1)
            with c_f4: f_cnt = st.number_input("매물 수", value=0, step=1)
            
            f_op = st.text_area("투자 의견 (히스토리에 누적됨)")
            
            if st.form_submit_button("✅ 정보 저장 / 업데이트"):
                if f_name:
                    if f_name not in st.session_state['memo_db']:
                        st.session_state['memo_db'][f_name] = {'history': []}
                        if f_addr:
                            try:
                                loc = Nominatim(user_agent="kimcs_app").geocode(f_addr, timeout=5)
                                if loc: st.session_state['geo_db'][f_name] = [loc.latitude, loc.longitude]
                            except:
                                st.session_state['geo_db'][f_name] = [37.566, 126.978]
                    
                    db_ref = st.session_state['memo_db'][f_name]
                    db_ref.update({'지역': f_reg, '기본': f_hh, '호가_매매': f_sale, '호가_전세': f_jeonse, 'kb시세': f_kb, '매물수': f_cnt, '작성일': datetime.datetime.now().strftime("%Y-%m-%d")})
                    if f_op:
                        db_ref['history'].append({'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': f_op})
                    st.success("저장 완료!")
                    st.rerun()

    # ── 2/3 메인 뷰어 ──
    with col_view:
        if not all_selected:
            st.info("왼쪽 패널에서 단지를 선택해 주세요.")
        else:
            # 🗺️ 1. 지도 영역
            st.markdown("##### 📍 입지 레이더 (지도)")
            center_coords = st.session_state['geo_db'].get(main_apt, [37.5665, 126.9780])
            m = folium.Map(location=center_coords, zoom_start=13)
            mc = MarkerCluster().add_to(m)
            
            for apt in all_selected:
                coords = st.session_state['geo_db'].get(apt, [37.5665, 126.9780])
                info = st.session_state['memo_db'].get(apt, {})
                popup_html = f"<b>{apt}</b><br>호가: {info.get('호가_매매', 0)}억<br>KB: {info.get('kb시세', 0)}억"
                folium.Marker(location=coords, popup=folium.Popup(popup_html, max_width=200), icon=folium.Icon(color='blue' if apt == main_apt else 'green', icon='home')).add_to(mc)
            st_folium(m, width=800, height=350, key="main_map")

            # 📈 2. 트렌드 그래프 영역
            st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
            c_sl1, c_sl2 = st.columns([7, 3])
            with c_sl1: st.markdown("##### 📈 국토부 실거래 기반 시세 트렌드 (가상 시뮬레이션)")
            with c_sl2: view_years = st.slider("조회 기간 (년)", 1, 5, 3)

            df_all_trends = pd.concat([get_molit_mock_data(apt, view_years) for apt in all_selected])
            
            # 메인 단지 하나만 있을 때는 매매/전세 모두 표시, 여러 개면 매매가만 비교 표시
            if len(all_selected) == 1:
                df_melt = df_all_trends.melt(id_vars=['계약월', '아파트명'], value_vars=['매매평균(억)', '전세평균(억)'], var_name='구분', value_name='금액(억)')
                chart = alt.Chart(df_melt).mark_line(point=True, strokeWidth=3).encode(
                    x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=11)),
                    y=alt.Y('금액(억):Q', scale=alt.Scale(zero=False)),
                    color=alt.Color('구분:N', scale=alt.Scale(domain=['매매평균(억)', '전세평균(억)'], range=['#0288D1', '#388E3C'])),
                    tooltip=['계약월', '구분', '금액(억)']
                ).properties(height=280)
            else:
                chart = alt.Chart(df_all_trends).mark_line(point=True, strokeWidth=3).encode(
                    x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=11)),
                    y=alt.Y('매매평균(억):Q', scale=alt.Scale(zero=False)),
                    color=alt.Color('아파트명:N'),
                    tooltip=['계약월', '아파트명', '매매평균(억)']
                ).properties(height=280)
            st.altair_chart(chart, use_container_width=True)

            # 📊 3. 하단 상세 데이터 테이블 및 요약
            st.markdown("##### 🗂️ 핵심 지표 & 투자 의견 (상세 비교)")
            
            # 메인 단지의 KB시세 및 대출한도 계산
            main_info = st.session_state['memo_db'].get(main_apt, {})
            kb = float(main_info.get('kb시세', 0))
            st.markdown(f"""
            <div style="display:flex; gap:15px; margin-bottom:15px;">
                <div style="background:#E1F5FE; padding:10px 15px; border-radius:8px; border-left:4px solid #0288D1;">
                    <span style="font-size:0.8rem; color:#555;">{main_apt} KB시세</span><br>
                    <span style="font-size:1.2rem; font-weight:bold; color:#01579B;">{kb} 억원</span>
                </div>
                <div style="background:#E8F5E9; padding:10px 15px; border-radius:8px; border-left:4px solid #388E3C;">
                    <span style="font-size:0.8rem; color:#555;">예상 최대 담보대출 한도 (LTV 70% 가정)</span><br>
                    <span style="font-size:1.2rem; font-weight:bold; color:#1B5E20;">{kb * 0.7:.2f} 억원</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            compare_data = []
            for apt in all_selected:
                info = st.session_state['memo_db'].get(apt, {})
                last_trend = get_molit_mock_data(apt, 1).iloc[-1]
                compare_data.append({
                    '단지명': apt,
                    '매매 호가(억)': info.get('호가_매매', 0),
                    '전세 호가(억)': info.get('호가_전세', 0),
                    '실거래 매매평균(억)': last_trend['매매평균(억)'],
                    '실거래 전세평균(억)': last_trend['전세평균(억)'],
                    '매물수': info.get('매물수', 0),
                    '기준일': info.get('작성일', '-')
                })
            st.dataframe(pd.DataFrame(compare_data), use_container_width=True, hide_index=True)

            st.markdown("**📝 누적 투자 의견**")
            for apt in all_selected:
                hist = st.session_state['memo_db'].get(apt, {}).get('history', [])
                if hist:
                    with st.expander(f"📖 {apt} 의견 펼쳐보기"):
                        for h in hist:
                            st.markdown(f"""<div class="timeline-box"><div class="timeline-date">📅 {h['date']} 기록</div><div class="timeline-content">{h['opinion']}</div></div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 탭 4: 매크로 & 계산기 (DSR 5년 자동, 최저시급 18년~)
# ═══════════════════════════════════════════
with tab_finance:
    calc_tab1, calc_tab2 = st.tabs(["🏦 DSR 계산기", "📊 최저시급 & 실시간 환율"])

    # ── DSR ──
    with calc_tab1:
        st.markdown("#### 🏦 DSR 합산 계산기 (1금융권 40% 기준)")
        col_dsr_l, col_dsr_r = st.columns([5, 5])

        with col_dsr_l:
            dsr_income = st.number_input("연 소득 (만원)", min_value=100, value=6000, step=100, key="dsr_in")
            dsr_limit = 40 

            st.markdown("##### ➕ 기존 대출 추가")
            with st.form("add_loan_form"):
                l_col1, l_col2 = st.columns(2)
                with l_col1:
                    loan_type = st.selectbox("대출 종류", ["주택담보대출(원리금균등)", "신용대출", "마이너스통장", "자동차할부/기타"])
                    loan_amt = st.number_input("대출 원금 (만원)", min_value=0, value=5000, step=100)
                with l_col2:
                    loan_rate = st.number_input("금리 (%)", min_value=0.1, value=4.5, step=0.1)
                    # 신용대출/마통 선택 시 사용자 인지를 돕는 안내문 (Streamlit 폼 특성상 기본값 동적 변경 대신 고정 안내)
                    st.caption("※ 신용/마통은 통상 5년으로 산정됩니다.")
                    loan_period = st.number_input("잔여/산정 기간 (년)", min_value=1, value=5 if loan_type in ["신용대출", "마이너스통장"] else 30, step=1)
                
                if st.form_submit_button("추가하기"):
                    st.session_state['dsr_loans'].append({'type': loan_type, 'amt': loan_amt, 'rate': loan_rate, 'period': loan_period})
                    st.rerun()

            if st.button("🗑️ 전체 초기화"):
                st.session_state['dsr_loans'] = []
                st.rerun()

            if st.session_state['dsr_loans']:
                loan_rows = [{'종류': l['type'][:10], '원금(만)': f"{l['amt']:,}", '금리': f"{l['rate']}%", '적용기간': f"{l['period']}년"} for l in st.session_state['dsr_loans']]
                st.dataframe(pd.DataFrame(loan_rows), use_container_width=True, hide_index=True)

        with col_dsr_r:
            st.markdown("##### DSR 산출 결과")
            def calc_annual(l):
                amt = l['amt'] * 10000
                r = l['rate'] / 100
                pm = l['period'] * 12
                mr = r / 12
                if "마이너스" in l['type']: return amt * r / 10000
                monthly = amt * mr / (1-(1+mr)**(-pm)) if mr > 0 else amt/pm
                return monthly * 12 / 10000

            total_annual = sum(calc_annual(l) for l in st.session_state['dsr_loans'])
            cur_dsr = (total_annual / dsr_income * 100) if dsr_income > 0 else 0
            
            box_cls = "result-box" if cur_dsr <= dsr_limit else "danger-box"
            st.markdown(f"""<div class="{box_cls}">
              <div class="r-label">현재 합산 DSR</div>
              <div class="r-value">{cur_dsr:.1f}%</div>
              <div class="r-sub">연간 원리금 상환액: {total_annual:,.0f} 만원</div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
            st.markdown("""
            **💡 대출 종류별 DSR 산정 만기 (은행업 감독규정 기준)**
            * **주택담보대출:** 실제 상환기간 (최장 40~50년 적용 가능)
            * **신용대출 / 마이너스통장:** 기본 **5년** 적용 (원금 분할상환 시 실제 기간 적용)
            * **기타 대출 (할부 등):** 실제 상환기간 (최장 8년)
            > *주의: 대출 원금이 같아도, 산정 만기(기간)가 짧을수록 1년에 갚아야 할 원금이 커지므로 DSR 비율이 급격하게 높아집니다.*
            """)

    # ── 최저시급 & 환율 ──
    with calc_tab2:
        st.markdown("#### 📊 최근 최저시급 트렌드 & 달러 가치 (2018~현재)")
        
        @st.cache_data(ttl=3600)
        def get_live_rate():
            try:
                return round(requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()['rates']['KRW'], 1)
            except:
                return 1450.0

        live_rate = get_live_rate()

        wage_df = pd.DataFrame({
            '연도': ['2018','2019','2020','2021','2022','2023','2024','2025','2026'],
            '최저시급(원)': [7530, 8350, 8590, 8720, 9160, 9620, 9860, 10030, 10320],
            '연평균환율(원/$)':[1100.3, 1165.7, 1180.1, 1144.0, 1291.9, 1305.5, 1363.0, 1421.0, live_rate],
        })
        wage_df['달러환산(USD)'] = (wage_df['최저시급(원)'] / wage_df['연평균환율(원/$)']).round(2)

        st.caption(f"📡 2026년 실시간 환율 적용 중: **{live_rate:,.1f} 원/달러**")

        base = alt.Chart(wage_df).encode(x=alt.X('연도:O', axis=alt.Axis(labelAngle=0, labelFontSize=11)))
        
        bars = base.mark_bar(color='#B3E5FC', opacity=0.8, width=35).encode(
            y=alt.Y('최저시급(원):Q', title='최저시급 (원)', axis=alt.Axis(titleColor='#01579B', format='d')),
        )
        bar_lbl = base.mark_text(align='center', baseline='bottom', dy=-5, fontSize=11, color='#01579B', fontWeight='bold').encode(
            y=alt.Y('최저시급(원):Q'), text=alt.Text('최저시급(원):Q', format='d')
        )
        line = base.mark_line(color='#388E3C', strokeWidth=3, point=alt.OverlayMarkDef(color='#388E3C', size=80)).encode(
            y=alt.Y('달러환산(USD):Q', title='달러 환산 (USD)', scale=alt.Scale(domain=[6.0, 8.5]), axis=alt.Axis(titleColor='#1B5E20', format='.2f')),
        )
        line_lbl = base.mark_text(align='center', baseline='top', dy=10, fontSize=11, color='#1B5E20', fontWeight='bold').encode(
            y=alt.Y('달러환산(USD):Q'), text=alt.Text('달러환산(USD):Q', format='.2f')
        )

        combined = alt.layer(bars, bar_lbl, line, line_lbl).resolve_scale(y='independent').properties(height=360)
        st.altair_chart(combined, use_container_width=True)

        display_df = wage_df.copy()
        display_df['인상액(원)'] = display_df['최저시급(원)'].diff().fillna(0).astype(int)
        display_df['인상률(%)'] = (display_df['최저시급(원)'].pct_change() * 100).round(1).fillna(0)
        st.dataframe(display_df[['연도','최저시급(원)','인상액(원)','인상률(%)','연평균환율(원/$)','달러환산(USD)']], use_container_width=True, hide_index=True)
