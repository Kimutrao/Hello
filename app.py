import streamlit as st
import pandas as pd
import numpy as np
import io, random, datetime, requests, math
import altair as alt
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
div[data-baseweb="tag"] { background-color: #B3E5FC !important; color: #01579B !important; }
.metric-card { background: #F1F8E9; border-left: 4px solid #388E3C; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }
.metric-card h4 { margin: 0 0 2px 0; font-size: 0.72rem; color: #666; }
.metric-card .value { font-size: 1.25rem; font-weight: 700; color: #1B5E20; }
.sec-div { border: none; border-top: 1.5px solid #B3E5FC; margin: 1rem 0; }
.timeline-box { background: #F9FBFD; border-left: 3px solid #0288D1; padding: 7px 11px; margin-bottom: 5px; border-radius: 0 5px 5px 0; }
.timeline-date { font-size: 0.74rem; color: #888; font-weight: 600; }
.timeline-content { font-size: 0.88rem; color: #222; margin-top: 2px; line-height: 1.5; }
.board-row { padding: 2px 0; border-bottom: 1px solid #E1F5FE; }
.result-box { background: #E8F5E9; border: 1.5px solid #66BB6A; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.result-box .r-label { font-size: 0.8rem; color: #555; margin-bottom: 2px; }
.result-box .r-value { font-size: 1.5rem; font-weight: 700; color: #1B5E20; }
.result-box .r-sub { font-size: 0.82rem; color: #388E3C; margin-top: 4px; }
.warn-box { background: #FFF8E1; border: 1.5px solid #FFB300; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.warn-box .r-label { font-size: 0.8rem; color: #555; margin-bottom: 2px; }
.warn-box .r-value { font-size: 1.5rem; font-weight: 700; color: #E65100; }
.warn-box .r-sub { font-size: 0.82rem; color: #E65100; margin-top: 4px; }
.danger-box { background: #FFEBEE; border: 1.5px solid #E53935; border-radius: 10px; padding: 16px 20px; margin-top: 10px; }
.danger-box .r-label { font-size: 0.8rem; color: #555; margin-bottom: 2px; }
.danger-box .r-value { font-size: 1.5rem; font-weight: 700; color: #B71C1C; }
.danger-box .r-sub { font-size: 0.82rem; color: #B71C1C; margin-top: 4px; }
.app-header { padding: 1rem 0 0.7rem 0; border-bottom: 2px solid #0288D1; margin-bottom: 1.2rem; }
.app-title { font-size: 1.6rem; font-weight: 700; color: #01579B; letter-spacing: -0.5px; }
.app-subtitle { font-size: 0.82rem; color: #777; margin-top: 2px; }
.lock-badge { display: inline-block; background: #FFF3E0; border: 1px solid #FFB300; border-radius: 6px; padding: 2px 10px; font-size: 0.76rem; color: #E65100; font-weight: 600; }
@media (max-width: 768px) { .app-title { font-size: 1.2rem; } .block-container { padding: 0.7rem 0.7rem !important; } button[data-baseweb="tab"] { font-size: 0.74rem !important; padding: 4px 7px !important; } }
.block-container { padding-top: 1.3rem !important; max-width: 1200px !important; }
div[data-testid="stExpander"] summary { font-weight: 600; color: #01579B; }
div[data-testid="stExpander"] { border-left: 3px solid #0288D1 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <div class="app-title">📗 김철수의 투자기록실</div>
  <div class="app-subtitle">부동산 시세 분석 · 투자 철학 · 금융 계산기</div>
</div>
""", unsafe_allow_html=True)

# ── 관리자 비밀번호 ──
try:
    ADMIN_PW = st.secrets["admin"]["password"]
except Exception:
    ADMIN_PW = "kimcs2024!"  # ← 본인 비밀번호로 변경

def is_admin():
    return st.session_state.get("admin_logged_in", False)

# ── Session State ──
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
        '상암월드컵파크10단지': {'지역': '서울 마포구', '기본': '860세대, 2010년식', '매매가': '11.5', '갭': '3억', '특징': '초품아, 마포 상암', 'kb시세': '11.2', 'history': [{'date': '2026-06-22', 'opinion': 'DMC 직주근접용 입장권으로 유효함.'}]},
        '호반베르디움더센트럴': {'지역': '경기 수원시', '기본': '1100세대, 2017년식', '매매가': '8.2', '갭': '2억', '특징': '신분당선 호매실 개통 예정', 'kb시세': '8.0', 'history': [{'date': '2026-06-22', 'opinion': '수원 권선구의 가성비 축 단지.'}]},
        '성복역롯데캐슬골드타운': {'지역': '경기 용인시', '기본': '2300세대, 2019년식', '매매가': '12.8', '갭': '4억', '특징': '성복역 지하 통로 연결', 'kb시세': '12.5', 'history': [{'date': '2026-06-22', 'opinion': '신분당선 라인 대장급 입지.'}]},
    }

if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = [
        {"category": "투자 마인드 & 철학", "title": "1. 부동산 시장 접근과 매수 의미", "date": "2026-06", "content": "지난달 생각의 연장선에서. 유의미한 상승이 지속될까? 잘 모르겠음.\n\n이제 아파트 시장은 돈을 벌기 위함보다는 미래에 사지 못하게 되는 것을 경계하며 구매가 가능할 때 구매를 해둬야하는 리스크 헷지 상품이 되어버림. 없다면 무조건 매수를 해야하는 존재."},
        {"category": "투자 마인드 & 철학", "title": "2. 임장의 의미 재정의", "date": "2026-06", "content": "임장도 이제 개념을 바꿔서 적용시켜야 하지 않을까. 많이 돌아다녀보는게 중요해짐. 가격을 비교하고 평가하는건 중요하지 않음. 동네의 특성, 분위기를 익혀야함."},
        {"category": "규제 & 정책 분석", "title": "3. 영끌금지와 생존 세팅값", "date": "2026-06", "content": "대한민국은 자유가 사라지는 중. 조금 더 큰 수익을 얻기위해 과한 영끌을 하기 보다 장기간 더 버틸 수 있는 세팅값에 의미를 두는게 좋지 않을까."},
        {"category": "시장 전망 & 매크로", "title": "4. 과열 조짐과 공급 절벽의 미래", "date": "2026-04", "content": "가격 Up, 거래량 Down, 매물 Down. 소량의 신고가가 전체 호가를 올리지만 거래량이 따라올 수 없는 상황."},
        {"category": "규제 & 정책 분석", "title": "5. 전월세 공급과 수요 억제책의 역설", "date": "2025-10", "content": "24~25년 갱신이 만료되는 26~27년 사이 수요자 다수 발생. 28년까지 준공 물량 별로 없음. 대출규제는 수요를 억누르고 있는 것뿐."},
        {"category": "규제 & 정책 분석", "title": "6. 대출 규제와 사면 안되는 자산", "date": "2025-07", "content": "정부의 대출규제 요약해보면 실거주 1주택만 하라는 압박. 빌라, 오피스텔은 사망선고."},
        {"category": "자유 메모", "title": "7. 실물 경기 체감과 소유의 기분", "date": "2025-02", "content": "체감경기가 상당히 안 좋음. 돈을 번 것 같은 '기분'과 '현실'을 철저히 구분해야 인생이 바뀜."},
    ]

# ── 사이드바 관리자 로그인 ──
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
    st.markdown("---")
    st.caption("Google 계정 연동: OAuth 설정 별도 필요")

tab_basic, tab_mind, tab_realestate, tab_finance = st.tabs([
    "📖 투자철학 요약", "🧠 기록 & 게시판", "🏢 관심단지 & 비교", "💰 계산기 & 매크로"
])

# ═══════════════════════════════════════════
# 탭 1: 투자철학
# ═══════════════════════════════════════════
with tab_basic:
    if not is_admin():
        st.markdown('<span class="lock-badge">🔒 읽기 전용 — 왼쪽 사이드바에서 관리자 로그인</span>', unsafe_allow_html=True)
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
# 탭 2: 기록 & 게시판
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
        if is_admin():
            if st.button("✍️ 새 글 작성", use_container_width=True):
                st.session_state['board_view'] = 'write'
                st.rerun()
        else:
            st.markdown('<span class="lock-badge">🔒 작성: 관리자만</span>', unsafe_allow_html=True)

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
            for line in post['content'].split('\n'):
                st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
            if is_admin():
                st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
                with st.form("edit_post_form"):
                    edit_content = st.text_area("내용 수정 (관리자)", value=post['content'], height=200)
                    if st.form_submit_button("수정 저장"):
                        for i, p in enumerate(st.session_state['blog_db']):
                            if p['title'] == post['title']:
                                st.session_state['blog_db'][i]['content'] = edit_content
                                st.session_state['current_post'] = st.session_state['blog_db'][i]
                                break
                        st.success("수정 완료!")
                        st.rerun()

        else:
            st.markdown(f"#### 📜 {st.session_state['selected_cat']}")
            for idx, post in enumerate(display_posts):
                col_t, col_c, col_d = st.columns([5, 3, 2])
                with col_t:
                    if st.button(post['title'], key=f"p_{idx}_{post['title'][:6]}", use_container_width=True):
                        st.session_state['current_post'] = post
                        st.session_state['board_view'] = 'read'
                        st.rerun()
                with col_c:
                    st.caption(f"🔹 {post['category']}")
                with col_d:
                    st.caption(f"📅 {post['date']}")

# ═══════════════════════════════════════════
# 탭 3: 관심단지 & 비교
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 관심단지 레이더 & 교차 비교")

    def get_mock_trends(apt_name):
        months = ['2024-07','2024-10','2025-01','2025-04','2025-07','2025-10','2026-01','2026-04']
        bp_map = {'상암월드컵파크10단지': 10.8, '호반베르디움더센트럴': 7.8, '성복역롯데캐슬골드타운': 12.2}
        bp = bp_map.get(apt_name, 9.0)
        random.seed(len(apt_name) * 7)
        trend, rows = 0.0, []
        for m in months:
            trend += random.uniform(-0.05, 0.15)
            rows.append({'계약월': m, '아파트명': apt_name, '거래금액(억)': round(bp + trend + random.uniform(-0.2, 0.2), 2)})
        return pd.DataFrame(rows)

    subtab_single, subtab_compare, subtab_add = st.tabs(["🔍 단지 상세", "📊 비교 분석", "➕ 단지 등록/수정"])

    with subtab_single:
        col_panel, col_view = st.columns([3, 7])
        with col_panel:
            st.markdown("##### 📍 지역 선택")
            all_regions = sorted(set(v['지역'] for v in st.session_state['memo_db'].values()))
            sel_region = st.selectbox("지역", ["전체"] + all_regions, key="single_region")
            region_apts = list(st.session_state['memo_db'].keys()) if sel_region == "전체" else [k for k, v in st.session_state['memo_db'].items() if v.get('지역') == sel_region]
            st.markdown("##### 🏢 단지 선택")
            chosen_apt = st.radio("단지", region_apts, key="single_apt") if region_apts else None
            if not region_apts:
                st.caption("등록된 단지가 없습니다.")
            if chosen_apt:
                if st.button("📊 비교 목록에 추가"):
                    if chosen_apt not in st.session_state['compare_apts']:
                        st.session_state['compare_apts'].append(chosen_apt)
                        st.success(f"'{chosen_apt}' 추가됨")

        with col_view:
            if chosen_apt:
                info = st.session_state['memo_db'][chosen_apt]
                st.markdown(f"##### 🎯 {chosen_apt}")
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("매매 호가", f"{info.get('매매가', '-')} 억")
                with c2: st.metric("KB 시세", f"{info.get('kb시세', '-')} 억")
                with c3: st.metric("갭", info.get('갭', '-'))
                df_trend = get_mock_trends(chosen_apt)
                chart = alt.Chart(df_trend).mark_line(point=True, strokeWidth=2.5).encode(
                    x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)),
                    y=alt.Y('거래금액(억):Q', scale=alt.Scale(zero=False), title='금액(억)'),
                    color=alt.value('#0288D1'), tooltip=['계약월', '거래금액(억)']
                ).properties(height=200)
                st.altair_chart(chart, use_container_width=True)
                st.markdown("**📄 투자 의견 히스토리**")
                for h in info.get('history', []):
                    st.markdown(f"""<div class="timeline-box"><div class="timeline-date">📅 {h['date']}</div><div class="timeline-content">{h['opinion']}</div></div>""", unsafe_allow_html=True)
                if is_admin():
                    with st.form(f"append_{chosen_apt}"):
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            up_price = st.text_input("매매 호가(억)", value=info.get('매매가', ''))
                            up_kb = st.text_input("KB시세(억)", value=info.get('kb시세', ''))
                        with col_f2:
                            up_gap = st.text_input("갭", value=info.get('갭', ''))
                            up_feat = st.text_input("특징", value=info.get('특징', ''))
                        new_op = st.text_area("새 투자 의견 추가")
                        if st.form_submit_button("💾 저장"):
                            st.session_state['memo_db'][chosen_apt].update({'매매가': up_price, 'kb시세': up_kb, '갭': up_gap, '특징': up_feat})
                            if new_op:
                                st.session_state['memo_db'][chosen_apt]['history'].append({'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': new_op})
                            st.success("저장 완료!")
                            st.rerun()
                else:
                    st.markdown('<span class="lock-badge">🔒 의견 추가는 관리자만</span>', unsafe_allow_html=True)

    with subtab_compare:
        st.markdown("##### 📊 비교 단지 목록")
        if not st.session_state['compare_apts']:
            st.info("👈 '단지 상세' 탭에서 단지를 추가하거나 아래에서 직접 선택하세요.")
        all_apts = list(st.session_state['memo_db'].keys())
        add_sel = st.multiselect("단지 직접 추가/선택", all_apts, default=st.session_state['compare_apts'], key="compare_ms")
        st.session_state['compare_apts'] = add_sel

        if st.session_state['compare_apts']:
            col_cl, col_cr = st.columns([8, 2])
            with col_cr:
                if st.button("🗑️ 초기화"):
                    st.session_state['compare_apts'] = []
                    st.rerun()

            compare_rows = []
            for apt in st.session_state['compare_apts']:
                info = st.session_state['memo_db'].get(apt, {})
                compare_rows.append({'단지명': apt, '지역': info.get('지역', '-'), '매매가(억)': info.get('매매가', '-'), 'KB시세(억)': info.get('kb시세', '-'), '갭': info.get('갭', '-'), '특징': info.get('특징', '-'), '세대수/연식': info.get('기본', '-')})
            st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

            df_all = pd.concat([get_mock_trends(a) for a in st.session_state['compare_apts']])
            compare_chart = alt.Chart(df_all).mark_line(point=True, strokeWidth=2).encode(
                x=alt.X('계약월:O', axis=alt.Axis(labelAngle=0, labelFontSize=10)),
                y=alt.Y('거래금액(억):Q', scale=alt.Scale(zero=False), title='금액(억)'),
                color=alt.Color('아파트명:N', legend=alt.Legend(title="단지")),
                tooltip=['계약월', '아파트명', '거래금액(억)']
            ).properties(height=300)
            st.altair_chart(compare_chart, use_container_width=True)

    with subtab_add:
        if not is_admin():
            st.warning("🔒 관리자만 단지를 등록/수정할 수 있습니다. 왼쪽 사이드바에서 로그인하세요.")
        else:
            st.markdown("#### ➕ 신규 단지 등록")
            with st.form("new_apt_form"):
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    new_reg = st.text_input("지역명", placeholder="경기 화성시")
                    new_name = st.text_input("단지명")
                    new_hh = st.text_input("세대수/연식", placeholder="2500세대, 2021년식")
                    new_kb = st.text_input("KB시세 (억)", placeholder="12.0")
                with col_n2:
                    new_price = st.text_input("매매 호가 (억)", placeholder="12.5")
                    new_gap = st.text_input("갭/전세가율", placeholder="3.5억 / 72%")
                    new_feat = st.text_input("주요 호재")
                    new_op = st.text_area("첫 투자 의견", height=80)
                if st.form_submit_button("✅ 등록"):
                    if new_name and new_reg:
                        st.session_state['memo_db'][new_name] = {'지역': new_reg, '기본': new_hh, '매매가': new_price, 'kb시세': new_kb, '갭': new_gap, '특징': new_feat, 'history': [{'date': datetime.datetime.now().strftime("%Y-%m-%d"), 'opinion': new_op}]}
                        st.success(f"'{new_name}' 등록 완료!")
                        st.rerun()
                    else:
                        st.warning("지역명과 단지명은 필수입니다.")

# ═══════════════════════════════════════════
# 탭 4: 계산기 & 매크로
# ═══════════════════════════════════════════
with tab_finance:
    st.subheader("💰 계산기 & 매크로 지표실")
    calc_tab1, calc_tab2, calc_tab3, calc_tab4 = st.tabs(["🏦 DSR 계산기", "📐 LTV & 취득세", "🔢 복리 계산기", "📊 최저시급 & 환율"])

    # ── DSR ──
    with calc_tab1:
        st.markdown("#### 🏦 DSR 합산 계산기 (대출 종류별 직접 입력)")
        st.caption("**DSR = 연간 총 원리금 상환액 ÷ 연 소득 × 100** | 1금융권 40% / 2금융권 50%")
        col_dsr_l, col_dsr_r = st.columns([5, 5])

        with col_dsr_l:
            dsr_income = st.number_input("연 소득 (만원)", min_value=100, value=6000, step=100, key="dsr_income")
            dsr_bank = st.radio("금융권", ["1금융권 (DSR 40%)", "2금융권 (DSR 50%)"], key="dsr_bank", horizontal=True)
            dsr_limit = 40 if "1금융" in dsr_bank else 50

            st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
            st.markdown("##### 기존 대출 입력")
            with st.form("add_loan_form"):
                l_col1, l_col2 = st.columns(2)
                with l_col1:
                    loan_type = st.selectbox("대출 종류", ["주택담보대출(원리금균등)", "주택담보대출(원금균등)", "주택담보대출(만기일시)", "신용대출", "마이너스통장", "카드론", "자동차할부/학자금"])
                    loan_amt = st.number_input("대출 원금 (만원)", min_value=0, value=10000, step=500, key="l_amt")
                with l_col2:
                    loan_rate = st.number_input("금리 (%)", min_value=0.1, value=4.0, step=0.1, key="l_rate")
                    loan_period = st.number_input("잔여기간 (년)", min_value=1, value=30, step=1, key="l_period")
                    stress_rate = st.number_input("스트레스 금리 가산 (%)", min_value=0.0, value=0.0, step=0.25, key="l_stress", help="수도권 주담대 +3.0%, 지방 +0.75%")
                if st.form_submit_button("➕ 대출 추가"):
                    st.session_state['dsr_loans'].append({'type': loan_type, 'amt': loan_amt, 'rate': loan_rate, 'period': loan_period, 'stress': stress_rate})
                    st.rerun()
            if st.button("🗑️ 전체 초기화", key="clear_loans"):
                st.session_state['dsr_loans'] = []
                st.rerun()
            if st.session_state['dsr_loans']:
                loan_rows = [{'#': i+1, '종류': l['type'][:10], '원금(만)': f"{l['amt']:,}", '금리(%)': f"{l['rate']}+{l['stress']}", '기간(년)': l['period']} for i, l in enumerate(st.session_state['dsr_loans'])]
                st.dataframe(pd.DataFrame(loan_rows), use_container_width=True, hide_index=True)

        with col_dsr_r:
            st.markdown("##### DSR 계산 결과")

            def calc_annual(loan):
                amt = loan['amt'] * 10000
                r = (loan['rate'] + loan['stress']) / 100
                pm = loan['period'] * 12
                mr = r / 12
                lt = loan['type']
                if "만기일시" in lt or "마이너스" in lt:
                    return amt * r / 10000
                elif "신용대출" in lt:
                    return amt * (0.20 + r) / 10000
                elif "카드론" in lt:
                    pm2 = 36
                    monthly = amt * mr / (1 - (1+mr)**(-pm2)) if mr > 0 else amt/pm2
                    return monthly * 12 / 10000
                elif "원금균등" in lt:
                    return ((amt/pm) + amt*r/12) * 12 / 10000
                else:
                    monthly = amt * mr / (1-(1+mr)**(-pm)) if mr > 0 else amt/pm
                    return monthly * 12 / 10000

            total_annual = sum(calc_annual(l) for l in st.session_state['dsr_loans'])
            cur_dsr = (total_annual / dsr_income * 100) if dsr_income > 0 else 0
            remaining = max(0, dsr_income * dsr_limit / 100 - total_annual)
            mr_ref = 0.04/12
            extra_loan_est = remaining / 12 / mr_ref * (1-(1+mr_ref)**-360) / 10000 if remaining > 0 else 0

            if cur_dsr <= dsr_limit * 0.8:
                box_cls = "result-box"
                emoji = "✅"
            elif cur_dsr <= dsr_limit:
                box_cls = "warn-box"
                emoji = "⚠️"
            else:
                box_cls = "danger-box"
                emoji = "❌"

            st.markdown(f"""<div class="{box_cls}">
              <div class="r-label">현재 DSR</div>
              <div class="r-value">{emoji} {cur_dsr:.1f}%</div>
              <div class="r-sub">한도: {dsr_limit}% | 연간 원리금 합계: {total_annual:,.0f}만원</div>
            </div>""", unsafe_allow_html=True)

            if cur_dsr <= dsr_limit:
                st.markdown(f"""<div class="result-box">
                  <div class="r-label">추가 여력 (연 원리금)</div>
                  <div class="r-value">{remaining:,.0f} 만원/년</div>
                  <div class="r-sub">≈ 금리 4%·30년 기준 추가 대출 가능 {extra_loan_est:.1f}억</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.error(f"DSR {dsr_limit}% 초과 — 신규 대출이 어렵습니다.")

            if st.session_state['dsr_loans']:
                detail = [{'종류': l['type'][:10], '연 원리금(만)': f"{calc_annual(l):,.0f}", 'DSR 기여': f"{calc_annual(l)/dsr_income*100:.1f}%"} for l in st.session_state['dsr_loans']]
                st.dataframe(pd.DataFrame(detail), use_container_width=True, hide_index=True)
            st.caption("※ 참고용 계산기. 실제 심사 결과와 다를 수 있습니다.")

    # ── LTV & 취득세 ──
    with calc_tab2:
        st.markdown("#### 📐 LTV 한도 & 취득세 계산기")
        apt_names = list(st.session_state['memo_db'].keys())
        col_ltv1, col_ltv2 = st.columns([1, 1])

        with col_ltv1:
            st.markdown("##### 🏠 주택 정보")
            auto_fill = st.selectbox("관심단지 KB시세 불러오기", ["직접 입력"] + apt_names, key="ltv_apt_sel")
            if auto_fill != "직접 입력":
                try:
                    default_price = int(float(st.session_state['memo_db'][auto_fill].get('kb시세', '10')) * 10000)
                except:
                    default_price = 100000
            else:
                default_price = 100000

            house_price = st.number_input("주택 KB시세/담보가 (만원)", min_value=1000, value=default_price, step=500, key="ltv_price")
            owner_cnt = st.radio("취득 후 주택 수", ["1주택 (무주택→1주택)", "2주택", "3주택 이상"], key="ltv_owner")
            is_regulated = st.radio("규제지역 여부", ["규제지역 (강남·서초·송파·용산)", "비규제지역"], key="ltv_regulated")
            is_first = st.checkbox("생애최초 구매 여부", key="ltv_first")

        with col_ltv2:
            st.markdown("##### 📊 LTV & 취득세 결과")
            regulated = "규제지역" in is_regulated
            if "1주택" in owner_cnt:
                ltv_rate = 50 if regulated else 70
            elif "2주택" in owner_cnt:
                ltv_rate = 30 if regulated else 60
            else:
                ltv_rate = 20 if regulated else 50
            if is_first and "1주택" in owner_cnt:
                ltv_rate = min(ltv_rate + 10, 80)
                st.caption("💚 생애최초 LTV +10% 우대 적용")

            max_loan = house_price * ltv_rate / 100
            st.markdown(f"""<div class="result-box">
              <div class="r-label">LTV {ltv_rate}% 기준 최대 대출 한도</div>
              <div class="r-value">{max_loan/10000:.2f} 억원</div>
              <div class="r-sub">({max_loan:,.0f}만원)</div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<hr class="sec-div">', unsafe_allow_html=True)
            price_eok = house_price / 10000
            if "1주택" in owner_cnt:
                acq_rate = 1.0 if price_eok <= 6 else (3.0 if price_eok > 9 else 1.0 + (price_eok-6)/3*2.0)
                if is_first: acq_rate = max(acq_rate - 0.5, 0.5)
            elif "2주택" in owner_cnt:
                acq_rate = 8.0 if regulated else (1.0 if price_eok <= 6 else (3.0 if price_eok > 9 else 1.0+(price_eok-6)/3*2.0))
            else:
                acq_rate = 12.0 if regulated else 8.0

            edu_r = 0.1 if acq_rate <= 1 else (0.2 if acq_rate <= 3 else 0.4)
            farm_r = 0.0 if acq_rate <= 1 else (0.2 if acq_rate <= 3 else 0.6)
            acq_tax = house_price * acq_rate / 100
            edu_tax = house_price * edu_r / 100
            farm_tax = house_price * farm_r / 100
            total_tax = acq_tax + edu_tax + farm_tax
            tax_box = "result-box" if acq_rate <= 3 else ("warn-box" if acq_rate <= 8 else "danger-box")
            st.markdown(f"""<div class="{tax_box}">
              <div class="r-label">취득 관련 세금 합계 ({acq_rate:.1f}+{edu_r:.1f}+{farm_r:.1f}%)</div>
              <div class="r-value">{total_tax/10000:.3f} 억원 ({total_tax:,.0f}만)</div>
              <div class="r-sub">취득세 {acq_tax:,.0f}만 | 지방교육세 {edu_tax:,.0f}만 | 농특세 {farm_tax:,.0f}만</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("**주택 취득세율표 (2025년 기준)**")
            st.dataframe(pd.DataFrame({
                '구분': ['1주택 ≤6억', '1주택 6~9억', '1주택 >9억', '2주택 비규제', '2주택 조정지역', '3주택 비규제', '3주택+ 조정지역'],
                '취득세율': ['1%', '1~3%', '3%', '1~3%', '8%', '8%', '12%'],
            }), use_container_width=True, hide_index=True)
            st.caption("※ 참고용. 정책 변경 시 달라질 수 있습니다.")

    # ── 복리 계산기 ──
    with calc_tab3:
        st.markdown("#### 🔢 적립식 복리 자산 계산기")
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            r1, r2 = st.columns(2)
            with r1:
                principal = st.number_input("초기 원금 (만원)", min_value=0, value=3000, step=100, key="cp")
                rtype = st.radio("수익률 기준", ["연 수익률(%)", "월 수익률(%)"], horizontal=True, key="crt")
                rval = st.number_input("수익률 (%)", value=8.0, step=1.0, key="crv")
            with r2:
                madd = st.number_input("매월 추가 적립 (만원)", min_value=0, value=100, step=10, key="cma")
                dtype = st.radio("기간 기준", ["년", "개월"], horizontal=True, key="cdt")
                dval = st.number_input("투자 기간", min_value=1, value=10, step=1, key="cdv")

            total_m = dval if dtype == "개월" else dval * 12
            mr = (rval/100) if "월" in rtype else (rval/100)/12
            bal, inv, hist = principal, principal, []
            for m in range(1, total_m+1):
                bal += madd; inv += madd; bal += bal * mr
                if m % 12 == 0 or m == total_m:
                    hist.append({"기간": f"{m//12}년" if m%12==0 else f"{m}개월", "총자산(만)": round(bal), "누적원금(만)": round(inv)})
            df_h = pd.DataFrame(hist)
            final_amt = df_h["총자산(만)"].iloc[-1]
            gain_amt = final_amt - inv
            st.markdown(f"""<div class="result-box">
              <div class="r-label">최종 자산</div>
              <div class="r-value">{final_amt/10000:.2f} 억원</div>
              <div class="r-sub">총 수익 {gain_amt/10000:.2f}억 | 수익률 {gain_amt/inv*100:.1f}%</div>
            </div>""", unsafe_allow_html=True)
        with col_c2:
            st.dataframe(df_h, use_container_width=True, hide_index=True, height=320)

    # ── 최저시급 & 환율 ──
    with calc_tab4:
        st.markdown("#### 📊 연도별 최저시급 & 당시 환율 달러 환산")
        st.caption("각 연도의 **당시 연평균 원/달러 환율**을 적용해 달러 가치를 계산합니다.")

        @st.cache_data(ttl=3600)
        def get_live_rate():
            try:
                return round(requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()['rates']['KRW'], 1)
            except:
                return 1440.0

        live_rate = get_live_rate()

        wage_df = pd.DataFrame({
            '연도':          ['2017','2018','2019','2020','2021','2022','2023','2024','2025','2026'],
            '최저시급(원)':  [6470,  7530,  8350,  8590,  8720,  9160,  9620,  9860,  10030, 10320],
            '연평균환율(원/$)':[1130.5,1100.3,1165.7,1180.1,1144.0,1291.9,1305.5,1363.0,1421.0, live_rate],
        })
        wage_df['달러환산(USD)'] = (wage_df['최저시급(원)'] / wage_df['연평균환율(원/$)']).round(2)

        st.caption(f"📡 2026년 실시간 환율: **{live_rate:,.0f} 원/달러**")

        # 이중 축 차트 + 막대/점 위에 레이블 표기
        base = alt.Chart(wage_df).encode(x=alt.X('연도:O', axis=alt.Axis(labelAngle=0, labelFontSize=11)))

        bars = base.mark_bar(color='#66BB6A', opacity=0.5, width=30).encode(
            y=alt.Y('최저시급(원):Q', title='최저시급 (원)', axis=alt.Axis(titleColor='#388E3C', format=',')),
        )
        bar_lbl = base.mark_text(align='center', baseline='bottom', dy=-3, fontSize=10, color='#1B5E20', fontWeight='bold').encode(
            y=alt.Y('최저시급(원):Q'), text=alt.Text('최저시급(원):Q', format=',d')
        )
        line = base.mark_line(color='#0288D1', strokeWidth=2.5, point=alt.OverlayMarkDef(color='#0288D1', size=60)).encode(
            y=alt.Y('달러환산(USD):Q', title='달러 환산 (USD)', axis=alt.Axis(titleColor='#0288D1', format='.2f')),
        )
        line_lbl = base.mark_text(align='center', baseline='top', dy=8, fontSize=10, color='#01579B', fontWeight='bold').encode(
            y=alt.Y('달러환산(USD):Q'), text=alt.Text('달러환산(USD):Q', format='.2f')
        )

        combined = alt.layer(bars, bar_lbl, line, line_lbl).resolve_scale(y='independent').properties(height=340)
        st.altair_chart(combined, use_container_width=True)

        display_df = wage_df.copy()
        display_df['인상액(원)'] = display_df['최저시급(원)'].diff().fillna(0).astype(int)
        display_df['인상률(%)'] = (display_df['최저시급(원)'].pct_change() * 100).round(1).fillna(0)
        st.dataframe(display_df[['연도','최저시급(원)','인상액(원)','인상률(%)','연평균환율(원/$)','달러환산(USD)']],
                     use_container_width=True, hide_index=True)
        st.caption("📌 27년 최저시급 확정 후 코드의 wage_df에 행을 추가하면 자동 반영됩니다.")
