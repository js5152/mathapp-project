import random
import numpy as np

# -------------------------------
# 1. 특수각 정의 (호도법 + LaTeX)
# -------------------------------
ANGLES = [
    (0, r"0"),
    (np.pi/6, r"\frac{\pi}{6}"),
    (np.pi/4, r"\frac{\pi}{4}"),
    (np.pi/3, r"\frac{\pi}{3}"),
    (np.pi/2, r"\frac{\pi}{2}"),
    (2*np.pi/3, r"\frac{2\pi}{3}"),
    (3*np.pi/4, r"\frac{3\pi}{4}"),
    (5*np.pi/6, r"\frac{5\pi}{6}"),
    (np.pi, r"\pi"),
    (3*np.pi/2, r"\frac{3\pi}{2}")
]

# -------------------------------
# 2. 정답 테이블 (LaTeX 문자열 통일)
# -------------------------------
SPECIAL = {
    "sin": {
        0: r"0",
        np.pi/6: r"1/2",
        np.pi/4: r"\sqrt{2}/2",
        np.pi/3: r"\sqrt{3}/2",
        np.pi/2: r"1",
        2*np.pi/3: r"\sqrt{3}/2",
        3*np.pi/4: r"\sqrt{2}/2",
        5*np.pi/6: r"1/2",
        np.pi: r"0",
        3*np.pi/2: r"-1"
    },
    "cos": {
        0: r"1",
        np.pi/6: r"\sqrt{3}/2",
        np.pi/4: r"\sqrt{2}/2",
        np.pi/3: r"1/2",
        np.pi/2: r"0",
        2*np.pi/3: r"-1/2",
        3*np.pi/4: r"-\sqrt{2}/2",
        5*np.pi/6: r"-\sqrt{3}/2",
        np.pi: r"-1",
        3*np.pi/2: r"0"
    },
    "tan": {
        0: r"0",
        np.pi/6: r"\sqrt{3}/3",
        np.pi/4: r"1",
        np.pi/3: r"\sqrt{3}",
        2*np.pi/3: r"-\sqrt{3}",
        3*np.pi/4: r"-1",
        5*np.pi/6: r"-\sqrt{3}/3",
        np.pi: r"0"
    }
}

# -------------------------------
# 3. 선택지 풀 (Distractor 후보군)
# -------------------------------
CHOICES_POOL = {
    "sin": [r"0", r"1/2", r"-1/2", r"\sqrt{2}/2", r"-\sqrt{2}/2", r"\sqrt{3}/2", r"-\sqrt{3}/2", r"1", r"-1"],
    "cos": [r"0", r"1/2", r"-1/2", r"\sqrt{2}/2", r"-\sqrt{2}/2", r"\sqrt{3}/2", r"-\sqrt{3}/2", r"1", r"-1"],
    "tan": [r"0", r"1", r"-1", r"\sqrt{3}", r"-\sqrt{3}", r"\sqrt{3}/3", r"-\sqrt{3}/3"]
}

# -------------------------------
# 4. 사분면 판별
# -------------------------------
def get_quadrant(angle):
    angle = angle % (2*np.pi)
    if 0 < angle < np.pi/2: return 1
    if np.pi/2 < angle < np.pi: return 2
    if np.pi < angle < 3*np.pi/2: return 3
    if 3*np.pi/2 < angle < 2*np.pi: return 4
    return 0

# -------------------------------
# 5. 오답 생성 (하이브리드 안정형)
# -------------------------------
def generate_distractors(func, angle, correct):
    pool = set(CHOICES_POOL[func])
    distractors = set()

    # (1) 부호 오류
    if correct != r"0":
        sign_error = correct[1:] if correct.startswith("-") else "-" + correct
        distractors.add(sign_error)

    # (2) sin-cos 혼동
    if func in ["sin", "cos"]:
        other_func = "cos" if func == "sin" else "sin"
        if angle in SPECIAL[other_func]:
            distractors.add(SPECIAL[other_func][angle])

    # (3) tan 역수 혼동
    if correct == r"\sqrt{3}":
        distractors.add(r"\sqrt{3}/3")
    elif correct == r"\sqrt{3}/3":
        distractors.add(r"\sqrt{3}")

    # 정답 제거
    distractors.discard(correct)

    # (4) 부족 채우기 → 항상 4개 보장
    pool_without_correct = list(pool - {correct})
    while len(distractors) < 4:
        distractors.add(random.choice(pool_without_correct))

    return list(distractors)

# -------------------------------
# 6. 문제 생성
# -------------------------------
def generate_quiz():
    while True:
        func = random.choice(["sin", "cos", "tan"])
        angle_val, angle_latex = random.choice(ANGLES)

        # tan 정의되지 않는 각도 skip
        if func == "tan" and angle_val not in SPECIAL["tan"]:
            continue
        break

    correct = SPECIAL[func][angle_val]
    distractors = generate_distractors(func, angle_val, correct)

    # 정답 위치 랜덤 삽입
    answer_index = random.randint(0, 4)
    choices = distractors.copy()
    choices.insert(answer_index, correct)

    return {
        "latex_question": rf"\{func}\left({angle_latex}\right)",
        "latex_answer": correct,
        "choices": choices,
        "answer_index": answer_index,
        "meta": {
            "func": func,
            "angle": angle_val,
            "quadrant": get_quadrant(angle_val)
        }
    }

# -------------------------------
# 7. 오답 유형 분류
# -------------------------------
def classify_error(user_ans, correct_ans, func, angle):
    # 부호 오류
    if user_ans.replace("-", "") == correct_ans.replace("-", ""):
        return "sign_error"

    # sin-cos 혼동
    if func in ["sin", "cos"]:
        other_func = "cos" if func == "sin" else "sin"
        if angle in SPECIAL[other_func] and user_ans == SPECIAL[other_func][angle]:
            return "func_confusion"

    # tan 역수 오류
    if (correct_ans == r"\sqrt{3}" and user_ans == r"\sqrt{3}/3") or \
       (correct_ans == r"\sqrt{3}/3" and user_ans == r"\sqrt{3}"):
        return "tan_inverse_error"

    # 그 외 → 계산 실수
    return "calculation_error"

# -------------------------------
# 8. 사용자 통계 업데이트
# -------------------------------
def update_user_stats(user_stats, error_type):
    if error_type not in user_stats:
        user_stats[error_type] = 0
    user_stats[error_type] += 1
