import streamlit as st
import os
from quizgen import basic_formulas as bf

st.set_page_config(page_title="곱셈·인수분해 공식 연습", layout="centered")
st.title("곱셈 / 인수분해 공식 연습")

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
st.latex(problem["latex_question"])

progress = st.session_state.correct_count / 10
st.progress(progress, text=f"{st.session_state.correct_count}/10 문제 정답")

# -------------------------------
# 정답 공개
# -------------------------------
if st.session_state.show_answer:
    st.info("정답")
    st.latex(problem["latex_answer"])

# -------------------------------
# 입력 폼
# -------------------------------
with st.form("answer_form", clear_on_submit=True):
    user_input = st.text_input("답안을 입력하세요 (예: b^2-9)")
    submitted = st.form_submit_button("제출")

    if submitted:
        is_correct = bf.check_expansion_answer(user_input, problem["answer_obj"])

        if is_correct:
            st.success("정답입니다!")
            st.session_state.correct_count += 1
            st.session_state.wrong_count = 0
            st.session_state.show_answer = False
            st.session_state.current_problem = make_problem(option)
            st.rerun()

        else:
            st.session_state.wrong_count += 1
            st.error("오답입니다.")

            video_path = f"media/{option}.mp4"
            if os.path.exists(video_path):
                st.video(video_path)

            if st.session_state.wrong_count < 3:
                st.warning("다시 풀어보세요. 같은 문제가 다시 나옵니다.")

            else:
                st.warning("3번 틀렸습니다. 정답을 확인하세요.")
                st.session_state.show_answer = True

                # 다음 문제 예약
                st.session_state.current_problem = make_problem(option)
                st.session_state.wrong_count = 0
                st.rerun()