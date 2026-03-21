import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import sys, os, datetime, re
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# -------------------------------
# 1. 페이지 설정 및 모듈 로드
# -------------------------------
st.set_page_config(page_title="수학 마스터 클래스", layout="centered")
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
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        s = st.secrets["connections"]["gsheets"]
        credentials = Credentials.from_service_account_info({
            "project_id": s["project_id"], "private_key": s["private_key"],
            "client_email": s["client_email"], "token_uri": s["token_uri"],
        }, scopes=scope)
        gc = gspread.authorize(credentials)
        sh = gc.open_by_url(s["spreadsheet"])
        worksheet = sh.worksheet("logs")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, st.session_state.user_name, st.session_state.current_type, result_text]
        worksheet.append_row(row)
    except Exception as e:
        st.sidebar.error(f"기록 실패: {e}")

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

# -------------------------------
# 4. 상태 초기화
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.current_problem = None
    st.session_state.current_type = ""
    st.session_state.correct_count = 0
    st.session_state.wrong_count = 0
    st.session_state.show_answer = False

# -------------------------------
# 5. 로그인 (생략 가능 시 이전 코드와 동일)
# -------------------------------
if not st.session_state.logged_in:
    st.title("👨‍🏫 수학 연습 로그인")
    name = st.text_input("이름")
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        df = conn.read(worksheet="users", ttl=300)
        matched = df[(df["name"].apply(normalize_login_data) == normalize_login_data(name)) &
                     (df["password"].apply(normalize_login_data) == normalize_login_data(pw))]
        if not matched.empty:
            st.session_state.logged_in = True
            st.session_state.user_name = matched.iloc[0]["name"]
            st.rerun()
        else: st.error("로그인 실패")
    st.stop()

# -------------------------------
# 6. 사이드바 메뉴
# -------------------------------
with st.sidebar:
    st.write(f"👤 {st.session_state.user_name} 학생")
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
    st.divider()
    main_menu = st.radio("📂 학습 메뉴", ["🧩 공식 연습", "📐 삼각함수 영상", "📝 삼각함수 퀴즈"])

# -------------------------------
# 7. 메뉴 1: 공식 연습 (강사님 요청 버전 최적화)
# -------------------------------
if main_menu == "🧩 공식 연습":
    st.title("곱셈 / 인수분해 공식 연습")
    
    with st.sidebar:
        st.subheader("연습 설정")
        option = st.selectbox("연습할 공식:", ("완전제곱식", "합차공식", "(x+a)(x+b)", "(ax+b)(cx+d)", "삼차식(세제곱)", "삼차식(합차변형)", "항3개제곱", "삼차식전개", "복이차식꼴", "세항의삼차공식"))
        is_factor = st.checkbox("🧩 인수분해 문제로 풀기 (체크 해제 시 전개 연습)")

    current_state_key = f"bf_{option}_{is_factor}"

    if st.session_state.current_type != current_state_key:
        st.session_state.current_type = current_state_key
        st.session_state.current_problem = make_problem(option, is_factor)
        st.session_state.correct_count = 0
        st.session_state.wrong_count = 0
        st.session_state.show_answer = False
        st.rerun()

    if st.session_state.correct_count >= 10:
        st.balloons()
        st.success(f"🎊 대단합니다! 10문제를 모두 맞혔습니다!")
        if st.button("다시 도전하기", type="primary", use_container_width=True):
            st.session_state.correct_count = 0
            st.rerun()
        st.stop()

    problem = st.session_state.current_problem
    if problem:
        st.markdown("### 문제")
        st.latex(problem["latex_question"])
        st.progress(st.session_state.correct_count/10, text=f"현재 {st.session_state.correct_count}/10 성공")

        st.write("정답을 고르세요:")
        choices = problem["choices"]
        for i, choice in enumerate(choices):
            st.markdown(f"$\quad {['①','②','③','④','⑤'][i]} \enspace {choice}$")

        def handle_answer_internal(user_choice):
            if user_choice.strip() == problem["latex_answer"].strip():
                append_log(f"정답({option})")
                st.session_state.correct_count += 1
                st.session_state.wrong_count = 0
                st.session_state.current_problem = make_problem(option, is_factor)
                st.success("정답입니다! 🎉")
                st.rerun()
            else:
                st.session_state.wrong_count += 1
                append_log(f"오답({option}_{st.session_state.wrong_count}차)")
                if st.session_state.wrong_count >= 3:
                    st.session_state.show_answer = True
                st.rerun()

        if st.session_state.show_answer:
            st.error("🚨 3회 오답: 정답을 확인하세요.")
            st.warning(f"정답: $ {problem['latex_answer']} $")
            if st.button("확인했습니다. 다음 문제 풀기", type="primary", use_container_width=True):
                st.session_state.show_answer = False
                st.session_state.wrong_count = 0
                st.session_state.current_problem = make_problem(option, is_factor)
                st.rerun()
        else:
            cols = st.columns(5)
            for i, col in enumerate(cols):
                with col:
                    # 중복 방지를 위해 key 수정
                    if st.button(f"{['①','②','③','④','⑤'][i]}", key=f"bf_btn_{i}_{current_state_key}", use_container_width=True):
                        handle_answer_internal(choices[i])
            
            if 0 < st.session_state.wrong_count < 3:
                st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")
                mode_name = "인수분해" if is_factor else "전개"
                video_filename = f"{mode_name}_{option}.mp4"
                video_path = os.path.join("media", video_filename)
                if os.path.exists(video_path):
                    st.video(video_path) # 효율적인 경로 재생

