from unittest import TestCase, main
from src.monkey import lexer, parser, ast


class TestParser(TestCase):

    def test_parser_let_statement(self):
        code = ("let x = 5;\n"
                "let y = 10;\n"
                "let foobar = 838383;\n")

        expected_identifiers = [
            "x",
            "y",
            "foobar"
        ]

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()

        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 3)

        for stmt, ident in zip(program.statements, expected_identifiers):
            self.assertEqual(stmt.token_literal, "let")
            self.assertIsInstance(stmt, ast.LetStatement)
            self.assertEqual(stmt.name.value, ident)
            self.assertEqual(stmt.name.token_literal, ident)

    def test_parser_errors(self):
        bad_code = ("let x 5;\n"
                    "let = 10;\n"
                    "let 838383;\n")

        lex = lexer.Lexer(bad_code)
        par = parser.Parser(lex)
        program = par.parse_program()

        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 3)

    def test_parser_return_statement(self):
        code = ("return 5;\n"
                "return 10;\n"
                "return 993322;\n")

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 3)
        self.assertEqual(len(par.errors), 0)

        for stmt in program.statements:
            self.assertIsInstance(stmt, ast.ReturnStatement)
            self.assertEqual(stmt.token_literal, "return")

    def test_parser_identifier_expressions(self):
        code = "foobar;"

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)

        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 1)
        self.assertEqual(len(par.errors), 0)

        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.assertIsInstance(stmt.expression, ast.Identifier)
        self.assertEqual(stmt.expression.value, "foobar")
        self.assertEqual(stmt.token_literal, "foobar")

    def test_parser_integer_literal_expressions(self):
        code = "5;"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)

        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 1)
        self.assertEqual(len(par.errors), 0)

        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.assertIsInstance(stmt.expression, ast.IntegerLiteral)
        self.assertEqual(stmt.expression.value, 5)
        self.assertEqual(stmt.token_literal, "5")


if __name__ == "__main__":
    main()
