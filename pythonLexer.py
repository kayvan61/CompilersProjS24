import ply.lex as lex

pythonProductions = {
    "S": [
        ['single_input'],
        ['file_input'],
        ['eval_input'],  
    ],
    "single_input": [
        ['NEWLINE'],
        ['simple_stmt'],
        ['compound_stmt', 'NEWLINE'],
    ],
    "file_input": [
        ['NEWLINE'],
        ['stmt'],
        ['file_input', 'NEWLINE'],
        ['file_input', 'stmt'],
    ],
    "eval_input": [
        ['testlist', 'NEWLINE'],
    ],

    "decorator": [
        ['@', 'dotted_name', 'NEWLINE'],
        ['@', 'dotted_name', '(', 'arguments', ')', 'NEWLINE'],
    ],
    "decorators": [
        ['decorator'],
        ['decorators', 'decorator'],
    ],
    "decorated": [
        ['decorators', 'classdef'],
        ['decorators', 'funcdef'],
        ['decorators', 'async_funcdef'],
    ],

    "async_funcdef": [
        ['ASYNC', 'funcdef'],
    ],
    "funcdef": [
        ['DEF', 'name', '(', ')', ':', 'suite'],
        ['DEF', 'name', '(', 'parameters', ')', ':', 'suite'],
        ['DEF', 'name', '(', ')', ':', 'RARROW', 'test', 'suite'],
        ['DEF', 'name', '(', 'parameters', ')', ':', 'RARROW', 'test', 'suite'],
    ],

    "parameters": [
        ['paramvalue', 'paramlist'],
        ['paramvalue', 'paramlist', ',' '/', 'paramlist'],
        ['paramvalue', 'paramlist', ',', 'starparams'],
        ['paramvalue', 'paramlist', ',', 'kwparams'],
        ['paramvalue', 'paramlist', ',' '/', 'paramlist', ',', 'starparams'],
        ['paramvalue', 'paramlist', ',' '/', 'paramlist', ',', 'kwparams'],
        ['starparams'],
        ['kwparams']
    ],
    "paramlist": [
        [],
        [',', 'paramvalue', 'paramlist'],
    ],

    "starparams": [
        ['starparam', 'poststarparams'],
        ['starguard', 'poststarparams'],
    ],
    "starparam": [
        ['*', 'typedparam'],
        ['*'],
    ],
    "poststarparams": [
        ['paramlist'],
        ['paramlist', ',', 'kwparams'],
    ],
    "kwparams": [
        ['**', 'typedparam'],
        ['**', 'typedparam', ','],
    ],

    "paramvalue": [
        ['typedparam'],
        ['typedparam', '=', 'test'],
    ],
    "typedparam": [
        ['name'],
        ['name', ':', 'test'],
    ],

    "lambdef": [
        ['LAMBDA', ':', 'test'],
        ['LAMBDA', 'lambda_params', ':', 'test'],
    ],
    "lambdef_nocond": [
        ['LAMBDA', ':', 'test_nocond'],
        ['LAMBDA', 'lambda_params', ':', 'test_nocond'],
    ],
    "lambda_params": [
        ['lambda_paramvalue', 'lambda_paramlist'],
        ['lambda_paramvalue', 'lambda_paramlist', ',', 'lambda_starparams'],
        ['lambda_paramvalue', 'lambda_paramlist', ',', 'lambda_kwparams'],
    ],
    "lambda_paramlist": [
        [],
        [',', 'lambda_paramvalue', 'lambda_paramlist'],
    ],
    "lambda_paramvalue": [
        ['name'],
        ['name', '=', 'test'],
    ],
    "lambda_starparams": [
        ['*', 'lambda_paramlist'],
        ['*', 'name', 'lambda_paramlist'],
        ['*', 'lambda_paramlist', ',', 'lambda_kwparams'],
        ['*', 'name', 'lambda_paramlist', ',', 'lambda_kwparams'],
    ],
    "lambda_kwparams": [
        ['**', 'name'],
        ['**', 'name', ','],
    ],

    "stmt": [
        ['simple_stmt'],
        ['compound_stmt'],
    ],
    "simple_stmt": [
        ['small_stmt', 'small_stmt_list', 'NEWLINE'],
        ['small_stmt', 'small_stmt_list', ';', 'NEWLINE'],
    ],
    "small_stmt_list": [
        [],
        [';', 'small_stmt', 'small_stmt_list'],
    ],
    "small_stmt": [
        ['expr_stmt'],
        ['assign_stmt'],
        ['del_stmt'],
        ['pass_stmt'],
        ['flow_stmt'],
        ['import_stmt'],
        ['global_stmt'],
        ['nonlocal_stmt'],
        ['assert_stmt'],
    ],
    "expr_stmt": [
        ['testlist_star_expr'],
    ],
    "assign_stmt": [
        ['annassign'],
        ['augassign'],
        ['assign'],
    ],

    "annassign": [
        ['testlist_star_expr', ':', 'test'],
        ['testlist_star_expr', ':', 'test', '=', 'test'],
    ],
    "assign": [
        ['testlist_star_expr', 'assign_follow_list'],
    ],
    "assign_follow_list": [
        ['=', 'yield_expr'],
        ['=', 'testlist_star_expr'],
        ['=', 'yield_expr', 'assign_follow_list'],
        ['=', 'testlist_star_expr', 'assign_follow_list'],
    ],
    "augassign": [
        ['testlist_star_expr', 'augassign_op', 'yield_expr'],
        ['testlist_star_expr', 'augassign_op', 'testlist'],
    ],
    "augassign_op": [
        ['PLUSEQUAL'],
        ['MINUSEQUAL'],
        ['STAREQUAL'],
        ['ATEQUAL'],
        ['SLASHEQUAL'],
        ['PERCENTEQUAL'],
        ['AMPEREQUAL'],
        ['VBAREQUAL'],
        ['CIRCUMFLEXEQUAL'],
        ['LEFTSHIFTEQUAL'],
        ['RIGHTSHIFTEQUAL'],
        ['DOUBLESTAREQUAL'],
        ['DOUBLESLASHEQUAL'],
    ],
    "testlist_star_expr": [
        ['test_or_star_expr'],
        ['test_or_star_expr', ',', 'testlist_star_expr'],
        ['test_or_star_expr', ','],
    ],

    "del_stmt": [
        ['DEL', 'exprlist'],
    ],
    "pass_stmt": [
        ['PASS'],
    ],
    "flow_stmt": [
        ['break_stmt'],
        ['continue_stmt'],
        ['return_stmt'],
        ['raise_stmt'],
        ['yield_stmt'],
    ],
    "break_stmt": [
        ['BREAK'],
    ],
    "continue_stmt": [
        ['CONTINUE'],
    ],
    "return_stmt": [
        ['RETURN'],
        ['RETURN', 'testlist'],
    ],
    "yield_stmt": [
        ['yield_expr'],
    ],
    "raise_stmt": [
        ['RAISE'],
        ['RAISE', 'test'],
        ['RAISE', 'test', 'FROM', 'test'],
    ],
    "import_stmt": [
        ['import_name'],
        ['import_from'],
    ],
    "import_name": [
        ['IMPORT', 'dotted_as_names'],
    ],
    "import_from": [
        ['FROM', 'dotted_name', 'IMPORT', '*'],
        ['FROM', 'dotted_name', 'IMPORT', '(', 'import_as_names', ')'],
        ['FROM', 'dotted_name', 'IMPORT', 'import_as_names'],
        ['FROM', 'dots', 'dotted_name', 'IMPORT', '*'],
        ['FROM', 'dots', 'dotted_name', 'IMPORT', '(', 'import_as_names', ')'],
        ['FROM', 'dots', 'dotted_name', 'IMPORT', 'import_as_names'],
        ['FROM', 'dots', 'IMPORT', '*'],
        ['FROM', 'dots', 'IMPORT', '(', 'import_as_names', ')'],
        ['FROM', 'dots', 'IMPORT', 'import_as_names'],
    ],
    "dots": [
        ['.'],
        ['.', 'dots']
    ],
    "import_as_name": [
        ['name'],
        ['name', 'AS', 'name'],
    ],
    "dotted_as_name": [
        ['dotted_name'],
        ['dotted_name', 'as', 'name'],
    ],
    "import_as_names": [
        ['import_as_name', 'import_as_name_list'],
        ['import_as_name', 'import_as_name_list', ','],
    ],
    "import_as_name_list": [
        [],
        [',', 'import_as_name', 'import_as_name_list']
    ],
    "dotted_as_names": [
        ['dotted_as_name', 'dotted_as_name_list'],
    ],
    "dotted_as_name_list": [
        [],
        [',', 'dotted_as_name', 'dotted_as_name_list'],
    ],
    "dotted_name": [
        ['name', 'dotted_name_list'],
    ],
    "dotted_name_list": [
        [],
        ['.', 'name', 'dotted_name_list'],
    ],
    "global_stmt": [
        ['GLOBAL', 'name', 'comma_name_list'],
    ],
    "nonlocal_stmt": [
        ['NONLOCAL', 'name', 'comma_name_list'],
    ],
    "comma_name_list": [
        [],
        [',', 'name', 'comma_name_list'],
    ],
    "assert_stmt": [
        ['ASSERT', 'test'],
        ['ASSERT', 'test', ',', 'test']
    ],

    "compound_stmt": [
        ['if_stmt'],
        ['while_stmt'],
        ['for_stmt'],
        ['try_stmt'],
        ['match_stmt'],
        ['with_stmt'],
        ['funcdef'],
        ['classdef'],
        ['decorated'],
        ['async_stmt'],
    ],
    "async_stmt": [
        ['ASYNC', 'funcdef'],
        ['ASYNC', 'with_stmt'],
        ['ASYNC', 'for_stmt'],
    ],
    "if_stmt": [
        ['IF', 'test', ':', 'suite', 'elifs'],
        ['IF', 'test', ':', 'suite', 'elifs', 'ELSE', ':', 'suite'],
    ],
    "elifs": [
        [],
        ['ELIF', 'test', ':', 'suite', 'elifs'],
    ],
    "while_stmt": [
        ['WHILE', 'test', ':', 'suite'],
        ['WHILE', 'test', ':', 'suite', 'ELSE', ':', 'suite'],
    ],
    "for_stmt": [
        ['for', 'exprlist', 'IN', 'testlist', ':', 'suite'],
        ['for', 'exprlist', 'IN', 'testlist', ':', 'suite', 'ELSE', ':', 'suite'],
    ],
    "try_stmt": [
        ['TRY', ':', 'suite', 'except_clauses'],
        ['TRY', ':', 'suite', 'except_clauses', 'ELSE', ':', 'suite'],
        ['TRY', ':', 'suite', 'except_clauses', 'finally'],
        ['TRY', ':', 'suite', 'except_clauses', 'ELSE', ':', 'suite', 'finally'],
        ['TRY', ':', 'suite', 'finally'],
    ],
    "finally": [
        ['FINALLY', ':', 'suite'],
    ],
    "except_clauses": [
        ['except_clause'],
        ['except_clause', 'except_clauses'],
    ],
    "except_clause": [
        ['EXCEPT', ':', 'suite'],
        ['EXCEPT', 'test', ':', 'suite'],
        ['EXCEPT', 'test', 'AS', 'name', ':', 'suite'],
    ],


    "with_stmt": [
        ['WITH', 'with_items', ':', 'suite'],
    ],
    "with_items": [
        ['with_item', 'with_item_list'],
    ],
    "with_item_list": [
        [],
        [',', 'with_item', 'with_item_list'],
    ],
    "with_item": [
        ['test'],
        ['test', 'AS', 'name']
    ],

    "match_stmt": [
        ['MATCH', 'test', ':', 'NEWLINE', 'cases'] # TODO MISSING INDENT DEDENT
    ],
    "cases": [
        ['case'],
        ['case', 'cases'],
    ],
    "case": [
        ['CASE', 'pattern', ':', 'suite'],
        ['CASE', 'pattern', 'IF', 'test', ':', 'suite'],
    ],

    "pattern": [
        ['sequence_item_pattern', ',',  '_sequence_pattern'],
        ['as_pattern'],
    ],
    "as_pattern": [
        ['or_pattern', 'AS', 'name'],
    ],
    "or_pattern": [
        ['closed_pattern', 'closed_pattern_list'],
    ],
    "closed_pattern_list": [
        [],
        ['|', 'closed_pattern', 'closed_pattern_list'],
    ],
    "closed_pattern": [
        ['literal_pattern'],
        ['NAME'],
        ['_'],
        ['attr_pattern'],
        ['(', 'as_pattern', ')'],
        ['[', '_sequence_pattern', ']'],
        ['(', ')'],
        ['(', 'sequence_item_pattern', ',',  '_sequence_pattern', ')'],
        ['{', '}'],
        ['{', 'mapping_item_pattern', 'mapping_item_list', '}' ],
        ['{', 'mapping_item_pattern', 'mapping_item_list', ',', '}' ],
        ['{', '**', 'NAME', '}'],
        ['{', '**', 'NAME', ',', '}'],
        ['{', 'mapping_item_pattern', 'mapping_item_list', ',', '**', 'NAME', '}'],
        ['{', 'mapping_item_pattern', 'mapping_item_list', ',', '**', 'NAME', ',', '}'],
        ['class_pattern'],
    ],
    "mapping_item_list": [
        [],
        [',', 'mapping_item_pattern', 'mapping_item_list'],
    ],

    "literal_pattern": [
        ['inner_literal_pattern'],
    ],
    "inner_literal_pattern": [
        ['NONE'],
        ['TRUE'],
        ['FALSE'],
        ['STRING'],
        ['number'],
    ],

    "attr_pattern": [
        ['NAME', '.', 'NAME', 'dot_name_list'],
    ],
    "dot_name_list": [
        [],
        ['.', 'NAME', 'dot_name_list'],
    ],
    "name_or_attr_pattern": [
        ['NAME', 'dot_name_list'],
    ],

    "mapping_item_pattern": [
        ['literal_pattern', ':', 'as_pattern'],
        ['attr_pattern', ':', 'as_pattern'],
    ],

    "_sequence_pattern": [
        [],
        ['sequence_item_pattern', 'sequence_item_list'],
        ['sequence_item_pattern', 'sequence_item_list', ','],
    ],
    "sequence_item_list": [
        [],
        [',', 'sequence_item_pattern', 'sequence_item_list'],
    ],
    "sequence_item_pattern": [
        ['as_pattern'],
        ['*', 'NAME'],
    ],

    "class_pattern": [
        ['name_or_attr_pattern', '(', ')'],
        ['name_or_attr_pattern', '(', 'arguments_pattern', ')'],
        ['name_or_attr_pattern', '(', 'arguments_pattern', ',', ')'],
    ],
    "arguments_pattern": [
        ['pos_arg_pattern'], 
        ['pos_arg_pattern', ',', 'keyws_arg_pattern'],
        ['keyws_arg_pattern'],
    ],
    "post_arg_pattern": [
        ['as_pattern', 'as_pattern_list'],
    ],
    "as_pattern_list": [
        [],
        [',', 'as_pattern', 'as_pattern_list'],
    ],
    "keyws_arg_pattern": [
        ['keyw_arg_pattern', 'keyw_arg_list'],
    ],
    "keyw_arg_list": [
        [],
        [',', 'keyw_arg_pattern', 'keyw_arg_list'],
    ],
    "keyw_arg_pattern": [
        ['NAME', '=', 'as_pattern'],
    ],
}

