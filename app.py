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

# ── 관리자 세팅 (로그인 폼 분리) ──
ADMIN_PW = "kimcs2024!"  
def is_admin(): return st.session_state.get("admin_logged_in", False)

defaults = {'admin_logged_in': False, 'board_view': 'list', 'current_post': None, 'selected_cat': '전체글보기', 'compare_apts': [], 'dsr_loans': []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {
        '상암월드컵파크10단지': {'지역': '서울 마포구', '기본': '860세대, 2010년식', 'kb시세': 11.2, '호가_매매': 11.5, '호가_전세': 6.5, '전월거래량': 5, '특징': '초품아, 마포 상암', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', 'kb시세': 8.0, '호가_매매': 8.2, '호가_전세': 5.2, '전월거래량': 12, '특징': '신분당선 호매실 호재', '작성일': '2026-06-22', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
    }
if 'geo_db' not in st.session_state:
    st.session_state['geo_db'] = {'상암월드컵파크10단지': [37.5843, 126.8821], '호반베르디움더센트럴': [37.2735, 126.9422]}

# ── 사이드바 ──
with st.sidebar:
    st.markdown("### 🔐 사이트 관리자 메뉴")
    if is_admin():
        st.success("✅ 인증 완료")
        if st.button("로그아웃"):
            st.session_state['admin_logged_in'] = False; st.rerun()
    else:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == ADMIN_PW: st.session_state['admin_logged_in'] = True; st.rerun()
            else: st.error("비번 오류")

# ── 탭 구성 ──
tab_basic, tab_mind, tab_realestate, tab_finance = st.tabs(["📖 투자철학", "🧠 기록 & 게시판", "🏢 단지 분석 & 비교", "💰 매크로 & 계산기"])

with tab_basic:
    st.write("부동산 본질은 리스크 헷지, 무리한 영끌 금지, 세금 계산 필수 (기존 텍스트 생략)")

with tab_mind:
    st.info("이전에 완성했던 게시판 기능이 이곳에 들어갑니다.")

# =================================================================
# 탭 3: 관심단지 분석 & 비교
# =================================================================
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

    sub_single, sub_comp, sub_hoga, sub_add = st.tabs(["🔍 단지 상세 분석", "📊 실거래가 비교", "📋 호가/매물 비교", "➕ 단지 관리(관리자)"])

    # ── [1] 단지 상세 분석 ──
    with sub_single:
        col_panel, col_view = st.columns([2.5, 7.5])
        
        with col_panel:
            st.markdown("##### 📍 타겟 선택")
            sel_region = st.selectbox("지역", ["전체"] + sorted(set(v['지역'] for v in st.session_state['memo_db'].values())))
            region_apts = list(st.session_state['memo_db'].keys()) if sel_region == "전체" else [k for k, v in st.session_state['memo_db'].items() if v.get('지역') == sel_region]
            chosen_apt = st.radio("분석할 단지", region_apts) if region_apts else None

        with col_view:
            if chosen_apt:
                info = st.session_state['memo_db'][chosen_apt]
                kb_price = float(info.get('kb시세', 0))
                
                st.markdown(f"#### 🎯 {chosen_apt}")
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; background:#F9FBFD; padding:15px; border-radius:10px; border:1px solid #B3E5FC;">
                    <div><span style="color:#666; font-size:0.9rem;">매매 호가 (최근 업데이트)</span><br><b style="font-size:1.4rem; color:#E65100;">{info.get('호가_매매', '-')} 억</b></div>
                    <div><span style="color:#666; font-size:0.9rem;">전세 호가</span><br><b style="font-size:1.4rem; color:#1B5E20;">{info.get('호가_전세', '-')} 억</b></div>
                    <div><span style="color:#666; font-size:0.9rem;">KB 시세 (기준가)</span><br><b style="font-size:1.4rem; color:#01579B;">{kb_price} 억</b></div>
                    <div><span style="color:#666; font-size:0.9rem;">전월 총 거래량</span><br><b style="font-size:1.4rem; color:#424242;">{info.get('전월거래량', '-')} 건</b></div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="sec-div">', unsafe_allow_html=True)

                g_col1, g_col2 = st.columns([7, 3])
                with g_col1: st.markdown("##### 📈 국토부 실거래가 추이 (건별 거래량 표기)")
                with g_col2: view_years = st.slider("조회 기간 (년)", 1, 5, 1, label_visibility="collapsed")
                
                df_raw = get_mock_scatter_data(chosen_apt, view_years)
                df_mean = df_raw.groupby('계약월', as_index=False)['실거래가(억)'].mean()
                
                base = alt.Chart(df_raw).encode(x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)))
                scatter = base.mark_circle(color='red', opacity=0.6, size=40).encode(y='실거래가(억):Q', tooltip=['계약월', '실거래가(억)'])
                line = alt.Chart(df_mean).mark_line(color='#0288D1', strokeWidth=3).encode(x='계약월:O', y='실거래가(억):Q')
                
                st.altair_chart((scatter + line).properties(height=300), use_container_width=True)

                bot_col1, bot_col2 = st.columns([5, 5])
                
                with bot_col1:
                    st.markdown("##### 📍 단지 지도")
                    coords = st.session_state['geo_db'].get(chosen_apt, [37.566, 126.978])
                    m = folium.Map(location=coords, zoom_start=15)
                    folium.Marker(coords, tooltip=chosen_apt, icon=folium.Icon(color='blue')).add_to(m)
                    st_folium(m, width=400, height=200, key=f"map_{chosen_apt}")
                    
                    st.markdown("##### 📝 특징 및 투자의견")
                    st.info(f"**특징:** {info.get('특징', '-')}")
                    for h in info.get('history', []):
                        st.markdown(f"<div class='timeline-box'><div class='timeline-date'>📅 {h['date']}</div><div class='timeline-content'>{h['opinion']}</div></div>", unsafe_allow_html=True)
                
                with bot_col2:
                    st.markdown("##### 💰 예상 대출 한도 (KB시세 기준)")
                    ltv_70 = f"{kb_price * 0.7:.2f}"
                    ltv_50 = f"{kb_price * 0.5:.2f}"
                    ltv_30 = f"{kb_price * 0.3:.2f}"
                    st.markdown(f"""
                    - **LTV 70% (생애최초 등):** <b style="color:#0288D1;">{ltv_70} 억</b>
                    - **LTV 50% (규제/일반):** <b style="color:#388E3C;">{ltv_50} 억</b>
                    - **LTV 30% (다주택 등):** <b style="color:#E65100;">{ltv_30} 억</b>
                    """, unsafe_allow_html=True)
                    
                    # ── [안전화 적용] 문자열 선행 포맷팅으로 SyntaxError 원천 차단 ──
                    st.markdown("##### 🏛️ 예상 취득세 (농특/교육세 포함 추정치)")
                    est_tax_1 = kb_price * 10000 * 0.011 if kb_price <= 6 else kb_price * 10000 * 0.033
                    est_tax_2 = kb_price * 10000 * 0.084
                    est_tax_3 = kb_price * 10000 * 0.124
                    
                    tax1_eok, tax1_man = f"{est_tax_1/10000:.2f}", f"{est_tax_1:,.0f}"
                    tax2_eok, tax2_man = f"{est_tax_2/10000:.2f}", f"{est_tax_2:,.0f}"
                    tax3_eok, tax3_man = f"{est_tax_3/10000:.2f}", f"{est_tax_3:,.0f}"
                    
                    st.markdown(f"""
                    - **1주택자 (1~3%):** 약 **{tax1_eok} 억** ({tax1_man}만)
                    - **2주택자 (조정 8%):** 약 **{tax2_eok} 억** ({tax2_man}만)
                    - **3주택자 (조정 12%):** 약 **{tax3_eok} 억** ({tax3_man}만)
                    """, unsafe_allow_html=True)

    # ── [2] 실거래가 다중 비교 ──
    with sub_comp:
        all_apts = list(st.session_state['memo_db'].keys())
        comp_apts = st.multiselect("비교 단지 선택", all_apts, default=all_apts[:2])
        if comp_apts:
            rows = []
            for apt in comp_apts:
                info = st.session_state['memo_db'].get(apt, {})
                df_raw = get_mock_scatter_data(apt, 1)
                rows.append({'단지명': apt, '지역': info.get('지역', '-'), '세대수': info.get('기본', '-'), '전월 실거래 평균(억)': df_raw['실거래가(억)'].mean().round(2), '전월 거래량': info.get('전월거래량', '-')})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── [3] 호가/매물 비교 ──
    with sub_hoga:
        st.markdown("#### 📋 단지별 현재 호가 현황판")
        hoga_rows = []
        for apt, info in st.session_state['memo_db'].items():
            hoga_rows.append({'단지명': apt, '지역': info.get('지역', '-'), 'KB시세(억)': info.get('kb시세', '-'), '매매 호가(억)': info.get('호가_매매', '-'), '전세 호가(억)': info.get('호가_전세', '-'), '호가 갭(억)': round(float(info.get('호가_매매',0)) - float(info.get('호가_전세',0)), 2), '특징': info.get('특징', '-')})
        st.dataframe(pd.DataFrame(hoga_rows), use_container_width=True, hide_index=True)

    # ── [4] 단지 등록 (관리자) ──
    with sub_add:
        if not is_admin(): st.warning("관리자 로그인 후 이용 가능합니다.")
        else: st.write("단지 등록 폼 (기존과 동일)")

