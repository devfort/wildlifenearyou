from django import template
from django.template import Context, loader, TemplateSyntaxError

register = template.Library()

# from django snippets: http://www.djangosnippets.org/snippets/300/
@register.tag
def switch(parser, token):
    """
    Switch tag.  Usage::

        {% switch meal %}
            {% case "spam" %}...{% endcase %}
            {% case "eggs" %}...{% endcase %}
            {% defaultcase %}...{% enddefaultcase %}
        {% endswitch %}

    Note that ``{% case %}`` arguments can be variables if you like (as can
    switch arguments, buts that's a bit silly).
    """
    # Parse out the arguments.
    args = token.split_contents()
    if len(args) != 2:
        raise TemplateSyntaxError("%s tag tags exactly 2 arguments." % args[0])

    # Pull out all the children of the switch tag (until {% endswitch %}).
    childnodes = parser.parse(("endswitch",))

    # Remove the {% endswitch %} node so it doesn't get parsed twice.
    parser.delete_first_token()

    # We just care about case children; all other direct children get ignored.
    casenodes = childnodes.get_nodes_by_type(CaseNode)
    defaultnodes = childnodes.get_nodes_by_type(DefaultCaseNode)

    return SwitchNode(args[1], casenodes, defaultnodes)

@register.tag
def case(parser, token):
    """
    Case tag. Used only inside ``{% switch %}`` tags, so see above for those docs.
    """
    args = token.split_contents()
    assert len(args) == 2

    # Same dance as above, except this time we care about all the child nodes
    children = parser.parse(("endcase",))
    parser.delete_first_token()
    return CaseNode(args[1], children)

@register.tag
def defaultcase(parser, token):
    """
    Defaultcase tag. Used only inside ``{% switch %}`` tags, so see above for those docs.
    """
    args = token.split_contents()
    assert len(args) == 1

    children = parser.parse(("enddefaultcase",))
    parser.delete_first_token()
    return DefaultCaseNode(children)

class SwitchNode(template.Node):
    def __init__(self, value, cases, defaultcases):
        self.value = value
        self.cases = cases
        self.defaultcases = defaultcases

    def render(self, context):
        # Resolve the value; if it's a non-existant variable don't even bother
        # checking the values of the cases since they'll never match.
        try:
            value = template.resolve_variable(self.value, context)
        except template.VariableDoesNotExist:
            return ""

        # Check each case, and if it matches return the rendered content
        # of that case (short-circuit).
        for case in self.cases:
            if case.equals(value, context):
                return case.render(context)

        for case in self.defaultcases:
            return case.render(context)

        # No matches; render nothing.
        return ""

class CaseNode(template.Node):
    def __init__(self, value, childnodes):
        self.value = value
        self.childnodes = childnodes

    def equals(self, otherval, context):
        """
        Check to see if this case's value equals some other value. This is
        called from ``SwitchNode.render()``, above.
        """
        try:
            return template.resolve_variable(self.value, context) == otherval
        except template.VariableDoesNotExist:
            # If the variable doesn't exist, it doesn't equal anything.
            return False

    def render(self, context):
        """Render this particular case, which means rendering its child nodes."""
        return self.childnodes.render(context)

class DefaultCaseNode(template.Node):
    def __init__(self, childnodes):
        self.childnodes = childnodes

    def render(self, context):
        """Render this particular case, which means rendering its child nodes."""
        return self.childnodes.render(context)
