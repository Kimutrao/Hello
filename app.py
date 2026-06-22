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
# 1. 페이지 설정 & 전역 CSS (푸른/초록톤)
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
.lock-badge { display: inline-block; background: #FFF3E0; border: 1px solid #FFB300; border-radius: 6px; padding: 2px 10px; font-size: 0.76rem; color: #E65100; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <div class="app-title">📗 김철수의 투자기록실</div>
  <div class="app-subtitle">부동산 시세 분석 · 투자 철학 · 금융 계산기</div>
</div>
""", unsafe_allow_html=True)

# ── 관리자 비밀번호 세팅 ──
ADMIN_PW = "kimcs2024!"  # 원하시는 비밀번호로 변경 가능
def is_admin():
    return st.session_state.get("admin_logged_in", False)

# ── Session State 초기화 ──
defaults = {
    'admin_logged_in': False,
    'board_view': 'list',
    'current_post': None,
    'selected_cat': '전체글보기',
    'compare_apts': [],
    'dsr_loans': [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지': {'지역': '서울 마포구', '기본': '860세대, 2010년식', '매매가': '11.5', '전세가': '6.5', '매물수': '12', '특징': '초품아, 마포 상암', 'kb시세': '11.2', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', '매매가': '8.2', '전세가': '5.2', '매물수': '8', '특징': '신분당선 호매실 개통 예정', 'kb시세': '8.0', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
        '성복역롯데캐슬골드타운': {'지역': '경기 용인시', '기본': '2300세대, 2019년식', '매매가': '12.8', '전세가': '7.5', '매물수': '25', '특징': '성복역 지하 통로 연결', 'kb시세': '12.5', 'history': [{'date': '2026-06-22', 'opinion': '신분당선 라인 대장급 입지.'}]},
    }

if 'geo_db' not in st.session_state:
    st.session_state['geo_db'] = {
        '상암월드컵파크10단지': [37.5843, 126.8821], '호반베르디움더센트럴': [37.2735, 126.9422], '성복역롯데캐슬골드타운': [37.3138, 127.0805]
    }

if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "1. 부동산 시장 접근과 매수 의미", "date": "2026-06", "content": "유의미한 상승이 지속될까? 잘 모르겠음. 이제 아파트 시장은 리스크 헷지 상품이 되어버림."},
        {"category": "규제 & 정책 분석", "title": "2. 영끌금지와 생존 세팅값", "date": "2026-06", "content": "장기간 더 버틸 수 있는 세팅값에 의미를 두는게 좋지 않을까."},
    ]

# ── 사이드바 (비밀번호 기능 유지) ──
with st.sidebar:
    st.markdown("### 🔐 관리자 로그인")
    if is_admin():
        st.success("✅ 관리자 모드 활성")
        if st.button("로그아웃"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
    else:
        pw = st.text_input("비밀번호", type="password", key="admin_pw_input")
        if st.button("로그인"):
            if pw == ADMIN_PW:
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")

# ── 메인 탭 ──
tab_basic, tab_mind, tab_realestate, tab_finance = st.tabs([
    "📖 투자철학", "🧠 기록 & 게시판", "🏢 관심단지 & 비교", "💰 계산기 & 매크로"
])

# ═══════════════════════════════════════════
# 탭 1 & 2: 투자철학 & 게시판 (이전과 동일하게 유지)
# ═══════════════════════════════════════════
with tab_basic:
    st.subheader("📖 흔들리지 않는 4가지 핵심 기준")
    # (내용 생략 - 기존과 동일)
    st.write("부동산의 본질은 리스크 헷지, 영끌 금지, 시장 소음 구별, 세금 계산의 중요성 등...")

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
        if is_admin():
            if st.button("✍️ 새 글 작성", use_container_width=True):
                st.session_state['board_view'] = 'write'
                st.rerun()

    with col_board:
        display_posts = list(st.session_state['blog_db']) if st.session_state['selected_cat'] == "전체글보기" else [p for p in st.session_state['blog_db'] if p['category'] == st.session_state['selected_cat']]

        if st.session_state['board_view'] == 'write' and is_admin():
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
            st.write(post['content'])

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
# 탭 3: 관심단지 & 비교 (하위 탭 3개로 완벽 분리)
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 관심단지 레이더 & 교차 비교")

    # [오류 해결!] freq='M' -> freq='ME' 로 변경하여 에러 완벽 차단
    @st.cache_data
    def get_mock_trends(apt_name, years=3):
        # 실시간 API 연동 전 1~5년 데이터 가상 렌더링
        months = pd.date_range(end=pd.Timestamp.today(), periods=years*12, freq='ME').strftime('%Y-%m').tolist()
        bp = float(st.session_state['memo_db'].get(apt_name, {}).get('kb시세', 9.0))
        random.seed(len(apt_name) * years)
        trend_s, trend_j, rows = 0.0, 0.0, []
        for m in months:
            trend_s += random.uniform(-0.06, 0.1)
            trend_j += random.uniform(-0.04, 0.08)
            sale = round(bp + trend_s + random.uniform(-0.1, 0.1), 2)
            jeonse = round((bp*0.6) + trend_j + random.uniform(-0.1, 0.1), 2)
            rows.append({'계약월': m, '아파트명': apt_name, '매매평균(억)': sale, '전세평균(억)': jeonse})
        return pd.DataFrame(rows)

    # 하위 탭 3개 생성
    subtab_single, subtab_compare, subtab_add = st.tabs(["🔍 단지 상세 (지도 포함)", "📊 다중 단지 비교 분석", "➕ 신규단지 등록/수정"])

    # ── [1] 단지 상세 탭 ──
    with subtab_single:
        col_panel, col_view = st.columns([3, 7])
        with col_panel:
            st.markdown("##### 📍 지역 선택")
            all_regions = sorted(set(v['지역'] for v in st.session_state['memo_db'].values()))
            sel_region = st.selectbox("지역", ["전체"] + all_regions, key="single_region")
            region_apts = list(st.session_state['memo_db'].keys()) if sel_region == "전체" else [k for k, v in st.session_state['memo_db'].items() if v.get('지역') == sel_region]
            
            st.markdown("##### 🏢 단지 선택")
            chosen_apt = st.radio("단지", region_apts, key="single_apt") if region_apts else None
            
            if chosen_apt:
                st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
                view_years = st.slider("그래프 조회 기간 (년)", 1, 5, 3)

        with col_view:
            if chosen_apt:
                info = st.session_state['memo_db'][chosen_apt]
                coords = st.session_state['geo_db'].get(chosen_apt, [37.5665, 126.9780])
                
                # 1. 지도 레이더
                st.markdown(f"##### 🎯 {chosen_apt} 지도 레이더")
                m = folium.Map(location=coords, zoom_start=14)
                popup_html = f"<b>{chosen_apt}</b><br>매매 호가: {info.get('호가_매매', '-')}억"
                folium.Marker(location=coords, popup=folium.Popup(popup_html, max_width=200), icon=folium.Icon(color='blue', icon='home')).add_to(m)
                st_folium(m, width=800, height=300, key=f"map_{chosen_apt}")

                # 2. 실거래 트렌드 그래프
                st.markdown(f"##### 📈 국토부 실거래가 추이 ({view_years}년)")
                df_trend = get_mock_trends(chosen_apt, view_years)
                df_melt = df_trend.melt(id_vars=['계약월', '아파트명'], value_vars=['매매평균(억)', '전세평균(억)'], var_name='구분', value_name='금액(억)')
                
                chart = alt.Chart(df_melt).mark_line(point=True, strokeWidth=3).encode(
                    x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)),
                    y=alt.Y('금액(억):Q', scale=alt.Scale(zero=False), title='금액(억)'),
                    color=alt.Color('구분:N', scale=alt.Scale(domain=['매매평균(억)', '전세평균(억)'], range=['#0288D1', '#388E3C'])),
                    tooltip=['계약월', '구분', '금액(억)']
                ).properties(height=280)
                st.altair_chart(chart, use_container_width=True)

                # 3. 하단 요약 정보 (KB시세 및 대출한도 포함)
                kb_val = float(info.get('kb시세', 0))
                st.markdown(f"""
                <div style="display:flex; gap:15px; margin-bottom:15px;">
                    <div style="background:#E1F5FE; padding:10px 15px; border-radius:8px; border-left:4px solid #0288D1;">
                        <span style="font-size:0.8rem; color:#555;">KB시세 (대출기준)</span><br>
                        <span style="font-size:1.2rem; font-weight:bold; color:#01579B;">{kb_val} 억원</span>
                    </div>
                    <div style="background:#E8F5E9; padding:10px 15px; border-radius:8px; border-left:4px solid #388E3C;">
                        <span style="font-size:0.8rem; color:#555;">예상 최대 담보대출 (LTV 70% 가정)</span><br>
                        <span style="font-size:1.2rem; font-weight:bold; color:#1B5E20;">{kb_val * 0.7:.2f} 억원</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**📄 투자 의견 히스토리**")
                for h in info.get('history', []):
                    st.markdown(f"""<div class="timeline-box"><div class="timeline-date">📅 {h['date']}</div><div class="timeline-content">{h['opinion']}</div></div>""", unsafe_allow_html=True)

    # ── [2] 다중 단지 비교 탭 ──
    with subtab_compare:
        st.markdown("##### 📊 비교할 단지를 여러 개 선택하세요")
        all_apts = list(st.session_state['memo_db'].keys())
        comp_apts = st.multiselect("비교 단지 선택", all_apts, default=all_apts[:2] if len(all_apts)>=2 else all_apts)
        
        if comp_apts:
            compare_rows = []
            for apt in comp_apts:
                info = st.session_state['memo_db'].get(apt, {})
                last_trend = get_mock_trends(apt, 1).iloc[-1]
                compare_rows.append({
                    '단지명': apt, '매매 호가(억)': info.get('호가_매매', '-'), '전세 호가(억)': info.get('호가_전세', '-'),
                    '실거래 매매(억)': last_trend['매매평균(억)'], '실거래 전세(억)': last_trend['전세평균(억)'],
                    '매물수': info.get('매물수', '-'), '특징': info.get('특징', '-')
                })
            st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

            df_all = pd.concat([get_mock_trends(a, 3) for a in comp_apts])
            compare_chart = alt.Chart(df_all).mark_line(point=True, strokeWidth=2).encode(
                x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)),
                y=alt.Y('매매평균(억):Q', scale=alt.Scale(zero=False), title='매매 실거래가(억)'),
                color=alt.Color('아파트명:N', legend=alt.Legend(title="단지명")),
                tooltip=['계약월', '아파트명', '매매평균(억)']
            ).properties(height=300)
            st.altair_chart(compare_chart, use_container_width=True)

    # ── [3] 단지 등록/수정 탭 ──
    with subtab_add:
        if not is_admin():
            st.warning("🔒 단지 등록 및 의견 업데이트는 관리자(본인)만 가능합니다.")
        else:
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                st.markdown("#### ➕ 신규 단지 등록 (지도 연동)")
                with st.form("new_apt_form"):
                    n_reg = st.text_input("지역명", placeholder="서울 마포구")
                    n_name = st.text_input("단지명", placeholder="마포래미안푸르지오")
                    n_addr = st.text_input("실제 도로명 주소 (지도 핀셋용)")
                    n_hh = st.text_input("세대수/연식")
                    n_kb = st.text_input("KB시세 (억)")
                    n_sale = st.text_input("매매 호가 (억)")
                    n_jeonse = st.text_input("전세 호가 (억)")
                    n_feat = st.text_input("주요 호재/특징")
                    n_op = st.text_area("첫 투자 의견 기록")
                    
                    if st.form_submit_button("신규 단지 저장"):
                        if n_name and n_addr:
                            try:
                                loc = Nominatim(user_agent="kimcs_app").geocode(n_addr, timeout=5)
                                st.session_state['geo_db'][n_name] = [loc.latitude, loc.longitude] if loc else [37.566, 126.978]
                            except:
                                st.session_state['geo_db'][n_name] = [37.566, 126.978]
                            
                            st.session_state['memo_db'][n_name] = {
                                '지역': n_reg, '기본': n_hh, 'kb시세': n_kb, '호가_매매': n_sale, '호가_전세': n_jeonse, '특징': n_feat,
                                'history': [{'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': n_op}] if n_op else []
                            }
                            st.success("등록 완료!")
                            st.rerun()

            with col_add2:
                st.markdown("#### ✏️ 기존 단지 정보 수정 및 의견 추가")
                edit_apt = st.selectbox("수정할 단지 선택", list(st.session_state['memo_db'].keys()))
                if edit_apt:
                    e_info = st.session_state['memo_db'][edit_apt]
                    with st.form("edit_apt_form"):
                        e_kb = st.text_input("KB시세 (억)", value=e_info.get('kb시세', ''))
                        e_sale = st.text_input("매매 호가 (억) 업데이트", value=e_info.get('호가_매매', ''))
                        e_jeonse = st.text_input("전세 호가 (억) 업데이트", value=e_info.get('호가_전세', ''))
                        e_cnt = st.text_input("현재 매물 수", value=e_info.get('매물수', ''))
                        e_append = st.text_area("추가 투자 의견 (타임라인에 누적됨)")
                        
                        if st.form_submit_button("정보 업데이트"):
                            e_info.update({'kb시세': e_kb, '호가_매매': e_sale, '호가_전세': e_jeonse, '매물수': e_cnt})
                            if e_append:
                                e_info['history'].append({'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': e_append})
                            st.success("업데이트 완료!")
                            st.rerun()

