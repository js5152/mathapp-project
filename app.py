import gspread
from google.oauth2.service_account import Credentials

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
# 2. 유틸리티 함수
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

def append_log(result_text):
    try:
        # 1. 권한 설정 (secrets에서 직접 가져오기)
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        # secrets.toml의 구조에 따라 st.secrets.connections.gsheets 또는 st.secrets["connections"]["gsheets"] 사용
        s = st.secrets["connections"]["gsheets"]
        
        credentials = Credentials.from_service_account_info({
            "project_id": s["project_id"],
            "private_key": s["private_key"],
            "client_email": s["client_email"],
            "token_uri": s["token_uri"],
        }, scopes=scope)
        
        # 2. 시트 열기
        gc = gspread.authorize(credentials)
        # URL로 직접 열기 (가장 확실함)
        sh = gc.open_by_url(s["spreadsheet"])
        worksheet = sh.worksheet("logs")
        
        # 3. 데이터 추가 (순서: timestamp, name, type, result)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, st.session_state.user_name, st.session_state.current_type, result_text]
        worksheet.append_row(row)
        
    except Exception as e:
        st.sidebar.error(f"최종 기록 실패: {e}")

def make_problem(option):
    mapping = {
        "완전제곱식": bf.generate_type1_expansion,
        "합차공식": bf.generate_type2_expansion,
        "(x+a)(x+b)": bf.generate_type3_expansion,
        "(ax+b)(cx+d)": bf.generate_type4_expansion,
        "삼차식(세제곱)": bf.generate_type5_expansion,
        "삼차식(합차변형)": bf.generate_type6_expansion,
        "항3개제곱": bf.generate_type7_expansion,
        "삼차식전개": bf.generate_type8_expansion,
        "복이차식꼴": bf.generate_type9_expansion,
        "세항의삼차공식": bf.generate_type10_expansion,
    }
    return mapping.get(option, lambda: None)()


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
# 4. 로그인 UI
# -------------------------------
if not st.session_state.logged_in:
    st.title("곱셈 / 인수분해 공식 연습")
    st.subheader("학생 로그인")
    input_name = st.text_input("이름")
    input_pw = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        df_users = conn.read(worksheet="users", ttl=0)
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
    st.stop()

# -------------------------------
# 5. 메인 UI 및 문제 풀이
# -------------------------------
st.title("곱셈 / 인수분해 공식 연습")

with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}** 학생")
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
    st.divider()

option = st.selectbox("연습할 공식을 선택하세요:", ("완전제곱식", "합차공식", "(x+a)(x+b)", "(ax+b)(cx+d)", "삼차식(세제곱)", "삼차식(합차변형)", "항3개제곱", "삼차식전개", "복이차식꼴", "세항의삼차공식"))

if st.session_state.current_type != option:
    st.session_state.current_type = option
    st.session_state.current_problem = make_problem(option)
    st.session_state.correct_count = 0
    st.session_state.wrong_count = 0
    st.session_state.show_answer = False
    st.rerun()

# --- 10문제 완료 체크 ---
if st.session_state.correct_count >= 10:
    st.balloons()
    st.success(f"🎊 대단합니다! {st.session_state.user_name} 학생, 10문제를 모두 맞혔습니다! 🎊")
    if st.button("다시 처음부터 도전하기", type="primary", use_container_width=True):
        st.session_state.correct_count = 0
        st.rerun()
    st.stop()

problem = st.session_state.current_problem
if problem:
    st.markdown("### 문제")
    st.latex(problem["latex_question"])
    st.progress(st.session_state.correct_count/10, text=f"현재 {st.session_state.correct_count}/10 문제 성공")

    # --- 보기 출력 (정렬된 수식 버전) ---
    st.write("정답을 고르세요:")
    choices = problem["choices"]
    
    # 이 부분이 강사님이 원하시던 LaTeX 정렬 버전입니다.
    st.markdown(f'''
    $\quad\quad ① \enspace\enspace {choices[0]}$  
    $\quad\quad ② \enspace\enspace {choices[1]}$  
    $\quad\quad ③ \enspace\enspace {choices[2]}$  
    $\quad\quad ④ \enspace\enspace {choices[3]}$
    ''')
    st.write("")

    # --- 정답 처리 로직 ---
    def handle_answer(user_choice):
        if user_choice == problem["latex_answer"]:
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
            st.rerun()

    # --- UI 분기: 일반 상황 vs 3번 틀린 상황 ---
    if st.session_state.show_answer:
        st.error(f"오답입니다! (3/3)")
        st.warning(f"정답: $ {problem['latex_answer']} $")
        
        video_path = f"media/{option}.mp4"
        if os.path.exists(video_path):
            st.video(video_path)
            st.info("💡 설명을 보고 '공부 완료' 버튼을 누르세요.")
        
        if st.button("공부 완료! 다음 문제 풀기", type="primary", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.wrong_count = 0
            st.session_state.current_problem = make_problem(option)
            st.rerun()
    else:
        # 일반 버튼 UI
        cols = st.columns(4)
        for i, col in enumerate(cols):
            with col:
                if st.button(f"{['①','②','③','④'][i]}", key=f"btn_{i}", use_container_width=True):
                    handle_answer(choices[i])
        
        # 1~2회 오답 시 힌트와 영상 노출
        if 0 < st.session_state.wrong_count < 3:
            st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")
            video_path = f"media/{option}.mp4"
            if os.path.exists(video_path):
                st.video(video_path)

