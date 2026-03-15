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

def make_problem(option, is_factor):
    # 1. 메뉴 이름과 basic_formulas의 type 번호를 매칭
    mapping = {
        "완전제곱식": 1, "합차공식": 2, "(x+a)(x+b)": 3, "(ax+b)(cx+d)": 4,
        "삼차식(세제곱)": 5, "삼차식(합차변형)": 6, "항3개제곱": 7,
        "삼차식전개": 8, "복이차식꼴": 9, "세항의삼차공식": 10
    }
    
    type_num = mapping.get(option)
    if type_num is None: return None
    
    # 2. 체크박스 상태에 따라 접미사 결정
    mode = "factorization" if is_factor else "expansion"
    
    # 3. 함수 이름 조립 (예: generate_type1_expansion)
    target_func_name = f"generate_type{type_num}_{mode}"
    
    # 4. bf 모듈에서 해당 함수가 있는지 확인하고 실행
    func = getattr(bf, target_func_name, None)
    
    if func:
        return func()
    else:
        # 아직 인수분해 함수를 안 만들었을 경우를 대비한 안내
        st.warning(f"아직 {option}의 인수분해 함수({target_func_name})가 준비되지 않았습니다.")
        return None 


    
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
        df_users = conn.read(worksheet="users", ttl=300)
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

# (앞부분 import 및 유틸리티 함수, 로그인 UI까지는 그대로 두시고)
# -------------------------------
# 5. 사이드바 메인 컨트롤러 (메인 메뉴 결정)
# -------------------------------
with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}** 학생")
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
    st.divider()
    
    # 👈 여기서 메뉴를 결정합니다.
    main_menu = st.radio(
        "📂 학습 메뉴 선택",
        ["🧩 공식 연습", "📐 삼각함수 영상"]
    )

# -------------------------------
# 6. 메뉴별 화면 분기
# -------------------------------

if main_menu == "🧩 공식 연습":
    st.title("곱셈 / 인수분해 공식 연습")
    
    with st.sidebar:
        st.subheader("연습 설정")
        option = st.selectbox("연습할 공식:", ("완전제곱식", "합차공식", "(x+a)(x+b)", "(ax+b)(cx+d)", "삼차식(세제곱)", "삼차식(합차변형)", "항3개제곱", "삼차식전개", "복이차식꼴", "세항의삼차공식"))
        is_factor = st.checkbox("🧩 인수분해 문제로 풀기 (체크 해제 시 전개 연습)")

    current_state_key = f"{option}_{is_factor}"

    if st.session_state.current_type != current_state_key:
        st.session_state.current_type = current_state_key
        st.session_state.current_problem = make_problem(option, is_factor)
        st.session_state.correct_count = 0
        st.session_state.wrong_count = 0
        st.session_state.show_answer = False
        st.rerun()

    # 10문제 완료 체크
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

        st.write("정답을 고르세요:")
        choices = problem["choices"]
        
        for i, choice in enumerate(choices):
            st.markdown(f"$\quad {['①','②','③','④','⑤'][i]} \enspace {choice}$")
        st.write("")

        # 내부 정답 처리 함수 (들여쓰기 주의)
        def handle_answer_internal(user_choice):
            if user_choice == problem["latex_answer"]:
                append_log("정답")
                st.session_state.correct_count += 1
                st.session_state.wrong_count = 0
                st.session_state.current_problem = make_problem(option, is_factor)
                st.success("정답입니다! 🎉")
                st.rerun()
            else:
                st.session_state.wrong_count += 1
                append_log(f"오답({st.session_state.wrong_count}차)")
                if st.session_state.wrong_count >= 3:
                    st.session_state.show_answer = True
                st.rerun()

        # UI 분기
        if st.session_state.show_answer:
            st.error("🚨 3회 오답: 정답을 확인하고 다음 문제로 넘어갑니다.")
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
                    if st.button(f"{['①','②','③','④','⑤'][i]}", key=f"btn_{i}", use_container_width=True):
                        handle_answer_internal(choices[i])
            
            if 0 < st.session_state.wrong_count < 3:
                st.divider()
                st.error(f"오답입니다! ({st.session_state.wrong_count}/3)")
                st.warning("💡 아래 영상을 보면서 다시 한번 풀어보세요!")
                mode_name = "인수분해" if is_factor else "전개"
                video_filename = f"{mode_name}_{option}.mp4"
                video_path = os.path.join("media", video_filename)
                if os.path.exists(video_path):
                    with open(video_path, 'rb') as f:
                        video_bytes = f.read()
                    st.video(video_bytes)

elif main_menu == "📐 삼각함수 영상":
    st.title("삼각함수 특수각 원리")
    st.subheader("사인($\\sin$) 값의 변화 관찰하기")
    st.info("동경이 회전함에 따라 수선(y좌표)의 길이가 어떻게 변하는지 확인해보세요.")
    
    # ⭐ 핵심: 마님 애니메이션 출력 구간
    # 1. 파일 이름 정의 (코랩에서 다운로드한 파일명과 똑같이!)
    video_filename = "SinSpecialAngles.mp4" 
    
    # 2. 파일 경로 생성 (media/ 폴더 안에 있다고 가정)
    video_path = os.path.join("media", video_filename)
    
    # 3. 파일이 실제로 존재하는지 확인 후 출력
    if os.path.exists(video_path):
        # 파일을 바이너리 읽기 모드('rb')로 엽니다.
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        
        # streamlit의 비디오 플레이어로 재생 (제일 깔끔한 방식)
        st.video(video_bytes)
        st.caption(f"📹 영상: {video_filename} (단위 원과 사인 값의 관계)")
        
    else:
        # 파일이 없을 경우 강사님을 위한 디버깅 메시지
        st.warning(f"⚠️ 아직 설명 영상이 업로드되지 않았습니다. (파일명 확인: {video_path})")
        st.info("💡 코랩에서 만든 mp4 파일을 다운로드해서 깃허브의 media/ 폴더에 'Push' 해주세요.")
        
    st.divider()
    st.markdown("""
    ### 💡 핵심 포인트
    1. **사인($\\sin$)**은 단위 원 위 점의 **y좌표(높이)**와 같습니다.
    2. 동경이 1, 2사분면에 있을 때는 **양수(+)**, 3, 4사분면에 있을 때는 **음수(-)**입니다.
    """)
    st.table({
        "각도(deg)": ["0°", "30°", "45°", "60°", "90°"],
        "호도법(rad)": ["0", "π/6", "π/4", "π/3", "π/2"],
        "sin 값": ["0", "1/2", "√2/2", "√3/2", "1"]
    })
