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

    # --- スタイルとフッターの設定（青枠を削除済み） ---
    st.markdown("""
        <style>
        /* エクスパンダー（入力欄）の枠を強調 */
        .streamlit-expanderHeader {
            background-color: #262730 !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            color: #00D1FF !important;
        }
        
        /* フォーム内の背景を少し変えて「入力エリア」感を出 */
        div[data-testid="stForm"] {
            border: 1px solid #30363D !important;
            background-color: #1A1C24 !important;
            padding: 20px !important;
        }

        /* 固定フッターのスタイル */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #0E1117;
            color: #666;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            border-top: 1px solid #30363D;
            z-index: 100;
        }
        .footer a {
            color: #00D1FF;
            text-decoration: none;
        }
        /* コンテンツがフッターに被らないよう余白を追加 */
        .main .block-container {
            padding-bottom: 80px;
        }
        </style>
        
        <div class="footer">
            go-pro-world.net since 2025 | 
            <a href="https://go-pro-world.net" target="_blank">go-pro-world.net</a>
        </div>
        """, unsafe_allow_html=True)

    # 青枠なしのシンプルなタイトル
    st.title("🛠️ 整備メモ・マニュアル")

    # --- メインエリア上部：新規登録（expanderで折りたたみ可能に） ---
    with st.expander("➕ 新規レコードを登録する", expanded=False):
        with st.form("input_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                category = st.selectbox("カテゴリ", ["整備系", "マニュアル系", "社内設備・ルール"])
                rec_date = st.date_input("日付", value=date.today())
            with col_b:
                model_name = st.text_input("型式", placeholder="例: PC128")
                serial_number = st.text_input("機番")
            
            content = st.text_area("作業内容・メモ")
            
            # フォーム送信ボタン（横幅いっぱいに広げるとおしゃれ）
            submitted = st.form_submit_button("保存する", use_container_width=True)
            
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
                        st.success("保存しました！")
                        st.rerun()  # メイン画面に即時反映
                    else:
                        st.error(f"保存失敗: {response.status_code}")
                except Exception as e:
                    st.error(f"通信エラー: {e}")

    st.markdown("---") # 区切り線

    # --- メインエリア：検索と表示 ---
    st.subheader("🔍 記録を検索・閲覧")
    search_q = st.text_input("型式、機番、内容で検索...", placeholder="キーワードを入力してEnter")

    try:
        # 検索クエリを付けてAPIからデータを取得
        res = requests.get(f"{API_URL}/records/", params={"q": search_q})
        records = res.json()

        if not records:
            st.info("該当するデータがありません。")
        else:
            # バックエンド側で降順に並べ替えていない場合は reversed を使用
            for r in reversed(records):
                # カードのような見た目にするためのコンテナ
                with st.container():
                    col1, col2, col3 = st.columns([1.2, 4, 0.5])
                    
                    with col1:
                        # カテゴリの色設定
                        if r["category"] == "整備系":
                            label_color = "green"
                        elif r["category"] == "マニュアル系":
                            label_color = "blue"
                        elif r["category"] == "社内設備・ルール":
                            label_color = "red"
                        else:
                            label_color = "orange"
                            
                        st.markdown(f":{label_color}[{r['category']}]")
                        st.caption(f"📅 {r['date'] or '日付なし'}")
                        
                    with col2:
                        st.markdown(f"**{r['model_name'] or '型式不明'}** (`{r['serial_number'] or '-'}`)")
                        st.write(r["content"])
                        
                    with col3:
                        # 削除ボタン
                        with st.popover("🗑️"):
                            st.write("削除しますか？")
                            if st.button("削除", key=f"conf_{r['id']}", type="primary", use_container_width=True):
                                try:
                                    res = requests.delete(f"{API_URL}/records/{r['id']}")
                                    if res.status_code == 200:
                                        st.rerun()
                                    else:
                                        st.error("失敗")
                                except Exception as e:
                                    st.error("エラー")
                    st.divider()

    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        