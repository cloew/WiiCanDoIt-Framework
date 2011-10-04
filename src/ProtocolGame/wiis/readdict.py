"""
Parses a dictionary from a string the Python way.
"""

def strtodict( s ) :
	"""Returns a dictionary represented by s.  May throw SyntaxError,
	as well as many others, I'm sure.
	"""
	codeline = "d = " + s
	x = {}
	exec( compile(codeline,'strtodict','single'), {}, x )
	return x.get('d',{})


