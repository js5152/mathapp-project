import streamlit as st
import sys, os, datetime, re
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# -------------------------------
# 0. 페이지 기본 설정
# -------------------------------
st.set_page_config(page_title="곱셈·인수분해 공식 연습", layout="centered")

# -------------------------------
# 1. 모듈 로드 및 연결 설정
# -------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from quizgen import basic_formulas as bf
except ImportError:
    st.error("quizgen 모듈을 찾을 수 없습니다.")
    st.stop()

# 구글 시트 연결
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"구글 시트 연결 실패: {e}")
    st.stop()

# -------------------------------
# 2. 유틸리티 함수 (데이터 정규화)
# -------------------------------
def normalize_login_data(value):
    """로그인 데이터 정규화 - 숫자 소수점 제거 및 특수 공백 제거"""
    if pd.isna(value):
        return ""
    value = str(value).strip()
    # 1. 숫자 .0 제거
    try:
        num_val = float(value)
        if num_val.is_integer():
            value = str(int(num_val))
    except:
        pass
    # 2. 선행 ' 제거
    if value.startswith("'"):
        value = value[1:]
    # 3. 공백/제로폭 문자 제거
    value = re.sub(r"[\s\u200b\u200c\u200d\ufeff]+", "", value)
    return value

# -------------------------------
# 3. 상태 초기화
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
# 4. 문제 생성 및 로그 저장 함수
# -------------------------------
def make_problem(option):
    mapping = {
        "완전제곱식": bf.generate_type1_expansion,
        "합차공식": bf.generate_type2_expansion,
        "(x+a)(x+b)": bf.generate_type3_expansion,
        "(ax+b)(cx+d)": bf.generate_type4_expansion,
    }
    return mapping.get(option, lambda: None)()

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
    except:
        pass # 기록 실패가 학습을 방해하지 않도록 처리

# -------------------------------
# 5. 로그인 UI
# -------------------------------
if not st.session_state.logged_in:
    st.title("곱셈 / 인수분해 공식 연습")
    st.subheader("학생 로그인")

    input_name = st.text_input("이름")
    input_pw = st.text_input("비밀번호", type="password")

    if st.button("로그인", use_container_width=True):
        try:
            # TTL=0으로 설정하여 매번 새로운 데이터를 가져옵니다.
            df_users = conn.read(worksheet="users", ttl=0)
            
            # 입력값 및 시트 데이터 정규화 대조
            in_n = normalize_login_data(input_name)
            in_p = normalize_login_data(input_pw)
            
            matched = df_users[
                (df_users["name"].apply(normalize_login_data) == in_n) &
                (df_users["password"].apply(normalize_login_data) == in_p)
            ]

            if not matched.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = matched.iloc[0]["name"]
                st.rerun()
            else:
                st.error("이름 또는 비밀번호가 틀렸습니다.")
        except Exception as e:
            st.error(f"로그인 처리 중 오류 발생: {e}")
    st.stop()

# -------------------------------
# 6. 메인 UI (문제 풀이 화면)
# -------------------------------
st.title("곱셈 / 인수분해 공식 연습")

with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}** 학생")
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
    st.divider()

# 공식 선택 및 문제 초기화
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

problem = st.session_state.current_problem

if problem:
    st.markdown("### 문제")
    st.latex(problem["latex_question"])
    st.progress(min(st.session_state.correct_count/10, 1.0), text=f"현재 {st.session_state.correct_count}/10 달성")

    def handle_answer(choice):
        if choice == problem["latex_answer"]:
            append_log("정답")
            st.session_state.correct_count += 1
            st.session_state.wrong_count = 0
            st.session_state.current_problem = make_problem(option)
            st.success("정답입니다! 🎉")
            st.rerun()
        else:
            st.session_state.wrong_count += 1
            append_log(f"오답({st.session_state.wrong_count}차)")
            if st.session_state.wrong_count >= 3:
                st.session_state.show_answer = True
            else:
                st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")
            st.rerun()

    if st.session_state.show_answer:
        st.warning("3번 틀렸습니다. 아래 정답을 확인하세요.")
        st.info(f"정답: $ {problem['latex_answer']} $")
        
        # 영상 출력 (파일명이 공식명과 일치해야 함)
        video_path = f"media/{option}.mp4"
        if os.path.exists(video_path):
            st.video(video_path)
        
        if st.button("공부 완료! 다음 문제 풀기", type="primary"):
            st.session_state.show_answer = False
            st.session_state.wrong_count = 0
            st.session_state.current_problem = make_problem(option)
            st.rerun()
    else:
        st.write("정답을 고르세요:")
        choices = problem["choices"]
        
        # 보기 출력
        st.markdown(f"① $ {choices[0]} $  \n② $ {choices[1]} $  \n③ $ {choices[2]} $  \n④ $ {choices[3]} $")
        
        cols = st.columns(4)
        for i, col in enumerate(cols):
            with col:
                if st.button(f"{i+1}번", key=f"btn_{i}", use_container_width=True):
                    handle_answer(choices[i])
