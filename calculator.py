import re

class Calculator(object):
	"""this class has a search phrase, the phrase will be checked against a regular expression making sure it 
	is a simple integer expression using only (+-/*) and will evaluate this expression if it is of the correct form"""
	def __init__(self, phrase):
		self.phrase = phrase

	def is_safe(self):
		pattern = re.compile('^((\d+\s*[\+\-\*\/]\s*\d+\s*)([\+\-\*\/]\s*\d+\s*)*)$')
		if pattern.match(self.phrase):
			return True
		else:
			return False

	def evaluate(self):
		#double check again that the expression is safe to evaluate
		if self.is_safe():
			#clear the namespace to make sure again that it is safe
			ns = {'__builtins__': None}
			try: 
				return eval(self.phrase, ns)
			except:
				return None
		else:
			return None