import streamlit as st
import sys
import os

# 현재 파일이 있는 폴더를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
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
st.markdown("### 문제")
st.latex(problem["latex_question"])

progress = min(st.session_state.correct_count / 10, 1.0)
st.progress(progress, text=f"{st.session_state.correct_count}/10 문제 정답")

# -------------------------------
# 정답 확인 로직 (버튼 클릭 시 실행)
# -------------------------------
# app.py 상단에 random 임포트 확인 (이미 있을 겁니다)
import random

def check_answer(user_choice):
    if user_choice == problem["latex_answer"]:
        # ... (정답 로직은 그대로) ...
        st.session_state.correct_count += 1
        st.session_state.wrong_count = 0
        st.session_state.current_problem = make_problem(option)
        st.success("정답입니다! 🎉")
        st.rerun()
    else:
        st.session_state.wrong_count += 1
        
        # 🚩 핵심: 오답일 때 현재 문제의 choices 리스트를 다시 섞어버립니다!
        random.shuffle(st.session_state.current_problem["choices"])
        
        st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")
        
        if st.session_state.wrong_count >= 3:
            st.session_state.show_answer = True
        else:
            # 🚩 3번 미만으로 틀렸을 때 애니메이션(Manim) 보여주는 로직
            video_path = f"media/{option}.mp4"
            if os.path.exists(video_path):
                st.video(video_path)
            st.warning("애니메이션을 보고 다시 도전해보세요! 보기 순서가 바뀌었습니다.")


# -------------------------------
# UI 구성: 객관식 버튼 또는 정답 공개
# -------------------------------

# 1. 3번 틀려서 정답을 보여줘야 하는 상황
if st.session_state.show_answer:
    st.warning("3번 틀렸습니다. 아래 정답을 확인하고 공부하세요.")
    st.info(f"정답: $ {problem['latex_answer']} $")
    
    # 오답 시 비디오 출력
    video_path = f"media/{option}.mp4"
    if os.path.exists(video_path):
        st.video(video_path)
    
    if st.button("공부 완료! 다음 문제 풀기", type="primary", use_container_width=True):
        st.session_state.show_answer = False
        st.session_state.wrong_count = 0
        st.session_state.current_problem = make_problem(option)
        st.rerun()

# 2. 일반적인 문제 풀이 상황 (버튼 4개 노출)
# -------------------------------
# UI 구성: 객관식 보기 출력 수정
# -------------------------------
# UI 구성: 보기 왼쪽 정렬 버전
# -------------------------------
else:
    st.write("정답을 고르세요:")
    choices = problem["choices"]
    
    # 마크다운을 써서 왼쪽 정렬(aligned) 수식을 만듭니다.
    # r'''...''' 안의 & 기호가 정렬 기준점이 됩니다.
    st.markdown(f'''
    $\quad\quad ① \enspace\enspace {choices[0]}$  


    $\quad\quad ② \enspace\enspace {choices[1]}$  


    $\quad\quad ③ \enspace\enspace {choices[2]}$  


    $\quad\quad ④ \enspace\enspace {choices[3]}$
    ''')
    
    st.write("") # 약간의 여백
    
    # 버튼은 아까처럼 번호로 배치
    cols = st.columns(4)
    btns = ["①", "②", "③", "④"]
    for i, col in enumerate(cols):
        with col:
            if st.button(btns[i], key=f"btn_{i}", use_container_width=True):
                check_answer(choices[i])
