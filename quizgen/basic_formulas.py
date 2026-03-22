import random
from sympy import symbols, expand, latex, Rational, factor, simplify, Integer, Symbol, Number  # 👈 Symbol, Number 추가
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# -------------------------------
# 기본 설정
# -------------------------------
x, y, z, a, b, c = symbols('x y z a b c')
variables = [x, a, b]


transformations = standard_transformations + (implicit_multiplication_application,)

# 🚩 채점 시 필요한 단어장에 Symbol과 Number를 추가합니다.
allowed = {
    "x": x, "y": y, "a": a, "b": b, 
    "Integer": Integer, 
    "Symbol": Symbol, 
    "Number": Number
}


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
    while len(choices) < 5:
        choices.add(latex(simplify(correct_obj + random.randint(2, 10))))

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
    a_val = random.randint(1, 15)
    b_val = random.randint(1, 15)
    expr = (x + a_val) * (x + b_val)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr)),
        "choices": generate_choices(expanded)
    }

def generate_type3_factorization():
    a_val = random.randint(1, 15)
    b_val = random.randint(1, 15)
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
    a_val = random.randint(1, 12)
    b_val = random.randint(1, 12)
    c_val = random.randint(1, 12)
    d_val = random.randint(1, 12)
    expr = (a_val*x + b_val) * (c_val*x + d_val)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr)),
        "choices": generate_choices(expanded)
    }

def generate_type4_factorization():
    a_val = random.randint(1, 10)
    b_val = random.randint(1, 10)
    c_val = random.randint(1, 10)
    d_val = random.randint(1, 10)
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
# 5. 삼차식 공식 (a+b)^3 및 (a-b)^3
# -------------------------------
def generate_type5_expansion():
    # 1. 변수와 숫자 범위를 넉넉하게 잡습니다. (중복 확률을 수학적으로 낮춤)
    var = random.choice([x, y, a, b]) # 변수를 4개로 늘림
    a_val = random.randint(1, 15)      # 숫자를 1~15로 늘림
    sign = random.choice([1, -1])
    
    expr = (var + sign * a_val)**3
    expanded = expand(expr)
    
    return {
        "latex_question": latex(expr),
        "answer_obj": expanded,
        "latex_answer": latex(expanded),
        "choices": generate_choices(expanded)
    }



# ------------------------------
# 5. 삼차식 공식 인수분해
# -------------------------------
def generate_type5_factorization():
    """(x±a)^3 인수분해 문제 (심플 & 랜덤 버전)"""
    # 1. 변수와 숫자 범위를 넉넉하게 잡아서 중복 확률을 낮춤
    var = random.choice([x, y, a, b]) 
    a_val = random.randint(1, 15) # 범위를 1~15로 확대
    sign = random.choice([1, -1])
    
    # (x + 3)^3 같은 인수분해된 형태가 실제 '정답' 객체가 됨
    expr = (var + sign * a_val)**3
    
    # 문제를 위해 전개된 식을 미리 계산
    expanded = expand(expr)

    return {
        "latex_question": latex(expanded), # 문제: x^3 + 9x^2 + 27x + 27
        "answer_obj": expr,                # 정답 객체: (x + 3)^3
        "latex_answer": latex(expr),       # 정답 텍스트
        "expanded_obj": expanded,
        "choices": generate_choices(expr)  # 객체를 넘겨서 오답 생성
    }

def generate_type6_expansion():
    """(x + a)(x^2 - ax + a^2) = x^3 + a^3 형태 문제 생성"""
    var = random.choice([x, a, b])
    a_val = random.randint(1, 10)
    
    if random.random() < 0.5:
        # x^3 + a^3 공식
        expr = (var + a_val) * (var**2 - a_val*var + a_val**2)
    else:
        # x^3 - a^3 공식
        expr = (var - a_val) * (var**2 + a_val*var + a_val**2)
        
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expanded,
        "latex_answer": latex(expanded),
        "choices": generate_choices(expanded)
    }
# -------------------------------
# 6. 삼차식(합차변형) 인수분해
# -------------------------------
def generate_type6_factorization():
    """x^3 + a^3 -> (x + a)(x^2 - ax + a^2) 인수분해"""
    var = random.choice([x, a, b])
    a_val = random.randint(1, 10)
    if random.random() < 0.5:
        expr = (var + a_val) * (var**2 - a_val*var + a_val**2)
    else:
        expr = (var - a_val) * (var**2 + a_val*var + a_val**2)
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# -------------------------------
# 7. 추가 공식 
# -------------------------------

# 5번 공식: (a+b+c)^2
def generate_type7_expansion():
    """(a + b + c)^2 변형 전개 (숫자 포함)"""
    # 1에서 5 사이의 랜덤한 숫자 3개를 뽑습니다.
    # 만약 문자로만 하고 싶으시면 이 단계를 건너뛰지만, 보통 문제는 숫자가 섞여야 제맛이죠!
    v = [random.randint(1, 10) for _ in range(3)]
    
    # 예: (x + 2y + 3z)^2 같은 느낌으로 만들려면
    expr = (v[0]*x + v[1]*y + v[2]*z)**2 
    
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expanded,
        "latex_answer": latex(expanded),
        "choices": generate_choices(expanded)
    }

