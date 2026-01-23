import streamlit as st
import sys
import os

# 현재 파일이 있는 폴더를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
from quizgen import basic_formulas as bf

st.set_page_config(page_title="곱셈·인수분해 공식 연습", layout="centered")
st.title("곱셈 / 인수분해 공식 연습")

import pandas as pd

# 1. 구글 시트 주소 가공 (Secrets에 넣은 주소 가져오기)
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
# 주소 뒤에 /edit 등이 붙어 있어도 작동하게끔 CSV 전용 주소로 변환합니다.
csv_url = f"{sheet_url.split('/edit')[0]}/gviz/tq?tqx=out:csv&sheet=users"

# 로그인 상태 관리
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# --- 로그인 화면 ---
if not st.session_state.logged_in:
    st.subheader("학생 로그인")
    input_name = st.text_input("이름")
    input_pw = st.text_input("비밀번호", type="password")
    
    if st.button("로그인"):
        try:
            # 2. pandas를 이용해 구글 시트를 직접 읽어오기
            df = pd.read_csv(csv_url)
            
            # 컬럼 이름이 대소문자 섞여있을 수 있으니 정리
            df.columns = [c.strip().lower() for c in df.columns]
            
            # 일치하는 학생 찾기
            user_match = df[(df['name'] == input_name) & (df['password'].astype(str) == input_pw)]
            
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = input_name
                st.success(f"{input_name} 학생, 환영합니다!")
                st.rerun()
            else:
                st.error("이름 또는 비밀번호가 틀렸습니다.")
        except Exception as e:
            st.error("시트 연결 오류: 구글 시트의 [공유] 설정이 '링크가 있는 모든 사용자 - 뷰어'인지 확인해주세요.")
    st.stop() # 로그인 전까지는 아래 코드로 못 넘어감

# --- 사이드바에 로그아웃 버튼 추가 ---
with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}** 학생")
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()
    st.divider() # 선 하나 그어주기


# --- 이 아래부터 기존 문제 풀이 코드 시작 ---


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

import datetime
import pandas as pd

def check_answer(user_choice):
    # 1. 기록을 위한 데이터 수집
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_name = st.session_state.user_name
    problem_type = option
    
    if user_choice == problem["latex_answer"]:
        # 정답 시 로그 생성
        try:
            new_log = pd.DataFrame([{"timestamp": now, "name": user_name, "type": problem_type, "result": "정답"}])
            conn.create(worksheet="logs", data=new_log)
        except: pass
        
        st.session_state.correct_count += 1
        st.session_state.wrong_count = 0
        st.session_state.show_answer = False
        st.session_state.current_problem = make_problem(option)
        st.success("정답입니다! 🎉")
        st.rerun()
    else:
        st.session_state.wrong_count += 1
        
        # 오답 시 로그 생성
        try:
            new_log = pd.DataFrame([{"timestamp": now, "name": user_name, "type": problem_type, "result": f"오답({st.session_state.wrong_count}차)"}])
            conn.create(worksheet="logs", data=new_log)
        except: pass
        
        random.shuffle(st.session_state.current_problem["choices"])
        
        if st.session_state.wrong_count >= 3:
            st.session_state.show_answer = True
            st.rerun()
        else:
            st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")
            video_path = f"media/{option}.mp4"
            if os.path.exists(video_path):
                st.video(video_path)
                st.info("💡 위 설명을 보고 다시 한번 정답을 골라보세요!")
            else:
                st.warning(f"설명 영상({video_path})을 준비 중입니다. 다시 풀어보세요!")

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