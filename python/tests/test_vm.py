from typing import Any, cast
from unittest import TestCase

from src.monkey import ast, compiler, lexer, obj, parser, vm


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestVirtualMachine(TestCase):
    def verify_vm_case(self, src_code: str, expected: Any):
        program = parse(src_code)
        comp = compiler.Compiler()
        comp.compile(program)
        virt = vm.VirtualMachine(comp.bytecode)
        virt.run()
        self.assertIsNotNone(virt.last_popped)
        self.verify_expected_object(expected, virt.last_popped)

    def verify_expected_object(self, expected: Any, actual: obj.Object | None):
        match expected:
            case bool():
                self.assertIsInstance(actual, obj.Boolean)
                actual = cast(obj.Boolean, actual)
                self.assertEqual(expected, actual.value)
            case int():
                self.assertIsInstance(actual, obj.Integer)
                actual = cast(obj.Integer, actual)
                self.assertEqual(expected, actual.value)
            case str():
                self.assertIsInstance(actual, obj.String)
                actual = cast(obj.String, actual)
                self.assertEqual(expected, actual.value)
            case list():
                self.assertIsInstance(actual, obj.Array)
                actual = cast(obj.Array, actual)
                for e, a in zip(expected, actual.elements):
                    self.verify_expected_object(e, a)
            case dict():
                self.assertIsInstance(actual, obj.Hash)
                actual = cast(obj.Hash, actual)
                for e, a in zip(expected.keys(), actual.pairs.keys()):
                    self.verify_expected_object(e, a)
                for e, a in zip(expected.values(), actual.pairs.values()):
                    self.verify_expected_object(e, a)

            case None:
                self.assertIsInstance(actual, obj.Null)
                self.assertEqual(expected, None)
            case _:
                print(expected, actual, flush=True)
                self.assertEqual(True, False)

    def test_vm_integer_arithmetic(self):
        tests = (
            ("1", 1),
            ("2", 2),
            ("245", 245),
            ("1 + 2", 3),
            ("1 - 2", -1),
            ("1 * 2", 2),
            ("4 / 2", 2),
            ("50 / 2 * 2 + 10 - 5", 55),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("5 * (2 + 10)", 60),
            ("-1", -1),
            ("--1", 1),
            ("---1", -1),
            ("50 + -50", 0),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_boolean_expressions(self):
        tests = (
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
            ("true != true", False),
            ("true == false", False),
            ("true != false", True),
            ("false == false", True),
            ("(1 < 2) == true", True),
            ("(1 < 2) == false", False),
            ("(1 > 2) == true", False),
            ("(1 > 2) == false", True),
            ("!true", False),
            ("!!true", True),
            ("!false", True),
            ("!1", False),
            ("!(true == true)", False),
            ("!!(true == true)", True),
            ("!(if (false) { 5; })", True),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_conditionals(self):
        tests = (
            ("if (true) { 10; }", 10),
            ("if (false) { 10; }", None),
            ("if (true) { 10; } else { 20; }", 10),
            ("if (false) { 10; } else { 20; }", 20),
            ("if (1) { 10; }", 10),
            ("if (1 < 2) { 10; }", 10),
            ("if (1 < 2) { 10; } else { 20; }", 10),
            ("if (1 > 2) { 10; } else { 20; }", 20),
            ("if (null) { 10 } else { 20 }", 20),
            ("if ((if (false) { 10 })) { 10 } else { 20 }", 20),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_let_statements(self):
        tests = (
            ("let one = 1; one;", 1),
            ("let one = 1; let two = 2; one + two;", 3),
            ("let one = 1; let two = one + one; one + two;", 3),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_string_literals(self):
        tests = (
            ('"monkey"', "monkey"),
            ('"mon" + "key"', "monkey"),
            ('"mon" + "key" + "banana"', "monkeybanana"),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_array_literals(self):
        tests = (
            ("[]", []),
            ("[1, 2, 3]", [1, 2, 3]),
            ("[1 + 2, 3 * 4, 5 + 6]", [3, 12, 11]),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_hash_literals(self):
        tests = (
            ("{}", {}),
            ("{1: 2, 3: 4, 5: 6}", {1: 2, 3: 4, 5: 6}),
            ("{1: 2 + 3, 4: 5 * 6}", {1: 2 + 3, 4: 5 * 6}),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_index_expressions(self):
        tests = (
            ("[1, 2, 3][1]", 2),
            ("[1, 2, 3][0 + 2]", 3),
            ("[[1, 2, 3]][0][0]", 1),
            ("[][0]", None),
            ("[1, 2, 3][999]", None),
            ("[1, 2][-1]", 2),
            ("{1: 1, 2: 2}[1]", 1),
            ("{1: 1, 2: 2}[2]", 2),
            ("{1: 1}[0]", None),
            ("{}[0]", None),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_function_calls(self):
        tests = [
            [
                "let fivePlusTen = fn() { 5 + 10; }; fivePlusTen()",
                15,
            ],
            [
                """
                let one = fn() { 1; }
                let two = fn() { 2; }
                one() + two()
                """,
                3,
            ],
            [
                """
                let a = fn() { 1 };
                let b = fn() { a() + 1 };
                let c = fn() { b() + 1 };
                c();
                """,
                3,
            ],
            [
                """
                let earlyExit = fn() { return 99; 100; };
                earlyExit()
                """,
                99,
            ],
            [
                """
                let noVal = fn() { return; };
                noVal()
                """,
                None,
            ],
            [
                """
                let returnsOne = fn() { return 1; };
                let returnsOneRunner = fn() { return returnsOne;};
                returnsOneRunner()();
                """,
                1,
            ],
        ]
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_function_calls_with_bindings(self):
        tests = [
            # [
            #     """
            #     let one = fn() { let one = 1; one };
            #     one();
            #     """,
            #     1,
            # ],
            [
                """
                let oneAndTwo = fn() { let one = 1; let two = 2; one + two; };
                oneAndTwo();
                """,
                3,
            ],
            [
                """
                let oneAndTwo = fn() { let one = 1; let two = 2; one + two; };
                let threeAndFour = fn() { let three = 3; let four = 4; three + four; };
                oneAndTwo() + threeAndFour();
                """,
                10,
            ],
            [
                """
                let firstFoobar = fn() { let foobar = 50; foobar; }
                let secondFoobar = fn() { let foobar = 100; foobar; }
                firstFoobar() + secondFoobar()
                """,
                150,
            ],
            [
                """
                let globalSeed = 50,
                let minusOne = fn() {
                    let num = 1;
                    globalSeed - num;
                }
                let minusTwo = fn() {
                    let num = 2;
                    globalSeed - num;
                }
                minusOne() + minusTwo();
                """,
                97,
            ],
            [
                """
                let returnsOneRunner = fn() {
                    let returnsOne = fn() { 1; };
                    returnsOne;
                }
                returnsOneRunner()();
                """,
                1,
            ],
        ]
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)