def generate_type7_factorization():
    """a^2+b^2+c^2+2ab+2bc+2ca -> (a+b+c)^2 인수분해"""
    # 숫자가 너무 크면 계산하기 힘드니 1~4 정도로 섞어줍니다.
    v = random.sample(range(1, 10), 3) 
    
    # (x + 2y + 3z)^2 같은 형태를 만듭니다.
    # 문자를 x, y, z로 고정하거나 강사님 스타일대로 섞으시면 됩니다.
    expr = (v[0]*x + v[1]*y + v[2]*z)**2 
    expanded = expand(expr)
    
    return {
        "latex_question": latex(expanded), # 펼쳐진 식을 문제로!
        "answer_obj": expr,
        "latex_answer": latex(expr),       # 묶인 식을 정답으로!
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# -------------------------------
# 8. (x+a)(x+b)(x+c) 전개 및 인수분해
# -------------------------------

def generate_type8_expansion():
    """(x+a)(x+b)(x+c) 전개 (중복 없는 숫자)"""
    pool = [i for i in range(-5, 6) if i != 0]
    vals = random.sample(pool, 3)
    
    expr = (x + vals[0]) * (x + vals[1]) * (x + vals[2])
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expanded,
        "latex_answer": latex(expanded),
        "choices": generate_choices(expanded)
    }

def generate_type8_factorization():
    """음수가 섞인 (x+a)(x+b)(x+c) 인수분해"""
    pool = [i for i in range(-5, 6) if i != 0]
    vals = random.sample(pool, 3)
    
    expr = (x + vals[0]) * (x + vals[1]) * (x + vals[2])
    expanded = expand(expr)
    
    return {
        "latex_question": latex(expanded),
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }

# 9번 공식: (a^2+ab+b^2)(a^2-ab+b^2) -> 숫자를 넣어 변형!
def generate_type9_expansion():
    """a^4 + a^2b^2 + b^4 형태 변형 (계수 추가)"""
    k = random.randint(1, 6) # 계수를 랜덤하게!
    # (a^2 + kab + k^2b^2)(a^2 - kab + k^2b^2)
    expr = (a**2 + k*a*b + (k**2)*b**2) * (a**2 - k*a*b + (k**2)*b**2)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expanded,
        "latex_answer": latex(expanded),
        "choices": generate_choices(expanded)
    }


# -------------------------------
# 9. 복이차식 꼴 인수분해 (계수 랜덤)
# -------------------------------
def generate_type9_factorization():
    """a^4 + k^2*a^2b^2 + k^4*b^4 -> (a^2+kab+k^2b^2)(a^2-kab+k^2b^2)"""
    k = random.randint(1, 6) # 숫자가 너무 크면 계산이 힘드니 1~4 권장
    
    # 인수분해된 형태 (정답)
    expr = (a**2 + k*a*b + (k**2)*b**2) * (a**2 - k*a*b + (k**2)*b**2)
    expanded = expand(expr)
    
    return {
        "latex_question": latex(expanded), # 문제: a^4 + k^2*a^2*b^2 + k^4*b^4
        "answer_obj": expr,
        "latex_answer": latex(expr),
        "expanded_obj": expanded,
        "choices": generate_choices(expr)
    }


# 10번 공식: (a+b+c)(a^2+b^2+c^2-ab-bc-ca)=a^3+b^3+c^3-3abc -> 변수나 상수를 살짝 변형!
def generate_type10_expansion():
    """(a+b+c)(a^2+b^2+c^2-ab-bc-ca) 변형"""
    # 단순 a, b, c 대신 x, y, 상수 하나를 섞어봅시다.
    k = random.randint(1, 5) 
    expr = (x + y + k) * (x**2 + y**2 + k**2 - x*y - y*k - k*x)
    expanded = expand(expr)
    return {
        "latex_question": latex(expr),
        "answer_obj": expanded,
        "latex_answer": latex(expanded),
        "choices": generate_choices(expanded)
    }

# -------------------------------
# 10. 세 항의 삼차공식 인수분해 (상수 랜덤)
# -------------------------------
def generate_type10_factorization():
    """a^3+b^3+k^3-3abk -> (a+b+k)(a^2+b^2+k^2-ab-bk-ka)"""
    k = random.randint(1, 5) # 변수 c 대신 상수 k를 섞어주면 더 실전 같습니다.
    
    # 인수분해된 형태 (정답)
    expr = (a + b + k) * (a**2 + b**2 + k**2 - a*b - b*k - k*a)
    expanded = expand(expr)
    
    return {
        "latex_question": latex(expanded), # 문제: a^3 + b^3 + k^3 - 3abk 가 전개된 식
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