# -------------------------------
# 8. 메뉴 2: 삼각함수 영상 (이전과 동일)
# -------------------------------
elif main_menu == "📐 삼각함수 영상":
    st.title("📐 원리 복습")
    tab1, tab2, tab3 = st.tabs(["Sin", "Cos", "Tan"])
    for tab, func in zip([tab1, tab2, tab3], ["Sin", "Cos", "Tan"]):
        with tab:
            video_path = os.path.join("media", f"{func}SpecialAngles.mp4")
            if os.path.exists(video_path): st.video(video_path)
            else: st.warning(f"{func} 영상 없음")

# -------------------------------
# 9. 메뉴 3: 삼각함수 퀴즈 (단판 승부 버전)
# -------------------------------
elif main_menu == "📝 삼각함수 퀴즈":
    st.title("📝 특수각 마스터")
    if st.session_state.current_type != "trig_quiz":
        st.session_state.current_type = "trig_quiz"; st.session_state.current_problem = tf.generate_quiz()
        st.session_state.correct_count = 0; st.session_state.show_answer = False; st.rerun()

    if st.session_state.correct_count >= 10:
        st.balloons(); st.success("🎊 삼각함수 정복!"); 
        if st.button("다시 도전", use_container_width=True): st.session_state.correct_count = 0; st.rerun()
        st.stop()

    problem = st.session_state.current_problem
    if problem:
        st.latex(problem["latex_question"] + " = ?")
        st.progress(st.session_state.correct_count / 10)
        
        def handle_trig(choice):
            if choice.strip() == problem["latex_answer"].strip():
                append_log("정답(trig)"); st.session_state.correct_count += 1
                st.session_state.current_problem = tf.generate_quiz(); st.rerun()
            else:
                err_type = tf.classify_error(choice, problem["latex_answer"], problem["meta"]["func"], problem["meta"]["angle"])
                append_log(f"오답({err_type})"); st.session_state.show_answer = True; st.rerun()

        if st.session_state.show_answer:
            st.error(f"🚨 정답은 ${problem['latex_answer']}$ 입니다.")
            if st.button("확인했습니다. 다음 문제", use_container_width=True):
                st.session_state.show_answer = False
                st.session_state.current_problem = tf.generate_quiz()
                st.rerun()
        else:
            # 1. 보기를 위에 LaTeX로 먼저 출력 (깨짐 방지)
            choices = problem["choices"]
            st.write("정답을 고르세요:")
            
            # 한 줄에 보기 하나씩 깔끔하게 수식으로 보여줌
            for i, choice in enumerate(choices):
                st.markdown(f"$\quad {['①','②','③','④','⑤'][i]} \enspace {choice}$")
            
            st.write("") # 간격 조절

            # 2. 버튼은 번호만 가로로 배치
            cols = st.columns(5)
            for i, col in enumerate(cols):
                with col:
                    # 버튼 안에는 수식 없이 번호만 넣어서 깔끔하게!
                    if st.button(f"{['①','②','③','④','⑤'][i]}", 
                                 key=f"trig_btn_{i}_{problem['latex_question']}", 
                                 use_container_width=True):
                        handle_trig(choices[i])
