import ply.lex as lex

# ANSI C grammar: https://www.lysator.liu.se/c/ANSI-C-grammar-y.html#compound-statement
cLangProductions = {
    "S": [
        ['program'],
    ],
    "program": [ # IDK WHAT THE ACTUAL START PRODUCTION IS
        ['function_definition'],
        ['program', 'function_definition'],
        ['statement'],
        ['program', 'statement']
    ],
    "primary_expression": [
        ['IDENTIFIER'],
        ['constant'],
        ['string'],
        ['(', 'expression', ')'],
        ['generic_selection'],
    ],
    "constant": [
        ['I_CONSTANT'],
        ['F_CONSTANT'],
    ],
    "string": [
        ['STRING_LITERAL'],
        ['FUNC_NAME'],
    ],
    "generic_selection": [
        ['GENERIC', '(', 'assignment_expression', ',', 'generic_assoc_list', ')']
    ],
    "generic_assoc_list": [
        ['generic_association'],
        ['generic_assoc_list', ',', 'generic_association']
    ],
    "generic_association": [
        ['type_name', ':', 'assignment_expression'],
        ['DEFAULT', ':', 'assignment_expression'],
    ],
    "postfix_expression": [
        ['primary_expression'],
        ['postfix_expression', '[', 'expression', ']'],
        ['postfix_expression', '(',')'],
        ['postfix_expression', '(', 'argument_expression_list', ')'],
        ['postfix_expression', '.', 'IDENTIFIER'],
        ['postfix_expression', 'PTR_OP', 'IDENTIFIER'],
        ['postfix_expression', 'INC_OP',],
        ['postfix_expression', 'DEC_OP'],
        ['(', 'type_name', ')', '{', 'initializer_list', '}'],
        ['(', 'type_name', ')', '{', 'initializer_list', ',', '}'],
    ],
    "argument_expression_list": [
        ['assignment_expression'],
        ['argument_expression_list', ',', 'assignment_expression'],
    ],
    "unary_expression": [
        ["postfix_expression"],
        ['INC_OP', 'unary_expression'],
        ['DEC_OP', 'unary_expression'],
        ['unary_operator', 'cast_expression'],
        ['SIZEOF', 'unary_expression'],
        ['SIZEOF', '(', 'type_name', ')'],
        ['ALIGNOF', '(', 'type_name', ')']
    ],
    "unary_operator": [
        ['&'],
        ['*'],
        ['+'],
        ['-'],
        ['~'],
        ['!'],
    ],
    "cast_expression": [
        ['unary_expression'],
        ['(', 'type_name', ')', 'cast_expression'],
    ],
    "multiplicative_expression": [
        ['cast_expression'],
        ['multiplicative_expression', '*', 'cast_expression'],
        ['multiplicative_expression', '/', 'cast_expression'],
        ['multiplicative_expression', '%', 'cast_expression'],
    ],
    "additive_expression": [
        ['multiplicative_expression'],
        ['additive_expression', '+', 'multiplicative_expression'],
        ['additive_expression', '-', 'multiplicative_expression'],
    ],
    "shift_expression": [
        ['additive_expression'],
        ['shift_expression', 'LEFT_OP', 'additive_expression'],
        ['shift_expression', 'RIGHT_OP', 'additive_expression']
    ],
    "relation_expression": [
        ['shift_expression'],
        ['relation_expression', '<', 'shift_expression'], 
        ['relation_expression', '>', 'shift_expression'], 
        ['relation_expression', 'LE_OP', 'shift_expression'], 
        ['relation_expression', 'GE_OP', 'shift_expression'], 
    ],
    "equality_expression": [
        ['relation_expression'],
        ['equality_expression', 'EQ_OP', 'relation_expression'],
        ['equality_expression', 'NE_OP', 'relation_expression'],
    ],
    "and_expression": [
        ['equality_expression'],
        ['and_expression', '&', 'equality_expression']
    ],
    "exclusive_or_expression": [
        ['and_expression'],
        ['exclusive_or_expression', '^', 'and_expression'],
    ],
    "inclusive_or_expression": [
        ['exclusive_or_expression'],
        ['inclusive_or_expression', '|', 'exclusive_or_expression'],
    ],
    "logical_and_expression": [
        ['inclusive_or_expression'],
        ['logical_and_expression', 'AND_OP', 'inclusive_or_expression'],
    ],
    "logical_or_expression": [
        ['logical_and_expression'],
        ['logical_or_expression', 'OR_OP', 'logical_and_expression'],
    ],
    "conditional_expression": [
        ['logical_or_expression'],
        ['logical_or_expression', '?', 'expression', ':', 'conditional_expression']
    ],
    "assignment_expression": [
        ['conditional_expression'],
        ['unary_expression', 'assignment_operator', 'assignment_expression']
    ],
    "assignment_operator": [
        ['='],
        ['MUL_ASSIGN'],
        ['DIV_ASSIGN'],
        ['MOD_ASSIGN'],
        ['ADD_ASSIGN'],
        ['SUB_ASSIGN'],
        ['LEFT_ASSIGN'],
        ['RIGHT_ASSIGN'],
        ['AND_ASSIGN'],
        ['XOR_ASSIGN'],
        ['OR_ASSIGN'],
    ],
    "expression": [
        ['assignment_expression'],
        ['expression', ',', 'assignment_expression'],
    ],
    "constant_expression": [
        ['conditional_expression']
    ],
    "declaration": [
        ['declaration_specifiers', ';'],
        ['declaration_specifiers', 'init_declarator_list', ';'],
        ['static_assert_declaration']
    ],
    "declaration_specifiers": [
        ['storage_class_specifier'],
        ['storage_class_specifier', 'declaration_specifiers'],
        ['type_specifier'],
        ['type_specifier', 'declaration_specifiers'],
        ['type_qualifier'],
        ['type_qualifier', 'declaration_specifiers'],
        ['function_specifier'],
        ['function_specifier', 'declaration_specifiers'],
        ['alignment_specifier'],
        ['alignment_specifier', 'declaration_specifiers'],
    ],
    "init_declarator_list": [
        ['init_declarator'],
        ['init_declarator_list', ',', 'init_declarator'],
    ],
    "init_declarator": [
        ['declarator'],
        ['declarator', '=', 'initializer'],
    ],
    "storage_class_specifier": [
        ['TYPEDEF'],
        ['EXTERN'],
        ['STATIC'],
        ['THREAD_LOCAL'],
        ['AUTO'],
        ['REGISTER'],
    ],
    "type_specifier": [
        ['VOID'],
        ['CHAR'],
        ['SHORT'],
        ['INT'],
        ['LONG'],
        ['FLOAT'],
        ['DOUBLE'],
        ['SIGNED'],
        ['UNSIGNED'],
        ['BOOL'],
        ['COMPLEX'],
        ['IMAGINARY'],
        ['atomic_type_specifier'],
        ['struct_or_union_specifier'],
        ['enum_specifier'],
        # ['TYPEDEF_NAME'] ????
    ],
    "struct_or_union_specifier": [
        ["struct_or_union", "IDENTIFIER", '{', 'struct_declaration_list', '}'],
        ["struct_or_union", '{', 'struct_declaration_list', '}'],
        ["struct_or_union", "IDENTIFIER"],
    ],
    "struct_or_union": [
        ['STRUCT'],
        ['UNION']
    ],
    "struct_declaration_list": [
        ['struct_declaration'],
        ['struct_declaration_list', 'struct_declaration'],
    ],
    "struct_declaration": [
        ['specifier_qualifier_list', ';'],
        ['specifier_qualifier_list', 'struct_declarator_list'],
        ['static_assert_declaration']
    ],
    "specifier_qualifier_list": [
        ['type_specifier', 'specifier_qualifier_list'],
        ['type_specifier'],
        ['type_qualifier', 'specifier_qualifier_list'],
        ['type_qualifier'],
    ],
    "struct_declarator_list": [
        ['struct_declarator'],
        ['struct_declarator_list', ',', 'struct_declarator'],
    ],
    "struct_declarator": [
        ["declarator"],
        [":", "constant_expression"],
        ["declarator", ':', 'constant_expression']
    ],
    "enum_specifier": [
        ["ENUM", '{', 'enumerator_list', '}'],
        ["ENUM", '{', 'enumerator_list', ',', '}'],
        ["ENUM", 'IDENTIFIER', '{', 'enumerator_list', '}'],
        ["ENUM", 'IDENTIFIER', '{', 'enumerator_list', ',', '}'],
        ["ENUM", 'IDENTIFIER'],
    ],
    "enumerator_list": [
        ['enumerator'],
        ['enumerator_list', 'enumerator'],
    ],
    "enumerator": [
        ['IDENTIFIER'],
        ['IDENTIFIER', '=', 'constant_expression'],
    ],
    "atomic_type_specifier": [
        ['ATOMIC', '(', 'type_name', ')'],
    ],
    "type_qualifier": [
        ['CONST'],
        ['RESTRICT'],
        ['VOLATILE'],
        ['ATOMIC'],
    ],
    "function_specifier": [
        ['INLINE'],
        ['NORETURN'],
    ],
    "alignment_specifier": [
        ['ALIGNAS', '(', 'type_name', ')'],
        ['ALIGNAS', '(', 'constant_expression', ')']
    ],
    "declarator": [
        ['pointer', 'direct_declarator'],
        ['direct_declarator'],
    ],
    "direct_declarator": [
        ['IDENTIFIER'],
        ['(', 'declarator', ')'],
        ['direct_declarator', '[', ']'],
        ['direct_declarator', '[', '*', ']'],
        ['direct_declarator', '[', 'STATIC', 'type_qualifier_list', 'assignment_expression', ']'],
        ['direct_declarator', '[', 'STATIC', 'assignment_expression', ']'],
        ['direct_declarator', '[', 'type_qualifier_list', '*', ']'],
        ['direct_declarator', '[', 'type_qualifier_list', 'STATIC', 'assignment_expression', ']'],
        ['direct_declarator', '[', 'type_qualifier_list', 'assignment_expression', ']'],
        ['direct_declarator', '[', 'type_qualifier_list', ']'],
        ['direct_declarator', '[', 'assignment_expression', ']'],
        ['direct_declarator', '(', 'parameter_type_list', ')'],
        ['direct_declarator', '(', 'identifier_list', ')'],
        ['direct_declarator', '(', ')'],
    ],
    "pointer": [
        ['*'],
        ['*', 'type_qualifier_list'],
        ['*', 'pointer'],
        ['*', 'type_qualifier_list', 'pointer'],
    ],
    "type_qualifier_list": [
        ['type_qualifier'],
        ['type_qualifier_list', 'type_qualifier'],
    ],
    "parameter_type_list": [
        ['parameter_list'],
        ['parameter_list', ',', 'ELLIPSIS'],
    ],
    "parameter_list": [
        ['parameter_declaration'],
        ['parameter_list', ',', 'parameter_declaration'],
    ],
    "parameter_declaration": [
        ['declaration_specifiers', 'declarator'],
        ['declaration_specifiers', 'abstract_declarator'],
        ['declaration_specifiers']
    ],
    "identifier_list": [
        ['IDENTIFIER'],
        ['identifier_list', 'IDENTIFIER'],
    ],
    "type_name": [
        ['specifier_qualifier_list'],
        ['specifier_qualifier_list', 'abstract_declarator']
    ],
    "abstract_declarator": [
        ['pointer'],
        ['direct_abstract_declarator'],
        ['pointer', 'direct_abstract_declarator'],
    ],
    "direct_abstract_declarator": [
        ['(', 'abstract_declarator', ')'],
        ['[', ']'],
        ['[', '*', ']'],
        ['[', 'STATIC', 'type_qualifier_list', 'assignment_expression', ']'],
        ['[', 'STATIC', 'assignment_expression', ']'],
        ['[', 'type_qualifier_list', 'STATIC', 'assignment_expression', ']'],
        ['[', 'type_qualifier_list', 'assignment_expression', ']'],
        ['[', 'type_qualifier_list', ']'],
        ['[', 'assignment_expression', ']'],
        ['direct_abstract_declarator', '[', ']'],
        ['direct_abstract_declarator', '[', '*', ']'],
        ['direct_abstract_declarator', '[', 'STATIC', 'type_qualifier_list', 'assignment_expression', ']'],
        ['direct_abstract_declarator', '[', 'STATIC', 'assignment_expression', ']'],
        ['direct_abstract_declarator', '[', 'type_qualifier_list', 'STATIC', 'assignment_expression', ']'],
        ['direct_abstract_declarator', '[', 'type_qualifier_list', 'assignment_expression', ']'],
        ['direct_abstract_declarator', '[', 'type_qualifier_list', ']'],
        ['direct_abstract_declarator', '[', 'assignment_expression', ']'],
        ['(', ')'],
        ['(', 'parameter_type_list', ')'],
        ['direct_abstract_declarator', '(', ')'],
        ['direct_abstract_declarator', '(', 'parameter_type_list', ')'],
    ],
    "initializer": [
        ['assignment_expression'],
        ['{', 'initializer_list', '}'],
        ['{', 'initializer_list', ',', '}'],
    ],
    "initializer_list": [
        ['designation', 'initializer'],
        ['initializer'],
        ['initializer_list', ',', 'designation', 'initializer'],
        ['initializer_list', ',', 'initializer'],
    ],
    "designation": [
        ['designator_list', '='],
    ],
    "designator_list": [
        ['designator'],
        ['designator_list', 'designator']
    ],
    "designator": [
        ['[', 'constant_expression', ']'],
        ['.', 'IDENTIFIER'],
    ],
    "static_assert_declaration": [
        ['STATIC_ASSERT', '(', 'constant_expression', ',', 'STRING_LITERAL', ')', ';'],
    ],
    "statement": [
        ['labeled_statement'],
        ['compound_statement'],
        ['expression_statement'],
        ['selection_statement'],
        ['iteration_statement'],
        ['jump_statement'],
    ],
    "labeled_statement": [
        ['IDENTIFIER', ':', 'statement'],
        ['CASE', 'constant_expression', ':', 'statement'],
        ['DEFAULT', ':', 'statement'],
    ],
    "compound_statement": [
        ['{', '}'],
        ['{', 'block_item_list', '}'],
    ],
    "block_item_list": [
        ['block_item'],
        ['block_item_list', 'block_item'],
    ],
    "block_item": [
        ['declaration'],
        ['statement'],
    ],
    "expression_statement": [
        [';'],
        ['expression', ';']
    ],
    "selection_statement": [
        ['IF', '(', 'expression', ')', 'statement'],
        ['IF', '(', 'expression', ')', 'statement', 'ELSE', 'statement'],
        ['SWITCH', '(', 'expression', ')', 'statement']
    ],
    "iteration_statement": [
        ['WHILE', '(', 'expression', ')', 'statement'],
        ['DO', 'statement', 'WHILE', '(', 'expression', ')', ';'],
        ['FOR', '(', 'expression_statement', 'expression_statement', ')', 'statement'],
        ['FOR', '(', 'expression_statement', 'expression_statement', 'expression', ')', 'statement'],
        ['FOR', '(', 'declaration', 'expression_statement', ')', 'statement'],
        ['FOR', '(', 'declaration', 'expression_statement', 'expression', ')', 'statement'],
    ],
    "jump_statement": [
        ['GOTO', 'IDENTIFIER'],
        ['CONTINUE', ';'],
        ['BREAK', ';'],
        ['RETURN', ';'],
        ['RETURN', 'expression', ';']
    ],
    "translation_unit": [
        ['external_declaration'],
        ['translation_unit', 'external_declaration'],
    ],
    "external_declaration": [
        ['function_definition'],
        ['declaration'],
    ],
    "function_definition": [
        ['declaration_specifiers', 'declarator', 'declaration_list', 'compound_statement'],
        ['declaration_specifiers', 'declarator', 'compound_statement'],
    ],
    "declaration_list": [
        ['declaration'],
        ['declaration_list', 'declaration'],
    ],
}

