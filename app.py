import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import sys, os, datetime, re
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# -------------------------------
# 1. 페이지 기본 설정 및 모듈 로드
# -------------------------------
st.set_page_config(page_title="수학 공식 & 삼각함수 마스터", layout="centered")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from quizgen import basic_formulas as bf
    from quizgen import trig_quiz as tf 
except ImportError:
    st.error("quizgen 모듈을 찾을 수 없습니다. 폴더 구조를 확인해주세요.")
    st.stop()

# -------------------------------
# 2. 구글 시트 연결 및 로그 함수
# -------------------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"구글 시트 연결 실패: {e}")
    st.stop()

def append_log(result_text):
    """구글 시트 'logs' 워크시트에 실시간 기록"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        s = st.secrets["connections"]["gsheets"]

        credentials = Credentials.from_service_account_info({
            "project_id": s["project_id"],
            "private_key": s["private_key"],
            "client_email": s["client_email"],
            "token_uri": s["token_uri"],
        }, scopes=scope)

        gc = gspread.authorize(credentials)
        sh = gc.open_by_url(s["spreadsheet"])
        worksheet = sh.worksheet("logs")

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, st.session_state.user_name, st.session_state.current_type, result_text]
        worksheet.append_row(row)
    except Exception as e:
        st.sidebar.error(f"로그 기록 실패: {e}")

# -------------------------------
# 3. 유틸리티 함수
# -------------------------------
def normalize_login_data(value):
    if pd.isna(value): return ""
    value = str(value).strip()
    try:
        num_val = float(value)
        if num_val.is_integer(): value = str(int(num_val))
    except: pass
    if value.startswith("'"): value = value[1:]
    value = re.sub(r"[\s\u200b\u200c\u200d\ufeff]+", "", value)
    return value

def make_problem(option, is_factor):
    """기존 곱셈/인수분해 공식 문제 생성기 호출"""
    mapping = {
        "완전제곱식": 1, "합차공식": 2, "(x+a)(x+b)": 3, "(ax+b)(cx+d)": 4,
        "삼차식(세제곱)": 5, "삼차식(합차변형)": 6, "항3개제곱": 7,
        "삼차식전개": 8, "복이차식꼴": 9, "세항의삼차공식": 10
    }
    type_num = mapping.get(option)
    if type_num is None: return None
    mode = "factorization" if is_factor else "expansion"
    func = getattr(bf, f"generate_type{type_num}_{mode}", None)
    return func() if func else None

def display_math_video(filename, description):
    """비디오 경로를 직접 전달하여 효율적으로 재생"""
    video_path = os.path.join("media", filename)
    if os.path.exists(video_path):
        st.video(video_path) # f.read() 없이 경로로 직접 재생
        st.info(description)
    else:
        st.warning(f"🎥 영상 파일({filename})이 media 폴더에 없습니다.")

# -------------------------------
# 4. 세션 상태 초기화
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.current_problem = None
    st.session_state.current_type = ""
    st.session_state.correct_count = 0
    st.session_state.show_answer = False

# -------------------------------
# 5. 로그인 화면
# -------------------------------
if not st.session_state.logged_in:
    st.title("👨‍🏫 수학 마스터 로그인")
    name = st.text_input("이름")
    pw = st.text_input("비밀번호", type="password")

    if st.button("로그인", use_container_width=True):
        df = conn.read(worksheet="users", ttl=300)
        matched = df[
            (df["name"].apply(normalize_login_data) == normalize_login_data(name)) &
            (df["password"].apply(normalize_login_data) == normalize_login_data(pw))
        ]
        if not matched.empty:
            st.session_state.logged_in = True
            st.session_state.user_name = matched.iloc[0]["name"]
            st.rerun()
        else:
            st.error("이름 또는 비밀번호가 틀렸습니다.")
    st.stop()

# -------------------------------
# 6. 사이드바
# -------------------------------
with st.sidebar:
    st.subheader(f"👋 {st.session_state.user_name} 학생")
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    main_menu = st.radio(
        "📂 학습 메뉴 선택",
        ["🧩 공식 연습", "📐 삼각함수 영상", "📝 삼각함수 퀴즈"]
    )

# -------------------------------
# 7. 메뉴 1: 공식 연습 (곱셈/인수분해)
# -------------------------------
if main_menu == "🧩 공식 연습":
    st.title("🧩 공식 연습")
    option = st.selectbox("유형 선택", ("완전제곱식", "합차공식", "(x+a)(x+b)", "(ax+b)(cx+d)"))
    is_factor = st.checkbox("인수분해 모드")

    key = f"{option}_{is_factor}"
    if st.session_state.current_type != key:
        st.session_state.current_type = key
        st.session_state.current_problem = make_problem(option, is_factor)
        st.session_state.correct_count = 0
        st.session_state.show_answer = False
        st.rerun()

    problem = st.session_state.current_problem
    if problem:
        st.latex(problem["latex_question"])
        
        def handle_bf(choice):
            if choice.strip() == problem["latex_answer"].strip():
                append_log(f"정답({option})")
                st.session_state.correct_count += 1
                st.session_state.current_problem = make_problem(option, is_factor)
                st.rerun()
            else:
                append_log(f"오답({option})")
                st.error("다시 생각해보세요!")

        cols = st.columns(len(problem["choices"]))
        for i, c in enumerate(problem["choices"]):
            with cols[i]:
                # 중복 방지를 위해 key에 key(유형) 정보 포함
                if st.button(f"${c}$", key=f"bf_btn_{i}_{key}"):
                    handle_bf(c)
    else:
        st.warning("⚠️ 해당 유형의 문제를 생성할 수 없습니다. 준비 중입니다.")

# -------------------------------
# 8. 메뉴 2: 삼각함수 영상
# -------------------------------
elif main_menu == "📐 삼각함수 영상":
    st.title("📐 원리 복습")
    tab1, tab2, tab3 = st.tabs(["Sin", "Cos", "Tan"])
    with tab1: display_math_video("SinSpecialAngles.mp4", "Sin 원리")
    with tab2: display_math_video("CosSpecialAngles.mp4", "Cos 원리")
    with tab3: display_math_video("TanSpecialAngles.mp4", "Tan 원리")

# -------------------------------
# 9. 메뉴 3: 삼각함수 퀴즈
# -------------------------------
elif main_menu == "📝 삼각함수 퀴즈":
    st.title("📝 특수각 마스터")

    if st.session_state.current_type != "trig_quiz":
        st.session_state.current_type = "trig_quiz"
        st.session_state.current_problem = tf.generate_quiz()
        st.session_state.correct_count = 0
        st.session_state.show_answer = False
        st.rerun()

    # 10문제 성공 달성 시 (리셋 로직 포함)
    if st.session_state.correct_count >= 10:
        st.balloons()
        st.success(f"🎊 {st.session_state.user_name} 학생, 10문제 성공! 미션 완료!")
        if st.button("처음부터 다시 도전", type="primary", use_container_width=True):
            st.session_state.correct_count = 0
            st.session_state.current_problem = tf.generate_quiz() # 새 문제 생성
            st.rerun()
        st.stop()

    problem = st.session_state.current_problem
    if problem:
        st.latex(problem["latex_question"] + " = ?")
        st.progress(st.session_state.correct_count / 10, text=f"성공: {st.session_state.correct_count}/10")

        def handle_trig(user_choice):
            if user_choice.strip() == problem["latex_answer"].strip():
                append_log("정답(trig)")
                st.session_state.correct_count += 1
                st.session_state.current_problem = tf.generate_quiz()
                st.rerun()
            else:
                err_type = tf.classify_error(
                    user_choice, problem["latex_answer"], 
                    problem["meta"]["func"], problem["meta"]["angle"]
                )
                append_log(f"오답({err_type})") 
                st.session_state.show_answer = True
                st.rerun()

        if st.session_state.show_answer:
            st.error(f"🚨 오답입니다! 정답은 ${problem['latex_answer']}$ 입니다.")
            if st.button("확인했습니다. 다음 문제로", use_container_width=True):
                st.session_state.show_answer = False
                st.session_state.current_problem = tf.generate_quiz()
                st.rerun()
        else:
            choices = problem["choices"]
            cols = st.columns(len(choices))
            for i, col in enumerate(cols):
                with col:
                    # 중복 방지를 위해 key에 문제 수식 포함
                    unique_key = f"trig_{i}_{problem['latex_question']}"
                    if st.button(f"${choices[i]}$", key=unique_key, use_container_width=True):
                        handle_trig(choices[i])
    else:
        st.error("문제를 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
