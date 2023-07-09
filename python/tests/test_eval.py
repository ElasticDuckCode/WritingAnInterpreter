from unittest import main, TestCase
from src.monkey import lexer, parser, obj, eval, env


class TestEval(TestCase):

    def verify_eval(self, code: str) -> obj.Object:
        e = env.Environment()
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        return eval.eval(program, e)

    def verify_integer_obj(self, o: obj.Integer, expect: int):
        self.assertIsInstance(o, obj.Integer)
        self.assertEqual(o.value, expect)

    def verify_boolean_obj(self, o: obj.Boolean, expect: bool):
        self.assertIsInstance(o, obj.Boolean)
        self.assertEqual(o.value, expect)

    def verify_string_obj(self, o: obj.String, expect: str):
        self.assertIsInstance(o, obj.String)
        self.assertEqual(o.value, expect)

    def verify_null_obj(self, o: obj.Null):
        self.assertEqual(o, obj.NULL)

    def test_eval_integer(self):
        cases = [
            ("5", 5),
            ("10", 10),
            ("-5", -5),
            ("-10", -10),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("-50 + 100 + -50", 0),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("20 + 2 * -10", 0),
            ("50 / 2 * 2 + 10", 60),
            ("2 * (5 + 10)", 30),
            ("3 * 3 * 3 + 10", 37),
            ("3 * (3 * 3) + 10", 37),
            ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50)
        ]
        for code, expect in cases:
            self.verify_integer_obj(self.verify_eval(code), expect)

    def test_eval_boolean(self):
        cases = [
            ("true", True),
            ("false", False),
            ("1 < 2", True),
            ("1 > 2", False),
            ("1 < 1", False),
            ("1 > 1", False),
            ("1 == 1", True),
            ("1 != 1", False),
            ("1 == 2", False),
            ("1 != 2", True),
            ("true == true", True),
            ("false == false", True),
            ("true == false", False),
            ("true != false", True),
            ("false != true", True),
            ("(1 < 2) == true", True),
            ("(1 < 2) == false", False),
            ("(1 > 2) == true", False),
            ("(1 > 2) == false", True),
        ]
        for code, expect in cases:
            self.verify_boolean_obj(self.verify_eval(code), expect)

    def test_eval_string(self):
        cases = [
            (r'"hello world";', "hello world"),
            (r'"hello\n world";', "hello\n world"),
            (r'"hello\n\t world\"";', "hello\n\t world\""),
        ]
        for code, expect in cases:
            self.verify_string_obj(self.verify_eval(code), expect)

    def test_eval_bang_operator(self):
        cases = (
            ("!true", False),
            ("!false", True),
            ("!5", False),
            ("!!true", True),
            ("!!false", False),
            ("!!5", True),
        )
        for code, expect in cases:
            self.verify_boolean_obj(self.verify_eval(code), expect)

    def test_eval_if_else_expressions(self):
        cases = (
            ("if (true) { 10 }", 10),
            ("if (false) { 10 }", None),
            ("if (1) { 10 }", 10),
            ("if (1 < 2) { 10 }", 10),
            ("if (1 > 2) { 10 }", None),
            ("if (1 < 2) { 10 } else { 20 }", 10),
            ("if (1 > 2) { 10 } else { 20 }", 20),
        )
        for code, expect in cases:
            o = self.verify_eval(code)
            if expect is not None:
                self.verify_integer_obj(o, expect)
            else:
                self.verify_null_obj(o)

    def test_eval_return_statement(self):
        cases = (
            ("return 10;", 10),
            ("return 10; 9;", 10),
            ("return 2 * 5; 9;", 10),
            ("9; return 2 * 5; 9;", 10),
            ("if (10 > 1) {\
                if (10 > 1) {\
                    return 10;\
                }\
                return 1;\
              }", 10)
        )
        for code, expect in cases:
            self.verify_integer_obj(self.verify_eval(code), expect)

    def test_eval_let_statements(self):
        cases = (
            ("let a = 5; a;", 5),
            ("let a = 5 * 5; a;", 25),
            ("let a = 5; let b = a; b;", 5),
            ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
        )
        for code, expect in cases:
            self.verify_integer_obj(self.verify_eval(code), expect)

    def test_eval_error_handling(self):
        cases = (
            ("5 + true;", "type mismatch: INTEGER + BOOLEAN"),
            ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"),
            ("-true;", "unknown operator: -BOOLEAN"),
            ("true + false;", "unknown operator: BOOLEAN + BOOLEAN"),
            ("5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN"),
            ("if (10 > 1) { true + false; }",
             "unknown operator: BOOLEAN + BOOLEAN"),
            ("if (10 > 1) {\
                if (10 > 1) {\
                    return true + false;\
                }\
                return 1;\
              }", "unknown operator: BOOLEAN + BOOLEAN"),
            ("foobar;", "identifier not found: foobar"),
            ('"hello" - "world";', "unknown operator: STRING - STRING")
        )
        for code, expect in cases:
            o = self.verify_eval(code)
            self.assertIsInstance(o, obj.Error)
            self.assertEqual(o.message, expect)

    def test_eval_function_define(self):
        code = "fn(x) { x + 2; };"
        evaluated = self.verify_eval(code)
        self.assertIsInstance(evaluated, obj.Function)
        self.assertEqual(len(evaluated.parameters), 1)
        self.assertEqual(evaluated.parameters[0].string, "x")
        self.assertEqual(evaluated.body.string, "(x + 2)")

    def test_eval_function_call(self):
        cases = (
            ("let identity = fn(x) { x; }; identity(5);", 5),
            ("let identity = fn(x) { return x; }; identity(5);", 5),
            ("let double = fn(x) { x * 2; }; double(5);", 10),
            ("let add = fn(x,y) { x + y; }; add(5,5);", 10),
            ("let add = fn(x,y) { x + y; }; add(5 + 5, add(5, 5));", 20),
            ("fn(x) { x; }(5);", 5),
        )
        for code, expect in cases:
            self.verify_integer_obj(self.verify_eval(code), expect)

    def test_eval_closures(self):
        code = """\
        let newAdder = fn(x) {\
            fn(y) { x + y };\
        }\
        let addTwo = newAdder(2);\
        addTwo(2);\
        """
        self.verify_integer_obj(self.verify_eval(code), 4)

    def test_eval_string_concat(self):
        code = r"""
        let x = "hello";
        let y = "world";
        x + " " + y;
        """
        self.verify_string_obj(self.verify_eval(code), "hello world")