reserved = {
        'auto':    'AUTO',
        'break':    'BREAK',
        'case':    'CASE',
        'char':    'CHAR',
        'const':    'CONST',
        'continue':    'CONTINUE',
        'default':    'DEFAULT',
        'do':    'DO',
        'double':    'DOUBLE',
        'else':    'ELSE',
        'enum':    'ENUM',
        'extern':    'EXTERN',
        'float':    'FLOAT',
        'for':    'FOR',
        'goto':    'GOTO',
        'if':    'IF',
        'inline': 'INLINE',
        'int':    'INT',
        'long':    'LONG',
        'register':    'REGISTER',
        'restrict': 'RESTRICT',
        'return':    'RETURN',
        'short':    'SHORT',
        'signed':    'SIGNED',
        'sizeof':    'SIZEOF',
        'static':    'STATIC',
        'struct':    'STRUCT',
        'switch':    'SWITCH',
        'typedef':    'TYPEDEF',
        'union':    'UNION',
        'unsigned':    'UNSIGNED',
        'void':    'VOID',
        'volatile':    'VOLATILE',
        'while':    'WHILE',
        "_Alignas": "ALIGNAS",
        "_Alignof": "ALIGNOF",
        "_Atomic": "ATOMIC",  
        "_Bool": "BOOL",           
        "_Complex": "COMPLEX",         
        "_Generic": "GENERIC", 
        "_Imaginary": "IMAGINARY",   
        "_Noreturn": "NORETURN",   
        "_Static_assert": "STATIC_ASSERT",  
        "_Thread_local": "THREAD_LOCAL",    
        "__func__": "FUNC_NAME",
    }

