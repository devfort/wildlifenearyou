import random

class Alternation(object):
    def __init__(self, *elems):
        self.elems = elems

    def __repr__(self):
        return "<Alternation [%s]>" % ", ".join([repr(x) for x in self.elems])

    def __or__(self, other):
        return Alternation(self, other)

class StringTerminal(object):
    def __init__(self, txt):
        self.txt = txt

    def __repr__(self):
        return repr(self.txt)

    def __or__(self, other):
        return Alternation(self, other)

def generate_string(grammar):
    class GeneratorVisitor(object):
        def visit(self, node):
            return getattr(self, "visit_%s" % node.__class__.__name__)(node)

        def visit_Alternation(self, node):
            return self.visit(random.choice(node.elems))

        def visit_StringTerminal(self, node):
            return node.txt

        def visit_tuple(self, node):
            return "".join([self.visit(x) for x in node])
        visit_list = visit_tuple

        def visit_str(self, node):
            return str(node)
        visit_int = visit_str

    return GeneratorVisitor().visit(grammar)
