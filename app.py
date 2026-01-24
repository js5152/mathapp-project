import streamlit as st
import sys, os, datetime, re
import pandas as pd

# -------------------------------
# 0. 페이지 기본 설정
# -------------------------------
st.set_page_config(page_title="곱셈·인수분해 공식 연습", layout="centered")

# -------------------------------
# 1. 모듈 로드
# -------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from quizgen import basic_formulas as bf
except ImportError:
    st.error("quizgen 모듈을 찾을 수 없습니다.")
    st.stop()

# -------------------------------
# 2. 구글시트 연결
# -------------------------------
try:
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"구글 시트 연결 실패: {e}")
    st.stop()

# -------------------------------
# 3. 상태 초기화
# -------------------------------
def init_states():
    defaults = {
        "logged_in": False,
        "user_name": "",
        "current_problem": None,
        "current_type": "",
        "correct_count": 0,
        "wrong_count": 0,
        "show_answer": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_states()

# -------------------------------
# 4. 유틸 함수
# -------------------------------
def clean_text(x: str):
    """공백/특수공백 제거 + 소문자"""
    if pd.isna(x):
        return ""
    x = str(x)
    x = re.sub(r"\s+", "", x)  # 모든 공백 제거
    return x.lower()

# -------------------------------
# 5. 문제 생성 함수
# -------------------------------
def make_problem(option):
    mapping = {
        "완전제곱식": bf.generate_type1_expansion,
        "합차공식": bf.generate_type2_expansion,
        "(x+a)(x+b)": bf.generate_type3_expansion,
        "(ax+b)(cx+d)": bf.generate_type4_expansion,
    }
    return mapping.get(option, lambda: None)()

# -------------------------------
# 6. 로그 저장 함수
# -------------------------------
def append_log(result_text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{
        "timestamp": now,
        "name": st.session_state.user_name,
        "type": st.session_state.current_type,
        "result": result_text
    }])
    try:
        conn.create(worksheet="logs", data=new_log)
    except Exception as e:
        st.error(f"로그 저장 실패: {e}")

# -------------------------------
# 7. 로그인 화면
# -------------------------------
if not st.session_state.logged_in:
    st.title("곱셈 / 인수분해 공식 연습")
    st.subheader("학생 로그인")

    input_name = st.text_input("이름")
    input_pw = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        try:
            df_users = conn.read(worksheet="users", ttl=0)

            # 컬럼 전처리
            df_users.columns = [str(c).strip().lower() for c in df_users.columns]

            # 컬럼 존재 검사
            if not {"name", "password"} <= set(df_users.columns):
                st.error("users 시트에 'name', 'password' 컬럼이 있어야 합니다.")
                st.stop()

            # 값 전처리 컬럼 생성
            df_users["_name_clean"] = df_users["name"].apply(clean_text)
            df_users["_pw_clean"] = df_users["password"].apply(clean_text)

            input_name_clean = clean_text(input_name)
            input_pw_clean = clean_text(input_pw)

            matched = df_users[
                (df_users["_name_clean"] == input_name_clean) &
                (df_users["_pw_clean"] == input_pw_clean)
            ]

            if not matched.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = input_name.strip()
                st.experimental_rerun()
            else:
                st.error("이름 또는 비밀번호가 틀렸습니다.")

        except Exception as e:
            st.error(f"연결 오류: {e}")

    st.stop()

# -------------------------------
# 8. 메인 UI
# -------------------------------
st.title("곱셈 / 인수분해 공식 연습")

with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}** 학생")
    if st.button("로그아웃"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()
    st.divider()

# -------------------------------
# 9. 공식 선택
# -------------------------------
st.session_state.current_type = st.selectbox(
    "연습할 공식을 선택하세요:",
    ("완전제곱식","합차공식","(x+a)(x+b)","(ax+b)(cx+d)")
)

if st.session_state.current_problem is None:
    st.session_state.current_problem = make_problem(st.session_state.current_type)

problem = st.session_state.current_problem

# -------------------------------
# 10. 문제 UI
# -------------------------------
if problem is None:
    st.warning("문제를 생성할 수 없습니다.")
    st.stop()

st.markdown("### 문제")
st.latex(problem["latex_question"])
st.progress(min(st.session_state.correct_count / 10, 1.0))

def handle_answer(choice):
    if choice == problem["latex_answer"]:
        append_log("정답")
        st.session_state.correct_count += 1
        st.session_state.wrong_count = 0
        st.session_state.show_answer = False
        st.session_state.current_problem = make_problem(st.session_state.current_type)
    else:
        st.session_state.wrong_count += 1
        append_log(f"오답({st.session_state.wrong_count})")
        if st.session_state.wrong_count >= 3:
            st.session_state.show_answer = True

# -------------------------------
# 11. 정답/보기 UI
# -------------------------------
if st.session_state.show_answer:
    st.warning("3번 틀렸습니다. 정답을 확인하세요.")
    st.info(f"정답: $ {problem['latex_answer']} $")
    if st.button("다음 문제"):
        st.session_state.show_answer = False
        st.session_state.wrong_count = 0
        st.session_state.current_problem = make_problem(st.session_state.current_type)
        st.experimental_rerun()
else:
    st.write("정답을 고르세요:")
    choices = problem["choices"]
    cols = st.columns(4)
    btns = ["①","②","③","④"]
    for i, col in enumerate(cols):
        with col:
            if st.button(btns[i], key=f"btn_{i}", use_container_width=True):
                handle_answer(choices[i])
                st.experimental_rerun()