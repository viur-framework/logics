#!/usr/bin/env python
#-*- coding: utf-8 -*-

from logics import Interpreter
from logics_parser import Node

class Template(Interpreter):
	startDelimiter = "{{"
	endDelimiter = "}}"

	startBlock = "#"
	endBlock = "/"

	def __init__(self, dfn = None):
		super(Template, self).__init__()
		self.ast = None

		if dfn:
			self.parse(dfn)

	def parse(self, s = None):
		assert self.startDelimiter
		assert self.endDelimiter
		assert self.startBlock
		assert self.endBlock

		assert self.startBlock != self.endBlock

		block = Node("tblock")
		blocks = []

		while s:
			#print("s = %r" %s)

			start = s.find(self.startDelimiter)
			if start < 0:
				break

			end = s.find(self.endDelimiter, start + len(self.startDelimiter))
			if end < 0:
				break

			if start > 0:
				block.children.append(Node("tstring", s[:start]))

			start += len(self.startDelimiter)

			expr = s[start:end]
			end += len(self.endDelimiter)

			#print("expr   = %r" % expr)

			if expr.startswith(self.startBlock):
				expr = expr[len(self.startBlock):]
				expr = super(Template, self).parse(expr)

				blocks.append((expr, block))
				block = Node("tblock")
			elif expr.startswith(self.endBlock):
				assert blocks, "endBlock without startBlock?"

				expr, nblock = blocks.pop()
				nblock.children.append(Node("tloop", children=[expr, block]))
				block = nblock
			else:
				expr = super(Template, self).parse(expr)
				block.children.append(expr)

			s = s[end:]

		assert not blocks, "%d blocks unclosed!" % len(blocks)

		if s:
			block.children.append(Node("tstring", s))

		self.ast = block


	def post_tstring(self, node):
		self.stack.append(node.match)

	def post_tblock(self, node):
		txt = ""

		for c in node.children:
			txt = str(self.stack.pop()) + txt

		self.stack.append(txt)

	def loop_tloop(self, node):
		pass # Just do nothing!

	def post_tloop(self, node):
		self.traverse(node.children[0])
		value = self.stack.pop()

		txt = ""

		if isinstance(value, list):
			fields = self.fields

			for i in value:
				if isinstance(i, dict):
					if self.fields is fields:
						self.fields = fields.copy()

					self.fields.update(i)

				self.traverse(node.children[1])
				txt += self.stack.pop()

			self.fields = fields

		elif value:
			if isinstance(value, dict):
				fields = self.fields
				self.fields = fields.copy()
				self.fields.update(value)

			self.traverse(node.children[1])
			txt = self.stack.pop()

			if isinstance(value, dict):
				self.fields = fields

		self.stack.append(txt)

	def render(self, fields = None):
		assert self.ast
		return self.execute(self.ast, fields)

x = Template("""Hello {{xxx}}
{{#persons}}{{name}} is {{age * 365}} days {{xxx}}
{{/}}
World!""")

print(x.render({"xxx": "Yolo", "persons": [{"name": "John", "age": 33}, {"name": "Doreen", "age": 25}]}))
print(x.render({"xxx": "Yolo", "persons": {"name": "John", "age": 33}}))
