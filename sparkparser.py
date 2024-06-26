#!/usr/bin/env python
#  Copyright (c) 2018 Rocky Bernstein
"""
SPARK example to parse simple arithmetic expressions
"""
import sys
from spark_parser import GenericParser, GenericASTTraversal
from spark_parser import AST
from spark_parser.scanner import GenericScanner, GenericToken

class ExprScanner(GenericScanner):
    """A simple integer expression Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self):
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, s):
        t = GenericToken(kind=name, attr=s)
        self.rv.append(t)

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    # Recognize white space, but we don't create a token for it.
    # This has the effect of stripping white space between tokens
    def t_whitespace(self, s):
        r' \s+ '
        pass

    # Recognize binary operators.
    # The routines for '+' and '-' are separated from '*' and '/'
    # keep operator precidence separate.
    def t_add_op(self, s):
        r'[+-]'
        self.add_token('ADD_OP', s)

    def t_mult_op(self, s):
        r'[/*]'
        self.add_token('MULT_OP', s)

    # Recognize integers
    def t_integer(self, s):
        r'\d+'
        self.add_token('INTEGER', s)


class BScanner(GenericScanner):
    """A simple parser for the character b.
    """

    def __init__(self):
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, s):
        t = GenericToken(kind=name, attr=s)
        self.rv.append(t)

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    # Recognize white space, but we don't create a token for it.
    # This has the effect of stripping white space between tokens
    def t_whitespace(self, s):
        r' \s+ '
        pass

    # Recognize binary operators.
    # The routines for '+' and '-' are separated from '*' and '/'
    # keep operator precidence separate.
    def t_add_op(self, s):
        r'b'
        self.add_token('B_CHAR', s)


# Some kinds of parsing debugging options you might want to consider...
#
# The most verbose debugging::
# DEFAULT_DEBUG = {'rules': True,
#                  'transition': True,
#                  'reduce' : True,
#                  'dups': True
#                 }
#
# The kind of debugging I generally use:
# DEFAULT_DEBUG = {'rules': False,
#                  'transition': False,
#                  'reduce' : True,   # show grammar rule reductions
#                  'dups': True
# }
DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce': False, 'dups': False}

class ExprParser(GenericParser):
    """A simple expression parser for numbers and arithmetic operators: +, , *, and /.

    Note: methods that begin p_ have docstrings that are grammar rules interpreted
    by SPARK.
    """

    def __init__(self, start='expr', debug=DEFAULT_DEBUG):
        GenericParser.__init__(self, start, debug)

    # Below are methods for the grammar rules and the AST tree-building
    # action to take. The method name starts with p_, but note that the
    # the method name itself after the p_ isn't used; it is just
    # suggestive of what the grammar rules in docstring comments do.

    def p_expr_add_term(self, args):
        ' expr ::= expr ADD_OP term '
        op = 'add' if args[1].attr == '+' else 'subtract'
        return AST(op, [args[0], args[2]])

    def p_expr2term(self, args):
        ' expr ::= term '
        return AST('single', [args[0]])

    def p_term_mult_factor(self, args):
        ' term ::= term MULT_OP factor '
        op = 'multiply' if args[1].attr == '*' else 'divide'
        return AST(op, [args[0], args[2]])

    def p_term2single(self, args):
        ' term ::= factor '
        return AST('single', [args[0]])

    def p_factor2integer(self, args):
        ' factor ::= INTEGER '
        return AST('single', [args[0]])
    
class BParser(GenericParser):
    """A simple expression parser for S -> L, L -> LL | b

    Note: methods that begin p_ have docstrings that are grammar rules interpreted
    by SPARK.
    """

    def __init__(self, start='start', debug=DEFAULT_DEBUG):
        self.scanner = BScanner()
        GenericParser.__init__(self, start, debug)

    # Below are methods for the grammar rules and the AST tree-building
    # action to take. The method name starts with p_, but note that the
    # the method name itself after the p_ isn't used; it is just
    # suggestive of what the grammar rules in docstring comments do.

    def p_s_l(self, args):
        ' start ::= l '
        return AST('s', [args[0]])

    def p_l_to_ll(self, args):
        ' l ::= l l '
        return AST('l', [args[0], args[1]])

    def p_l_to_b(self, args):
        ' l ::= B_CHAR '
        return AST('l', [args[0]])
    
    def scan_and_parse(self, string):
        tokens = self.scanner.tokenize(string)
        return self.parse(tokens)


def scan_expression(data):
    """
    Tokenize *filename* into integers, numbers, and operators
    """
    scanner = BScanner()
    return scanner.tokenize(data)

def parse_expression(tokens):
    parser = BParser()
    return parser.parse(tokens)


if __name__ == '__main__':
    data = "bbbb"
    print(data)
    tokens = scan_expression(data)
    print(tokens)
    tree = parse_expression(tokens)
    print(tree)

    print("------------\n\n")


    print(BParser().scan_and_parse(data))
