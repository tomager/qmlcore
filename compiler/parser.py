from .grammar import *
from . import lang

from .outerlex import Lex, TokenType as tok

def parsePyParsing(loc, text, pyparse_grammar_top):
	return pyparse_grammar_top.parseString(text, parseAll = True)

def parseGenericScope(s):
	s.token(tok.OPEN_BRACE)
	count = 1
	value = ""
	while True:
		if s.eof():
			raise Exception("%s:%d: Syntax error: failed trying to parse {}-scope starting here" % (self.fn, self.toks[self.i].lineno))
		if s.type() == tok.OPEN_BRACE:
			count = count + 1
		if s.type() == tok.CLOSE_BRACE:
			s.nextToken()
			count = count - 1
			if not count:
				return value
			value += "}"
		else:
			value += s.value()
			s.nextToken()
			
def parseExpr(s):
	value = ""
	while s.type() != tok.SEMICOLON:
		value += s.value()
		s.nextToken()
	return expression.parseString(value, parseAll = True)
			
# enum_property_declaration
def parseEnumPropertyDecl(s):
	s.token(tok.PROPERTY)
	s.token(tok.ENUM)
	name = s.identifier()
	s.token(tok.OPEN_BRACE)
	values = []
	default = None
	while True:
		values.append(s.identifier())
		if not s.optionalToken(tok.COMMA):
			break
	s.token(tok.CLOSE_BRACE)
	if s.optionalToken(tok.COLON):
		default = s.identifier()
	s.token(tok.SEMICOLON)
	return lang.EnumProperty(name, values, default)

# alias_property_declaration
def parseAliasPropertyDecl(s):
	s.token(tok.PROPERTY)
	s.token(tok.ALIAS)
	name = s.identifier()
	s.token(tok.COLON)
	target = ".".join(s.delimitedIdentifier(tok.PERIOD))
	s.token(tok.SEMICOLON)
	return lang.AliasProperty(name, target)

# property_declaration
def parsePropertyDecl(s):
	start = s.clone()
	s.token(tok.PROPERTY)
	if s.optionalToken(tok.CONST):
		type = 'const'
	else:
		type = s.identifier()
	properties = []
	has_component_decl = False
	while True:
		name = s.identifier()
		value = None
		if s.optionalToken(tok.COLON):
			if s.lookAhead().optionalTokens(tok.IDENTIFIER, tok.OPEN_BRACE):
				value = parseComponentDecl(s)
				has_component_decl = True
			elif s.lookAhead().optionalToken(tok.OPEN_BRACE):
				value = parseGenericScope(s)
			else:
				value = parseExpr(s)
		properties.append((name, value))

		if not s.optionalToken(tok.COMMA):
			break

	if has_component_decl:
		if len(properties) != 1:
			start.error("Component declaring property must be standalone")
	else:
		s.token(tok.SEMICOLON)
		
	return lang.Property(type, properties)

# const_property_declaration
def parseConstPropertyDecl(s):
	start = s.clone()
	s.token(tok.PROPERTY)
	s.token(tok.CONST)
	properties = []
	has_component_decl = False

	name = s.identifier()
	value = None
	s.token(tok.COLON)
	value = parseGenericScope(s)
	properties.append((name, value))

	return lang.Property("const", properties)

# method_declaration [ASYNC] ID... : { code }
# method_declaration_qml [ASYNC] FUNCTION
def parseMethodDeclaration(s):
	names = []
	args = []
	async_ = s.optionalToken(tok.ASYNC)

	if s.optionalToken(tok.FUNCTION):
		event = False
		names.append(".".join(s.delimitedIdentifier(tok.PERIOD)))
		if s.optionalToken(tok.OPEN_PAREN):
			if not s.optionalToken(tok.CLOSE_PAREN):
				args = s.delimitedIdentifier(tok.COMMA)
				s.token(tok.CLOSE_PAREN)
		code = parseGenericScope(s)
	else:
		event = True
		names.append(s.identifier())
		while s.optionalToken(tok.COMMA):
			names.append(s.identifier())
		if s.optionalToken(tok.OPEN_PAREN):
			if not s.optionalToken(tok.CLOSE_PAREN):
				args = s.delimitedIdentifier(tok.COMMA)
				s.token(tok.CLOSE_PAREN)
		s.token(tok.COLON)
		code = parseGenericScope(s)
		
	return lang.Method(names, args, code, event, async_)

# signal_declaration
def parseSignalDecl(s):
	s.token(tok.SIGNAL)
	name = s.identifier()
	s.token(tok.SEMICOLON)
	return lang.Signal(name)

# assign_declaration non_capitalized_ID : EXPR ;
def parseAssignDecl(s):
	name = s.identifier()
	s.token(tok.COLON)
	value = parseExpr(s)
	s.token(tok.SEMICOLON)
	return lang.Assignment(name, value)