# =================================================================
# 탭 4: 계산기 & 매크로 (안전화 수식 적용)
# =================================================================
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
                        st.info("※ 규정에 따라 산정기간 5년이 강제 적용됩니다.")
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
            
            box_cls = "result-box" if cur_dsr <= 40 else "danger-box"
            dsr_f, annual_f = f"{cur_dsr:.1f}", f"{total_annual:,.0f}"
            st.markdown(f"""<div class="{box_cls}">
              <div class="r-label">현재 합산 DSR</div>
              <div class="r-value">{dsr_f}%</div>
              <div class="r-sub">연간 상환액: {annual_f} 만원</div>
            </div>""", unsafe_allow_html=True)

    # ── 2. LTV/취득세 ──
    with calc_tab2:
        st.info("여기에 주택수별 세금 종합 시뮬레이터가 연동됩니다.")

    # ── 3. 복리 계산기 ──
    with calc_tab3:
        col_c1, col_c2 = st.columns([4, 6])
        with col_c1:
            principal = st.number_input("원금 (만원)", value=3000, step=100)
            rate_val = st.number_input("연 수익률(%)", value=8.0, step=1.0)
            madd = st.number_input("매월 추가(만원)", value=100, step=10)
            dval = st.number_input("기간(년)", value=10, step=1)
        with col_c2:
            mr = (rate_val/100)/12; bal, inv, hist = principal, principal, []
            for m in range(1, dval*12+1):
                madd_val = madd
                bal += madd_val; inv += madd_val; bal += bal * mr
                if m % 12 == 0: hist.append({"연차": f"{m//12}년", "총자산": round(bal), "누적원금": round(inv)})
            df_h = pd.DataFrame(hist)
            
            base_c = alt.Chart(df_h).encode(x=alt.X('연차:O', axis=alt.Axis(labelAngle=0)))
            area = base_c.mark_area(opacity=0.3, color='#9E9E9E').encode(y=alt.Y('누적원금:Q'))
            line = base_c.mark_line(color='#388E3C', strokeWidth=3, point=True).encode(y='총자산:Q')
            st.altair_chart((area + line).properties(height=250), use_container_width=True)
            
            bal_f, inv_f, interest_f = f"{bal/10000:.2f}", f"{inv:,.0f}", f"{(bal-inv):,.0f}"
            st.markdown(f"""<div class="result-box">
              <div class="r-label">최종 자산 결산</div>
              <div class="r-value">{bal_f} 억원</div>
              <div class="r-sub">원금 합계: {inv_f}만 원 | 순수 이자: {interest_f}만 원</div>
            </div>""", unsafe_allow_html=True)

    # ── 4. 최저시급 ──
    with calc_tab4:
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

        base = alt.Chart(wage_df).encode(x=alt.X('연도:O', axis=alt.Axis(labelAngle=0)))
        bars = base.mark_bar(color='#B3E5FC', opacity=0.8, width=35).encode(y=alt.Y('최저시급(원):Q', title='최저시급 (KRW)'))
        line = base.mark_line(color='#388E3C', strokeWidth=3, point=alt.OverlayMarkDef(size=60)).encode(y=alt.Y('달러환산(USD):Q', title='달러 가치 (USD)', scale=alt.Scale(domain=[6.0, 8.5])))
        line_txt = line.mark_text(align='left', dx=8, dy=-5, fontSize=11, color='#1B5E20', fontWeight='bold').encode(text=alt.Text('달러환산(USD):Q', format='.2f'))

        st.altair_chart(alt.layer(bars, line, line_txt).resolve_scale(y='independent').properties(height=350), use_container_width=True)
        st.dataframe(wage_df, use_container_width=True, hide_index=True)
