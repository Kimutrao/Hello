import streamlit as st
import pandas as pd
import numpy as np
import io
import random
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─────────────────────────────────────────
# 페이지 설정 & 전역 CSS
# ─────────────────────────────────────────
st.set_page_config(
    page_title="김철수의 투자기록실",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* ── 전체 폰트·배경 ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
}

/* ── 초록 계열 포인트 컬러 정의 ── */
:root {
    --green-50:  #EAF5E9;
    --green-100: #C8E6C9;
    --green-400: #66BB6A;
    --green-600: #388E3C;
    --green-800: #1B5E20;
}

/* ── 상단 헤더 타이틀 ── */
.app-header {
    padding: 1.2rem 0 0.8rem 0;
    border-bottom: 2px solid #388E3C;
    margin-bottom: 1.4rem;
}
.app-title {
    font-size: 1.7rem;
    font-weight: 700;
    color: #1B5E20;
    letter-spacing: -0.5px;
}
.app-subtitle {
    font-size: 0.85rem;
    color: #555;
    margin-top: 2px;
}

/* ── 탭 스타일 (초록 포인트) ── */
div[data-baseweb="tab-list"] {
    gap: 4px;
    background: #F1F8E9;
    border-radius: 10px;
    padding: 4px 6px;
}
button[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #388E3C !important;
    background: transparent !important;
    border: none !important;
    padding: 6px 14px !important;
    transition: background 0.18s;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: #388E3C !important;
    color: #fff !important;
}
button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: #C8E6C9 !important;
}

/* ── 버튼 초록 ── */
.stButton > button {
    background-color: #388E3C !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 1.1rem !important;
    transition: background 0.18s, transform 0.1s;
}
.stButton > button:hover {
    background-color: #2E7D32 !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: scale(0.98) !important;
}

/* ── 다운로드 버튼 ── */
.stDownloadButton > button {
    background-color: #2E7D32 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
}

/* ── multiselect·selectbox ── */
div[data-baseweb="select"] > div {
    border-color: #66BB6A !important;
    border-radius: 8px !important;
}
div[data-baseweb="tag"] {
    background-color: #C8E6C9 !important;
    color: #1B5E20 !important;
    border-radius: 6px !important;
}

/* ── 카드 스타일 ── */
.metric-card {
    background: #F1F8E9;
    border-left: 4px solid #388E3C;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.metric-card h4 {
    margin: 0 0 4px 0;
    font-size: 0.75rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.metric-card .value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1B5E20;
}

/* ── 섹션 구분선 ── */
.section-divider {
    border: none;
    border-top: 1.5px solid #C8E6C9;
    margin: 1.2rem 0;
}

/* ── 모바일 반응형 ── */
@media (max-width: 768px) {
    .app-title { font-size: 1.2rem; }
    .block-container { padding: 0.8rem 0.8rem !important; }
    button[data-baseweb="tab"] {
        font-size: 0.78rem !important;
        padding: 5px 8px !important;
    }
}

/* ── expander 초록 accent ── */
div[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #2E7D32;
}
div[data-testid="stExpander"] {
    border-left: 3px solid #66BB6A !important;
    border-radius: 6px !important;
}

/* ── 데이터프레임 헤더 ── */
div[data-testid="stDataFrame"] thead tr th {
    background-color: #E8F5E9 !important;
    color: #2E7D32 !important;
    font-weight: 600 !important;
}

/* ── 성공/알림 ── */
div[data-testid="stAlert"][data-type="success"] {
    border-left: 4px solid #388E3C !important;
    background: #F1F8E9 !important;
}

/* ── 메모 섹션 ── */
.memo-block {
    background: #FAFFFE;
    border: 1px solid #C8E6C9;
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 8px;
}

