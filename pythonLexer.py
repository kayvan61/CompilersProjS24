import ply.lex as lex

pythonProductions = {
    
}

reserved = {
        'False': 'FALSE',
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
		'elif': 'ELIF',
		'if': 'IF',
		'or': 'OR',
		'yield': 'YIELD',
        'match': 'MATCH',
        'case': 'CASE',
        'type': 'TYPE',
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

    literals = "()[]:,;+-*/|&<>=.%{}~^@!_"

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