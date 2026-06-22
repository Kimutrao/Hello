import streamlit as st
import pandas as pd
import numpy as np
import io, random, datetime, requests
import altair as alt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# ─────────────────────────────────────────
# 1. 페이지 설정 & 전역 CSS
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
.metric-card { background: #F1F8E9; border-left: 4px solid #388E3C; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }
.sec-div { border: none; border-top: 1.5px solid #B3E5FC; margin: 1rem 0; }
.timeline-box { background: #F9FBFD; border-left: 3px solid #0288D1; padding: 7px 11px; margin-bottom: 5px; border-radius: 0 5px 5px 0; }
.timeline-date { font-size: 0.74rem; color: #888; font-weight: 600; }
.timeline-content { font-size: 0.88rem; color: #222; margin-top: 2px; line-height: 1.5; }
.result-box { background: #E8F5E9; border: 1.5px solid #66BB6A; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.result-box .r-label { font-size: 0.8rem; color: #555; margin-bottom: 2px; }
.result-box .r-value { font-size: 1.5rem; font-weight: 700; color: #1B5E20; }
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

# ── 헬퍼 함수: 데이터프레임 무조건 가운데 정렬 ──
def display_centered_df(df):
    styles = [dict(selector="th", props=[('text-align', 'center')]), dict(selector="td", props=[('text-align', 'center')])]
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}).set_table_styles(styles), use_container_width=True, hide_index=True)

# ── 사이드바 비밀번호 세팅 ──
ADMIN_PW = "kimcs2024!"  
def is_admin(): return st.session_state.get("admin_logged_in", False)

defaults = {'admin_logged_in': False, 'board_view': 'list', 'current_post': None, 'selected_cat': '전체글보기', 'dsr_loans': []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지 (33평)': {'지역': '서울 마포구', '기본': '860세대, 2010년식', 'kb시세': 11.2, '호가_매매': 11.5, '호가_전세': 6.5, '전월거래량': 5, '특징': '초품아, 마포 상암', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴 (25평)': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', 'kb시세': 8.0, '호가_매매': 8.2, '호가_전세': 5.2, '전월거래량': 12, '특징': '신분당선 호매실 호재', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
        '성복역롯데캐슬골드타운 (34평)': {'지역': '경기 용인시', '기본': '2300세대, 2019년식', 'kb시세': 12.5, '호가_매매': 12.8, '호가_전세': 7.5, '전월거래량': 25, '특징': '성복역 지하 통로 연결', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': '신분당선 라인 대장급 입지.'}]},
    }
if 'geo_db' not in st.session_state:
    st.session_state['geo_db'] = {'상암월드컵파크10단지 (33평)': [37.5843, 126.8821], '호반베르디움더센트럴 (25평)': [37.2735, 126.9422], '성복역롯데캐슬골드타운 (34평)': [37.3138, 127.0805]}

if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "26년 4월 부동산 생각기록", "date": "2026-04", "content": "매물숫자를 보니 어처구니가 없을 정도로 없다. 소유를 위한 것이라면 무조건 매수, 투자를 위한 것이라면 깊은 고민이 필요하다."},
        {"category": "규제 & 정책 분석", "title": "25년 10월 전월세 공급과 수요", "date": "2025-10", "content": "28년까지 준공 물량 부족. 대출규제는 수요억제책일 뿐 수요의 왜곡과 가격상승을 만든다."},
    ]

with st.sidebar:
    st.markdown("### 🔐 사이트 관리자 메뉴")
    if is_admin():
        st.success("✅ 인증 완료")
        if st.button("로그아웃"): st.session_state['admin_logged_in'] = False; st.rerun()
    else:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == ADMIN_PW: st.session_state['admin_logged_in'] = True; st.rerun()
            else: st.error("비번 오류")

tab_basic, tab_mind, tab_realestate, tab_finance = st.tabs(["📖 투자철학", "🧠 기록 & 게시판", "🏢 단지 분석 & 비교", "💰 매크로 & 계산기"])

# ═══════════════════════════════════════════
# 탭 1 & 2: 투자철학 & 게시판 
# ═══════════════════════════════════════════
with tab_basic:
    st.subheader("📖 흔들리지 않는 4가지 핵심 기준")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("💡 1. 부동산의 본질은 리스크 헷지", expanded=True):
            st.markdown("- 돈을 벌기 위함이 아니라, 사지 못하게 되는 것을 막는 수단\n- 현재 아파트는 무조건 매수해 두어야 하는 주거 입장권이자 생존 방어막입니다.")
        with st.expander("🔑 2. 영끌 금지와 개인의 상황"):
            st.markdown("- 보편적인 정답은 없다. 오직 나의 생애주기만 있을 뿐.\n- 자산이 없는 30대라면 최대한 대출을 당겨 자산을 선점하는 것이 맞습니다.")
    with col2:
        with st.expander("🔇 3. 시장의 소음 구별법", expanded=True):
            st.markdown("- 금액을 논하는 자는 멀리하고, 시대 흐름을 논하는 자를 곁에 두라.\n- 하락장엔 비관론, 상승장엔 낙관론을 외치는 유튜버의 목적은 오직 조회수입니다.")
        with st.expander("💸 4. 세금을 계산하지 않은 투자는 허상"):
            st.markdown("- 보유세와 거래세의 밸런스 게임\n- 취득세, 양도세, 보유세 시뮬레이션 없이 무작정 주택 수만 늘리는 것은 빈 수레입니다.")

with tab_mind:
    cat_list = ["전체글보기", "투자 마인드 & 철학", "규제 & 정책 분석", "시장 전망 & 매크로", "자유 메모"]
    col_menu, col_board = st.columns([2, 8])
    with col_menu:
        st.markdown("#### 📂 카테고리")
        selected_cat = st.radio("카테고리", cat_list, key="board_cat_radio", label_visibility="collapsed")
        if selected_cat != st.session_state['selected_cat']:
            st.session_state['selected_cat'] = selected_cat; st.session_state['board_view'] = 'list'; st.rerun()
        if is_admin():
            if st.button("✍️ 새 글 작성", use_container_width=True): st.session_state['board_view'] = 'write'; st.rerun()
    with col_board:
        display_posts = list(st.session_state['blog_db']) if st.session_state['selected_cat'] == "전체글보기" else [p for p in st.session_state['blog_db'] if p['category'] == st.session_state['selected_cat']]
        if st.session_state['board_view'] == 'write' and is_admin():
            with st.form("write_form"):
                new_cat = st.selectbox("카테고리", cat_list[1:])
                new_title = st.text_input("제목")
                new_content = st.text_area("내용", height=280)
                if st.form_submit_button("등록") and new_title and new_content:
                    st.session_state['blog_db'].insert(0, {"category": new_cat, "title": new_title, "content": new_content, "date": datetime.datetime.now().strftime("%Y-%m")})
                    st.session_state['board_view'] = 'list'; st.rerun()
        elif st.session_state['board_view'] == 'read':
            post = st.session_state['current_post']
            if st.button("⬅️ 목록으로"): st.session_state['board_view'] = 'list'; st.rerun()
            st.markdown(f"### {post['title']}")
            st.caption(f"분류: {post['category']} | {post['date']}")
            st.markdown('<hr style="border-top:1px solid #B3E5FC; margin:6px 0;">', unsafe_allow_html=True)
            for line in post['content'].split('\n'): st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
        else:
            st.markdown(f"#### 📜 {st.session_state['selected_cat']}")
            for idx, post in enumerate(display_posts):
                col_t, col_c, col_d = st.columns([6, 2, 2])
                with col_t:
                    if st.button(post['title'], key=f"p_{idx}", use_container_width=True):
                        st.session_state['current_post'] = post; st.session_state['board_view'] = 'read'; st.rerun()
                with col_c: st.caption(f"🔹 {post['category']}")
                with col_d: st.caption(f"📅 {post['date']}")

# ═══════════════════════════════════════════
# 탭 3: 관심단지 분석 & 비교 (지도 확대, Y축 겹침 방지 등)
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 관심단지 레이더 & 교차 비교")

    @st.cache_data
    def get_mock_scatter_data(apt_name, years):
        months = pd.date_range(end=pd.Timestamp.today(), periods=years*12, freq='ME').strftime('%Y-%m').tolist()
        bp = float(st.session_state['memo_db'].get(apt_name, {}).get('kb시세', 9.0))
        random.seed(len(apt_name) * years)
        trend, raw_trades = 0.0, []
        for m in months:
            trend += random.uniform(-0.06, 0.1)
            base_m = bp + trend
            for _ in range(random.randint(1, 4)):
                raw_trades.append({'계약월': m, '아파트명': apt_name, '실거래가(억)': round(base_m + random.uniform(-0.15, 0.15), 2)})
        return pd.DataFrame(raw_trades)

    sub_single, sub_comp, sub_hoga, sub_add = st.tabs(["🔍 단지 상세 분석", "📊 실거래가 비교", "📋 호가/매물 현황", "➕ 단지 관리(관리자)"])

    # ── [1] 단지 상세 분석 (지도 최상단 확대 배치) ──
    with sub_single:
        col_panel, col_view = st.columns([2.5, 7.5])
        
        with col_panel:
            st.markdown("##### 📍 타겟 선택")
            sel_region = st.selectbox("지역", ["전체"] + sorted(set(v['지역'] for v in st.session_state['memo_db'].values())))
            region_apts = list(st.session_state['memo_db'].keys()) if sel_region == "전체" else [k for k, v in st.session_state['memo_db'].items() if v.get('지역') == sel_region]
            chosen_apt = st.radio("분석할 단지", region_apts) if region_apts else None

            st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
            if chosen_apt:
                info = st.session_state['memo_db'][chosen_apt]
                st.markdown("##### 📝 특징 및 투자의견")
                st.info(f"**특징:** {info.get('특징', '-')}")
                for h in info.get('history', []):
                    st.markdown(f"<div class='timeline-box'><div class='timeline-date'>📅 {h['date']}</div><div class='timeline-content'>{h['opinion']}</div></div>", unsafe_allow_html=True)

        with col_view:
            if chosen_apt:
                info = st.session_state['memo_db'][chosen_apt]
                
                # 상단 1: 지도 대형 배치
                st.markdown(f"#### 🎯 {chosen_apt}")
                coords = st.session_state['geo_db'].get(chosen_apt, [37.566, 126.978])
                m = folium.Map(location=coords, zoom_start=15)
                folium.Marker(coords, tooltip=chosen_apt, icon=folium.Icon(color='blue')).add_to(m)
                st_folium(m, width="100%", height=350, key=f"map_{chosen_apt}")

                # 상단 2: 시세 요약 정보 (KB시세 제거)
                st.markdown(f"""
                <div style="display:flex; justify-content:space-around; background:#F9FBFD; padding:15px; border-radius:10px; border:1px solid #B3E5FC; margin-top:10px;">
                    <div style="text-align:center;"><span style="color:#666; font-size:0.9rem;">매매 호가 (최근 업데이트)</span><br><b style="font-size:1.4rem; color:#E65100;">{info.get('호가_매매', '-')} 억</b></div>
                    <div style="text-align:center;"><span style="color:#666; font-size:0.9rem;">전세 호가</span><br><b style="font-size:1.4rem; color:#1B5E20;">{info.get('호가_전세', '-')} 억</b></div>
                    <div style="text-align:center;"><span style="color:#666; font-size:0.9rem;">전월 총 거래량</span><br><b style="font-size:1.4rem; color:#424242;">{info.get('전월거래량', '-')} 건</b></div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="sec-div">', unsafe_allow_html=True)

                # 하단 1: 그래프 (1년 기본, 우측 조절기)
                g_col1, g_col2 = st.columns([7, 3])
                with g_col1: st.markdown("##### 📈 국토부 실거래가 추이 (건별 거래량 표기)")
                with g_col2: view_years = st.slider("조회 기간 (년)", 1, 5, 1, label_visibility="collapsed")
                
                df_raw = get_mock_scatter_data(chosen_apt, view_years)
                df_mean = df_raw.groupby('계약월', as_index=False)['실거래가(억)'].mean()
                
                base = alt.Chart(df_raw).encode(x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)))
                scatter = base.mark_circle(color='red', opacity=0.6, size=40).encode(y='실거래가(억):Q', tooltip=['계약월', '실거래가(억)'])
                line = alt.Chart(df_mean).mark_line(color='#0288D1', strokeWidth=3).encode(x='계약월:O', y='실거래가(억):Q')
                st.altair_chart((scatter + line).properties(height=300), use_container_width=True)

    # ── [2] 실거래가 다중 비교 ──
    with sub_comp:
        all_apts = list(st.session_state['memo_db'].keys())
        comp_apts = st.multiselect("비교 단지 선택", all_apts, default=all_apts[:2])
        if comp_apts:
            rows = []
            for apt in comp_apts:
                info = st.session_state['memo_db'].get(apt, {})
                df_raw = get_mock_scatter_data(apt, 1)
                rows.append({'단지명': apt, '지역': info.get('지역', '-'), '세대수/연식': info.get('기본', '-'), '전월 평균(억)': df_raw['실거래가(억)'].mean().round(2), '전월 거래량': info.get('전월거래량', '-')})
            display_centered_df(pd.DataFrame(rows))

            df_all_list = []
            for apt in comp_apts:
                df_apt = get_mock_scatter_data(apt, 3).groupby('계약월', as_index=False)['실거래가(억)'].mean()
                df_apt['아파트명'] = apt
                df_all_list.append(df_apt)
            
            df_all = pd.concat(df_all_list)
            compare_chart = alt.Chart(df_all).mark_line(point=True, strokeWidth=2.5).encode(
                x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)),
                y=alt.Y('실거래가(억):Q', scale=alt.Scale(zero=False), title='매매 평균가(억)'),
                color=alt.Color('아파트명:N', legend=alt.Legend(title="비교 단지")),
                tooltip=['계약월', '아파트명', '실거래가(억)']
            ).properties(height=350)
            st.altair_chart(compare_chart, use_container_width=True)

    # ── [3] 호가/매물 비교 ──
    with sub_hoga:
        st.markdown("#### 📋 단지별 현재 매매/전세 호가 현황판")
        hoga_rows = []
        for apt, info in st.session_state['memo_db'].items():
            hoga_rows.append({'단지명': apt, '매매 호가(억)': info.get('호가_매매', '-'), '전세 호가(억)': info.get('호가_전세', '-'), '호가 갭(억)': round(float(info.get('호가_매매',0)) - float(info.get('호가_전세',0)), 2), '특징': info.get('특징', '-')})
        display_centered_df(pd.DataFrame(hoga_rows))

    # ── [4] 단지 등록 (관리자) ──
    with sub_add:
        if not is_admin(): st.warning("관리자 로그인 후 이용 가능합니다.")
        else:
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                st.markdown("#### ➕ 신규 단지 등록")
                with st.form("new_apt_form"):
                    n_reg = st.text_input("지역명", placeholder="서울 마포구")
                    n_name = st.text_input("단지명 (평형 기재)", placeholder="마포래미안푸르지오 (33평)")
                    n_addr = st.text_input("도로명 주소 (지도 핀셋용)")
                    n_hh = st.text_input("세대수/연식")
                    n_kb = st.text_input("KB시세 (억)")
                    n_sale = st.text_input("매매 호가 (억)")
                    n_jeonse = st.text_input("전세 호가 (억)")
                    n_vol = st.text_input("전월 거래량")
                    n_feat = st.text_input("특징")
                    n_op = st.text_area("투자 의견")
                    
                    if st.form_submit_button("신규 단지 저장"):
                        if n_name and n_addr:
                            try:
                                loc = Nominatim(user_agent="kimcs_app").geocode(n_addr, timeout=5)
                                st.session_state['geo_db'][n_name] = [loc.latitude, loc.longitude] if loc else [37.566, 126.978]
                            except:
                                st.session_state['geo_db'][n_name] = [37.566, 126.978]
                            st.session_state['memo_db'][n_name] = {'지역': n_reg, '기본': n_hh, 'kb시세': n_kb, '호가_매매': n_sale, '호가_전세': n_jeonse, '전월거래량': n_vol, '특징': n_feat, 'history': [{'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': n_op}] if n_op else []}
                            st.success("등록 완료!"); st.rerun()

            with col_add2:
                st.markdown("#### ✏️ 기존 단지 정보 업데이트")
                edit_apt = st.selectbox("업데이트 단지 선택", list(st.session_state['memo_db'].keys()))
                if edit_apt:
                    e_info = st.session_state['memo_db'][edit_apt]
                    with st.form("edit_apt_form"):
                        e_kb = st.text_input("KB시세 (억)", value=e_info.get('kb시세', ''))
                        e_sale = st.text_input("매매 호가 (억)", value=e_info.get('호가_매매', ''))
                        e_jeonse = st.text_input("전세 호가 (억)", value=e_info.get('호가_전세', ''))
                        e_vol = st.text_input("전월 거래량", value=e_info.get('전월거래량', ''))
                        e_append = st.text_area("추가 투자 의견 (타임라인 누적)")
                        if st.form_submit_button("정보 업데이트"):
                            e_info.update({'kb시세': e_kb, '호가_매매': e_sale, '호가_전세': e_jeonse, '전월거래량': e_vol})
                            if e_append: e_info['history'].append({'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': e_append})
                            st.success("업데이트 완료!"); st.rerun()

# ═══════════════════════════════════════════
# 탭 4: 계산기 & 매크로 (복리그래프 값 표시, 취득세 복구, 중앙정렬)
# ═══════════════════════════════════════════
with tab_finance:
    st.subheader("💰 통합 계산기 & 매크로 지표")
    calc_tab1, calc_tab2, calc_tab3, calc_tab4 = st.tabs(["🏦 DSR 계산기", "📐 LTV / 취득세", "🔢 복리 계산기", "📊 최저시급 & 환율"])

    # ── 1. DSR 계산기 ──
    with calc_tab1:
        col_dsr_l, col_dsr_r = st.columns([5, 5])
        with col_dsr_l:
            dsr_income = st.number_input("연 소득 (만원)", min_value=100, value=6000, step=100)
            with st.form("add_loan_form"):
                st.markdown("##### ➕ 기존 대출 추가")
                l_col1, l_col2 = st.columns(2)
                with l_col1:
                    l_type = st.selectbox("대출 종류", ["주택담보대출(원리금균등)", "신용대출", "마이너스통장"])
                    l_amt = st.number_input("원금 (만)", value=5000, step=100)
                with l_col2:
                    l_rate = st.number_input("금리(%)", value=4.5, step=0.1)
                    if l_type in ["신용대출", "마이너스통장"]:
                        st.info("※ 상환기간 5년 적용")
                        l_period = 5
                    else:
                        l_period = st.number_input("잔여 기간(년)", value=30, step=1)
                if st.form_submit_button("추가"):
                    st.session_state['dsr_loans'].append({'type': l_type, 'amt': l_amt, 'rate': l_rate, 'period': l_period})
                    st.rerun()

            if st.button("초기화"): st.session_state['dsr_loans'] = []; st.rerun()

        with col_dsr_r:
            def calc_annual(l):
                pm = l['period'] * 12; mr = l['rate'] / 100 / 12
                if "마이너스" in l['type']: return l['amt'] * l['rate'] / 100
                return (l['amt'] * mr / (1-(1+mr)**(-pm))) * 12 if mr > 0 else (l['amt']/pm)*12
            
            total_annual = sum(calc_annual(l) for l in st.session_state['dsr_loans'])
            cur_dsr = (total_annual / dsr_income * 100) if dsr_income > 0 else 0
            
            dsr_f, annual_f = f"{cur_dsr:.1f}", f"{total_annual:,.0f}"
            st.markdown(f"""<div class="{'result-box' if cur_dsr <= 40 else 'danger-box'}">
              <div class="r-label">현재 합산 DSR</div>
              <div class="r-value">{dsr_f}%</div>
              <div class="r-sub">연간 상환액: {annual_f} 만원</div>
            </div>""", unsafe_allow_html=True)

            if st.session_state['dsr_loans']:
                loan_rows = [{'종류': l['type'][:10], '원금': f"{l['amt']:,}만", '적용기간': f"{l['period']}년", 'DSR비중': f"{(calc_annual(l)/dsr_income*100):.1f}%"} for l in st.session_state['dsr_loans']]
                display_centered_df(pd.DataFrame(loan_rows))

    # ── 2. LTV/취득세 ──
    with calc_tab2:
        st.markdown("#### 📐 주택수별 LTV 한도 & 취득세 시뮬레이터")
        col_ltv1, col_ltv2 = st.columns([4, 6])
        with col_ltv1:
            h_price = st.number_input("주택 매매가/KB시세 (만원)", min_value=1000, value=100000, step=1000)
            o_cnt = st.radio("취득 후 보유 주택 수", ["1주택", "2주택", "3주택 이상"])
            i_reg = st.radio("해당 지역 규제 여부", ["규제지역 (강남/서초/송파/용산)", "비규제지역"])
            i_first = st.checkbox("생애최초 주택 구입")

        with col_ltv2:
            regulated = "규제지역" in i_reg
            # LTV 로직
            ltv_rate = 50 if regulated else 70
            if "2주택" in o_cnt: ltv_rate = 30 if regulated else 60
            elif "3주택" in o_cnt: ltv_rate = 20 if regulated else 50
            if i_first and "1주택" in o_cnt: ltv_rate = min(ltv_rate + 10, 80)
            
            max_loan = h_price * ltv_rate / 100
            st.markdown(f"""<div class="result-box">
              <div class="r-label">최대 대출 한도 (LTV {ltv_rate}%)</div>
              <div class="r-value">{max_loan/10000:.2f} 억원 ({max_loan:,.0f}만)</div>
            </div>""", unsafe_allow_html=True)

            # 취득세 로직
            p_eok = h_price / 10000
            if "1주택" in o_cnt:
                acq_rate = 1.0 if p_eok <= 6 else (3.0 if p_eok > 9 else 1.0 + (p_eok-6)/3*2.0)
            elif "2주택" in o_cnt:
                acq_rate = 8.0 if regulated else (1.0 if p_eok <= 6 else (3.0 if p_eok > 9 else 1.0+(p_eok-6)/3*2.0))
            else:
                acq_rate = 12.0 if regulated else 8.0
            
            edu_r = 0.1 if acq_rate <= 1 else (0.2 if acq_rate <= 3 else 0.4)
            farm_r = 0.0 if acq_rate <= 1 else (0.2 if acq_rate <= 3 else 0.6)
            total_tax = h_price * (acq_rate + edu_r + farm_r) / 100

            tax_box = "result-box" if acq_rate <= 3 else ("warn-box" if acq_rate <= 8 else "danger-box")
            st.markdown(f"""<div class="{tax_box}">
              <div class="r-label">예상 취득세 합계 (세율 {acq_rate + edu_r + farm_r:.1f}%)</div>
              <div class="r-value">{total_tax/10000:.2f} 억원 ({total_tax:,.0f}만)</div>
            </div>""", unsafe_allow_html=True)

    # ── 3. 복리 계산기 ──
    with calc_tab3:
        col_c_left, col_c_right = st.columns([6, 4])
        with col_c_right:
            st.markdown("##### 입력 패널")
            principal = st.number_input("초기 원금 (만원)", value=3000, step=100)
            rate_val = st.number_input("연 수익률 (%)", value=8.0, step=1.0)
            madd = st.number_input("매월 추가 납입 (만원)", value=100, step=10)
            dval = st.number_input("투자 기간 (년)", value=10, step=1)
            
        with col_c_left:
            mr = (rate_val/100)/12; bal, inv = principal, principal
            hist = [{"연차": 0, "총자산(만)": principal, "누적원금(만)": principal, "누적이자(만)": 0}] 
            for m in range(1, dval*12+1):
                bal += madd; inv += madd; bal += bal * mr
                if m % 12 == 0: hist.append({"연차": m//12, "총자산(만)": round(bal), "누적원금(만)": round(inv), "누적이자(만)": round(bal-inv)})
            
            df_h = pd.DataFrame(hist)
            
            base_c = alt.Chart(df_h).encode(x=alt.X('연차:Q', axis=alt.Axis(format='d', title='투자 기간 (년)')))
            area = base_c.mark_area(opacity=0.3, color='#9E9E9E').encode(y=alt.Y('누적원금(만):Q'))
            line = base_c.mark_line(color='#388E3C', strokeWidth=3, point=True).encode(y=alt.Y('총자산(만):Q', title='금액 (만원)'))
            
            # 그래프 위에 자산 액수(데이터 레이블) 텍스트 표기
            text_asset = line.mark_text(align='left', dx=5, dy=-10, fontSize=11, color='#1B5E20', fontWeight='bold').encode(
                text=alt.Text('총자산(만):Q', format=',')
            )
            st.altair_chart((area + line + text_asset).interactive().properties(height=300), use_container_width=True)
            
            bal_f, inv_f, interest_f = f"{bal/10000:.2f}", f"{inv:,.0f}", f"{(bal-inv):,.0f}"
            st.markdown(f"""<div class="result-box">
              <div class="r-label">최종 자산 결산</div>
              <div class="r-value">{bal_f} 억원</div>
              <div class="r-sub">투입 원금: {inv_f}만 원 | <b style="color:#D32F2F; font-size:1.0rem;">순수 이자 수익: {interest_f}만 원</b></div>
            </div>""", unsafe_allow_html=True)

            st.markdown("##### 📋 연차별 데이터")
            display_centered_df(df_h)

    # ── 4. 최저시급 ──
    with calc_tab4:
        @st.cache_data(ttl=3600)
        def get_live_rate():
            try: return round(requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()['rates']['KRW'], 1)
            except: return 1450.0
        live_rate = get_live_rate()

        wage_df = pd.DataFrame({
            '연도': [2018,2019,2020,2021,2022,2023,2024,2025,2026],
            '최저시급(원)': [7530, 8350, 8590, 8720, 9160, 9620, 9860, 10030, 10320],
            '연평균환율(원/$)':[1100.3, 1165.7, 1180.1, 1144.0, 1291.9, 1305.5, 1363.0, 1421.0, live_rate],
        })
        wage_df['달러환산(USD)'] = (wage_df['최저시급(원)'] / wage_df['연평균환율(원/$)']).round(2)

        # resolve_scale(y='independent')를 통해 좌/우 Y축 겹침 완벽 해결, 우측 Y축 레이블(달러)만 유지
        base = alt.Chart(wage_df).encode(x=alt.X('연도:O', axis=alt.Axis(labelAngle=0)))
        
        bars = base.mark_bar(color='#B3E5FC', opacity=0.8, width=35).encode(
            # 왼쪽 Y축만 남김
            y=alt.Y('최저시급(원):Q', title='최저시급 (KRW)')
        )
        bar_lbl = base.mark_text(align='center', baseline='bottom', dy=-5, fontSize=11, color='#01579B', fontWeight='bold').encode(
            y=alt.Y('최저시급(원):Q'), text=alt.Text('최저시급(원):Q', format=',')
        )
        
        line = base.mark_line(color='#388E3C', strokeWidth=3, point=alt.OverlayMarkDef(size=60)).encode(
            # 오른쪽 Y축 (달러) 표기
            y=alt.Y('달러환산(USD):Q', title='달러 가치 (USD)', scale=alt.Scale(domain=[6.0, 8.5]))
        )
        line_lbl = line.mark_text(align='left', dx=8, dy=-5, fontSize=11, color='#1B5E20', fontWeight='bold').encode(
            text=alt.Text('달러환산(USD):Q', format='.2f')
        )

        st.altair_chart(alt.layer(bars, bar_lbl, line, line_lbl).resolve_scale(y='independent').properties(height=350), use_container_width=True)
        
        st.markdown("##### 📋 세부 데이터 테이블")
        formatted_df = wage_df.copy()
        formatted_df['인상액(원)'] = formatted_df['최저시급(원)'].diff().fillna(0).astype(int)
        formatted_df['인상률(%)'] = (formatted_df['최저시급(원)'].pct_change() * 100).round(1).fillna(0)
        formatted_df = formatted_df[['연도','최저시급(원)','인상액(원)','인상률(%)','연평균환율(원/$)','달러환산(USD)']]
        
        for col in ['최저시급(원)', '인상액(원)']: formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,}")
        for col in ['인상률(%)', '연평균환율(원/$)', '달러환산(USD)']: formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.1f}" if col != '달러환산(USD)' else f"${x:.2f}")
        
        display_centered_df(formatted_df)
