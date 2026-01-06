import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- 関数定義：LLMへの問い合わせ ---
def generate_response(input_text, role_selection, api_key):
    """
    ユーザーの入力と選択された役割を受け取り、LLMの回答を返す関数
    """
    
    # 1. ラジオボタンの選択値に応じてシステムメッセージ（役割）を切り替える
    if role_selection == "ポジティブな熱血コーチ":
        system_prompt = """
        あなたは超熱血でポジティブなコーチです。
        どんな悩みに対しても「君ならできる！」「最高だ！」といった言葉を使い、
        暑苦しいくらいの情熱とビックリマーク(！)を多用して、相手を全力で励ましてください。
        """
    else: # 冷静沈着な論理的コンサルタント
        system_prompt = """
        あなたは感情を表に出さない、世界トップレベルのコンサルタントです。
        精神論は一切排除し、事実と論理（ロジック）に基づいて、
        簡潔かつ具体的で、少し厳しいくらいの改善策を提示してください。
        """

    # 2. LangChainのChatOpenAIモデルを初期化
    llm = ChatOpenAI(
        openai_api_key=api_key,
        model_name="gpt-4o-mini", # コストパフォーマンスの良いモデル
        temperature=0.7
    )

    # 3. メッセージリストの作成
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=input_text)
    ]

    # 4. LLMを実行して回答を取得
    result = llm.invoke(messages)
    
    # 5. 回答のテキスト部分だけを戻り値として返す
    return result.content


# ==========================================
# ここからメインの画面表示処理
# ==========================================

# ページの設定
st.set_page_config(page_title="AIアドバイザー切り替えアプリ", page_icon="🤖")

# タイトルとアプリの概要説明
st.title("🤖 性格切り替えAIアドバイザー")
st.markdown("""
### アプリの概要
このアプリは、あなたの質問や相談に対して、AIが回答してくれるツールです。
最大の特徴は、**「回答者の性格（専門家のタイプ）」を選べること**です。

### 操作方法
1. サイドバーに **OpenAI APIキー** を入力してください。
2. **「専門家の種類」** をラジオボタンで選択してください。
3. **「相談したい内容」** をテキストボックスに入力し、送信ボタンを押してください。
""")

# --- サイドバー：APIキー入力 ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("OpenAI APIキーを入力", type="password")

# --- メインエリア：入力フォーム ---
st.divider() # 区切り線

# ラジオボタン：専門家の種類を選択
selected_role = st.radio(
    "回答してほしい専門家を選んでください",
    ["ポジティブな熱血コーチ", "冷静沈着な論理的コンサルタント"],
    horizontal=True # 横並びにするオプション
)

# テキスト入力フォーム
user_input = st.text_area("相談したい内容を入力してください", height=150, placeholder="例：最近、やる気が起きなくて困っています...")

# 送信ボタン
if st.button("AIに相談する"):
    # エラーハンドリング：APIキーがない場合
    if not api_key:
        st.error("⚠️ サイドバーにOpenAI APIキーを入力してください。")
    # エラーハンドリング：入力がない場合
    elif not user_input:
        st.warning("⚠️ 相談内容を入力してください。")
    else:
        # --- ここで自作関数を呼び出す ---
        with st.spinner("AI専門家が回答を考えています..."):
            try:
                # 定義した関数に「テキスト」「役割」「APIキー」を渡す
                response_text = generate_response(user_input, selected_role, api_key)
                
                # 結果表示
                st.success("回答が届きました！")
                st.markdown(f"**【{selected_role}からのアドバイス】**")
                st.write(response_text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")


from dotenv import load_dotenv

load_dotenv()