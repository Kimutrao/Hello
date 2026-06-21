import streamlit as st
import pandas as pd
import numpy as np
import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 1. 페이지 기본 설정
st.set_page_config(page_title="통합 투자 대시보드", layout="wide")
st.title("🚀 나만의 통합 투자 & 전자책 스튜디오")

# 임시 DB (Session State)
if 'memo_db' not in st.session_state:
    st.session_state['memo_db'] = {}
if 'blog_db' not in st.session_state:
    st.session_state['blog_db'] = {
        "1. 투자 마인드 & 철학": [],
        "2. 규제 & 정책 분석": [],
        "3. 시장 전망 & 매크로": [],
        "4. 개인적인 생각 & 기타": []
    }

tab_market, tab_writer = st.tabs(["📊 지역별 시세 흐름 비교", "📝 블로그 글 전자책 만들기"])

# =================================================================
# 탭 1: 지역/금액대별 시세 흐름 비교
# =================================================================
with tab_market:
    st.subheader("🔍 관심 단지 교차 비교 분석")

    @st.cache_data
    def load_custom_data():
        dates = ['2025-01', '2025-04', '2025-07', '2025-10', '2026-01', '2026-04']
        complexes = [
            ('서울 마포구', '상암월드컵파크10단지', 11.0), ('경기 수원시', '호반베르디움더센트럴', 8.0),
            ('경기 용인시', '성복역롯데캐슬골드타운', 13.0), ('경기 안양시', '더샵아이파크', 10.5),
            ('경기 의왕시', '푸르지오엘센트로', 13.5), ('서울 은평구', '녹번역e편한세상캐슬', 13.0),
            ('경기 안양시', '래미안메가트리아', 10.0), ('인천 남동구', '힐스테이트인천시청역', 5.5),
            ('인천 서구', '호수공원역파라곤', 7.5), ('경기 광명시', '철산자이더헤리티지', 13.0),
            ('경기 용인시', '보원아파트', 7.0)
        ]
        
        data = []
        for region, apt, base_price in complexes:
            for d in dates:
                data.append({
                    '지역': region, '아파트명': apt, '계약월': d,
                    '거래금액(억)': round(base_price + np.random.uniform(-0.5, 0.5), 2),
                    '층수': np.random.randint(5, 30)
                })
        df = pd.DataFrame(data)
        
        def assign_price_group(price):
            if price <= 6: return "6억 이하"
            elif price <= 9: return "6~9억"
            elif price <= 12: return "9~12억"
            elif price <= 15: return "12~15억"
            else: return "15억 이상"
        df['금액대'] = df['거래금액(억)'].apply(assign_price_group)
        return df

    df = load_custom_data()

    col1, col2 = st.columns(2)
    with col1:
        selected_prices = st.multiselect("💰 금액대 선택", ["6억 이하", "6~9억", "9~12억", "12~15억", "15억 이상"], default=["9~12억", "12~15억"])
    with col2:
        selected_regions = st.multiselect("📍 지역 선택", list(df['지역'].unique()), default=list(df['지역'].unique()))

    filtered_df = df[(df['금액대'].isin(selected_prices)) & (df['지역'].isin(selected_regions))]
    selected_apts = st.multiselect("🏢 3. 시세를 비교할 단지 선택", list(filtered_df['아파트명'].unique()))

    if selected_apts:
        final_df = filtered_df[filtered_df['아파트명'].isin(selected_apts)]
        st.divider()
        col_graph, col_details = st.columns([7, 3])
        
        with col_graph:
            st.markdown("### 📈 단지별 시세 흐름 비교")
            chart_data = final_df.pivot_table(index='계약월', columns='아파트명', values='거래금액(억)', aggfunc='mean')
            st.line_chart(chart_data)
            
        with col_details:
            st.markdown("### 📋 실거래 및 임장 노트")
            detail_target = st.selectbox("조회/수정할 단지를 선택하세요", selected_apts)
            
            detail_df = final_df[final_df['아파트명'] == detail_target][['계약월', '거래금액(억)', '층수']]
            st.dataframe(detail_df.sort_values(by='계약월', ascending=False), use_container_width=True, hide_index=True)
            
            st.markdown("#### 📝 단지 상세 정보")
            target_info = st.session_state['memo_db'].get(detail_target, {'세대수': '', '특징': '', '투자의견': ''})
            
            with st.form(f"form_{detail_target}"):
                new_hh = st.text_input("세대수/주차대수 등", value=target_info['세대수'])
                new_feat = st.text_input("주요 특징 (호재, 연식 등)", value=target_info['특징'])
                new_opinion = st.text_area("💡 나의 투자 의견", value=target_info['투자의견'])
                
                if st.form_submit_button("정보 저장하기"):
                    st.session_state['memo_db'][detail_target] = {'세대수': new_hh, '특징': new_feat, '투자의견': new_opinion}
                    st.success("임시 저장 완료!")

# =================================================================
# 탭 2: 블로그 글 전자책 만들기
# =================================================================
with tab_writer:
    col_input, col_preview = st.columns([1, 1])
    
    with col_input:
        st.subheader("📥 블로그 글 붙여넣기")
        with st.form("blog_form", clear_on_submit=True):
            b_title = st.text_input("글 제목", placeholder="예: 26년 4월의 생각")
            b_category = st.selectbox("카테고리", list(st.session_state['blog_db'].keys()))
            b_content = st.text_area("블로그 본문 내용", height=300)
            
            if st.form_submit_button("📁 저장하기") and b_title and b_content:
                st.session_state['blog_db'][b_category].append({"title": b_title, "content": b_content})
                st.success("보관되었습니다!")
                
    with col_preview:
        st.subheader("📖 현재 모인 내 전자책")
        
        def create_word_document(db):
            doc = Document()
            doc.add_heading("나만의 부동산 투자 철학 기록", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            for category, articles in db.items():
                if articles:
                    doc.add_page_break()
                    doc.add_heading(category, level=1)
                    for article in articles:
                        doc.add_heading(article['title'], level=2)
                        doc.add_paragraph(article['content'])
                        doc.add_paragraph("-" * 40)
            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()

        total_articles = sum(len(articles) for articles in st.session_state['blog_db'].values())
        
        if total_articles == 0:
            st.write("아직 저장된 글이 없습니다.")
        else:
            for category, articles in st.session_state['blog_db'].items():
                with st.expander(f"📂 {category} ({len(articles)}편)"):
                    for i, art in enumerate(articles):
                        st.markdown(f"**{i+1}. {art['title']}**")
            
            st.divider()
            word_file = create_word_document(st.session_state['blog_db'])
            st.download_button(
                label="📥 워드(.docx) 파일로 다운로드", data=word_file,
                file_name="부동산_투자_기록.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
