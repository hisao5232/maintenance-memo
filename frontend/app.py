import streamlit as st
import requests
import os
from datetime import date

# docker-compose.ymlで設定した環境変数からAPIのURLを取得
API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="Maintenance Memo APP",
    page_icon="🚜",
    layout="wide" # 画面幅を広く使う
)

# ヘッダーを少しおしゃれに
st.markdown("""
    <div style="background-color:#2E5BFF;padding:10px;border-radius:10px;margin-bottom:25px;">
        <h1 style="color:white;text-align:center;margin:0;">🚜 Maintenance Management</h1>
    </div>
    """, unsafe_allow_html=True)

# --- ログインチェック用関数 ---
def check_password():
    """ユーザー名とパスワードが正しいかチェックする"""
    def password_entered():
        if (
            st.session_state["username"] == os.getenv("APP_USERNAME")
            and st.session_state["password"] == os.getenv("APP_PASSWORD")
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セッションにパスワードを残さない
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回表示：ログインフォームを出す
        st.title("🛠️ 整備メモ ログイン")
        st.text_input("ユーザー名", key="username")
        st.text_input("パスワード", type="password", key="password")
        st.button("ログイン", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # パスワード間違い時
        st.text_input("ユーザー名", key="username")
        st.text_input("パスワード", type="password", key="password")
        st.button("ログイン", on_click=password_entered)
        st.error("😕 ユーザー名またはパスワードが違います")
        return False
    else:
        # ログイン成功
        return True

# --- メイン処理 ---
if check_password():  
    st.title("🛠️ 整備メモ・マニュアル")

    # --- サイドバー：新規登録 ---
    st.sidebar.header("新規登録")
    with st.sidebar.form("input_form", clear_on_submit=True):
        category = st.selectbox("カテゴリ", ["整備系", "マニュアル系", "社内設備・ルール"])
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
                    col1, col2, col3 = st.columns([1, 4, 1])
                    
                    with col1:
                        with col1:
                            # カテゴリごとにラベルの色を変える設定
                            if r["category"] == "整備系":
                                label_color = "green"
                            elif r["category"] == "マニュアル系":
                                label_color = "blue"
                            elif r["category"] == "社内設備・ルール":
                                label_color = "red"
                            else:
                                label_color = "orange"
                                
                            st.markdown(f":{label_color}[{r['category']}]")
                            st.caption(r["date"] or "日付なし")
                        
                    with col2:
                        st.subheader(f"{r['model_name'] or '型式不明'} ({r['serial_number'] or '-'})")
                        st.write(r["content"])
                        
                    with col3:
                        # --- ここから削除ボタン（ポップオーバー形式） ---
                        with st.popover("🗑️"):
                            st.write("このメモを削除しますか？")
                            if st.button("はい、削除します", key=f"conf_{r['id']}", type="primary"):
                                try:
                                    res = requests.delete(f"{API_URL}/records/{r['id']}")
                                    if res.status_code == 200:
                                        st.success("削除完了")
                                        st.rerun()  # 画面を更新
                                    else:
                                        st.error("削除失敗")
                                except Exception as e:
                                    st.error(f"通信エラー: {e}")
                    st.divider()

    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")


