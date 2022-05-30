#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
vistache is a template language inspired by the simple syntax and semantics
of Mustache, but allowing for expressions based on ViUR logics as its values.
"""

__author__ = "Jan Max Meyer"
__copyright__ = "Copyright 2018-2020 by Mausbrand Informationssysteme GmbH"
__version__ = "3.0.0"
__license__ = "LGPLv3"
__status__ = "Production"

import string
from .logics import Interpreter
from .parser import Node, ParseException
from .utility import parseInt, parseFloat

def htmlInsertImage(info, size = None, fallback = None, flip = None):
    isServingUrl = False
    size = parseInt(size, 0)

    if not info:
        info = fallback

    attr = {}

    # check if image is supposed to be mirrored
    if flip is True:
        attr["style"] = "transform: scaleX(-1);"

    # Check for ViUR image info
    if isinstance(info, dict) and all([key in info.keys() for key in ["dlkey", "servingurl"]]):
        img = str(info["servingurl"])

        title = info.get("title", info.get("name"))
        if title:
            attr["title"] = title

        if not img:
            img = "/file/download/" + str(info["dlkey"])
        elif not img.startswith("/_ah/img/"): #DevServer must be punished!
            isServingUrl = True
            img += ("=s%d" % size)

    # Use info as string
    elif info:
        img = str(info)

    else:
        return ""

    attr["src"] = img
    if not isServingUrl and size > 0:
        attr["width"] = size

    return "<img " + " ".join([("%s=\"%s\"" % (k, v)) for k, v in attr.items() if v is not None]) + ">"


class Template(Interpreter):

    def __init__(self,
            dfn = None, emptyValue=None, replaceCharRefs=False,
            startDelimiter="{{", endDelimiter="}}",
            stripLeft="-", stripRight="-",
            startBlock="#", altBlock="|", endBlock="/"
        ):

        super(Template, self).__init__()
        self.ast = None

        self.emptyValue = emptyValue
        self.replaceCharRefs = replaceCharRefs

        self.startDelimiter = startDelimiter
        self.endDelimiter = endDelimiter

        self.stripLeft = stripLeft
        self.stripRight = stripRight

        self.startBlock = startBlock
        self.altBlock = altBlock
        self.endBlock = endBlock

        # Vistache provides generator functions
        self.addFunction(htmlInsertImage)
        self.addFunction("formatCurrency", self.functions["currency"]) # Vistache compatiblity

        if dfn:
            self.parse(dfn)

    def parse(self, s=None, row=1, col=1):

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
        assert self.altBlock
        assert self.endBlock
        assert self.stripLeft
        assert self.stripRight

        assert self.startBlock != self.endBlock and self.startBlock != self.altBlock

        block = Node("tblock")
        blocks = []

        while s:
            #print("s = %r" %s)

            # First, isolate a valid logics expression from the stream

            # Find start delimiter
            estart = start = s.find(self.startDelimiter)
            if start < 0:
                break

            estart += len(self.startDelimiter)

            # Find end delimiter
            eend = end = s.find(self.endDelimiter, estart)
            if end < 0:
                break

            # Check for right-strip marker
            if s[end - len(self.stripRight):end] == self.stripRight:
                eend -= len(self.stripRight)
                end += len(self.endDelimiter)

                # Strip right whitespace by moving the end pointer
                while s[end] in string.whitespace:
                    end += 1
            else:
                end += len(self.endDelimiter)

            # Generate tstring node for static prefix
            if start > 0:
                prefix = s[:start]

                # Check for left-strip marker
                if s[estart:].startswith(self.stripLeft):
                    estart += len(self.stripLeft)
                    prefix = prefix.rstrip(string.whitespace) #this should comply with the stripRight character set

                row, col = updatePos(s[:start], row, col)
                block.children.append(Node("tstring", prefix))

            expr = s[estart:eend]

            if self.replaceCharRefs:
                for find, repl in {
                    "&gt;": ">",
                    "&lt;": "<"
                }.items():
                    expr = expr.replace(find, repl)

            #print("expr   = %r %d %d" % (expr, row, col))

            # Now, compile the blocks into according AST nodes

            # {{#}} startBlock
            if expr.startswith(self.startBlock):
                row, col = updatePos(self.startDelimiter, row, col)

                expr = expr[len(self.startBlock):]

                try:
                    node = super(Template, self).parse(expr)
                except ParseException as e:
                    raise ParseException(row + e.row - 1, col + e.col - 1, e.expecting)

                blocks.append((block, [node], []))
                block = Node("tblock")

            # {{|}} altBlock
            elif expr.startswith(self.altBlock):
                if not blocks:
                    raise ParseException(row, col, "Alternative block without opening block")

                row, col = updatePos(self.altBlock, row, col)
                expr = expr[len(self.altBlock):]

                parent, cnodes, cblocks = blocks[-1]

                if expr.strip(): # look for else-if block
                    try:
                        node = super(Template, self).parse(expr.strip())
                    except ParseException as e:
                        raise ParseException(row + e.row - 1, col + e.col - 1, e.expecting)

                    cnodes.append(node)

                elif not cnodes[-1]: # disallow multiple else blocks
                    raise ParseException(row, col, "Multiple alternative blocks without condition are not allowed")
                else:
                    cnodes.append(None) # else-block

                cblocks.append(block)
                blocks[-1] = (parent, cnodes, cblocks)

                row, col = updatePos(expr, row, col)
                block = Node("tblock")

            # {{/#}} endBlock
            elif expr.startswith(self.endBlock):
                if not blocks:
                    raise ParseException(row, col, "Closing block without opening block")

                row, col = updatePos(self.startDelimiter + expr, row, col)

                parent, cnodes, cblocks = blocks.pop()
                cblocks.append(block)

                assert len(cnodes) == len(cblocks)

                node = None
                while cnodes:
                    condition = cnodes.pop()
                    if not condition: #else
                        node = cblocks.pop()
                    else:
                        node = Node("tloop", children=[condition, cblocks.pop(), node])

                parent.children.append(node)
                block = parent

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
            v = self.stack.pop()
            if v is None:
                v = self.emptyValue

            txt = str(v) + txt

        self.stack.append(txt)

    def loop_tloop(self, node):
        pass # Just do nothing!

    def post_tloop(self, node):
        self.traverse(node.children[0])
        value = self.stack.pop()

        txt = ""

        if isinstance(value, list):
            if value:
                # Save & duplicate the current fields config
                fields = self.fields
                keys = []
                self.fields = fields.copy()

                # Setup loop variable
                self.fields["loop"] = {
                    "length": len(value),
                    "parent": self.fields["loop"] if "loop" in self.fields and isinstance(self.fields["loop"], dict) else None
                }

                for idx, val in enumerate(value):
                    # Update loop variable on each iteration
                    self.fields["loop"].update({
                        "item": val,
                        "index": idx + 1,
                        "index0": idx,
                        "first": val is value[0],
                        "last": val is value[-1]
                    })

                    if isinstance(val, dict):
                        for key in keys:
                            del self.fields[key]

                        self.fields.update(val)
                        keys = [key for key in self.fields.keys() if key != "loop" and key not in fields.keys()]

                    # Call subsequent AST nodes
                    self.traverse(node.children[1])

                    # Enhance result
                    txt += self.stack.pop()

                # Restore original fields
                self.fields = fields
            elif node.children[2]:
                self.traverse(node.children[2])
                txt += self.stack.pop()

        elif value:
            if isinstance(value, dict):
                fields = self.fields
                self.fields = fields.copy()
                self.fields.update({k: v for k, v in value.items() if k not in self.fields})

            self.traverse(node.children[1])
            txt = self.stack.pop()

            if isinstance(value, dict):
                self.fields = fields

        elif node.children[2]:
            self.traverse(node.children[2])
            txt += self.stack.pop()

        self.stack.append(txt)

    def render(self, fields = None):
        if not self.ast:
            return ""

        return self.execute(self.ast, fields)



def main(**kwargs):
    import argparse, json

    ap = argparse.ArgumentParser(description="ViUR Vistache Template Engine")

    ap.add_argument("template", type=str, help="The template to be processed; This can either be a string or a file.")
    ap.add_argument("-D", "--debug", help="Print debug output", action="store_true")
    ap.add_argument("-e", "--environment", help="Import environment as variables", action="store_true")
    ap.add_argument("-v", "--var",  help="Assign1 variables; value can also be a JSON-file", action="append", nargs=2, metavar=("var", "value"))
    ap.add_argument("-r", "--run", help="Run expression using interpreter", action="store_true")
    ap.add_argument("-V", "--version", action="version", version="vistache %s" % __version__)

    args = ap.parse_args()

    # Try to read input from a file.
    try:
        f = open(args.template, "r")
        expr = f.read()
        f.close()

    except IOError:
        expr = args.template

    done = False
    vars = {}

    if args.debug:
        print("expr", expr)

    if args.environment:
        import os
        vars.update(os.environ)

    # Read variables
    if args.var:
        for var in args.var:
            try:
                f = open(var[1], "r")
                vars[var[0]] = json.loads(f.read())
                f.close()

            except ValueError:
                vars[var[0]] = None

            except IOError:
                vars[var[0]] = var[1]

    if args.debug:
        print("vars", vars)

    tpl = Template(dfn=expr, **kwargs)
    if args.run:
        print(tpl.render(vars))
        done = True

    if not done:
        tpl.ast.dump()