/* ── content 블록 여백 ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-title">📗 김철수의 투자기록실</div>
    <div class="app-subtitle">부동산 시세 분석 · 투자 철학 · 금융 기록</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Session State 초기화
# ─────────────────────────────────────────
if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {}
if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = {
        "투자 마인드 & 철학": [],
        "규제 & 정책 분석": [],
        "시장 전망 & 매크로": [],
        "개인적인 생각 & 기타": []
    }

# ─────────────────────────────────────────
# 탭 구성
# ─────────────────────────────────────────
tab_basic, tab_mind, tab_realestate, tab_finance, tab_price = st.tabs([
    "📖 투자기초",
    "🧠 기준, 마인드",
    "🏢 부동산",
    "💰 금융, 탈금융",
    "📊 시세비교",
])

# ═══════════════════════════════════════════
# 탭 1: 투자기초
# ═══════════════════════════════════════════
with tab_basic:
    st.subheader("📖 투자의 기초 개념")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("💡 복리의 법칙 (Rule of 72)", expanded=True):
            st.markdown("""
**72를 연수익률로 나누면 원금이 2배 되는 기간**

| 연수익률 | 2배 기간 |
|---------|---------|
| 6% | 12년 |
| 8% | 9년 |
| 10% | 7.2년 |
| 12% | 6년 |

> 수익률의 차이는 단기엔 작아 보이지만,  
> 20년 이상이면 엄청난 격차를 만들어냅니다.
""")
        with st.expander("📐 자산배분 기초"):
            st.markdown("""
**시장 국면에 따른 자산 배분 전략**

- **공격적 포트폴리오**: 주식 80% / 채권 10% / 현금 10%
- **균형 포트폴리오**: 주식 60% / 부동산 20% / 채권 20%
- **방어적 포트폴리오**: 현금 40% / 채권 30% / 주식 30%

> 나의 리스크 허용 범위와 투자 기간을 먼저 정의하세요.
""")

    with col2:
        with st.expander("🔑 투자의 3요소", expanded=True):
            st.markdown("""
**수익성 · 안전성 · 유동성**

세 가지를 동시에 만족하는 자산은 없습니다.  
반드시 우선순위를 정하고 투자하세요.

- **수익성** ↑ → 안전성 · 유동성 ↓
- **안전성** ↑ → 수익성 ↓
- **유동성** ↑ → 수익성 ↓

> **나의 우선순위**: 안전성 > 수익성 > 유동성  
> 이 기준에 맞지 않는 투자는 하지 않는다.
""")
        with st.expander("📅 투자 타임라인"):
            st.markdown("""
**단계별 접근**

| 기간 | 전략 |
|------|------|
| 1~3년 | 종잣돈 마련, 현금 흐름 최적화 |
| 3~7년 | 레버리지 활용, 갭투자 |
| 7~15년 | 실물자산 비중 확대 |
| 15년+ | 수익형 부동산, 배당주 |
""")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.info("📌 이 탭의 내용은 직접 수정하려면 코드에서 편집하거나, '기준, 마인드' 탭에 글을 추가하세요.")

# ═══════════════════════════════════════════
# 탭 2: 기준, 마인드
# ═══════════════════════════════════════════
with tab_mind:
    st.subheader("🧠 나의 투자 기준과 마인드")

    col_in, col_out = st.columns([1, 1])

    with col_in:
        st.markdown("#### ✏️ 글 저장하기")
        with st.form("mind_form", clear_on_submit=True):
            m_title = st.text_input("제목", placeholder="예: 손절 기준을 다시 생각하며")
            m_cat = st.selectbox("카테고리", ["투자 마인드 & 철학", "규제 & 정책 분석", "시장 전망 & 매크로", "개인적인 생각 & 기타"])
            m_content = st.text_area("내용", height=260, placeholder="생각을 자유롭게 적어보세요...")
            submitted = st.form_submit_button("💾 저장하기")
            if submitted and m_title and m_content:
                st.session_state['blog_db'][m_cat].append({"title": m_title, "content": m_content})
                st.success("✅ 저장되었습니다!")
            elif submitted:
                st.warning("제목과 내용을 모두 입력해주세요.")

    with col_out:
        st.markdown("#### 📚 저장된 기록")
        total = sum(len(v) for v in st.session_state['blog_db'].values())
        st.markdown(f"총 **{total}편** 저장됨")

        for cat, articles in st.session_state['blog_db'].items():
            if articles:
                with st.expander(f"📂 {cat}  ({len(articles)}편)"):
                    for i, art in enumerate(articles):
                        st.markdown(f"**{i+1}. {art['title']}**")
                        st.caption(art['content'][:120] + ("..." if len(art['content']) > 120 else ""))
                        st.markdown("---")

        if total > 0:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            def create_word_document(db):
                doc = Document()
                heading = doc.add_heading("김철수의 투자기록실", level=0)
                heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for category, articles in db.items():
                    if articles:
                        doc.add_page_break()
                        doc.add_heading(category, level=1)
                        for article in articles:
                            doc.add_heading(article['title'], level=2)
                            doc.add_paragraph(article['content'])
                            doc.add_paragraph("─" * 30)
                bio = io.BytesIO()
                doc.save(bio)
                return bio.getvalue()

            word_bytes = create_word_document(st.session_state['blog_db'])
            st.download_button(
                "📥 전자책 워드(.docx)로 다운로드",
                data=word_bytes,
                file_name="김철수_투자기록실.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

# ═══════════════════════════════════════════
# 탭 3: 부동산
# ═══════════════════════════════════════════
with tab_realestate:
    st.subheader("🏢 부동산 분석 & 임장 노트")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        with st.expander("📌 갭투자 기본 공식", expanded=True):
            st.markdown("""
**갭 = 매매가 - 전세가**

투자금 효율 = `전세가율 ÷ (1 - 전세가율)`

| 전세가율 | 레버리지 배율 |
|---------|------------|
| 60% | 1.5배 |
| 70% | 2.3배 |
| 80% | 4배 |
| 85% | 5.7배 |

> 전세가율이 높을수록 레버리지는 강력하지만,  
> 역전세 리스크도 함께 상승합니다.
""")

    with col_b:
        with st.expander("🔍 임장 체크리스트", expanded=True):
            st.markdown("""
**현장 방문 전 확인사항**

- [ ] 등기부등본 (근저당·가압류 확인)
- [ ] 전세가율 현황 (HUG·국토부)
- [ ] 인근 신규 입주 물량 (2년치)
- [ ] 학군·학원가 위치
- [ ] 대중교통 접근성 (지하철 도보 몇 분?)
- [ ] 주차장 세대당 비율
- [ ] 관리비 수준
- [ ] 재건축·리모델링 추진 여부
""")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📝 단지별 임장 메모")

    with st.form("realestate_memo_form"):
        apt_name = st.text_input("단지명", placeholder="예: 래미안메가트리아")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            apt_hh = st.text_input("세대수/주차", placeholder="예: 2678세대, 1.2대/세대")
            apt_feat = st.text_input("주요 특징", placeholder="예: 5호선 도보 3분, 2019년식")
        with col_r2:
            apt_gap = st.text_input("현재 갭/전세가율", placeholder="예: 갭 1.5억, 전세가율 72%")
            apt_pros = st.text_input("호재 요인", placeholder="예: GTX-A 개통 예정")
        apt_opinion = st.text_area("💡 투자 의견 및 메모", height=120)
        if st.form_submit_button("단지 메모 저장"):
            st.session_state['memo_db'][apt_name] = {
                '세대수': apt_hh, '특징': apt_feat,
                '갭': apt_gap, '호재': apt_pros,
                '투자의견': apt_opinion
            }
            st.success(f"✅ '{apt_name}' 메모 저장 완료!")

    if st.session_state['memo_db']:
        st.markdown("#### 📋 저장된 단지 메모")
        for name, info in st.session_state['memo_db'].items():
            with st.expander(f"🏠 {name}"):
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.markdown(f"**세대수/주차**: {info.get('세대수', '-')}")
                    st.markdown(f"**갭/전세가율**: {info.get('갭', '-')}")
                with col_i2:
                    st.markdown(f"**특징**: {info.get('특징', '-')}")
                    st.markdown(f"**호재**: {info.get('호재', '-')}")
                st.markdown(f"**투자의견**: {info.get('투자의견', '-')}")

# ═══════════════════════════════════════════
# 탭 4: 금융, 탈금융
# ═══════════════════════════════════════════
with tab_finance:
    st.subheader("💰 금융 & 탈금융 전략")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        with st.expander("📈 주요 금융상품 비교", expanded=True):
            st.markdown("""
| 상품 | 수익 방식 | 리스크 | 유동성 |
|------|---------|-------|-------|
| 예금/적금 | 이자 | 낮음 | 중간 |
| 채권(ETF) | 이자+시세 | 낮음 | 높음 |
| 배당주 | 배당+시세 | 중간 | 높음 |
| 리츠(REITs) | 배당+시세 | 중간 | 높음 |
| 금/원자재 | 시세차익 | 중간 | 높음 |
| 해외주식 | 시세차익 | 높음 | 높음 |
""")

    with col_f2:
        with st.expander("🏦 탈금융 자산 전략", expanded=True):
            st.markdown("""
**금융자산 의존도 낮추는 방법**

1. **실물자산 비중 확대**
   - 부동산 (직접 보유)
   - 금·은 (실물 보유)

2. **현금 흐름 만들기**
   - 월세 수익
   - 배당 포트폴리오
   - 사업소득 다각화

3. **디플레 & 인플레 헷지**
   - 인플레 → 부동산, 원자재, TIPS
   - 디플레 → 현금, 장기채권

> **목표**: 월 현금흐름 > 고정지출  
> 이 순간이 진정한 경제적 자유의 시작
""")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("🔢 간단 복리 계산기")

    col_calc1, col_calc2 = st.columns([1, 1])
    with col_calc1:
        principal = st.number_input("원금 (만원)", min_value=100, max_value=100000, value=3000, step=100)
        rate = st.slider("연 수익률 (%)", min_value=1, max_value=30, value=8)
        years = st.slider("투자 기간 (년)", min_value=1, max_value=40, value=10)

    with col_calc2:
        final_amount = principal * ((1 + rate / 100) ** years)
        gain = final_amount - principal

        st.markdown(f"""
<div class="metric-card">
    <h4>최종 자산</h4>
    <div class="value">{final_amount:,.0f} 만원</div>
</div>
<div class="metric-card">
    <h4>총 수익</h4>
    <div class="value">+{gain:,.0f} 만원</div>
</div>
<div class="metric-card">
    <h4>수익률</h4>
    <div class="value">{gain/principal*100:.1f}%</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 탭 5: 시세비교 (국토부 실거래 데이터)
# ═══════════════════════════════════════════
with tab_price:
    st.subheader("📊 국토부 실거래 기반 시세 비교")

    @st.cache_data
    def load_transaction_data():
        """
        각 단지의 월별 실거래 데이터를 건별로 생성
        실제 서비스에서는 국토부 API(공공데이터포털)로 대체
        """
        random.seed(42)
        np.random.seed(42)

        complexes = [
            ('서울 마포구',  '상암월드컵파크10단지',  11.0),
            ('경기 수원시',  '호반베르디움더센트럴',  8.0),
            ('경기 용인시',  '성복역롯데캐슬골드타운', 13.0),
            ('경기 안양시',  '더샵아이파크',          10.5),
            ('경기 의왕시',  '푸르지오엘센트로',      13.5),
            ('서울 은평구',  '녹번역e편한세상캐슬',   13.0),
            ('경기 안양시',  '래미안메가트리아',      10.0),
            ('인천 남동구',  '힐스테이트인천시청역',   5.5),
            ('인천 서구',    '호수공원역파라곤',       7.5),
            ('경기 광명시',  '철산자이더헤리티지',    13.0),
            ('경기 용인시',  '보원아파트',             7.0),
        ]

        months = [
            '2024-01','2024-02','2024-03','2024-04','2024-05','2024-06',
            '2024-07','2024-08','2024-09','2024-10','2024-11','2024-12',
            '2025-01','2025-02','2025-03','2025-04','2025-05','2025-06',
            '2025-07','2025-08','2025-09','2025-10','2025-11','2025-12',
            '2026-01','2026-02','2026-03','2026-04',
        ]

        rows = []
        for region, apt, base_price in complexes:
            trend = 0.0
            for m in months:
                trend += np.random.uniform(-0.08, 0.12)
                n_trades = random.randint(1, 5)
                for _ in range(n_trades):
                    floor = random.randint(2, 29)
                    price = round(base_price + trend + np.random.uniform(-0.3, 0.3), 2)
                    price = max(price, base_price * 0.7)
                    rows.append({
                        '지역': region,
                        '아파트명': apt,
                        '계약월': m,
                        '거래금액(억)': price,
                        '층수': floor,
                    })

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

    # ── 필터 UI (좌측 컬럼에 세로 배치) ──
    col_filter, col_main = st.columns([1, 3])

    with col_filter:
        st.markdown("#### 🔎 필터")

        st.markdown("**💰 금액대 선택**")
        selected_prices = st.multiselect(
            "금액대",
            ["6억 이하", "6~9억", "9~12억", "12~15억", "15억 이상"],
            default=["9~12억", "12~15억"],
            label_visibility="collapsed",
        )

        st.markdown("**📍 지역 선택**")
        all_regions = sorted(df_all['지역'].unique().tolist())
        selected_regions = st.multiselect(
            "지역",
            all_regions,
            default=all_regions,
            label_visibility="collapsed",
        )

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        filtered_df = df_all[
            df_all['금액대'].isin(selected_prices) &
            df_all['지역'].isin(selected_regions)
        ]
        available_apts = sorted(filtered_df['아파트명'].unique().tolist())

        st.markdown("**🏢 단지 선택**")
        selected_apts = st.multiselect(
            "단지",
            available_apts,
            default=[],
            label_visibility="collapsed",
            placeholder="단지를 선택하세요",
        )

    # ── 메인 차트 영역 ──
    with col_main:
        if not selected_apts:
            st.info("👈 왼쪽에서 비교할 단지를 선택하세요.")
        else:
            final_df = filtered_df[filtered_df['아파트명'].isin(selected_apts)].copy()

            # ── 전체 흐름 라인 차트 ──
            st.markdown("### 📈 단지별 월별 평균 시세 흐름")
            chart_data = (
                final_df
                .groupby(['계약월', '아파트명'])['거래금액(억)']
                .mean()
                .reset_index()
                .pivot(index='계약월', columns='아파트명', values='거래금액(억)')
            )
            st.line_chart(chart_data, height=320)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            # ── 단지 1개 선택 시: 건별 산점도 ──
            if len(selected_apts) == 1:
                apt_name = selected_apts[0]
                apt_df = final_df[final_df['아파트명'] == apt_name].copy()
                apt_df = apt_df.sort_values('계약월')

                st.markdown(f"### 🔵 {apt_name} — 건별 실거래 상세")
                st.caption(f"총 {len(apt_df)}건 | 거래금액마다 점(●) 1개 표시")

                # 월별 정렬 인덱스
                month_list = sorted(apt_df['계약월'].unique().tolist())
                month_idx = {m: i for i, m in enumerate(month_list)}
                apt_df['월_인덱스'] = apt_df['계약월'].map(month_idx)

                # 산점도용 데이터프레임 (x=월, y=거래금액)
                scatter_df = apt_df[['계약월', '거래금액(억)', '층수']].copy()
                scatter_df = scatter_df.rename(columns={'거래금액(억)': '거래금액_억'})

                # Streamlit scatter chart: x축=계약월, y=거래금액
                # 월별 전체 데이터를 wide format으로
                # 각 행이 1건의 거래 → 계약월별 scatter
                scatter_wide = scatter_df.set_index('계약월')[['거래금액_억']]

                import altair as alt
                scatter_chart = (
                    alt.Chart(scatter_df)
                    .mark_circle(size=80, color='#388E3C', opacity=0.75)
                    .encode(
                        x=alt.X('계약월:O',
                                sort=month_list,
                                title='계약월',
                                axis=alt.Axis(labelAngle=-45, labelFontSize=11)),
                        y=alt.Y('거래금액_억:Q',
                                title='거래금액 (억원)',
                                scale=alt.Scale(zero=False)),
                        tooltip=[
                            alt.Tooltip('계약월:O', title='계약월'),
                            alt.Tooltip('거래금액_억:Q', title='거래금액(억)', format='.2f'),
                            alt.Tooltip('층수:Q', title='층수'),
                        ]
                    )
                    .properties(height=360)
                    .configure_axis(grid=True, gridColor='#E8F5E9')
                    .configure_view(stroke=None)
                )
                st.altair_chart(scatter_chart, use_container_width=True)

                st.markdown("#### 📋 건별 실거래 내역")
                display_df = apt_df[['계약월', '거래금액(억)', '층수']].sort_values(
                    by=['계약월', '거래금액(억)'], ascending=[False, False]
                ).reset_index(drop=True)
                display_df.index += 1
                st.dataframe(display_df, use_container_width=True, height=320)

            else:
                # ── 여러 단지 선택 시: 요약 통계 테이블 ──
                st.markdown("### 📋 단지별 거래 요약")
                summary = (
                    final_df.groupby('아파트명')['거래금액(억)']
                    .agg(
                        거래건수='count',
                        평균가격='mean',
                        최저가='min',
                        최고가='max',
                    )
                    .round(2)
                    .reset_index()
                )
                st.dataframe(summary, use_container_width=True, hide_index=True)

                st.markdown("#### 📋 전체 거래 내역")
                detail_view = final_df[['아파트명', '계약월', '거래금액(억)', '층수']].sort_values(
                    by=['계약월', '거래금액(억)'], ascending=[False, False]
                ).reset_index(drop=True)
                detail_view.index += 1
                st.dataframe(detail_view, use_container_width=True, height=400)
