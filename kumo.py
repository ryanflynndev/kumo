

DIGITS = '0123456789'
#This is all our digits, and helps use determine if our char is a digit or not.

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f' in File {self.pos_start.fname} at line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class Position:
    def __init__(self, index, ln, col, fname, ftext):
        self.index = index 
        self.ln = ln
        self.col = col 
        self.fname = fname 
        self.ftext = ftext
    
    def advance(self, current_char):
        self.index += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self 
    
    def copy(self): 
        return Position(self.index, self.ln, self.col, self.fname, self.ftext)

#These are all our tokens
TT_INT = 'TT_INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        #This makes a token with a type for example INT and a value which can be something like 5

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
        #This is just a way to represent that information. If it has a value it will go INT:5 if not it will just go PLUS for example.

class Lexer:
    def __init__(self, fname, text):
        self.fname = fname
        self.text = text
        #text we will be processing
        self.pos = Position(-1, 0, -1, fname, text)
        #current pos
        self.current_char = None 
        #current char
        self.advance()
        #We call the advance method on intialization of our lexer. This will make it start out at 0.

    def advance(self):
        self.pos.advance(self.current_char)
        #This advances to the next character in the text
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
        #This grabs the current character only if the index is not the length of the text. If it is we set the current char to none.

    def make_tokens(self):
        tokens = []
        # This will hold our tokens
        while self.current_char != None: 
            #This a loop that will got through every char what token the current char will hold as long as the current char is not None.
            if self.current_char in ' \t':
                self.advance() 
                #This ignores all spaces and tabs, and calls advance when it sees one
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
                #This looks to see if our char is in the digits constant, and if so it makes into a number.
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None 

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


class NumberNode: 
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


def run(fname, text):
    lexer = Lexer(fname, text)
    tokens, error = lexer.make_tokens()

    return tokens, error
