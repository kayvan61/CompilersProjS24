import argparse
import time
from lark import Lark

grammars = {
    "b_grammar": '''
                 start: l
                 l: l l | B

                 B: "b"
                 ''',
    "a_grammar": '''
                 start: a
                 a : a A | A

                 A: "a"
                 ''',
    "c_lang_grammar": 
    '''
    start   : program 
    program : function_definition 
            | program function_definition 
            | statement 
            | program statement 
    primary_expression  : IDENTIFIER 
                        | constant 
                        | string 
                        | "(" expression ")" 
                        | generic_selection 
    constant    : I_CONSTANT 
                | F_CONSTANT 
    string  : STRING_LITERAL 
            | FUNC_NAME 
    generic_selection   : GENERIC "(" assignment_expression "," generic_assoc_list ")" 
    generic_assoc_list  : generic_association 
                        | generic_assoc_list "," generic_association 
    generic_association : type_name ":" assignment_expression 
                        | DEFAULT ":" assignment_expression 
    postfix_expression  : primary_expression 
                        | postfix_expression "[" expression "]" 
                        | postfix_expression "(" ")" 
                        | postfix_expression "(" argument_expression_list ")" 
                        | postfix_expression "." IDENTIFIER 
                        | postfix_expression PTR_OP IDENTIFIER 
                        | postfix_expression INC_OP 
                        | postfix_expression DEC_OP 
                        | "(" type_name ")" "{" initializer_list "}" 
                        | "(" type_name ")" "{" initializer_list "," "}" 
    argument_expression_list    : assignment_expression 
                                | argument_expression_list "," assignment_expression 
    unary_expression    : postfix_expression 
                        | INC_OP unary_expression 
                        | DEC_OP unary_expression 
                        | unary_operator cast_expression 
                        | SIZEOF unary_expression 
                        | SIZEOF "(" type_name ")" 
                        | ALIGNOF "(" type_name ")" 
    unary_operator  : "&" 
                    | "*" 
                    | "+" 
                    | "-" 
                    | "~" 
                    | "!" 
    cast_expression : unary_expression 
                    | "(" type_name ")" cast_expression 
    multiplicative_expression   : cast_expression 
                                | multiplicative_expression "*" cast_expression 
                                | multiplicative_expression "/" cast_expression 
                                | multiplicative_expression "%" cast_expression 
    additive_expression : multiplicative_expression 
                        | additive_expression "+" multiplicative_expression 
                        | additive_expression "-" multiplicative_expression 
    shift_expression    : additive_expression 
                        | shift_expression LEFT_OP additive_expression 
                        | shift_expression RIGHT_OP additive_expression 
    relation_expression : shift_expression 
                        | relation_expression "<" shift_expression 
                        | relation_expression ">" shift_expression 
                        | relation_expression LE_OP shift_expression 
                        | relation_expression GE_OP shift_expression 
    equality_expression : relation_expression 
                        | equality_expression EQ_OP relation_expression 
                        | equality_expression NE_OP relation_expression 
    and_expression  : equality_expression 
                    | and_expression "&" equality_expression 
    exclusive_or_expression : and_expression 
                            | exclusive_or_expression "^" and_expression 
    inclusive_or_expression : exclusive_or_expression 
                            | inclusive_or_expression "|" exclusive_or_expression 
    logical_and_expression  : inclusive_or_expression 
                            | logical_and_expression AND_OP inclusive_or_expression 
    logical_or_expression   : logical_and_expression 
                            | logical_or_expression OR_OP logical_and_expression 
    conditional_expression  : logical_or_expression 
                            | logical_or_expression "?" expression ":" conditional_expression 
    assignment_expression   : conditional_expression 
                            | unary_expression assignment_operator assignment_expression 
    assignment_operator : "=" 
                        | MUL_ASSIGN 
                        | DIV_ASSIGN 
                        | MOD_ASSIGN 
                        | ADD_ASSIGN 
                        | SUB_ASSIGN 
                        | LEFT_ASSIGN 
                        | RIGHT_ASSIGN 
                        | AND_ASSIGN 
                        | XOR_ASSIGN 
                        | OR_ASSIGN 
    expression  : assignment_expression 
                | expression "," assignment_expression 
    constant_expression : conditional_expression 
    declaration : declaration_specifiers ";" 
                | declaration_specifiers init_declarator_list ";" 
                | static_assert_declaration 
    declaration_specifiers  : storage_class_specifier 
                            | storage_class_specifier declaration_specifiers 
                            | type_specifier 
                            | type_specifier declaration_specifiers 
                            | type_qualifier 
                            | type_qualifier declaration_specifiers 
                            | function_specifier 
                            | function_specifier declaration_specifiers 
                            | alignment_specifier 
                            | alignment_specifier declaration_specifiers 
    init_declarator_list    : init_declarator 
                            | init_declarator_list "," init_declarator 
    init_declarator : declarator 
                    | declarator "=" initializer 
    storage_class_specifier : TYPEDEF 
                            | EXTERN 
                            | STATIC 
                            | THREAD_LOCAL 
                            | AUTO 
                            | REGISTER 
    type_specifier  : VOID 
                    | CHAR 
                    | SHORT 
                    | INT 
                    | LONG 
                    | FLOAT 
                    | DOUBLE 
                    | SIGNED 
                    | UNSIGNED 
                    | BOOL 
                    | COMPLEX 
                    | IMAGINARY 
                    | atomic_type_specifier 
                    | struct_or_union_specifier 
                    | enum_specifier 
    struct_or_union_specifier   : struct_or_union IDENTIFIER "{" struct_declaration_list "}" 
                                | struct_or_union "{" struct_declaration_list "}" 
                                | struct_or_union IDENTIFIER 
    struct_or_union : STRUCT 
                    | UNION 
    struct_declaration_list : struct_declaration 
                            | struct_declaration_list struct_declaration 
    struct_declaration  : specifier_qualifier_list ";" 
                        | specifier_qualifier_list struct_declarator_list 
                        | static_assert_declaration 
    specifier_qualifier_list    : type_specifier specifier_qualifier_list 
                                | type_specifier 
                                | type_qualifier specifier_qualifier_list 
                                | type_qualifier 
    struct_declarator_list  : struct_declarator 
                            | struct_declarator_list "," struct_declarator 
    struct_declarator   : declarator 
                        | ":" constant_expression 
                        | declarator ":" constant_expression 
    enum_specifier  : ENUM "{" enumerator_list "}" 
                    | ENUM "{" enumerator_list "," "}" 
                    | ENUM IDENTIFIER "{" enumerator_list "}" 
                    | ENUM IDENTIFIER "{" enumerator_list "," "}" 
                    | ENUM IDENTIFIER 
    enumerator_list : enumerator 
                    | enumerator_list enumerator 
    enumerator  : IDENTIFIER 
                | IDENTIFIER "=" constant_expression 
    atomic_type_specifier   : ATOMIC "(" type_name ")" 
    type_qualifier  : CONST 
                    | RESTRICT 
                    | VOLATILE 
                    | ATOMIC 
    function_specifier  : INLINE 
                        | NORETURN 
    alignment_specifier : ALIGNAS "(" type_name ")" 
                        | ALIGNAS "(" constant_expression ")" 
    declarator  : pointer direct_declarator 
                | direct_declarator 
    direct_declarator   : IDENTIFIER 
                        | "(" declarator ")" 
                        | direct_declarator "[" "]" 
                        | direct_declarator "[" "*" "]" 
                        | direct_declarator "[" STATIC type_qualifier_list assignment_expression "]" 
                        | direct_declarator "[" STATIC assignment_expression "]" 
                        | direct_declarator "[" type_qualifier_list "*" "]" 
                        | direct_declarator "[" type_qualifier_list STATIC assignment_expression "]" 
                        | direct_declarator "[" type_qualifier_list assignment_expression "]" 
                        | direct_declarator "[" type_qualifier_list "]" 
                        | direct_declarator "[" assignment_expression "]" 
                        | direct_declarator "(" parameter_type_list ")" 
                        | direct_declarator "(" identifier_list ")" 
                        | direct_declarator "(" ")" 
    pointer : "*" 
            | "*" type_qualifier_list 
            | "*" pointer 
            | "*" type_qualifier_list pointer 
    type_qualifier_list : type_qualifier 
                        | type_qualifier_list type_qualifier 
    parameter_type_list : parameter_list 
                        | parameter_list "," ELLIPSIS 
    parameter_list  : parameter_declaration 
                    | parameter_list "," parameter_declaration 
    parameter_declaration   : declaration_specifiers declarator 
                            | declaration_specifiers abstract_declarator 
                            | declaration_specifiers 
    identifier_list : IDENTIFIER 
                    | identifier_list IDENTIFIER 
    type_name   : specifier_qualifier_list 
                | specifier_qualifier_list abstract_declarator 
    abstract_declarator : pointer 
                        | direct_abstract_declarator 
                        | pointer direct_abstract_declarator 
    direct_abstract_declarator  : "(" abstract_declarator ")" 
                                | "[" "]" 
                                | "[" "*" "]" 
                                | "[" STATIC type_qualifier_list assignment_expression "]" 
                                | "[" STATIC assignment_expression "]" 
                                | "[" type_qualifier_list STATIC assignment_expression "]" 
                                | "[" type_qualifier_list assignment_expression "]" 
                                | "[" type_qualifier_list "]" 
                                | "[" assignment_expression "]" 
                                | direct_abstract_declarator "[" "]" 
                                | direct_abstract_declarator "[" "*" "]" 
                                | direct_abstract_declarator "[" STATIC type_qualifier_list assignment_expression "]" 
                                | direct_abstract_declarator "[" STATIC assignment_expression "]" 
                                | direct_abstract_declarator "[" type_qualifier_list STATIC assignment_expression "]" 
                                | direct_abstract_declarator "[" type_qualifier_list assignment_expression "]" 
                                | direct_abstract_declarator "[" type_qualifier_list "]" 
                                | direct_abstract_declarator "[" assignment_expression "]" 
                                | "(" ")" 
                                | "(" parameter_type_list ")" 
                                | direct_abstract_declarator "(" ")" 
                                | direct_abstract_declarator "(" parameter_type_list ")" 
    initializer : assignment_expression 
                | "{" initializer_list "}" 
                | "{" initializer_list "," "}" 
    initializer_list    : designation initializer 
                        | initializer 
                        | initializer_list "," designation initializer 
                        | initializer_list "," initializer 
    designation : designator_list "=" 
    designator_list : designator 
                    | designator_list designator 
    designator  : "[" constant_expression "]" 
                | "." IDENTIFIER 
    static_assert_declaration   : STATIC_ASSERT "(" constant_expression "," STRING_LITERAL ")" ";" 
    statement   : labeled_statement 
                | compound_statement 
                | expression_statement 
                | selection_statement 
                | iteration_statement 
                | jump_statement 
    labeled_statement   : IDENTIFIER ":" statement 
                        | CASE constant_expression ":" statement 
                        | DEFAULT ":" statement 
    compound_statement  : "{" "}" 
                        | "{" block_item_list "}" 
    block_item_list : block_item 
                    | block_item_list block_item 
    block_item  : declaration 
                | statement 
    expression_statement    : ";" 
                            | expression ";" 
    selection_statement : IF "(" expression ")" statement 
                        | IF "(" expression ")" statement ELSE statement 
                        | SWITCH "(" expression ")" statement 
    iteration_statement : WHILE "(" expression ")" statement 
                        | DO statement WHILE "(" expression ")" ";" 
                        | FOR "(" expression_statement expression_statement ")" statement 
                        | FOR "(" expression_statement expression_statement expression ")" statement 
                        | FOR "(" declaration expression_statement ")" statement 
                        | FOR "(" declaration expression_statement expression ")" statement 
    jump_statement  : GOTO IDENTIFIER 
                    | CONTINUE ";" 
                    | BREAK ";" 
                    | RETURN ";" 
                    | RETURN expression ";" 
    translation_unit    : external_declaration 
                        | translation_unit external_declaration 
    external_declaration    : function_definition 
                            | declaration 
    function_definition : declaration_specifiers declarator declaration_list compound_statement 
                        | declaration_specifiers declarator compound_statement 
    declaration_list    : declaration 
                        | declaration_list declaration


    # start of tokens

    AUTO.9: "auto"
    BREAK.9: "break"
    CASE.9: "case"
    CHAR.9: "char"
    CONST.9: "const"
    CONTINUE.9: "continue"
    DEFAULT.9: "default"
    DO.9: "do"
    DOUBLE.9: "double"
    ELSE.9: "else"
    ENUM.9: "enum"
    EXTERN.9: "extern"
    FLOAT.9: "float"
    FOR.9: "for"
    GOTO.9: "goto"
    IF.9: "if"
    INLINE.9: "inline"
    INT.9: "int"
    LONG.9: "long"
    REGISTER.9: "register"
    RESTRICT.9: "restrict"
    RETURN.9: "return"
    SHORT.9: "short"
    SIGNED.9: "signed"
    SIZEOF.9: "sizeof"
    STATIC.9: "static"
    STRUCT.9: "struct"
    SWITCH.9: "switch"
    TYPEDEF.9: "typedef"
    UNION.9: "union"
    UNSIGNED.9: "unsigned"
    VOID.9: "void"
    VOLATILE.9: "volatile"
    WHILE.9: "while"
    ALIGNAS.9: "_Alignas"
    ALIGNOF.9: "_Alignof"
    ATOMIC.9: "_Atomic"
    BOOL.9: "_Bool"
    COMPLEX.9: "_Complex"    
    GENERIC.9: "_Generic"
    IMAGINARY.9: "_Imaginary"
    NORETURN.9: "_Noreturn"
    STATIC_ASSERT.9: "_Static_assert"
    THREAD_LOCAL.9: "_Thread_local"
    FUNC_NAME.9: "__func__"

    IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/

    # TODO MISSING HEX, OCTAL ESCAPES
    I_CONSTANT.7: /((0[xX])[a-fA-F0-9]+(((u|U)(l|L|ll|LL)?)|((l|L|ll|LL)(u|U)?))?)|([1-9][0-9]*(((u|U)(ll|LL|l|L)?)|((ll|LL|l|L)(u|U)?))?)|(0[0-7]*(((u|U)(ll|LL|l|L)?)|((ll|LL|l|L)(u|U)?))?)|((u|U|L)?'([^'\\\n]|\\[\'"?\\abfnrtv])+')/x
    F_CONSTANT.8: /([0-9]+([Ee][+-]?[0-9]+)(f|F|l|L)?)|([0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?(f|F|l|L)?)|([0-9]+\.([Ee][+-]?[0-9]+)?(f|F|l|L)?)|((0[xX])[a-fA-F0-9]+([Pp][+-]?[0-9]+)(f|F|l|L)?)|((0[xX])[a-fA-F0-9]*\.[a-fA-F0-9]+([Pp][+-]?[0-9]+)(f|F|l|L)?)|((0[xX])[a-fA-F0-9]+\.([Pp][+-]?[0-9]+)(f|F|l|L)?)/

    # TODO MISSING HEX, OCTAL ESCAPES
    STRING_LITERAL: /((u8|u|U|L)?"([^"\\\n]|\\['\"?\\abfnrtv])*"[ \t\v\n\f]*)+/x

    ELLIPSIS: "..."
    RIGHT_ASSIGN.3: ">>="
    LEFT_ASSIGN.3: "<<="
    ADD_ASSIGN.3: "+="
    SUB_ASSIGN.3: "-="
    MUL_ASSIGN.3: "*="
    DIV_ASSIGN.3: "/="
    MOD_ASSIGN.3: "%="
    AND_ASSIGN.3: "&="
    XOR_ASSIGN.3: "^="
    OR_ASSIGN.3: "|="
    RIGHT_OP.2: ">>"
    LEFT_OP.2: "<<"
    INC_OP.2: "++"
    DEC_OP.2: "--"
    PTR_OP.2: "->"
    AND_OP.2: "&&"
    OR_OP.2: "||"
    LE_OP.2: "<="
    GE_OP.2: ">="
    EQ_OP.2: "=="
    NE_OP.2: "!="

    WHITE_SPACE.10: /[ \t\v\n\f]/x
    %ignore WHITE_SPACE

    COMMENT.10: /\/\/.*/
    %ignore COMMENT

    %import common.C_COMMENT
    %ignore C_COMMENT
    ''',
    "python_grammar": """
        start   : single_input 
            | file_input 
            | eval_input 
        single_input    : simple_stmt 
                        | compound_stmt 
        file_input  : stmt 
                    | file_input 
                    | file_input stmt 
        eval_input  : testlist 
        decorator   : "@" dotted_name 
                    | "@" dotted_name "(" arguments ")" 
        decorators  : decorator 
                    | decorators decorator 
        decorated   : decorators classdef 
                    | decorators funcdef 
                    | decorators async_funcdef 
        async_funcdef   : "async" funcdef 
        funcdef : "def" name "(" ")" ":" suite 
                | "def" name "(" parameters ")" ":" suite 
                | "def" name "(" ")" ":" RARROW test suite 
                | "def" name "(" parameters ")" ":" RARROW test suite 
        parameters  : paramvalue paramlist 
                    | paramvalue paramlist "," "/" paramlist 
                    | paramvalue paramlist "," starparams 
                    | paramvalue paramlist "," kwparams 
                    | paramvalue paramlist "," "/" paramlist "," starparams 
                    | paramvalue paramlist "," "/" paramlist "," kwparams 
                    | starparams 
                    | kwparams 
        paramlist   : 
                    | "," paramvalue paramlist 
        starparams  : starparam poststarparams 
                    | starguard poststarparams 
        starparam   : "*" typedparam 
                    | "*" 
        starguard   : "*" 
        poststarparams  : paramlist 
                        | paramlist "," kwparams 
        kwparams    : DOUBLESTAR typedparam 
                    | DOUBLESTAR typedparam "," 
        paramvalue  : typedparam 
                    | typedparam "=" test 
        typedparam  : name 
                    | name ":" test 
        lambdef : "lambda" ":" test 
                | "lambda" lambda_params ":" test 
        lambdef_nocond  : "lambda" ":" test_nocond 
                        | "lambda" lambda_params ":" test_nocond 
        lambda_params   : lambda_paramvalue lambda_paramlist 
                        | lambda_paramvalue lambda_paramlist "," lambda_starparams 
                        | lambda_paramvalue lambda_paramlist "," lambda_kwparams 
        lambda_paramlist    : 
                            | "," lambda_paramvalue lambda_paramlist 
        lambda_paramvalue   : name 
                            | name "=" test 
        lambda_starparams   : "*" lambda_paramlist 
                            | "*" name lambda_paramlist 
                            | "*" lambda_paramlist "," lambda_kwparams 
                            | "*" name lambda_paramlist "," lambda_kwparams 
        lambda_kwparams : DOUBLESTAR name 
                        | DOUBLESTAR name "," 
        stmt    : simple_stmt 
                | compound_stmt 
        simple_stmt : small_stmt small_stmt_list 
                    | small_stmt small_stmt_list ";" 
        small_stmt_list : 
                        | ";" small_stmt small_stmt_list 
        small_stmt  : expr_stmt 
                    | assign_stmt 
                    | del_stmt 
                    | pass_stmt 
                    | flow_stmt 
                    | import_stmt 
                    | global_stmt 
                    | nonlocal_stmt 
                    | assert_stmt 
        expr_stmt   : testlist_star_expr 
        assign_stmt : annassign 
                    | augassign 
                    | assign 
        annassign   : testlist_star_expr ":" test 
                    | testlist_star_expr ":" test "=" test 
        assign  : testlist_star_expr assign_follow_list 
        assign_follow_list  : "=" yield_expr 
                            | "=" testlist_star_expr 
                            | "=" yield_expr assign_follow_list 
                            | "=" testlist_star_expr assign_follow_list 
        augassign   : testlist_star_expr augassign_op yield_expr 
                    | testlist_star_expr augassign_op testlist 
        augassign_op    : PLUSEQUAL 
                        | MINUSEQUAL 
                        | STAREQUAL 
                        | ATEQUAL 
                        | SLASHEQUAL 
                        | PERCENTEQUAL 
                        | AMPEREQUAL 
                        | VBAREQUAL 
                        | CIRCUMFLEXEQUAL 
                        | LEFTSHIFTEQUAL 
                        | RIGHTSHIFTEQUAL 
                        | DOUBLESTAREQUAL 
                        | DOUBLESLASHEQUAL 
        testlist_star_expr  : test_or_star_expr 
                            | test_or_star_expr "," testlist_star_expr 
                            | test_or_star_expr "," 
        del_stmt    : "del" exprlist 
        pass_stmt   : "pass" 
        flow_stmt   : break_stmt 
                    | continue_stmt 
                    | return_stmt 
                    | raise_stmt 
                    | yield_stmt 
        break_stmt  : "break" 
        continue_stmt   : "continue" 
        return_stmt : "return" 
                    | "return" testlist 
        yield_stmt  : yield_expr 
        raise_stmt  : "raise" 
                    | "raise" test 
                    | "raise" test "from" test 
        import_stmt : import_name 
                    | import_from 
        import_name : "import" dotted_as_names 
        import_from : "from" dotted_name "import" "*" 
                    | "from" dotted_name "import" "(" import_as_names ")" 
                    | "from" dotted_name "import" import_as_names 
                    | "from" dots dotted_name "import" "*" 
                    | "from" dots dotted_name "import" "(" import_as_names ")" 
                    | "from" dots dotted_name "import" import_as_names 
                    | "from" dots "import" "*" 
                    | "from" dots "import" "(" import_as_names ")" 
                    | "from" dots "import" import_as_names 
        dots    : "." 
                | "." dots 
        import_as_name  : name 
                        | name "as" name 
        dotted_as_name  : dotted_name 
                        | dotted_name "as" name 
        import_as_names : import_as_name import_as_name_list 
                        | import_as_name import_as_name_list "," 
        import_as_name_list : 
                            | "," import_as_name import_as_name_list 
        dotted_as_names : dotted_as_name dotted_as_name_list 
        dotted_as_name_list : 
                            | "," dotted_as_name dotted_as_name_list 
        dotted_name : name dotted_name_list 
        dotted_name_list    : 
                            | "." name dotted_name_list 
        global_stmt : "global" name comma_name_list 
        nonlocal_stmt   : "nonlocal" name comma_name_list 
        comma_name_list : 
                        | "," name comma_name_list 
        assert_stmt : "assert" test 
                    | "assert" test "," test 
        compound_stmt   : if_stmt 
                        | while_stmt 
                        | for_stmt 
                        | try_stmt 
                        | match_stmt 
                        | with_stmt 
                        | funcdef 
                        | classdef 
                        | decorated 
                        | async_stmt 
        async_stmt  : "async" funcdef 
                    | "async" with_stmt 
                    | "async" for_stmt 
        if_stmt : "if" test ":" suite elifs 
                | "if" test ":" suite elifs "else" ":" suite 
        elifs   : 
                | "elif" test ":" suite elifs 
        while_stmt  : "while" test ":" suite 
                    | "while" test ":" suite "else" ":" suite 
        for_stmt    : "for" exprlist "in" testlist ":" suite 
                    | "for" exprlist "in" testlist ":" suite "else" ":" suite 
        try_stmt    : "try" ":" suite except_clauses 
                    | "try" ":" suite except_clauses "else" ":" suite 
                    | "try" ":" suite except_clauses finally 
                    | "try" ":" suite except_clauses "else" ":" suite finally 
                    | "try" ":" suite finally 
        finally : "finally" ":" suite 
        except_clauses  : except_clause 
                        | except_clause except_clauses 
        except_clause   : "except" ":" suite 
                        | "except" test ":" suite 
                        | "except" test "as" name ":" suite 
        with_stmt   : "with" with_items ":" suite 
        with_items  : with_item with_item_list 
        with_item_list  : 
                        | "," with_item with_item_list 
        with_item   : test 
                    | test "as" name 
        match_stmt  : "match" test ":" cases 
        cases   : case 
                | case cases 
        case    : "case" pattern ":" suite 
                | "case" pattern "if" test ":" suite 
        pattern : sequence_item_pattern "," _sequence_pattern 
                | as_pattern 
        as_pattern  : or_pattern "as" name 
        or_pattern  : closed_pattern closed_pattern_list 
        closed_pattern_list : 
                            | "|" closed_pattern closed_pattern_list 
        closed_pattern  : literal_pattern 
                        | NAME 
                        | "_" 
                        | attr_pattern 
                        | "(" as_pattern ")" 
                        | "[" _sequence_pattern "]" 
                        | "(" ")" 
                        | "(" sequence_item_pattern "," _sequence_pattern ")" 
                        | "{" "}" 
                        | "{" mapping_item_pattern mapping_item_list "}" 
                        | "{" mapping_item_pattern mapping_item_list "," "}" 
                        | "{" DOUBLESTAR NAME "}" 
                        | "{" DOUBLESTAR NAME "," "}" 
                        | "{" mapping_item_pattern mapping_item_list "," DOUBLESTAR NAME "}" 
                        | "{" mapping_item_pattern mapping_item_list "," DOUBLESTAR NAME "," "}" 
                        | class_pattern 
        mapping_item_list   : 
                            | "," mapping_item_pattern mapping_item_list 
        literal_pattern : inner_literal_pattern 
        inner_literal_pattern   : "None" 
                                | "True" 
                                | "False" 
                                | STRING 
                                | number 
        attr_pattern    : NAME "." NAME dot_name_list 
        dot_name_list   : 
                        | "." NAME dot_name_list 
        name_or_attr_pattern    : NAME dot_name_list 
        mapping_item_pattern    : literal_pattern ":" as_pattern 
                                | attr_pattern ":" as_pattern 
        _sequence_pattern   : 
                            | sequence_item_pattern sequence_item_list 
                            | sequence_item_pattern sequence_item_list "," 
        sequence_item_list  : 
                            | "," sequence_item_pattern sequence_item_list 
        sequence_item_pattern   : as_pattern 
                                | "*" NAME 
        class_pattern   : name_or_attr_pattern "(" ")" 
                        | name_or_attr_pattern "(" arguments_pattern ")" 
                        | name_or_attr_pattern "(" arguments_pattern "," ")" 
        arguments_pattern   : pos_arg_pattern 
                            | pos_arg_pattern "," keyws_arg_pattern 
                            | keyws_arg_pattern 
        pos_arg_pattern : as_pattern as_pattern_list 
        as_pattern_list : 
                        | "," as_pattern as_pattern_list 
        keyws_arg_pattern   : keyw_arg_pattern keyw_arg_list 
        keyw_arg_list   : 
                        | "," keyw_arg_pattern keyw_arg_list 
        keyw_arg_pattern    : NAME "=" as_pattern 
        suite   : simple_stmt 
                | stmt_list 
        stmt_list   : stmt 
                    | stmt stmt_list 
        test    : or_test 
                | or_test "if" or_test "else" test 
                | lambdef 
                | assign_expr 
        assign_expr : name COLONEQUAL test 
        test_nocond : or_test 
                    | lambdef_nocond 
        or_test : and_test or_and_test_list 
        or_and_test_list    : 
                            | "or" and_test or_and_test_list 
        and_test    : not_test_ and_not_test_list 
        and_not_test_list   : 
                            | "and" not_test_ and_not_test_list 
        not_test_   : "not" not_test_ 
                    | comparison 
        comparison  : expr comp_op_expr_list 
        comp_op_expr_list   : 
                            | comp_op expr comp_op_expr_list 
        star_expr   : "*" expr 
        expr    : or_expr 
        or_expr : xor_expr bar_xor_list 
        bar_xor_list    : 
                        | "|" xor_expr bar_xor_list 
        xor_expr    : and_expr xor_and_list 
        xor_and_list    : 
                        | "^" and_expr xor_and_list 
        and_expr    : shift_expr and_shift_list 
        and_shift_list  : 
                        | "&" shift_expr and_shift_list 
        shift_expr  : arith_expr shift_arith_list 
        shift_arith_list    : 
                            | _shift_op arith_expr shift_arith_list 
        arith_expr  : term add_term_list 
        add_term_list   : 
                        | _add_op term add_term_list 
        term    : factor mul_factor_list 
        mul_factor_list : 
                        | _mul_op factor mul_factor_list 
        factor  : _unary_op factor 
                | power 
        _unary_op   : "+" 
                    | "-" 
                    | "~" 
        _add_op : "+" 
                | "-" 
        _shift_op   : LEFTSHIFT 
                    | RIGHTSHIFT 
        _mul_op : "*" 
                | "@" 
                | "/" 
                | "%" 
                | DOUBLESLASH 
        comp_op : "<" 
                | ">" 
                | EQEQUAL 
                | GREATEREQUAL 
                | LESSEQUAL 
                | NOTEQUAL 
                | "in" 
                | "not" "in" 
                | "is" 
                | "is" "not" 
        power   : await_expr 
                | await_expr DOUBLESTAR factor 
        await_expr  : atom_expr 
                    | "await" atom_expr 
        atom_expr   : atom_expr "(" ")" 
                    | atom_expr "(" arguments ")" 
                    | atom_expr "[" subscriptlist "]" 
                    | atom_expr "." name 
                    | atom 
        atom    : "(" yield_expr ")" 
                | "(" ")" 
                | "(" _tuple_inner ")" 
                | "(" test_or_star_expr comp_fors ")" 
                | "(" test_or_star_expr comp_fors comp_if ")" 
                | "[" "]" 
                | "[" _exprlist "]" 
                | "[" test_or_star_expr comp_fors "]" 
                | "[" test_or_star_expr comp_fors comp_if "]" 
                | "{" "}" 
                | "{" _dict_exprlist "}" 
                | "{" key_value comp_fors "}" 
                | "{" key_value comp_fors comp_if "}" 
                | "{" _exprlist "}" 
                | "{" test comp_fors "}" 
                | "{" test comp_fors comp_if "}" 
                | name 
                | number 
                | string_concat 
                | "(" test ")" 
                | ELLIPSIS 
                | "None" 
                | "True" 
                | "False" 
        string_concat   : string 
                        | string string_concat 
        _tuple_inner    : test_or_star_expr "," 
                        | test_or_star_expr test_star_list 
                        | test_or_star_expr test_star_list "," 
        test_star_list  : "," test_or_star_expr 
                        | "," test_or_star_expr test_star_list 
        test_or_star_expr   : test 
                            | star_expr 
        subscriptlist   : subscript 
                        | subscript "," 
                        | subscript sub_comma_list 
                        | subscript sub_comma_list "," 
        sub_comma_list  : "," subscript 
                        | "," subscript sub_comma_list 
        subscript   : test 
                    | ":" 
                    | test ":" 
                    | test ":" test 
                    | test ":" sliceop 
                    | test ":" test sliceop 
                    | ":" test 
                    | ":" test sliceop 
                    | ":" sliceop 
        sliceop : ":" 
                | ":" test 
        exprlist    : expr 
                    | star_expr 
                    | expr "," 
                    | expr expr_star_expr_list 
                    | expr expr_star_expr_list "," 
                    | star_expr "," 
                    | star_expr expr_star_expr_list 
                    | star_expr expr_star_expr_list "," 
        expr_star_expr_list : "," expr 
                            | "," star_expr 
                            | "," expr expr_star_expr_list 
                            | "," star_expr expr_star_expr_list 
        testlist    : test 
                    | testlist_tuple 
        testlist_tuple  : test "," 
                        | test comma_test_list 
                        | test comma_test_list "," 
        comma_test_list : "," test 
                        | "," test comma_test_list 
        _dict_exprlist  : key_value key_value_expr_list 
                        | key_value key_value_expr_list "," 
                        | DOUBLESTAR expr key_value_expr_list 
                        | DOUBLESTAR expr key_value_expr_list "," 
        key_value_expr_list : 
                            | "," key_value key_value_expr_list 
                            | "," DOUBLESTAR expr key_value_expr_list 
        key_value   : test ":" test 
        _exprlist   : test_or_star_expr test_star_zero_list 
                    | test_or_star_expr test_star_zero_list "," 
        test_star_zero_list : 
                            | "," test_or_star_expr test_star_zero_list 
        classdef    : "class" name ":" suite 
                    | "class" name "(" ")" ":" suite 
                    | "class" name "(" arguments ")" ":" suite 
        arguments   : argvalue argvalue_list 
                    | argvalue argvalue_list "," 
                    | argvalue argvalue_list "," starargs 
                    | argvalue argvalue_list "," kwargs 
                    | starargs 
                    | kwargs 
                    | test comp_fors 
                    | test comp_fors comp_if 
        argvalue_list   : 
                        | "," argvalue argvalue_list 
        starargs    : stararg stararg_list argvalue_list 
                    | stararg stararg_list argvalue_list "," kwargs 
        stararg_list    : 
                        | "," stararg stararg_list 
        stararg : "*" test 
        kwargs  : DOUBLESTAR test argvalue_list 
        argvalue    : test 
                    | test "=" test 
        comp_fors   : comp_for 
                    | comp_for comp_fors 
        comp_for    : "for" exprlist "in" or_test 
                    | "async" "for" exprlist "in" or_test 
        comp_if : "if" test_nocond 
        yield_expr  : "yield" 
                    | "yield" testlist 
                    | "yield" "from" test 
        number  : DEC_NUMBER 
                | HEX_NUMBER 
                | BIN_NUMBER 
                | OCT_NUMBER 
                | FLOAT_NUMBER 
                | IMAG_NUMBER 
        string  : STRING 
                | LONG_STRING 
        name    : NAME 
                | "match" 
                | "case" 
                | "type" 
                | "_" 



        # start of tokens

		NAME: /[^\W\d]\w*/

        DEC_NUMBER:   /([1-9]([_]?[0-9])*)|[0]+([_]?[0])*/
        HEX_NUMBER.2: /0[xX]([_]?([0-9a-fA-F]))+/
        OCT_NUMBER.2: /0[oO]([_]?[0-7])+/
        BIN_NUMBER.2: /0[bB]([_]?[01])+/

        FLOAT_NUMBER.2: /([0-9]([_]?[0-9])*[eE][+-][0-9]([_]?[0-9])*)|(((\.[0-9]([_]?[0-9])*)|([0-9]([_]?[0-9])*\.[0-9]([_]?[0-9])*))([eE][+-][0-9]([_]?[0-9])*)?)/
        IMAG_NUMBER.2: /(([0-9]([_]?[0-9])*)|(([0-9]([_]?[0-9])*[eE][+-][0-9]([_]?[0-9])*)|(((\.[0-9]([_]?[0-9])*)|([0-9]([_]?[0-9])*\.[0-9]([_]?[0-9])*))([eE][+-][0-9]([_]?[0-9])*)?)))[jJ]/

        %import python.STRING -> STRING
        %import python.LONG_STRING -> LONG_STRING

        %import common.SH_COMMENT
        %ignore SH_COMMENT

        WHITE_SPACE.10: /[ \t\f\t\r]/
        %ignore WHITE_SPACE

        EQEQUAL: "=="
		NOTEQUAL: "!="
		LESSEQUAL: "<="
		GREATEREQUAL: ">="
		LEFTSHIFT.4: "<<"
		RIGHTSHIFT.4: ">>"
		DOUBLESTAR: "**"
		PLUSEQUAL: "+="
		MINUSEQUAL: "-="
		STAREQUAL: "*="
		SLASHEQUAL: "/="
		PERCENTEQUAL: "%="
		AMPEREQUAL: "&="
		VBAREQUAL: "|="
		CIRCUMFLEXEQUAL: "^=" 
		LEFTSHIFTEQUAL.5: "<<="
		RIGHTSHIFTEQUAL.5: ">>="
		DOUBLESTAREQUAL: "**="
		DOUBLESLASH: "//"
		DOUBLESLASHEQUAL.5: "//=" 
		ATEQUAL: "@="
		RARROW: "->"
		ELLIPSIS: "..."
		COLONEQUAL: ":="
    """
}

# @profile
def main(input_string, grammar, args):    
    parser = None

    with open('gfg.py', 'r') as file:
        input_string = file.read()

    if args.cyk:
        parser = Lark(grammar, parser='cyk', ordered_sets=False)
    elif args.earley:
        print("Earley")
        parser = Lark(grammar, parser='earley', ambiguity="forest", lexer='basic')

    start_time = time.time()
    res = parser.parse(input_string)
    print(res)

    end_time = time.time()

    print(end_time-start_time)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse the given input string with the specified grammar')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--cyk', action='store_true', help='Process using cyk')
    group.add_argument('--earley', action='store_true', help='Process using earley')

    parser.add_argument('--grammar', type=str, default="b_grammar", help='grammar to use')
    parser.add_argument('--input', type=str, required=True, help='input string to parse')

    args = parser.parse_args()
    

    print(args.input)
    main(args.input, grammars[args.grammar], args)
