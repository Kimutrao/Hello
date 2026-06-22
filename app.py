import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import altair as alt
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─────────────────────────────────────────
# 1. 페이지 설정 & 전역 CSS
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
.stButton > button:active { transform: scale(0.98) !important; }

/* 카드 스타일 */
.metric-card { background: #F1F8E9; border-left: 4px solid #388E3C; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
.metric-card h4 { margin: 0 0 4px 0; font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 0.4px; }
.metric-card .value { font-size: 1.4rem; font-weight: 700; color: #1B5E20; }
.section-divider { border: none; border-top: 1.5px solid #C8E6C9; margin: 1.2rem 0; }

/* 게시판 스타일 */
.board-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #EAF5E9; align-items: center; }
.board-row:hover { background-color: #F1F8E9; }
.board-title { font-size: 1rem; font-weight: 500; color: #1B5E20; cursor: pointer; }
.board-date { font-size: 0.8rem; color: #888; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 2. 헤더 & 세션 초기화
# ─────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-title">📗 김철수의 투자기록실</div>
    <div class="app-subtitle">부동산 시세 분석 · 투자 철학 · 금융 기록</div>
</div>
""", unsafe_allow_html=True)

if 'memo_db' not in st.session_state: st.session_state['memo_db'] = {}
if 'blog_db' not in st.session_state: 
    st.session_state['blog_db'] = [] # 리스트 형태로 변경 (게시판 용도)
if 'board_view' not in st.session_state: st.session_state['board_view'] = 'list' # list, read, write
if 'current_post' not in st.session_state: st.session_state['current_post'] = None
if 'selected_cat' not in st.session_state: st.session_state['selected_cat'] = "전체글보기"

# ─────────────────────────────────────────
# 3. 탭 구성
# ─────────────────────────────────────────
tab_basic, tab_mind, tab_realestate, tab_finance, tab_price = st.tabs([
    "📖 투자철학 요약", "🧠 기록 & 게시판", "🏢 부동산 & 대출", "💰 복리 계산기 & 매크로", "📊 시세비교"
])

# ═══════════════════════════════════════════
# 탭 1: 투자철학 요약 
# ═══════════════════════════════════════════
with tab_basic:
    st.subheader("📖 흔들리지 않는 4가지 핵심 기준")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("💡 1. 부동산의 본질은 '리스크 헷지'", expanded=True):
            st.markdown("""
            **돈을 벌기 위함이 아니라, 사지 못하게 되는 것을 막는 수단**
            * 알파 수익(대박)을 원한다면 달러, 미국 주식, 코인 등 대체재가 많습니다.
            * 현재 아파트는 **무조건 매수해 두어야 하는 '주거 입장권'**이자 생존 방어막입니다.
            * 소형 빌라, 오피스텔 등 엉뚱한 곳에서 로우리스크-하이리턴을 꿈꾸며 소액 투자하지 마세요.
            """)
        with st.expander("🔑 2. 영끌 금지와 개인의 상황"):
            st.markdown("""
            **보편적인 정답은 없다. 오직 '나의 생애주기'만 있을 뿐.**
            * 자산이 없는 30대라면 최대한 대출을 당겨 자산을 선점하는 것이 맞습니다.
            * 하지만 소득 감소가 예상되는 40대 이상이라면 공격적인 대출은 독입니다. (1금융권 수준만 실행)
            * 유튜버들이 외치는 '강남 상급지'가 모두에게 정답은 아닙니다. 내 생활권과 접근성을 우선하세요.
            """)

    with col2:
        with st.expander("🔇 3. 시장의 소음 구별법", expanded=True):
            st.markdown("""
            **금액(얼마 간다)을 논하는 자는 멀리하고, 시대 흐름을 논하는 자를 곁에 두라.**
            * 하락장에선 비관론을, 상승장에선 무한 낙관론을 외치는 유튜버의 목적은 오직 '조회수'입니다.
            * 특정 시점이나 단지의 매수/매도를 지시하는 채널은 차단하는 것이 삶에 이롭습니다.
            * 스스로 생각하는 힘을 기르지 못하면 영원히 남의 뒤만 쫓다 피해자가 됩니다.
            """)
        with st.expander("💸 4. 세금을 계산하지 않은 투자는 허상"):
            st.markdown("""
            **보유세와 거래세의 밸런스 게임**
            * 집값이 오르면 세금만 늘어날 뿐, 1주택자의 상급지 갈아타기는 오히려 더 어려워집니다.
            * 2주택 이상부터는 오로지 '세금의 영역'입니다.
            * 취득세, 양도세, 보유세 시뮬레이션 없이 무작정 주택 수만 늘리는 것은 빈 수레와 같습니다.
            """)

# ═══════════════════════════════════════════
# 탭 2: 기록 & 게시판 
# ═══════════════════════════════════════════
with tab_mind:
    st.subheader("🧠 나의 생각 기록장")
    
    cat_list = ["전체글보기", "투자 마인드 & 철학", "규제 & 정책 분석", "시장 전망 & 매크로", "자유 메모"]
    
    col_menu, col_board = st.columns([2, 8])
    
    # [좌측 메뉴바]
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

    # [우측 메인보드]
    with col_board:
        if st.session_state['selected_cat'] == "전체글보기":
            display_posts = reversed(st.session_state['blog_db']) 
        else:
            display_posts = reversed([p for p in st.session_state['blog_db'] if p['category'] == st.session_state['selected_cat']])
        display_posts = list(display_posts)

        if st.session_state['board_view'] == 'write':
            st.markdown("#### ✏️ 새 글 작성")
            with st.form("write_form"):
                new_cat = st.selectbox("카테고리", cat_list[1:])
                new_title = st.text_input("제목")
                new_content = st.text_area("내용", height=300)
                
                col_btn1, col_btn2 = st.columns([1, 8])
                with col_btn1:
                    if st.form_submit_button("등록"):
                        if new_title and new_content:
                            import datetime
                            today = datetime.datetime.now().strftime("%y.%m.%d")
                            st.session_state['blog_db'].append({"category": new_cat, "title": new_title, "content": new_content, "date": today})
                            st.session_state['board_view'] = 'list'
                            st.rerun()
                        else:
                            st.error("제목과 내용을 입력하세요.")
                with col_btn2:
                    if st.form_submit_button("취소"):
                        st.session_state['board_view'] = 'list'
                        st.rerun()

        elif st.session_state['board_view'] == 'read':
            post = st.session_state['current_post']
            if st.button("목록으로 돌아가기"):
                st.session_state['board_view'] = 'list'
                st.rerun()
            
            st.markdown(f"### {post['title']}")
            st.caption(f"분류: {post['category']} | 작성일: {post['date']}")
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.write(post['content'])

        else:
            st.markdown(f"#### 📜 {st.session_state['selected_cat']}")
            if not display_posts:
                st.info("등록된 글이 없습니다.")
            else:
                for idx, post in enumerate(display_posts):
                    with st.container():
                        c1, c2, c3 = st.columns([6, 2, 2])
                        with c1:
                            if st.button(post['title'], key=f"post_{post['title']}_{idx}"):
                                st.session_state['current_post'] = post
                                st.session_state['board_view'] = 'read'
                                st.rerun()
                        with c2:
                            st.caption(post['category'])
                        with c3:
                            st.caption(post['date'])
                        st.markdown("<hr style='margin:0px; padding:0px; border-top: 1px solid #EAF5E9;'>", unsafe_allow_html=True)
            
            if st.session_state['blog_db']:
                st.write("")
                def create_word_document(db):
                    doc = Document()
                    doc.add_heading("김철수의 투자기록실", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for post in db:
                        doc.add_heading(f"[{post['category']}] {post['title']}", level=2)
                        doc.add_paragraph(post['content'])
                        doc.add_paragraph("─" * 40)
                    bio = io.BytesIO()
                    doc.save(bio)
                    return bio.getvalue()
                
                word_bytes = create_word_document(st.session_state['blog_db'])
                st.download_button("📥 내 기록 전체를 전자책(Word)으로 저장", data=word_bytes, file_name="나의_투자기록.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ═══════════════════════════════════════════
# 탭 3: 부동산 & 대출 계산기
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 부동산 임장 노트 및 대출 계산기")
    
    col_memo, col_loan = st.columns([1, 1])
    
    with col_memo:
        st.markdown("#### 📝 단지별 임장 메모")
        with st.form("realestate_memo_form"):
            apt_name = st.text_input("단지명", placeholder="예: 래미안메가트리아")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                apt_hh = st.text_input("세대수/연식", placeholder="예: 2678세대, 19년식")
                apt_gap = st.text_input("현재 갭/전세가율", placeholder="예: 갭 2.5억, 65%")
            with c_m2:
                apt_feat = st.text_input("주요 특징/호재", placeholder="예: 초품아, 신분당선 연장")
                apt_opinion = st.text_input("💡 투자의견", placeholder="예: 12억 언더면 진입 고려")
            if st.form_submit_button("단지 메모 저장"):
                st.session_state['memo_db'][apt_name] = {'기본': apt_hh, '갭': apt_gap, '특징': apt_feat, '의견': apt_opinion}
                st.success("저장 완료!")
                
        if st.session_state['memo_db']:
            for name, info in st.session_state['memo_db'].items():
                with st.expander(f"🏠 {name}"):
                    st.write(f"- **기본정보**: {info.get('기본', '-')} / **특징**: {info.get('특징', '-')}")
                    st.write(f"- **갭투자**: {info.get('갭', '-')} / **투자의견**: {info.get('의견', '-')}")

    with col_loan:
        st.markdown("#### 🏦 DSR & LTV 계산기")
        st.caption("※ 정확한 DSR은 기타 대출 조건에 따라 달라질 수 있습니다.")
        
        with st.container(border=True):
            st.markdown("**1. DSR (총부채원리금상환비율) 계산**")
            dsr_income = st.number_input("연소득 (만원)", min_value=100, value=7000, step=500)
            dsr_debt = st.number_input("1년간 갚아야 할 총 원금+이자 (만원)", min_value=0, value=2500, step=100)
            
            if dsr_income > 0:
                dsr_result = (dsr_debt / dsr_income) * 100
                color = "red" if dsr_result > 40 else "green"
                st.markdown(f"👉 **나의 DSR:** <span style='color:{color}; font-weight:bold; font-size:1.2rem;'>{dsr_result:.1f}%</span> (보통 40% 규제)", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("**2. LTV (주택담보대출비율) 계산**")
            st.caption("KB시세나 매매가 중 낮은 금액을 입력하세요.")
            ltv_price = st.number_input("주택 기준가격 (만원)", min_value=1000, value=100000, step=1000)
            ltv_loan = st.number_input("받으려는 주담대 금액 (만원)", min_value=0, value=40000, step=1000)
            
            if ltv_price > 0:
                ltv_result = (ltv_loan / ltv_price) * 100
                st.markdown(f"👉 **나의 LTV:** <span style='color:#1B5E20; font-weight:bold; font-size:1.2rem;'>{ltv_result:.1f}%</span>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 탭 4: 복리 계산기 & 환율/매크로 (통합 완료)
# ═══════════════════════════════════════════
with tab_finance:
    st.subheader("💰 적립식 복리 계산기 & 성장 그래프")

    col_calc1, col_calc2 = st.columns([1, 1])
    
    # [좌측] 입력 폼
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

    # [우측] 결과 및 로직
    with col_calc2:
        total_months = dur_val if dur_type == "개월(Months)" else dur_val * 12
        monthly_rate = (rate_val / 100) if rate_type == "월 수익률(%)" else (rate_val / 100) / 12

        balance = principal
        invested_total = principal
        history = []

        for m in range(1, total_months + 1):
            balance += monthly_addition 
            invested_total += monthly_addition
            interest = balance * monthly_rate 
            balance += interest
            history.append({"기간(월)": m, "총자산": balance, "누적원금": invested_total})

        df_calc = pd.DataFrame(history)
        final_amount = df_calc["총자산"].iloc[-1]
        gain = final_amount - invested_total
        return_rate = (gain / invested_total) * 100 if invested_total > 0 else 0

        st.markdown(f"""
        <div class="metric-card">
            <h4>최종 자산 (예상)</h4>
            <div class="value">{final_amount/10000:,.2f} 억 원 <span style="font-size:0.9rem; color:#666;">({final_amount:,.0f} 만원)</span></div>
        </div>
        <div class="metric-card">
            <h4>순수익금 (이자) / 누적 원금</h4>
            <div class="value" style="color:#D32F2F;">+{gain:,.0f} 만원 <span style="font-size:0.9rem; color:#666;">(원금: {invested_total:,.0f} 만원)</span></div>
        </div>
        <div class="metric-card">
            <h4>최종 수익률</h4>
            <div class="value">{return_rate:,.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # 복리 그래프
    st.markdown("#### 📈 자산 성장 그래프 (원금 vs 총자산)")
    base_chart = alt.Chart(df_calc).encode(x=alt.X('기간(월):Q', title='투자기간 (개월수)'))
    area_principal = base_chart.mark_area(opacity=0.4, color='#9E9E9E').encode(
        y=alt.Y('누적원금:Q', title='금액 (만원)'),
        tooltip=['기간(월)', '누적원금', '총자산']
    )
    line_total = base_chart.mark_line(color='#388E3C', strokeWidth=3).encode(y='총자산:Q')
    st.altair_chart((area_principal + line_total).interactive(), use_container_width=True)

    # ─────────────────────────────────────────
    # ★ 추가된 최저시급 / 환율 매크로 지표 부분
    # ─────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📉 [매크로 지표] 원화 가치 하락과 실질 최저시급(USD)의 역설")
    st.write("원화 기준 최저시급은 꾸준히 올랐지만, 고환율로 인해 달러 기준 실질 가치는 오히려 하락했습니다.")

    data = {
        '연도': ['2020', '2021', '2022', '2023', '2024', '2025', '2026'],
        '최저시급(원)': [8590, 8720, 9160, 9620, 9860, 10030, 10320],
        '적용환율': [1086.3, 1188.8, 1264.5, 1288.0, 1472.5, 1439.0, 1521.4],
        '달러환산(USD)': [7.91, 7.34, 7.24, 7.47, 6.70, 6.97, 6.78]
    }
    df_wage = pd.DataFrame(data)

    base = alt.Chart(df_wage).encode(x=alt.X('연도:O', title='연도'))
    bar = base.mark_bar(opacity=0.4, color='#C8E6C9', width=30).encode(
        y=alt.Y('최저시급(원):Q', title='최저시급 (KRW)'),
        tooltip=['연도', '최저시급(원)', '적용환율']
    )
    line = base.mark_line(color='#1B5E20', strokeWidth=3, point=alt.OverlayMarkDef(color='#1B5E20', size=100)).encode(
        y=alt.Y('달러환산(USD):Q', title='달러 환산액 (USD)', scale=alt.Scale(domain=[6.0, 8.5])),
        tooltip=['연도', '달러환산(USD)']
    )
    chart = alt.layer(bar, line).resolve_scale(y='independent').properties(height=350)
    
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(df_wage, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════
# 탭 5: 시세비교 (클로드 작성 코드 그대로 유지)
# ═══════════════════════════════════════════
with tab_price:
    st.info("이곳은 국토부 실거래 데이터 필터링 및 산점도(Scatter) 그래프 영역입니다.")
    
    @st.cache_data
    def load_transaction_data():
        random.seed(42)
        np.random.seed(42)
        complexes = [
            ('서울 마포구',  '상암월드컵파크10단지',  11.0), ('경기 수원시',  '호반베르디움더센트럴',  8.0),
            ('경기 용인시',  '성복역롯데캐슬골드타운', 13.0), ('경기 안양시',  '더샵아이파크',          10.5),
            ('경기 의왕시',  '푸르지오엘센트로',      13.5), ('서울 은평구',  '녹번역e편한세상캐슬',   13.0),
            ('경기 안양시',  '래미안메가트리아',      10.0), ('인천 남동구',  '힐스테이트인천시청역',   5.5),
            ('인천 서구',    '호수공원역파라곤',       7.5), ('경기 광명시',  '철산자이더헤리티지',    13.0),
            ('경기 용인시',  '보원아파트',             7.0),
        ]
        months = [f"2024-{str(m).zfill(2)}" for m in range(1,13)] + [f"2025-{str(m).zfill(2)}" for m in range(1,13)] + [f"2026-{str(m).zfill(2)}" for m in range(1,5)]
        rows = []
        for region, apt, base_price in complexes:
            trend = 0.0
            for m in months:
                trend += np.random.uniform(-0.08, 0.12)
                for _ in range(random.randint(1, 5)):
                    price = round(max(base_price + trend + np.random.uniform(-0.3, 0.3), base_price * 0.7), 2)
                    rows.append({'지역': region, '아파트명': apt, '계약월': m, '거래금액(억)': price, '층수': random.randint(2, 29)})
        df = pd.DataFrame(rows)
        def assign_price_group(p):
            if p <= 6:   return "6억 이하"
            elif p <= 9:  return "6~9억"
            elif p <= 12: return "9~12억"
            elif p <= 15: return "12~15억"
            else:         return "15억 이상"
        df['금액대'] = df['거래금액(억)'].apply(assign_price_group)
        return df

    df_all = load_transaction_data()

    col_filter, col_main = st.columns([1, 3])
    with col_filter:
        st.markdown("#### 🔎 필터")
        selected_prices = st.multiselect("💰 금액대 선택", ["6억 이하", "6~9억", "9~12억", "12~15억", "15억 이상"], default=["9~12억", "12~15억"])
        all_regions = sorted(df_all['지역'].unique().tolist())
        selected_regions = st.multiselect("📍 지역 선택", all_regions, default=all_regions)
        filtered_df = df_all[df_all['금액대'].isin(selected_prices) & df_all['지역'].isin(selected_regions)]
        available_apts = sorted(filtered_df['아파트명'].unique().tolist())
        selected_apts = st.multiselect("🏢 단지 선택", available_apts, default=[], placeholder="단지를 선택하세요")

    with col_main:
        if not selected_apts:
            st.info("👈 왼쪽에서 비교할 단지를 선택하세요.")
        else:
            final_df = filtered_df[filtered_df['아파트명'].isin(selected_apts)].copy()
            st.markdown("### 📈 단지별 월별 평균 시세 흐름")
            chart_data = final_df.groupby(['계약월', '아파트명'])['거래금액(억)'].mean().reset_index().pivot(index='계약월', columns='아파트명', values='거래금액(억)')
            st.line_chart(chart_data, height=320)

            if len(selected_apts) == 1:
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                apt_name = selected_apts[0]
                apt_df = final_df[final_df['아파트명'] == apt_name].sort_values('계약월')
                st.markdown(f"### 🔵 {apt_name} — 건별 실거래 상세")
                
                month_list = sorted(apt_df['계약월'].unique().tolist())
                scatter_chart = (
                    alt.Chart(apt_df.rename(columns={'거래금액(억)': '거래금액_억'}))
                    .mark_circle(size=80, color='#388E3C', opacity=0.75)
                    .encode(
                        x=alt.X('계약월:O', sort=month_list, axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('거래금액_억:Q', scale=alt.Scale(zero=False)),
                        tooltip=['계약월', '거래금액_억', '층수']
                    ).properties(height=360)
                )
                st.altair_chart(scatter_chart, use_container_width=True)
                st.dataframe(apt_df[['계약월', '거래금액(억)', '층수']].sort_values(by=['계약월', '거래금액(억)'], ascending=[False, False]), use_container_width=True)
            else:
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("### 📋 단지별 거래 요약")
                summary = final_df.groupby('아파트명')['거래금액(억)'].agg(거래건수='count', 평균가격='mean', 최저가='min', 최고가='max').round(2).reset_index()
                st.dataframe(summary, use_container_width=True, hide_index=True)