class CLangLexer(object):

    tokens = [
        'IDENTIFIER',
        'I_CONSTANT',
        'F_CONSTANT',
        'STRING_LITERAL',
        'ELLIPSIS',
        'RIGHT_ASSIGN',
        'LEFT_ASSIGN',
        'ADD_ASSIGN',
        'SUB_ASSIGN',
        'MUL_ASSIGN',
        'DIV_ASSIGN',
        'MOD_ASSIGN',
        'AND_ASSIGN',
        'XOR_ASSIGN',
        'OR_ASSIGN',
        'RIGHT_OP',
        'LEFT_OP',
        'INC_OP',
        'DEC_OP',
        'PTR_OP',
        'AND_OP',
        'OR_OP',
        'LE_OP',
        'GE_OP',
        'EQ_OP',
        'NE_OP',
    ] + list(reserved.values())

    # Regular expression rules for simple tokens
    t_I_CONSTANT    = r'((0[xX])[a-fA-F0-9]+(((u|U)(l|L|ll|LL)?)|((l|L|ll|LL)(u|U)?))?)|([1-9][0-9]*(((u|U)(l|L|ll|LL)?)|((l|L|ll|LL)(u|U)?))?)|(0[0-7]*(((u|U)(l|L|ll|LL)?)|((l|L|ll|LL)(u|U)?))?)|((u|U|L)?\'([^\'\\\n]|(\\([\'"?\\abfnrtv]|[0-7]{1,3}|x[a-fA-F0-9]+)))+\')'
    t_STRING_LITERAL= r"((u8|u|U|L)?\"([^\"\\\n]|(\\(['\"?\\abfnrtv]|[0-7]{1,3}|x[a-fA-F0-9]+)))*\"[ \t\v\n\f]*)+"
    t_ELLIPSIS      = r'\.\.\.'
    t_RIGHT_ASSIGN  = r'>>='
    t_LEFT_ASSIGN   = r'<<='
    t_ADD_ASSIGN    = r'[+]='
    t_SUB_ASSIGN    = r'-='
    t_MUL_ASSIGN    = r'[*]='
    t_DIV_ASSIGN    = r'/='
    t_MOD_ASSIGN    = r'%='
    t_AND_ASSIGN    = r'&='
    t_XOR_ASSIGN    = r'^='
    t_OR_ASSIGN     = r'[|]='
    t_RIGHT_OP      = r'>>'
    t_LEFT_OP       = r'<<'
    t_INC_OP        = r'[+][+]'
    t_DEC_OP        = r'--'
    t_PTR_OP        = r'->'
    t_AND_OP        = r'&&'
    t_OR_OP         = r'[|][|]'
    t_LE_OP         = r'<='
    t_GE_OP         = r'>='
    t_EQ_OP         = r'=='
    t_NE_OP         = r'!='

    literals = ";{},:=()[].&!~-+*/%<>^|?"

    def t_IDENTIFIER(self,t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'IDENTIFIER')
        return t
    
    def t_COMMENT(self,t):
        r'//.*'
        pass

    def t_F_CONSTANT(self, t):
        r'([0-9]+([Ee][+-]?[0-9]+)(f|F|l|L)?)|([0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?(f|F|l|L)?)|([0-9]+\.([Ee][+-]?[0-9]+)?(f|F|l|L)?)|((0[xX])[a-fA-F0-9]+([Pp][+-]?[0-9]+)(f|F|l|L)?)|((0[xX])[a-fA-F0-9]*\.[a-fA-F0-9]+([Pp][+-]?[0-9]+)(f|F|l|L)?)|((0[xX])[a-fA-F0-9]+\.([Pp][+-]?[0-9]+)(f|F|l|L)?)'
        return t

    def t_MULTI_LINE_COMMENT(self,t):
        r'/[*]'
        l = t.lexer
        while True:
            if l.lexpos == l.lexlen:
                break
            if l.lexdata[l.lexpos] == '*' and l.lexdata[l.lexpos + 1] == '/':
                break
            l.skip(1)
        l.skip(2)
        pass

    t_ignore  = ' \t\v\n\f'

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

if __name__ == "__main__":
    # Build the lexer and try it out
    l = CLangLexer()
    l.build()           # Build the lexer
    test =  '''
            192412e-1010 0.001 .123e+10 10. 11.e-23 '\\na aa' 126310981234 0x9faA1 07123
            '''
    l.input(test)     # Test it

    while True:
        tok = l.token()
        if not tok:
            print("-----------")
            break
        print(tok.type, tok.value)

    # print(l.tokens)