reserved = {
        'False': 'FALSE',
        'await': 'AWAIT',
		'else': 'ELSE',
		'import': 'IMPORT',
		'pass': 'PASS',
		'None': 'NONE',
		'break': 'BREAK',
		'except': 'EXCEPT',
		'in': 'IN',
		'raise': 'RAISE',
		'True': 'TRUE',
		'class': 'CLASS',
		'finally': 'FINALLY',
		'is': 'IS',
		'return': 'RETURN',
		'and': 'AND',
		'continue': 'CONTINUE',
		'for': 'FOR',
		'lambda': 'LAMBDA',
		'try': 'TRY',
		'as': 'AS',
		'def': 'DEF',
		'from': 'FROM',
		'nonlocal': 'NONLOCAL',
		'while': 'WHILE',
		'assert': 'ASSERT',
		'del': 'DEL',
		'global': 'GLOBAL',
		'not': 'NOT',
		'with': 'WITH',
        'async': 'ASYNC',
		'elif': 'ELIF',
		'if': 'IF',
		'or': 'OR',
		'yield': 'YIELD',
        'match': 'MATCH',
        'case': 'CASE',
        'type': 'TYPE',
        '_': '_',
    }

class PythonLexer(object):

    tokens = [
        'NAME',
        'DEC_NUMBER',
        'HEX_NUMBER',
        'BIN_NUMBER',
        'OCT_NUMBER',
        'FLOAT_NUMBER',
        'IMAG_NUMBER',
        'STRING',
        'LONG_STRING',
        'NEWLINE',
        # 'INDNET',
        # 'DEDENT',
        'EQEQUAL',
        'NOTEQUAL',
        'LESSEQUAL',
        'GREATEREQUAL',
        'LEFTSHIFT',
        'RIGHTSHIFT',
        'DOUBLESTAR',
        'PLUSEQUAL',
        'MINUSEQUAL',
        'STAREQUAL',
        'SLASHEQUAL',
        'PERCENTEQUAL',
        'AMPEREQUAL',
        'VBAREQUAL',
        'CIRCUMFLEXEQUAL',
        'LEFTSHIFTEQUAL',
        'RIGHTSHIFTEQUAL',
        'DOUBLESTAREQUAL',
        'DOUBLESLASH',
        'DOUBLESLASHEQUAL',
        'ATEQUAL',
        'RARROW',
        'ELLIPSIS',
        'COLONEQUAL',
        'COMMENT',
    ] + list(reserved.values())

    # Regular expression rules for simple tokens

    t_DEC_NUMBER    = r'([1-9]([_]?[0-9])*)|[0]+([_]?[0])*'
    t_STRING        = r'([uUbBfF]?[rR]?|[rR][uUbBfF])("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' 
    t_LONG_STRING   = r'([uUbBfF]?[rR]?|[rR][uUbBfF])("""(.|\n)*?(?<!\\)(\\\\)*?"""|\'\'\'(.|\n)*?(?<!\\)(\\\\)*?\'\'\')'
    t_NEWLINE		= r'\r?\n[\t ]*'
    # t_INDNET		= r''
    # t_DEDENT		= r''
    t_EQEQUAL		= r'=='
    t_NOTEQUAL		= r'!='
    t_LESSEQUAL		= r'<='
    t_GREATEREQUAL	= r'>='
    t_LEFTSHIFT		= r'<<'
    t_RIGHTSHIFT	= r'>>'
    t_DOUBLESTAR	= r'[*][*]'
    t_PLUSEQUAL		= r'[+]='
    t_MINUSEQUAL	= r'[-]='
    t_STAREQUAL		= r'[*]='
    t_SLASHEQUAL	= r'/='
    t_PERCENTEQUAL	= r'%='
    t_AMPEREQUAL	= r'&='
    t_VBAREQUAL		= r'\|='
    t_CIRCUMFLEXEQUAL	= r'^='
    t_LEFTSHIFTEQUAL	= r'<<='
    t_RIGHTSHIFTEQUAL	= r'>>='
    t_DOUBLESTAREQUAL	= r'[*][*]='
    t_DOUBLESLASH		= r'//'
    t_DOUBLESLASHEQUAL	= r'//='
    t_ATEQUAL		    = r'@='
    t_RARROW		    = r'[-]>'
    t_ELLIPSIS		    = r'\.\.\.'
    t_COLONEQUAL		= r':='

    literals = "()[]:,;+-*/|&<>=.%{}~^@!"

    def t_NAME(self,t):
        r'[^\W\d]\w*'
        t.type = reserved.get(t.value, 'NAME')
        return t
    
    def t_HEX_NUMBER(self, t):
        r'0[xX]([_]?([0-9a-fA-F]))+'
        return t
    
    def t_BIN_NUMBER(self, t):
        r'0[bB]([_]?[01])+'
        return t
    
    def t_OCT_NUMBER(self, t):
        r'0[oO]([_]?[0-7])+'
        return t

    def t_IMAGE_NUMBER(self, t):
        r'(([0-9]([_]?[0-9])*)|(([0-9]([_]?[0-9])*[eE][+-][0-9]([_]?[0-9])*)|(((\.[0-9]([_]?[0-9])*)|([0-9]([_]?[0-9])*\.[0-9]([_]?[0-9])*))([eE][+-][0-9]([_]?[0-9])*)?)))[jJ]'
        return t

    def t_FLOAT_NUMBER(self, t):
        r'([0-9]([_]?[0-9])*[eE][+-][0-9]([_]?[0-9])*)|(((\.[0-9]([_]?[0-9])*)|([0-9]([_]?[0-9])*\.[0-9]([_]?[0-9])*))([eE][+-][0-9]([_]?[0-9])*)?)'
        return t

    def t_COMMENT(self,t):
        r'\#[^\n]*'
        pass

    t_ignore  = ' \t\f'

    # Error handling rule
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, data):
        self.lexer.input(data)

    # Test it output
    def token(self):
        return self.lexer.token()
    

