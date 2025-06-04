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

    def accept(self, tokenExpected):
        if self.currentToken.kind == tokenExpected:
            self.currentToken = self.scanner.scan()
        else:
            self.syntaxError('% expected here', Token.spell(tokenExpected))

    def acceptIt(self):
        self.currentToken = self.scanner.scan()

    def syntaxError(self, messageTemplate, tokenQuoted):
        pos = self.currentToken.GetSourcePos()
        if not (tokenQuoted.startswith('"') and tokenQuoted.endswith('"')):
            tokenQuoted = f'"{tokenQuoted}"'
        self.errorReporter.reportError(messageTemplate, tokenQuoted, pos)
        raise SyntaxError()

    @staticmethod
    def isTypeSpecifier(token):
        return token in (Token.VOID, Token.INT, Token.BOOL, Token.FLOAT)

    def parse(self):
        self.currentToken = self.scanner.scan()
        try:
            self.parseProgram()
            if self.currentToken.kind != Token.EOF:
                self.syntaxError('% not expected after end of program', self.currentToken.GetLexeme())
        except SyntaxError:
            while self.currentToken.kind != Token.EOF:
                self.acceptIt()
        return

    def parseProgram(self):
        while Parser.isTypeSpecifier(self.currentToken.kind):
            self.acceptIt()
            if self.currentToken.kind != Token.ID:
                self.syntaxError('% expected here', 'ID')
            self.accept(Token.ID)
            if self.currentToken.kind == Token.LEFTPAREN:
                self.parseFunPart()
            else:
                self.parseVarPart()

    def parseFunPart(self):
        self.acceptIt()
        if Parser.isTypeSpecifier(self.currentToken.kind):
            self.parseParamsList()
        self.accept(Token.RIGHTPAREN)
        self.parseCompoundStmt()

    def parseParamsList(self):
        self.parseParamsDecl()
        while self.currentToken.kind == Token.COMMA:
            self.acceptIt()
            self.parseParamsDecl()

    def parseParamsDecl(self):
        if not Parser.isTypeSpecifier(self.currentToken.kind):
            self.syntaxError('% expected here', 'type specifier')
        self.acceptIt()
        self.accept(Token.ID)
        if self.currentToken.kind == Token.LEFTBRACKET:
            self.acceptIt()
            self.accept(Token.INTLITERAL)
            self.accept(Token.RIGHTBRACKET)

    def parseCompoundStmt(self):
        self.accept(Token.LEFTBRACE)
        while Parser.isTypeSpecifier(self.currentToken.kind):
            self.parseVariableDefinition()
        while self.currentToken.kind not in (Token.RIGHTBRACE, Token.EOF):
            try:
                self.parseStmt()
            except SyntaxError:
                while self.currentToken.kind not in (Token.RIGHTBRACE, Token.EOF, Token.SEMICOLON):
                    self.acceptIt()
                if self.currentToken.kind == Token.SEMICOLON:
                    self.acceptIt()
        if self.currentToken.kind == Token.RIGHTBRACE:
            self.accept(Token.RIGHTBRACE)
        else:
            self.syntaxError('} expected here', Token.spell(self.currentToken.kind))

    def parseVariableDefinition(self):
        self.acceptIt()
        if self.currentToken.kind != Token.ID:
            self.syntaxError('% expected here', 'ID')
        self.accept(Token.ID)
        if self.currentToken.kind == Token.LEFTBRACKET:
            self.acceptIt()
            self.accept(Token.INTLITERAL)
            self.accept(Token.RIGHTBRACKET)
        if self.currentToken.kind == Token.ASSIGN:
            self.acceptIt()
            self.parseInitializer()
        while self.currentToken.kind == Token.COMMA:
            self.acceptIt()
            self.accept(Token.ID)
            if self.currentToken.kind == Token.LEFTBRACKET:
                self.acceptIt()
                self.accept(Token.INTLITERAL)
                self.accept(Token.RIGHTBRACKET)
            if self.currentToken.kind == Token.ASSIGN:
                self.acceptIt()
                self.parseInitializer()
        self.accept(Token.SEMICOLON)

    def parseStmt(self):
        if self.currentToken.kind == Token.LEFTBRACE:
            self.parseCompoundStmt()
        elif Parser.isTypeSpecifier(self.currentToken.kind):
            self.parseVariableDefinition()
        elif self.currentToken.kind == Token.IF:
            self.acceptIt()
            self.accept(Token.LEFTPAREN)
            self.parseExpr()
            self.accept(Token.RIGHTPAREN)
            self.parseStmt()
            if self.currentToken.kind == Token.ELSE:
                self.acceptIt()
                self.parseStmt()
        elif self.currentToken.kind == Token.FOR:
            self.acceptIt()
            self.accept(Token.LEFTPAREN)
            if self.currentToken.kind != Token.SEMICOLON:
                if Parser.isTypeSpecifier(self.currentToken.kind):
                    self.parseVariableDefinition()
                else:
                    self.parseExpr()
                    self.accept(Token.SEMICOLON)
            else:
                self.accept(Token.SEMICOLON)
            if self.currentToken.kind != Token.SEMICOLON:
                self.parseExpr()
            self.accept(Token.SEMICOLON)
            if self.currentToken.kind != Token.RIGHTPAREN:
                self.parseExpr()
            self.accept(Token.RIGHTPAREN)
            self.parseStmt()
        elif self.currentToken.kind == Token.WHILE:
            self.acceptIt()
            self.accept(Token.LEFTPAREN)
            self.parseExpr()
            self.accept(Token.RIGHTPAREN)
            self.parseStmt()
        elif self.currentToken.kind == Token.RETURN:
            self.acceptIt()
            if self.currentToken.kind != Token.SEMICOLON:
                self.parseExpr()
            self.accept(Token.SEMICOLON)
        elif self.currentToken.kind == Token.SEMICOLON:
            self.acceptIt()
        elif self.currentToken.kind == Token.ID:
            self.parseExpr()
            if self.currentToken.kind != Token.SEMICOLON:
                self.syntaxError('";" expected here', Token.spell(self.currentToken.kind))
            self.accept(Token.SEMICOLON)
        else:
            self.parseExpr()
            if self.currentToken.kind != Token.SEMICOLON:
                self.syntaxError('";" expected here', Token.spell(self.currentToken.kind))
            self.accept(Token.SEMICOLON)

    def parseExpr(self):
        if self.currentToken.kind not in (
            Token.ID, Token.INTLITERAL, Token.FLOATLITERAL, Token.BOOLLITERAL, Token.STRINGLITERAL,
            Token.LEFTPAREN, Token.NOT, Token.MINUS
        ):
            self.syntaxError('% is not a valid expression start', self.currentToken.GetLexeme())

        paren_level = 0
        brace_level = 0
        bracket_level = 0
        token_count = 0
        while True:
            if self.currentToken.kind == Token.LEFTPAREN:
                paren_level += 1
            elif self.currentToken.kind == Token.RIGHTPAREN:
                if paren_level == 0:
                    break
                paren_level -= 1
            elif self.currentToken.kind == Token.LEFTBRACE:
                brace_level += 1
            elif self.currentToken.kind == Token.RIGHTBRACE:
                if brace_level > 0:
                    brace_level -= 1
                else:
                    break
            elif self.currentToken.kind == Token.LEFTBRACKET:
                bracket_level += 1
            elif self.currentToken.kind == Token.RIGHTBRACKET:
                if bracket_level > 0:
                    bracket_level -= 1
                else:
                    break
            elif self.currentToken.kind in (Token.SEMICOLON, Token.EOF) and paren_level == 0 and brace_level == 0:
                break
            self.acceptIt()
            token_count += 1
            if token_count > 500:
                break

        if paren_level > 0:
            self.syntaxError(') expected here', self.currentToken.GetLexeme())
        if brace_level > 0:
            self.syntaxError('} expected here', self.currentToken.GetLexeme())
        if bracket_level > 0:
            self.syntaxError('] expected here', self.currentToken.GetLexeme())

    def parseVarPart(self):
        if self.currentToken.kind == Token.LEFTBRACKET:
            self.acceptIt()
            self.accept(Token.INTLITERAL)
            self.accept(Token.RIGHTBRACKET)

        if self.currentToken.kind == Token.ASSIGN:
            self.acceptIt()
            self.parseInitializer()

        while self.currentToken.kind == Token.COMMA:
            self.acceptIt()
            self.accept(Token.ID)
            if self.currentToken.kind == Token.LEFTBRACKET:
                self.acceptIt()
                self.accept(Token.INTLITERAL)
                self.accept(Token.RIGHTBRACKET)
            if self.currentToken.kind == Token.ASSIGN:
                self.acceptIt()
                self.parseInitializer()

        self.accept(Token.SEMICOLON)

    def parseInitializer(self):
        paren_level = 0
        brace_level = 0
        while True:
            if self.currentToken.kind == Token.LEFTPAREN:
                paren_level += 1
            elif self.currentToken.kind == Token.RIGHTPAREN:
                if paren_level > 0:
                    paren_level -= 1
                else:
                    break
            elif self.currentToken.kind == Token.LEFTBRACE:
                brace_level += 1
            elif self.currentToken.kind == Token.RIGHTBRACE:
                if brace_level > 0:
                    brace_level -= 1
                else:
                    break
            elif self.currentToken.kind == Token.SEMICOLON and paren_level == 0 and brace_level == 0:
                break
            elif self.currentToken.kind == Token.EOF:
                break
            self.acceptIt()
        if paren_level > 0:
            self.syntaxError(') expected here', self.currentToken.GetLexeme())
        if brace_level > 0:
            self.syntaxError('} expected here', self.currentToken.GetLexeme())
