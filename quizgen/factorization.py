import random
from sympy import symbols, expand, latex, Rational, factor, simplify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# 변수 정의
x, y, a, b = symbols('x y a b')
variables = [x, a, b]

transformations = (standard_transformations + (implicit_multiplication_application,))
allowed = {"x": x, "y": y, "a": a, "b": b}

def get_coeff():
    if random.random() < 0.3:
        return Rational(random.randint(1, 3), random.randint(2, 4))
    return random.randint(1, 5)

# -------------------------------
# 1. 완전제곱식 인수분해 문제
# -------------------------------
def generate_factor_square_binomial():
    var = random.choice(variables)
    c1 = get_coeff()
    c2 = get_coeff()
    expr = (c1*var + c2)**2
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),  # 문제: 전개된 다항식
        "answer_obj": expr,                 # 정답: 인수분해된 꼴
        "latex_answer": latex(expr),
        "expanded_obj": expanded            # 채점용
    }

# -------------------------------
# 2. 합차공식 인수분해 문제
# -------------------------------
def generate_factor_diff_of_squares():
    var = random.choice(variables)
    c1 = get_coeff()
    expr = (var + c1)*(var - c1)
    expanded = expand(expr)
    return {
        "latex_question": latex(expanded),  # 문제: 전개된 다항식
        "answer_obj": expr,                 # 정답: 인수분해된 꼴
        "latex_answer": latex(expr),
        "expanded_obj": expanded
    }

# -------------------------------
# 채점 로직 (인수분해용, 강화된 버전)
# -------------------------------
def check_factor_answer(user_input_str, expanded_expr):
    try:
        processed_input = user_input_str.replace('^', '**')
        user_expr = parse_expr(processed_input,
                               transformations=transformations,
                               local_dict=allowed,
                               global_dict={},
                               evaluate=True)

        # 문제 외 변수 차단
        if user_expr.free_symbols - expanded_expr.free_symbols:
            return False

        # 1. 학생 답안을 전개했을 때 문제와 같아야 함
        if expand(user_expr) != expanded_expr:
            return False

        # 2. 학생 답안이 전개된 꼴이면 오답 처리 (곱셈 구조가 남아 있어야 함)
        if user_expr == expand(user_expr):
            return False

        # 3. 표준 인수분해 형태와 비교
        if simplify(user_expr - factor(expanded_expr)) == 0:
            return True

        return False
    except Exception:
        return False

# -------------------------------
# 테스트 실행
# -------------------------------
if __name__ == "__main__":
    print("=== 완전제곱식 인수분해 문제 ===")
    sq_problem = generate_factor_square_binomial()
    print("문제:", sq_problem["latex_question"])
    print("정답:", sq_problem["latex_answer"])
    print("채점 결과:", check_factor_answer("(5*x+3)^2", sq_problem["expanded_obj"]))

    print("\n=== 합차공식 인수분해 문제 ===")
    ds_problem = generate_factor_diff_of_squares()
    print("문제:", ds_problem["latex_question"])
    print("정답:", ds_problem["latex_answer"])
    print("채점 결과:", check_factor_answer("(a-4)*(a+4)", ds_problem["expanded_obj"]))