import math

def round_up_to_multiple_of_4(x):
    return int(math.ceil(x / 4.0)) * 4


def print_prod_rhs(prod):
    for term in prod:
        if len(term) == 1:
            print(f"\"{term}\" ", end="")
        else:
            print(f"{term} ", end="")
    print()

if __name__ == "__main__":
    # Build the lexer and try it out
    l = PythonLexer()
    l.build()           # Build the lexer
    test =  '''
            == != ... >= # comment def asdf 
             
               >>= def 
               100 00 0xaFd2301 0b1010_1_01 0o12571521
               123401243e-123 .0123 0.0123 123143.0 12.1230E+12
               123401243e-123j .0123J 123j 123143.0j 12.1230E+12J
               f"testing {test} one two three" 'hello \t world'

                """
                test
                """

                . ...
            '''
    l.input(test)     # Test it

    while True:
        tok = l.token()
        if not tok:
            print("-----------")
            break
        print(tok.type, tok.value)

    # print(l.tokens)

    # Convert GFG productions to Lark productions
    # for non_terminal, prods in cLangProductions.items():
    #     name_len = (len(non_terminal) + 1)
    #     num_spaces = round_up_to_multiple_of_4(name_len)

    #     diff_space = ' ' * (num_spaces - name_len)
    #     spaces = ' ' * num_spaces

    #     print(f"{non_terminal}{diff_space} : ", end = "")

    #     print_prod_rhs(prods[0])

    #     for i in range(1, len(prods)):
    #         prod = prods[i]
    #         print(f"{spaces}| ", end="")
    #         print_prod_rhs(prod)