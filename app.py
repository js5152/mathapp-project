import streamlit as st
import sys, os, random, datetime
import pandas as pd

# -------------------------------
# 경로 설정
# -------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from quizgen import basic_formulas as bf

# -------------------------------
# 구글시트 연결 (핵심)
# -------------------------------
conn = st.connection("gsheets", type="gspread")

# -------------------------------
# 페이지 기본 설정
# -------------------------------
st.set_page_config(page_title="곱셈·인수분해 공식 연습", layout="centered")
st.title("곱셈 / 인수분해 공식 연습")

# -------------------------------
# 로그인 상태
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# -------------------------------
# 로그인 화면
# -------------------------------
if not st.session_state.logged_in:
    st.subheader("학생 로그인")
    input_name = st.text_input("이름")
    input_pw = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        try:
            df = conn.read(worksheet="users", ttl=0)
            df.columns = [c.strip().lower() for c in df.columns]

            user_match = df[(df["name"] == input_name) &
                             (df["password"].astype(str) == input_pw)]

            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = input_name
                st.success(f"{input_name} 학생, 환영합니다!")
                st.rerun()
            else:
                st.error("이름 또는 비밀번호가 틀렸습니다.")
        except Exception as e:
            st.error(e)

    st.stop()

# -------------------------------
# 사이드바
# -------------------------------
with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}** 학생")
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()
    st.divider()

# -------------------------------
# 상태 초기화
# -------------------------------
if "current_problem" not in st.session_state:
    st.session_state.current_problem = None
if "current_type" not in st.session_state:
    st.session_state.current_type = None
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "wrong_count" not in st.session_state:
    st.session_state.wrong_count = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# -------------------------------
# 문제 생성기
# -------------------------------
def make_problem(option):
    if option == "완전제곱식":
        return bf.generate_type1_expansion()
    elif option == "합차공식":
        return bf.generate_type2_expansion()
    elif option == "(x+a)(x+b)":
        return bf.generate_type3_expansion()
    elif option == "(ax+b)(cx+d)":
        return bf.generate_type4_expansion()

# -------------------------------
# 유형 선택
# -------------------------------
option = st.selectbox(
    "연습할 공식을 선택하세요:",
    ("완전제곱식", "합차공식", "(x+a)(x+b)", "(ax+b)(cx+d)")
)

if st.session_state.current_type != option:
    st.session_state.current_type = option
    st.session_state.current_problem = make_problem(option)
    st.session_state.correct_count = 0
    st.session_state.wrong_count = 0
    st.session_state.show_answer = False
    st.rerun()

# -------------------------------
# 문제 출력
# -------------------------------
problem = st.session_state.current_problem
st.markdown("### 문제")
st.latex(problem["latex_question"])

progress = min(st.session_state.correct_count / 10, 1.0)
st.progress(progress, text=f"{st.session_state.correct_count}/10 문제 정답")

# -------------------------------
# 로그 기록 함수
# -------------------------------
def write_log(result_text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{
        "timestamp": now,
        "name": st.session_state.user_name,
        "type": option,
        "result": result_text
    }])
    conn.create(worksheet="logs", data=new_log)

# -------------------------------
# 정답 처리
# -------------------------------
def check_answer(user_choice):
    if user_choice == problem["latex_answer"]:
        write_log("정답")
        st.session_state.correct_count += 1
        st.session_state.wrong_count = 0
        st.session_state.show_answer = False
        st.session_state.current_problem = make_problem(option)
        st.success("정답입니다!")
        st.rerun()
    else:
        st.session_state.wrong_count += 1
        write_log(f"오답({st.session_state.wrong_count}차)")

        if st.session_state.wrong_count >= 3:
            st.session_state.show_answer = True
            st.rerun()
        else:
            st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")

# -------------------------------
# UI 구성
# -------------------------------
if st.session_state.show_answer:
    st.warning("3번 틀렸습니다. 정답을 확인하세요.")
    st.info(f"정답: $ {problem['latex_answer']} $")

    if st.button("다음 문제"):
        st.session_state.show_answer = False
        st.session_state.wrong_count = 0
        st.session_state.current_problem = make_problem(option)
        st.rerun()

else:
    st.write("정답을 고르세요:")
    choices = problem["choices"]

    st.markdown(f'''
    $\\quad\\quad ① \\enspace {choices[0]}$  

    $\\quad\\quad ② \\enspace {choices[1]}$  

    $\\quad\\quad ③ \\enspace {choices[2]}$  

    $\\quad\\quad ④ \\enspace {choices[3]}$
    ''')

    cols = st.columns(4)
    btns = ["①", "②", "③", "④"]
    for i, col in enumerate(cols):
        with col:
            if st.button(btns[i], key=f"btn_{i}", use_container_width=True):
                check_answer(choices[i])