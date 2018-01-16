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

	def parse(self, dfn):
		assert self.startDelimiter
		assert self.endDelimiter
		assert self.startBlock
		assert self.endBlock

		assert self.startBlock != self.endBlock

		block = Node("tblock")
		blocks = []

		while dfn:
			#print("dfn = %r" %dfn)

			start = dfn.find(self.startDelimiter)
			if start < 0:
				break

			end = dfn.find(self.endDelimiter, start + len(self.startDelimiter))
			if end < 0:
				break

			if start > 0:
				block.children.append(Node("tstring", dfn[:start]))

			start += len(self.startDelimiter)

			expr = dfn[start:end]
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

			dfn = dfn[end:]

		assert not blocks, "%d blocks unclosed!" % len(blocks)

		if dfn:
			block.children.append(Node("tstring", dfn))

		self.ast = block


	def post_tstring(self, node):
		self.stack.append(node.match)

	def post_tblock(self, node):
		txt = ""

		for c in node.children:
			txt = self.stack.pop() + txt

		self.stack.append(txt)

	def loop_tloop(self, node):
		pass # Just do nothing!

	def post_tloop(self, node):
		print(self.stack)

		self.traverse(node.children[0])
		iterator = self.stack.pop()

		try:
			iter(iterator)
			isIterable = True
		except TypeError:
			isIterable = False

		txt = ""

		if isIterable:
			for i in iterator:
				#self.execute(self.sat, fields, prefix=)
				self.traverse(node.children[1])
				txt += self.stack.pop()

		elif iterator:
			node.children[1].dump()

			self.traverse(node.children[1])
			txt = self.stack.pop()

		print("txt = %r" % txt)
		self.stack.append(txt)

	def render(self, fields = None):
		assert self.ast
		return self.execute(self.ast, fields)

x = Template("""
hello
{{#abc}}so{{#def}}lange{{/}}long{{/}}
world {{xxx}}
""")

#x.ast.dump()
print(x.render({"xxx": "Yolo", "abc": True}))

