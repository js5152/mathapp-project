from manim import *

# (a+b)^2 전체 흐름 관리자
class SquareExpansionAll(Scene):
    def construct(self):
        self.part1_symbolic()
        self.clear()
        self.part2_area()
        self.clear()
        self.part3_circle_copy()

    # ----------------------------
    # Part 1: 기호 전개 연출
    # ----------------------------
    def part1_symbolic(self):
    # 1. (a+b)^2 등장
        expr = MathTex("(a+b)^2", font_size=96)
        self.play(Write(expr))
        self.wait(0.5)

    # 2. 작아지며 위로
        self.play(expr.animate.scale(0.5).to_edge(UP))
        self.wait(0.3)
  
    # -------------------
    # a 두 번 바운스 → a^2
    # -------------------
        a1 = expr[0][1]  # 첫 a
        a2 = expr[0][3]  # 두 번째 a

        for _ in range(2):
            self.play(a1.animate.scale(1.3), a2.animate.scale(1.3), run_time=0.15)
            self.play(a1.animate.scale(1/1.3), a2.animate.scale(1/1.3), run_time=0.15)

        a_sq = MathTex("a^2").move_to(DOWN*1.5 + LEFT*3)
        self.play(FadeIn(a_sq, shift=DOWN))
        self.wait(0.3)

    # -------------------
    # 2, a, b 순서 바운스 → 2ab
    # -------------------
        two = MathTex("2").move_to(expr.get_center() + LEFT*0.3)
        a_mid = a1.copy()
        b_mid = expr[0][5]

        for obj in [two, a_mid, b_mid]:
            self.play(obj.animate.scale(1.3), run_time=0.15)
            self.play(obj.animate.scale(1/1.3), run_time=0.15)

        twoab = MathTex("+2ab").next_to(a_sq, RIGHT, buff=0.8)
        self.play(FadeIn(twoab, shift=DOWN))
        self.wait(0.3)

    # -------------------
    # b 두 번 바운스 → b^2
    # -------------------
        b1 = expr[0][5]

        for _ in range(2):
            self.play(b1.animate.scale(1.3), run_time=0.15)
            self.play(b1.animate.scale(1/1.3), run_time=0.15)

        b_sq = MathTex("+b^2").next_to(twoab, RIGHT, buff=0.8)
        self.play(FadeIn(b_sq, shift=DOWN))
        self.wait(1)
    # ----------------------------
    # Part 2: 도형 넓이 분해
    # ----------------------------
    def part2_area(self):
        title = Text("Part 2: 도형으로 보기", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # 👉 다음 단계에서 여기 채움
        square = Square()
        self.play(Create(square))
        self.wait(2)
        self.play(FadeOut(square))

    # ----------------------------
    # Part 3: 원 + 복사 연출
    # ----------------------------
    def part3_circle_copy(self):
        title = Text("Part 3: 복사로 만들기", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # 👉 다음 단계에서 여기 채움
        c = Circle()
        self.play(Create(c))
        self.wait(2)
        self.play(FadeOut(c))