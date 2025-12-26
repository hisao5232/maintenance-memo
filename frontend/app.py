import streamlit as st
import requests
import os
from datetime import date

# docker-compose.ymlで設定した環境変数からAPIのURLを取得
API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="整備メモ", page_icon="🛠️")

st.title("🛠️ 整備メモ・マニュアル")

# --- サイドバー：新規登録 ---
st.sidebar.header("新規登録")
with st.sidebar.form("input_form", clear_on_submit=True):
    category = st.selectbox("カテゴリ", ["整備系", "マニュアル系"])
    rec_date = st.date_input("日付", value=date.today())
    model_name = st.text_input("型式", placeholder="例: PC128")
    serial_number = st.text_input("機番")
    content = st.text_area("作業内容・メモ")
    
    submitted = st.form_submit_button("保存する")
    
    if submitted:
        payload = {
            "category": str(category) if category else None,
            "date": rec_date.isoformat() if rec_date else None,
            "model_name": str(model_name) if model_name else None,
            "serial_number": str(serial_number) if serial_number else None,
            "content": str(content) if content else None
        }

        try:
            response = requests.post(f"{API_URL}/records/", json=payload)
            if response.status_code == 200:
                st.sidebar.success("保存しました！")
            else:
                st.sidebar.error(f"保存失敗: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"通信エラー: {e}")

# --- メインエリア：検索と表示 ---
search_q = st.text_input("型式、機番、内容で検索...", placeholder="キーワードを入力してEnter")

try:
    # 検索クエリを付けてAPIからデータを取得
    res = requests.get(f"{API_URL}/records/", params={"q": search_q})
    records = res.json()

    if not records:
        st.info("データがありません。")
    else:
        # 新しい順に表示
        for r in reversed(records):
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    label_color = "green" if r["category"] == "整備系" else "blue"
                    st.markdown(f":{label_color}[{r['category']}]")
                    st.caption(r["date"] or "日付なし")
                with col2:
                    st.subheader(f"{r['model_name'] or '型式不明'} ({r['serial_number'] or '-'})")
                    st.write(r["content"])
                st.divider()

except Exception as e:
    st.error(f"データの読み込みに失敗しました: {e}")


