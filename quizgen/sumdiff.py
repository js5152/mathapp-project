import random
from sympy import symbols, expand, latex, Rational
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# 사용할 변수 후보
x, y, a, b = symbols('x y a b')
variables = [x, a, b, (x, y)]  # 1개 또는 2개 변수

# 변환 옵션 (4x → 4*x 같은 암묵적 곱셈 허용)
transformations = (standard_transformations + (implicit_multiplication_application,))

# 허용 변수 딕셔너리 (학생 답안 검증용)
allowed = {"x": x, "y": y, "a": a, "b": b}

def get_coeff():
    """계수: 정수 또는 분수(Rational)"""
    if random.random() < 0.3:  # 30% 확률로 분수
        return Rational(random.randint(1, 3), random.randint(2, 4))
    return random.randint(1, 5)

# -------------------------------
# 1번 공식: 완전제곱식 (a±b)^2
# -------------------------------
def generate_square_binomial():
    var = random.choice(variables)
    c1 = get_coeff()
    c2 = get_coeff() * random.choice([1, -1])  # ± 부호 랜덤
    
    if isinstance(var, tuple):  # 변수가 2개인 경우
        base = c1*var[0] + c2*var[1]
    else:
        base = c1*var + c2
    
    expr = base**2
    
    return {
        "latex_question": latex(expr),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr))
    }

# -------------------------------
# 2번 공식: 합차공식 (a+b)(a-b)
# -------------------------------
def generate_diff_of_squares():
    var = random.choice(variables)
    c1 = get_coeff()
    c2 = get_coeff()
    
    if isinstance(var, tuple):
        base1 = c1*var[0]
        base2 = c2*var[1]
    else:
        base1 = c1*var
        base2 = c2
    
    expr = (base1 + base2) * (base1 - base2)
    
    return {
        "latex_question": latex((base1 + base2) * (base1 - base2)),
        "answer_obj": expand(expr),
        "latex_answer": latex(expand(expr))
    }

# -------------------------------
# 채점 로직 (개선된 버전)
# -------------------------------
def check_answer(user_input_str, answer_obj):
    try:
        processed_input = user_input_str.replace('^', '**')
        user_expr = parse_expr(processed_input,
                               transformations=transformations,
                               local_dict=allowed,
                               global_dict={},   # 안전성 강화
                               evaluate=True)
        
        # 1. 문제 외 변수 차단
        if user_expr.free_symbols - answer_obj.free_symbols:
            return False
        
        # 2. 전개 여부 확인 (구조 비교)
        if user_expr != expand(user_expr):
            return False
        
        # 3. 정답 비교 (expand 기반)
        return expand(user_expr - answer_obj) == 0
    except Exception:
        return False

# -------------------------------
# 테스트 실행
# -------------------------------
if __name__ == "__main__":
    print("=== 완전제곱식 문제 ===")
    sq_problem = generate_square_binomial()
    print("문제:", sq_problem["latex_question"])
    print("정답:", sq_problem["latex_answer"])
    print("채점 결과:", check_answer("4x^2 + 4x + 1", sq_problem["answer_obj"]))
    
    print("\n=== 합차공식 문제 ===")
    ds_problem = generate_diff_of_squares()
    print("문제:", ds_problem["latex_question"])
    print("정답:", ds_problem["latex_answer"])
    print("채점 결과:", check_answer("x^2 - 9", ds_problem["answer_obj"]))
