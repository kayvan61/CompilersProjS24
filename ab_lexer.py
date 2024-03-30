# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

class ABLexer(object):
    # List of token names.   This is always required
    tokens = [
        'a',
        'b'
    ]

    # Regular expression rules for simple tokens
    t_a  = r'[a]'
    t_b  = r'[b]'

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
    l = ABLexer()
    l.build()           # Build the lexer
    l.input("abbb")     # Test it

    while True:
        tok = l.token()
        if not tok:
            print("-----------")
            break
        print(tok.type, tok.value)

    print(l.tokens)