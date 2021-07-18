import ply.lex as lex
from enum import Enum, auto

class TokenType(Enum):
	COMMENT = auto()
	WHITESPACE = auto()
	NEWLINE = auto()
	PROPERTY = auto()
	ENUM = auto()
	CONST = auto()
	ALIAS = auto()
	ASYNC = auto()
	FUNCTION = auto()
	SIGNAL = auto()
	IDENTIFIER = auto()
	STRING = auto()
	NUMBER = auto()
	OPEN_BRACE = auto()
	CLOSE_BRACE = auto()
	COMMA = auto()
	SEMICOLON = auto()
	COLON = auto()
	PERIOD = auto()
	ASSIGN = auto()
	OPEN_PAREN = auto()
	CLOSE_PAREN = auto()
	OPEN_BRACKET = auto()
	CLOSE_BRACKET = auto()
	DOLLAR = auto()
	LOGICAL_NOT = auto()
	BITWISE_NOT = auto()
	PLUS = auto()
	MINUS = auto()
	TYPEOF = auto()
	TIMES = auto()
	DIVIDE = auto()
	MOD = auto()
	BACKSLASH = auto()
	LSHIFT = auto()
	RSHIFT = auto()
	LT = auto()
	LE = auto()
	GT = auto()
	GE = auto()
	INSTANCEOF = auto()
	IN = auto()
	EQ = auto()
	NEQ = auto()
	EQ3 = auto()
	NEQ3 = auto()
	BITWISE_AND = auto()
	BITWISE_XOR = auto()
	BITWISE_OR = auto()
	LOGICAL_AND = auto()
	LOGICAL_OR = auto()
	QUESTION = auto()

reserved = {
	'property' : 'PROPERTY',
	'enum' : 'ENUM',
	'const' : 'CONST',
	'alias' : 'ALIAS',
	'async' : 'ASYNC',
	'function' : 'FUNCTION',
	'signal' : 'SIGNAL',
}

tokens = [
	'COMMENT',
	'WHITESPACE',
	'NEWLINE',
	'IDENTIFIER',
	'STRING',
	'NUMBER',
	'OPEN_BRACE',
	'CLOSE_BRACE',
	'COMMA',
	'SEMICOLON',
	'COLON',
	'PERIOD',
	'ASSIGN',
	'OPEN_PAREN',
	'CLOSE_PAREN',
	'OPEN_BRACKET',
	'CLOSE_BRACKET',
	'DOLLAR',
	'LOGICAL_NOT',
	'BITWISE_NOT',
	'PLUS',
	'MINUS',
	'TYPEOF',
	'TIMES',
	'DIVIDE',
	'MOD',
	'BACKSLASH',
	'LSHIFT',
	'RSHIFT',
	'LT',
	'LE',
	'GT',
	'GE',
	'INSTANCEOF',
	'IN',
	'EQ',
	'NEQ',
	'EQ3',
	'NEQ3',
	'BITWISE_AND',
	'BITWISE_XOR',
	'BITWISE_OR',
	'LOGICAL_AND',
	'LOGICAL_OR',
	'QUESTION',
]
tokens = tokens + list(reserved.values())

t_COMMENT = r'(/\*(.|\n)*?\*/)|(//.*)'
t_WHITESPACE = r'[ \t]+'
t_STRING = r'"(([^"\n]|(\\"))*")|(\'([^\\\'\n]|(\\\'))*\')'
t_NUMBER = r'[0-9]+'
t_OPEN_BRACE   = r'{'
t_CLOSE_BRACE   = r'}'
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_PERIOD = r'\.'
t_ASSIGN = r'='
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACKET = r'\['
t_CLOSE_BRACKET = r'\]'
t_DOLLAR = r'\$'
t_LOGICAL_NOT = r'!'
t_BITWISE_NOT = r'~'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TYPEOF = r'typeof'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_MOD = r'%'
t_BACKSLASH = r'\\'
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_INSTANCEOF = r'instanceof'
t_IN = r'in'
t_EQ = r'=='
t_NEQ = r'!='
t_EQ3 = r'==='
t_NEQ3 = r'!=='
t_BITWISE_AND = r'&'
t_BITWISE_XOR = r'\^'
t_BITWISE_OR = r'\|'
t_LOGICAL_AND = r'&&'
t_LOGICAL_OR = r'\|\|'
t_QUESTION = r'\?'