# behavior_declaration
def parseBehaviorDecl(s):
	s.identifier("Behavior")
	s.identifier("on")
	names = []
	names.append(".".join(s.delimitedIdentifier(tok.PERIOD)))
	while s.optionalToken(tok.COMMA):
		names.append(".".join(s.delimitedIdentifier(tok.PERIOD)))
	s.token(tok.OPEN_BRACE)
	animation = parseComponentDecl(s)
	s.token(tok.CLOSE_BRACE)
	return lang.Behavior(names, animation)

# id_declaration
def parseIDDecl(s):
	s.identifier("id")
	s.token(tok.COLON)
	name = s.identifier()
	s.token(tok.SEMICOLON)
	return lang.IdAssignment(name)

def parseComponentDecl(s):
	# component_declaration << (component_type + component_scope)
	name = s.identifier()
	s.token(tok.OPEN_BRACE)
	body = []
	while not s.optionalToken(tok.CLOSE_BRACE):

		# list_element_declaration
		if s.optionalIdentifier("ListElement"):
			#print("parsing list_element_declaration")
			body.append(parsePyParsing(s.loc(), parseGenericScope(s), json_object))
			continue
		
		# behavior_declaration
		if s.lookAhead().optionalIdentifier("Behavior"):
			#print("parsing behavior_declaration")
			body.append(parseBehaviorDecl(s))
			continue
		
		# signal_declaration
		if s.lookAhead().optionalToken(tok.SIGNAL):
			#print("parsing signal_declaration")
			body.append(parseSignalDecl(s))
			continue

		# alias_property_declaration
		if s.lookAhead().optionalTokens(tok.PROPERTY, tok.ALIAS):
			#print("parsing alias_property_declaration")
			body.append(parseAliasPropertyDecl(s))
			continue

		# const_property_declaration
		if s.lookAhead().optionalTokens(tok.PROPERTY, tok.CONST):
			#print("parsing const_property_declaration")
			body.append(parseConstPropertyDecl(s))
			continue

		# enum_property_declaration
		if s.lookAhead().optionalTokens(tok.PROPERTY, tok.ENUM):
			#print("parsing enum_property_declaration")
			body.append(parseEnumPropertyDecl(s))
			continue

		# property_declaration
		if s.lookAhead().optionalToken(tok.PROPERTY):
			#print("parsing property_declaration")
			body.append(parsePropertyDecl(s))
			continue
		
		# id_declaration
		if s.lookAhead().optionalIdentifier("id"):
			#print("parsing id_declaration")
			body.append(parseIDDecl(s))
			continue

		# method_declaration [ASYNC] ID... : { code }
		r = s.lookAhead()
		r.optionalToken(tok.ASYNC)
		if r.optionalDelimitedList(tok.IDENTIFIER, tok.COMMA) and \
		   r.optionalToken(tok.OPEN_PAREN) or \
		   (r.optionalToken(tok.COLON) and r.optionalToken(tok.OPEN_BRACE)):
			#print("parsing method_declaration")
			body.append(parseMethodDeclaration(s))
			continue

		# method_declaration_qml [ASYNC] FUNCTION
		r = s.lookAhead()
		r.optionalToken(tok.ASYNC)
		if r.optionalToken(tok.FUNCTION):
			#print("parsing method_declaration_qml")
			body.append(parseMethodDeclaration(s))
			continue

		# assign_declaration non_capitalized_ID : EXPR ;
		r = s.lookAhead()
		if r.optionalNoncapitalizedIdentifier() and r.optionalToken(tok.COLON) and \
		   r.findToken(tok.SEMICOLON, tok.OPEN_BRACE):
			#print("parsing assign_declaration")
			body.append(parseAssignDecl(s))
			continue

		# component_declaration
		r = s.lookAhead()
		if r.optionalCapitalizedIdentifier() and r.optionalToken(tok.OPEN_BRACE):
			#print("parsing component_declaration")
			body.append(parseComponentDecl(s))
			continue
	
		# todo: these don't appear in core/*.qml, and disambiguate trivially as follows:
		# assign_component_declaration ID : ID { ...
		# static_const_declaration CONST ...
		# assign_scope ID { ... (ID starts with lowercase)
		# component_declaration ID { (ID starts with uppercase)

		s.error("unhandled component decl")

	return lang.Component(name, body)

import sys, traceback
def parse(data, fn="inline"):
	try:
		s = Lex(data, fn)
		return [parseComponentDecl(s)]
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)

	sys.exit(1)

	global doc_root_component
	doc_root_component = None
	tree = source.parseString(data, parseAll = True)
	if len(tree) > 0:
		tree[0].doc = doc_root_component
	return tree
