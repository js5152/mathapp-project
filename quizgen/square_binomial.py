import random
from sympy import symbols, expand, latex, Rational, simplify
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

def generate_square_binomial():
    """완전제곱식 문제 생성"""
    var = random.choice(variables)
    c1 = get_coeff()
    c2 = get_coeff() * random.choice([1, -1])  # ± 부호 랜덤
    
    if isinstance(var, tuple):  # 변수가 2개인 경우 (예: x, y)
        base = c1*var[0] + c2*var[1]
    else:  # 변수가 1개인 경우
        base = c1*var + c2
    
    expr = base**2
    
    return {
        "latex_question": latex(expr),             # 문제 표시용
        "answer_obj": expand(expr),                # 채점용 객체
        "latex_answer": latex(expand(expr))        # 정답 표시용
    }

def check_answer(user_input_str, answer_obj):
    """학생 답안 채점"""
    try:
        # ^ → ** 변환
        processed_input = user_input_str.replace('^', '**')
        # 문자열을 sympy 수식으로 파싱 (허용 변수만 사용)
        user_expr = parse_expr(processed_input,
                               transformations=transformations,
                               local_dict=allowed,
                               evaluate=True)
        
        # 1. 문제에 없는 변수를 쓰면 오답 처리
        if user_expr.free_symbols - answer_obj.free_symbols:
            return False
        
        # 2. 전개가 완벽히 안 된 경우 오답 처리
        if not user_expr.equals(expand(user_expr)):
            return False
        
        # 3. 정답과 동치인지 확인
        return simplify(user_expr - answer_obj) == 0
    except Exception:
        return False

# --- 테스트 ---
if __name__ == "__main__":
    problem = generate_square_binomial()
    print("문제:", problem["latex_question"])
    print("정답:", problem["latex_answer"])
    
    # 예시 답안 입력
    user_input = "4x^2 + 4x + 1"  # 학생이 입력한 답
    print("채점 결과:", check_answer(user_input, problem["answer_obj"]))