def t_IDENTIFIER(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	t.type = reserved.get(t.value,'IDENTIFIER')
	return t

def t_NEWLINE(t):
	r'\n'
	t.lexer.lineno = t.lexer.lineno + 1
	return t

def t_error(t):
	raise Exception("Illegal character '%s'" % t.value[0])

class Lex:
	def __init__(self, data, fn="inline"):
		if not data:
			return
		self.fn = fn
		lexer = lex.lex()
		self.i = 0
		try:
			lexer.input(data)
			self.toks = [tok for tok in lexer]
		except Exception as e:
			raise Exception("%s:%i: %s" % (self.fn, lexer.lineno,str(e)))
		for tok in self.toks:
			tok.type = TokenType[tok.type]
			#print(tok,"value",tok.value)
		
	def clone(self):
		copy = Lex(None)
		copy.fn = self.fn
		copy.i = self.i
		copy.toks = self.toks
		return copy
	def lookAhead(self):
		return self.clone()
	def eof(self):
		return self.i>=len(self.toks)
	def skipWhitespace(self):
		while not self.eof() and \
		      (self.toks[self.i].type == TokenType.WHITESPACE or
		       self.toks[self.i].type == TokenType.NEWLINE or
		       self.toks[self.i].type == TokenType.COMMENT):
			self.i = self.i + 1
	def token(self, required_type):
		self.skipWhitespace()
		if self.eof() or self.toks[self.i].type != required_type:
			raise Exception("%s:%d: Syntax error: expected %s but received %s (%s)" % (self.fn, self.toks[self.i].lineno, required_type, self.toks[self.i].type, self.toks[self.i].value))
		value = self.toks[self.i].value
		self.i = self.i + 1
		return value
	def identifier(self, required_value = None):
		value = self.token(TokenType.IDENTIFIER)
		if required_value and value != required_value:
			self.error("Expected identifier '%s' but got '%s'" % (required_value, value))
		return value
	def delimitedIdentifier(self, delim_type):
		values = []
		values.append(self.token(TokenType.IDENTIFIER))
		while self.optionalToken(delim_type):
			values.append(self.token(TokenType.IDENTIFIER))
		return values
	def optionalTokens(self, *args):
		for arg in args:
			if not self.optionalToken(arg):
				return False;
		return True
	def optionalDelimitedList(self, value_type, delim_type):
		if not self.optionalToken(value_type):
			return False
		while self.optionalToken(delim_type):
			if not self.optionalToken(value_type):
				return False
		return True

	def optionalToken(self, required_type):
		self.skipWhitespace()
		#if not self.eof(): print("wtf",id(self),self.toks[self.i])
		if self.eof() or self.toks[self.i].type != required_type:
			return False
		self.i = self.i + 1
		return True
	def optionalIdentifier(self, required_id):
		self.skipWhitespace()
		if self.eof() or self.toks[self.i].type != TokenType.IDENTIFIER:
			return False
		if self.toks[self.i].value != required_id:
			return False
		self.i = self.i + 1
		return True

	def optionalNoncapitalizedIdentifier(self):
		self.skipWhitespace()
		if self.type() == TokenType.IDENTIFIER and \
		   len(self.value()) and self.value()[0]>='a' and self.value()[0]<='z':
			self.nextToken()
			return True
		return False
	def optionalCapitalizedIdentifier(self):
		self.skipWhitespace()
		if self.type() == TokenType.IDENTIFIER and \
		   len(self.value()) and self.value()[0]>='A' and self.value()[0]<='Z':
			self.nextToken()
			return True
		return False
	def findToken(self, find_token, fail_if_find_first):
		while not self.eof():
			if self.optionalToken(find_token):
				return True
			if self.optionalToken(fail_if_find_first):
				return False
			self.nextToken()
		self.error("Expected either %s or %s" % (find_token, fail_if_find_first))
		
	
	def nextToken(self):
		self.i = self.i + 1
	def type(self):
		return self.toks[self.i].type
	def value(self):
		return self.toks[self.i].value
	def loc(self):
		return self.toks[self.i].lineno
	def error(self, msg):
		raise Exception("%s:%d: %s" % (self.fn, self.toks[self.i].lineno, msg))
