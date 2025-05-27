from Scanner.SourcePos import *
from Scanner.Token import *
from Scanner.Scanner import *
from Parser.SyntaxError import *
from ErrorReporter import *

class Parser:
    def __init__(self, lexer, reporter):
        self.scanner = lexer
        self.errorReporter = reporter
        self.currentToken = 0

    # accept() checks whether the current token matches tokenExpected.
    # If so, it fetches the next token
    # If not, it reports a syntax error.
    def accept(self, tokenExpected):
        if self.currentToken.kind == tokenExpected:
            self.currentToken = self.scanner.scan()
        else:
            self.syntaxError('% expected here', Token.spell(tokenExpected))
    
    # acceptIt() unconditionally accepts the current token
    # and fetches the next token from the scanner.
    def acceptIt(self):
        self.currentToken = self.scanner.scan()
    
    def syntaxError(self, messageTemplate, tokenQuoted):
        pos = self.currentToken.GetSourcePos()
        self.errorReporter.reportError(messageTemplate, tokenQuoted, pos)
        raise SyntaxError()

    @staticmethod
    def isTypeSpecifier(token):
        if token in (Token.VOID, Token.INT, Token.BOOL, Token.FLOAT):
            return True
        else:
            return False
    
    # toplevel parse() routine:
    def parse(self):
        self.currentToken = self.scanner.scan() # get first token from scanner...

        try:
            self.parseProgram()
            if self.currentToken.kind != Token.EOF:
                self.syntaxError('% not expected after end of program', self.currentToken.GetLexeme())
        except SyntaxError as s:
            return  # to be refined in Assignment 3...
        return
    
    #    
    # parseProgram():
    #
    # program ::= ( (VOID|INT|BOOL|FLOAT) ID ( FunPart | VarPart ) )*
    #
    #

    def parseProgram(self):
        while Parser.isTypeSpecifier(self.currentToken.kind):
            self.acceptIt()
            self.accept(Token.ID)
            if self.currentToken.kind == Token.LEFTPAREN:
                self.parseFunPart()
            else:
                self.parseVarPart()
    
    #
    # parseFunPart():
    #
    # FunPart ::= ( "(" ParamsList? ")" CompoundStmt )
    #
    #

    def parseFunPart(self):
        # We already know that the current token is "(".
        # Otherwise use accept() !
        self.acceptIt()
        if Parser.isTypeSpecifier(self.currentToken.kind):
            self.parseParamsList()
        self.accept(Token.RIGHTPAREN)
        self.parseCompoundStmt()
    
    #
    # parseParamsList():
    #
    # ParamsList ::= ParamsDecl ( "," ParamsDecl ) *
    #
    #

    def parseParamsList(self):
        # to be completed by you...
        pass
    
    #
    # parseCompoundStmt():
    #
    # CompoundStmt ::= "{" VariableDefinition* Stmt* "}"
    #
    #

    def parseCompoundStmt(self):
        # to be completed by you...
        pass

    #
    # parseVarPart():
    #
    # VarPart ::= ( "[" INTLITERAL "]" )?  ( "=" initializer ) ? ( "," init_decl)* ";"
    #
    #

    def parseVarPart(self):
        # to be completed by you...
        pass
        