import streamlit as st
import openai

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

    # 2. OpenAI SDK を直接呼び出して回答を取得
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text}
    ]

    # OpenAI Python SDK のバージョン違いに対応する（新しいクライアント API を優先）
    try:
        # 新しい API（openai>=1.x）の場合
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
    except Exception:
        # 古い互換 API にフォールバック
        openai.api_key = api_key
        # 一部の openai パッケージでは ChatCompletion が名前空間にない場合があるため安全に呼ぶ
        if hasattr(openai, 'ChatCompletion'):
            resp = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            )
        else:
            # さらに古い互換や包装ライブラリ向けに http request を直接呼ぶ簡易実装
            resp = openai.Completion.create(  # type: ignore[attr-defined]
                model="gpt-4o-mini",
                prompt='\n'.join([m['content'] for m in messages]),
                temperature=0.7,
            )

    # レスポンスから本文を安全に取り出す
    choice = None
    try:
        choice = resp.choices[0]
    except Exception:
        pass

    # いくつかの形に対応して content を取得
    content = None
    if choice is not None:
        # dataclass/obj style
        if hasattr(choice, 'message'):
            msg = choice.message
            content = getattr(msg, 'content', None) or (msg.get('content') if isinstance(msg, dict) else None)
        # dict style
        elif isinstance(choice, dict):
            content = choice.get('message', {}).get('content') or choice.get('text')

    return content if content is not None else str(resp)


# ==========================================
# ここからメインの画面表示処理
# ==========================================

# dotenv は任意（無ければ無視）
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

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