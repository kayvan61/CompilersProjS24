# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

class BLexer(object):
    # List of token names.   This is always required
    tokens = [
       'b',
       'a'
    ]

    # Regular expression rules for simple tokens
    t_b  = r'[b]'
    t_a  = r'[a]'

    # A string containing ignored characters (spaces, tabs and newlines)
    t_ignore  = ' \t\n'

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
    def token(self,):
        return self.lexer.token()

if __name__ == "__main__":
    # Build the lexer and try it out
    l = BLexer()
    l.build()           # Build the lexer
    l.input("bbb")     # Test it

    while True:
        tok = l.token()
        if not tok:
            print("-----------")
            break
        print(tok.type, tok.value)

    print(l.tokens)