# ═══════════════════════════════════════════
# 탭 4: 계산기 & 매크로 (DSR 5년 고정, 최저시급 오류 수정)
# ═══════════════════════════════════════════
with tab_finance:
    st.subheader("💰 계산기 & 매크로 지표실")
    calc_tab1, calc_tab2, calc_tab3 = st.tabs(["🏦 DSR 계산기", "🔢 복리 계산기", "📊 최저시급 & 환율"])

    # ── 1. DSR 계산기 ──
    with calc_tab1:
        col_dsr_l, col_dsr_r = st.columns([5, 5])
        with col_dsr_l:
            dsr_income = st.number_input("연 소득 (만원)", min_value=100, value=6000, step=100)
            
            with st.form("add_loan_form"):
                st.markdown("##### ➕ 기존 대출 추가")
                l_type = st.selectbox("대출 종류", ["주택담보대출(원리금균등)", "신용대출", "마이너스통장", "자동차할부/기타"])
                l_amt = st.number_input("대출 원금 (만원)", min_value=0, value=5000, step=100)
                l_rate = st.number_input("금리 (%)", min_value=0.1, value=4.5, step=0.1)
                
                # 신용대출/마통은 잔여기간을 5년으로 고정 안내 (입력 무시됨)
                if l_type in ["신용대출", "마이너스통장"]:
                    st.info("💡 신용대출 및 마이너스통장은 규정에 따라 산정기간이 **5년**으로 고정 적용됩니다.")
                    l_period = 5
                else:
                    l_period = st.number_input("잔여/산정 기간 (년)", min_value=1, value=30, step=1)
                
                if st.form_submit_button("추가하기"):
                    st.session_state['dsr_loans'].append({'type': l_type, 'amt': l_amt, 'rate': l_rate, 'period': l_period})
                    st.rerun()

            if st.button("🗑️ 전체 초기화"):
                st.session_state['dsr_loans'] = []
                st.rerun()

        with col_dsr_r:
            st.markdown("##### 📊 DSR 산출 결과 (1금융권 40% 기준)")
            def calc_annual(l):
                amt = l['amt'] * 10000; r = l['rate'] / 100; pm = l['period'] * 12; mr = r / 12
                if "마이너스" in l['type']: return amt * r / 10000
                return (amt * mr / (1-(1+mr)**(-pm))) * 12 / 10000 if mr > 0 else (amt/pm)*12/10000

            total_annual = sum(calc_annual(l) for l in st.session_state['dsr_loans'])
            cur_dsr = (total_annual / dsr_income * 100) if dsr_income > 0 else 0
            
            box_cls = "result-box" if cur_dsr <= 40 else "danger-box"
            st.markdown(f"""<div class="{box_cls}">
              <div class="r-label">현재 합산 DSR</div>
              <div class="r-value">{cur_dsr:.1f}%</div>
              <div class="r-sub">연간 총 원리금 상환액: {total_annual:,.0f} 만원</div>
            </div>""", unsafe_allow_html=True)

            if st.session_state['dsr_loans']:
                loan_rows = [{'종류': l['type'][:10], '원금(만)': f"{l['amt']:,}", '금리': f"{l['rate']}%", '산정기간': f"{l['period']}년", '연원리금(만)': f"{calc_annual(l):.0f}"} for l in st.session_state['dsr_loans']]
                st.dataframe(pd.DataFrame(loan_rows), use_container_width=True, hide_index=True)

            st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
            st.markdown("""
            **💡 대출 종류별 DSR 산정 만기 규정**
            * **주택담보대출:** 실제 약정 상환기간 (최장 40~50년 적용)
            * **신용대출 / 마이너스통장:** 대출금액 상관없이 무조건 **5년** 적용 (매우 중요)
            * **기타 대출 (할부 등):** 실제 상환기간
            """)

    # ── 2. 복리 계산기 ──
    with calc_tab2:
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            principal = st.number_input("초기 원금 (만원)", min_value=0, value=3000, step=100)
            rate_val = st.number_input("연 수익률 (%)", value=8.0, step=1.0)
            madd = st.number_input("매월 추가 적립 (만원)", min_value=0, value=100, step=10)
            dval = st.number_input("투자 기간 (년)", min_value=1, value=10, step=1)
        with col_c2:
            total_m = dval * 12; mr = (rate_val/100)/12; bal, inv = principal, principal
            for m in range(1, total_m+1):
                bal += madd; inv += madd; bal += bal * mr
            st.markdown(f"""<div class="result-box">
              <div class="r-label">최종 자산</div>
              <div class="r-value">{bal/10000:.2f} 억원</div>
              <div class="r-sub">투입 원금: {inv:,.0f}만 | 총 이자수익: {bal-inv:,.0f}만</div>
            </div>""", unsafe_allow_html=True)

    # ── 3. 최저시급 (2018년 시작, Y축 텍스트 겹침 완벽 수정) ──
    with calc_tab3:
        st.markdown("#### 📊 최근 최저시급 트렌드 & 달러 가치 (2018~현재)")
        
        @st.cache_data(ttl=3600)
        def get_live_rate():
            try: return round(requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()['rates']['KRW'], 1)
            except: return 1450.0

        live_rate = get_live_rate()

        wage_df = pd.DataFrame({
            '연도': ['2018','2019','2020','2021','2022','2023','2024','2025','2026'],
            '최저시급(원)': [7530, 8350, 8590, 8720, 9160, 9620, 9860, 10030, 10320],
            '연평균환율(원/$)':[1100.3, 1165.7, 1180.1, 1144.0, 1291.9, 1305.5, 1363.0, 1421.0, live_rate],
        })
        wage_df['달러환산(USD)'] = (wage_df['최저시급(원)'] / wage_df['연평균환율(원/$)']).round(2)

        st.caption(f"📡 현재 실시간 환율 적용 중: **{live_rate:,.1f} 원/달러**")

        base = alt.Chart(wage_df).encode(x=alt.X('연도:O', axis=alt.Axis(labelAngle=0)))
        
        bars = base.mark_bar(color='#B3E5FC', opacity=0.8, width=35).encode(
            y=alt.Y('최저시급(원):Q', title='최저시급 (원)', axis=alt.Axis(titleColor='#01579B'))
        )
        bar_lbl = base.mark_text(align='center', baseline='bottom', dy=-5, fontSize=11, color='#01579B', fontWeight='bold').encode(
            y=alt.Y('최저시급(원):Q'), text=alt.Text('최저시급(원):Q', format='d')
        )
        
        line = base.mark_line(color='#388E3C', strokeWidth=3, point=alt.OverlayMarkDef(color='#388E3C', size=80)).encode(
            y=alt.Y('달러환산(USD):Q', title='달러 환산 (USD)', scale=alt.Scale(domain=[6.0, 8.5]), axis=alt.Axis(titleColor='#1B5E20'))
        )
        line_lbl = base.mark_text(align='center', baseline='bottom', dy=-10, fontSize=11, color='#1B5E20', fontWeight='bold').encode(
            y=alt.Y('달러환산(USD):Q'), text=alt.Text('달러환산(USD):Q', format='.2f')
        )

        combined = alt.layer(bars, bar_lbl, line, line_lbl).resolve_scale(y='independent').properties(height=360)
        st.altair_chart(combined, use_container_width=True)
