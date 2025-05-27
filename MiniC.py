from Scanner.Token import *
from Scanner.SourceFile import *
from Scanner.SourcePos import *
from Scanner.Scanner import *
from Parser.Parser import *

import sys

class MiniC:
    def __init__(self):
        self.scanner = 0
        self.parser = 0
        self.reporter = 0

    def compileProgram(self, sourceName):
        print("********** " + "MiniC Compiler" + " **********")
        source = SourceFile(sourceName)
        
        print("Syntax Analysis ...")        
        self.scanner = Scanner(source)
        """
        Enable this to observe the sequence of tokens
        delivered by the scanner:
        """
        #scanner.enableDebugging()
        self.reporter = ErrorReporter()
        self.parser = Parser(self.scanner, self.reporter)
        self.parser.parse() # 1st pass

        '''
        The following loop was used with the first assignment
        to repeatedly request tokens from the scanner.
        The above call to parser.parse() has replaced it
        with Assignment 2.
        '''
        #while True:
        #    t = scanner.scan()  # scan 1 token
        #    if t.kind == Token.EOF: break

        successful = (self.reporter.numErrors == 0)
        if successful:
            print("Compilation was successful.")
        else:
            print("Compilation was unsuccessful.")


miniC = MiniC()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: MiniC filename")
        exit(1)
    sourceName = sys.argv[1]
    miniC.compileProgram(sourceName)