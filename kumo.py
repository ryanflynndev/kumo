#Imports

from strings_with_arrows import *


#This is all our digits, and helps us determine if our char is a digit or not.
DIGITS = '0123456789'


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        #When we make an error we take in the position start and end of the error. And we take the name and some descriptive details
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        #This creates a string that shows the error name and details
        result = f'{self.error_name}: {self.details}'
        #This shows the file name and line number of where it occurred
        result += f' in File {self.pos_start.fname} at line {self.pos_start.ln + 1}'
        #Formats the error text with arrows and a lot more info
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        #This is an error that occurs when an illegal character shows up.
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        #This is an error that occurs when there is invalid syntax
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class Position:
    #Keeps track of index, line number, column number, filename and file text. This is for error reporting
    def __init__(self, index, ln, col, fname, ftext):
        self.index = index 
        self.ln = ln
        self.col = col 
        self.fname = fname 
        self.ftext = ftext
    
    def advance(self, current_char):
        #When we advance we increase the index and column number
        self.index += 1
        self.col += 1
        #Everytime we see a new line we will update the line number and reset the column number
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self 
    
    def copy(self): 
        #This creates a copy of the position
        return Position(self.index, self.ln, self.col, self.fname, self.ftext)

#These are all our tokens
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        #This makes a token with a type for example INT and a value which can be something like 5
        self.type = type_
        self.value = value
        #Checking if there is a position start, and if there is creating the end from it
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

    def __repr__(self):
        #This is just a way to represent that information. If it has a value it will go INT:5 if not it will just go PLUS for example.
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

class Lexer:
    def __init__(self, fname, text):
        #text we will be processing
        self.fname = fname
        self.text = text
        #current position
        self.pos = Position(-1, 0, -1, fname, text)
        #current char
        self.current_char = None 
        #We call the advance method on intialization of our lexer. This will make it start out at 0.
        self.advance()
        

    def advance(self):
        #This advances to the next character in the text
        self.pos.advance(self.current_char)
        #This grabs the current character only if the index is not the length of the text. If it is we set the current char to none.
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
        

    def make_tokens(self):
        # This will hold our tokens
        tokens = []
        #This a loop that will got through every char what token the current char will hold as long as the current char is not None.
        while self.current_char != None: 
            if self.current_char in ' \t':
                #This ignores all spaces and tabs, and calls advance when it sees one
                self.advance() 
                #This looks to see if our char is in the digits constant, and if so it makes into a number.
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
                
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                #Here we store the pos and the current illegal character
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                #Then we return both a empty list of tokens and an illegal character error with the starting pos. The position after advance is called and the illegal character
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        #Adds end of file token at the end
        tokens.append(Token(TT_EOF), pos_start=self.pos)
        #Here we return the tokens and none for the error
        return tokens, None 

    def make_number(self):
        #Here we are making the string representation of our number, and keeping track of how many decimals there are
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        
        #Here we are making sure the current char exists, and that is either a digit or a .
        while self.current_char != None and self.current_char in DIGITS + '.':
            
            if self.current_char == '.':
                #If we find a dot we increment our dot count, and we add the "." to our string repr of our number. If there is more than one we break, because a number can't have more than one decimal.
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'

            else:
                #if it is not a decimal/dot then we just append the current char to our num string
                num_str += self.current_char
            #Goes to next character after drtermining what it is    
            self.advance()
        
        if dot_count == 0:
            #if there are no decimals our char is an integer
            return Token(TT_INT, int(num_str), pos_start, self.pos)
            
        else:
            #if there are decimals then our char is a float
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
            


class NumberNode: 
    #The Number Node is the node in our parser that will take the corresponding number token either a float or int
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        #string representation of number node
        return f'{self.tok}'

class BinOpNode:
    #This is a node for our operator. Ex: PLUS
    def __init__(self, left_node, op_tok, right_node):
        #We take in a left and right node and add our operator token
        self.left_node = left_node
        self.op_tok = op_tok 
        self.right_node = right_node
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

#This ParseResult class will check if there are any errors

class ParseResult:
    def __init__(self):
        self.error = None 
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

class Parser:
    def __init__(self, tokens):
        #Parser goes through the tokens
        self.tokens = tokens 
        self.tok_idx = -1
        self.advance()

    def advance(self):
        #We increment the token index
        self.tok_idx += 1
        #As long as there are still tokens we will go though and find the current token and return it after advancing.
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expression()
        #Checks to see if there is code that still hasn't been parsed. Which means there is a syntax error
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '+', '-', '*' or '/'"))
        return res

    def factor(self):
        #Making a parse result instance every time
        res = ParseResult()
        #Here we grab the current token
        tok = self.current_tok
        #Then we see if its type is of an INT or a FLOAT. If so we advance to the next token and create a number node with the token.
        if tok.type in (TT_INT, TT_FLOAT):
            #does nothing right now 
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        #Returns invalid syntax error if type is not int or float
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int or float"))

    def term(self):
        #Calling binary operation on a factor 
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expression(self):
        #Calling a binary operation on the term
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        # Making an instance of ParseResult for every operation
        res = ParseResult()
        #Takes in either a factor or term
        left = res.register(func())
        #checking if there is an error
        if res.error: return res
        #While the token type is one of the operators given we keep making nodes
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            #check if error
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)

def run(fname, text):
    #Now we finally run our lexer with a file name and the text we want to run
    lexer = Lexer(fname, text)
    #We make tokens out of it
    tokens, error = lexer.make_tokens()
    if error: return None, error
    #Generating the Abstract Syntax Tree
    parser = Parser(tokens)
    ast = parser.parse()

    #Now we return the ast and the error
    return ast, error




#Parser Notes:
# When we add two numbers in our language we will have an expression, two terms, and two factors.
# 10 + 5 * 2
#This is an expression with two terms(10 and 5*2), and three factors (10, 5, and 2)