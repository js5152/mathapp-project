import random
from sympy import symbols, expand, latex, Rational, factor, simplify, Integer
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# -------------------------------
# 기본 설정
# -------------------------------
x, y, a, b = symbols('x y a b')
variables = [x, a, b]

transformations = standard_transformations + (implicit_multiplication_application,)
allowed = {"x": x, "y": y, "a": a, "b": b, "Integer": Integer}

# -------------------------------
# 입력 정규화
# -------------------------------
def normalize_input(s: str) -> str:
    return (s.replace("−", "-")   # 유니코드 마이너스
              .replace("–", "-")
              .replace("×", "*")
              .replace("·", "*")
              .replace("^", "**")
              .replace(" ", ""))

# -------------------------------
# 계수 생성
# -------------------------------
def get_coeff():
    if random.random() < 0.3:
        return Rational(random.randint(1, 3), random.randint(2, 4))
    return random.randint(1, 5)

def generate_choices(correct_obj):
    """정답 객체를 받아 LaTeX 형태의 선택지 4개를 반환 (정답 1 + 오답 3)"""
    choices = set()
    correct_latex = latex(correct_obj)
    choices.add(correct_latex)
    
    # 오답 생성 로직 (정답과 비슷하게 변형)
    # 1. 부호 반전 (+를 -로, -를 +로)
    try:
        # 식 안의 모든 숫자 부호를 뒤집어보는 시도
        distractor1 = latex(simplify(correct_obj * -1))
        choices.add(distractor1)
    except: pass

    # 2. 상수항이나 계수 살짝 바꾸기
    # 단순하게 정답 문자열에서 +를 -로, -를 +로 바꿔서 오답 생성
    s_correct = latex(correct_obj)
    distractor2 = s_correct.replace('+', 'tmp').replace('-', '+').replace('tmp', '-')
    choices.add(distractor2)
    
    # 3. 제곱을 빼먹거나 계수를 1씩 더해보기 (랜덤 변형)
    distractor3 = latex(simplify(correct_obj + 1))
    choices.add(distractor3)

    # 4. 부족한 오답 채우기 (4개가 될 때까지)
    while len(choices) < 4:
        choices.add(latex(simplify(correct_obj + random.randint(2, 5))))

    final_choices = list(choices)
    random.shuffle(final_choices) # 순서 섞기
    return final_choices


# -------------------------------
# 1. 완전제곱식
# -------------------------------
def generate_type1_expansion():
    var = random.choice(variables)
    c1 = get_coeff()
    c2 = get_coeff()
    expr = (c1*var + c2)**2
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr)),
        "choices": generate_choices(expanded) 
    }

def generate_type1_factorization():
    var = random.choice(variables)
    c1 = get_coeff()
    c2 = get_coeff()
    expr = (c1*var + c2)**2
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# -------------------------------
# 2. 합차공식
# -------------------------------
def generate_type2_expansion():
    var = random.choice(variables)
    c1 = get_coeff()
    expr = (var + c1)*(var - c1)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr)),
        "choices": generate_choices(expanded)
    }

def generate_type2_factorization():
    var = random.choice(variables)
    c1 = get_coeff()
    expr = (var + c1)*(var - c1)
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# -------------------------------
# 3. (x+a)(x+b)
# -------------------------------
def generate_type3_expansion():
    a_val = random.randint(1, 5)
    b_val = random.randint(1, 5)
    expr = (x + a_val) * (x + b_val)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr)),
        "choices": generate_choices(expanded)
    }

def generate_type3_factorization():
    a_val = random.randint(1, 5)
    b_val = random.randint(1, 5)
    expr = (x + a_val) * (x + b_val)
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# -------------------------------
# 4. (ax+b)(cx+d)
# -------------------------------
def generate_type4_expansion():
    a_val = random.randint(1, 5)
    b_val = random.randint(1, 5)
    c_val = random.randint(1, 5)
    d_val = random.randint(1, 5)
    expr = (a_val*x + b_val) * (c_val*x + d_val)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr)),
        "choices": generate_choices(expanded)
    }

def generate_type4_factorization():
    a_val = random.randint(1, 5)
    b_val = random.randint(1, 5)
    c_val = random.randint(1, 5)
    d_val = random.randint(1, 5)
    expr = (a_val*x + b_val) * (c_val*x + d_val)
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# -------------------------------
# 채점 로직
# -------------------------------
def check_expansion_answer(user_input_str, answer_obj):
    try:
        processed_input = normalize_input(user_input_str)
        user_expr = parse_expr(
            processed_input,
            transformations=transformations,
            local_dict=allowed,
            global_dict={},
            evaluate=True
        )
        if user_expr.free_symbols - answer_obj.free_symbols:
            return False
        return user_expr.equals(answer_obj)
    except Exception as e:
        print("채점 에러:", e)
        return False

def check_factor_answer(user_input_str, expanded_expr):
    try:
        processed_input = normalize_input(user_input_str)
        user_expr = parse_expr(
            processed_input,
            transformations=transformations,
            local_dict=allowed,
            global_dict={},
            evaluate=True
        )
        if user_expr.free_symbols - expanded_expr.free_symbols:
            return False
        correct = factor(expanded_expr)
        return user_expr.equals(correct)
    except Exception as e:
        print("채점 에러:", e)
        return False

# -------------------------------
# 로컬 테스트
# -------------------------------
if __name__ == "__main__":
    expr = (b - 3)*(b + 3)
    ans = expand(expr)

    print("정답:", ans)
    print(check_expansion_answer("b^2-9", ans))    # True
    print(check_expansion_answer("b^2−9", ans))    # True
    print(check_expansion_answer("b*b-9", ans))    # True
