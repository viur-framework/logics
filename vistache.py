#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
vistache is a template language based on the simplicity of Mustache,
but allowing for expressions based on ViUR logics as its values.
"""

from logics import Interpreter
from parser import Node, ParseException

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

	def parse(self, s = None, row = 1, col = 1):

		def updatePos(s, row, col):
			rows = s.count("\n")
			if rows:
				row += rows
				col = len(s[s.rfind("\n") + 1:])

			else:
				col += len(s)

			return row, col

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
				row, col = updatePos(s[:start], row, col)
				block.children.append(Node("tstring", s[:start]))

			start += len(self.startDelimiter)
			expr = s[start:end]
			end += len(self.endDelimiter)

			#print("expr   = %r %d %d" % (expr, row, col))

			if expr.startswith(self.startBlock):
				row, col = updatePos(self.startDelimiter, row, col)

				expr = expr[len(self.startBlock):]

				try:
					node = super(Template, self).parse(expr)
				except ParseException as e:
					raise ParseException(row + e.row - 1, col + e.col - 1, e.expecting)

				blocks.append((node, block))
				block = Node("tblock")

			elif expr.startswith(self.endBlock):
				if not blocks:
					raise ParseException(row, col, "Closing block without opening block")

				row, col = updatePos(self.startDelimiter + expr, row, col)

				node, nblock = blocks.pop()
				nblock.children.append(Node("tloop", children=[node, block]))
				block = nblock

			else:
				row, col = updatePos(self.startDelimiter, row, col)

				try:
					node = super(Template, self).parse(expr)
				except ParseException as e:
					raise ParseException(row + e.row - 1, col + e.col - 1, e.expecting)

				row, col = updatePos(expr, row, col)
				block.children.append(node)

			row, col = updatePos(self.endDelimiter, row, col)

			s = s[end:]

		if blocks:
			raise ParseException(row, col, "%d blocks are still open, expecting %s" % (len(blocks), "".join([("%s%s%s" % (self.startDelimiter, self.endBlock, self.endDelimiter)) for b in blocks])))

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
		if not self.ast:
			return ""

		return self.execute(self.ast, fields)
