"""
Components for Brython. 
author: Jeyson Molina <jeyson.mco@gmail.com>
"""

ELEMENT, TEXT = 1, 3
DOMEVENTS = ('onclick',
             'oncontextmenu'	,
             'ondblclick',
             'onmousedown',
             'onmouseenter',
             'onmouseleave',
             'onmousemove',
             'onmouseover',
             'onmouseout',
             'onmouseup',
             'onkeydown',
             'onkeypress',
             'onkeyup',)

VAR = 'DYNODE'
HTML_TAGS = ['A', 'ABBR', 'ACRONYM', 'ADDRESS', 'APPLET', 'AREA', 'B', 'BASE',
             'BASEFONT', 'BDO', 'BIG', 'BLOCKQUOTE', 'BODY', 'BR', 'BUTTON',
             'CAPTION', 'CENTER', 'CITE', 'CODE', 'COL', 'COLGROUP', 'DD',
             'DEL', 'DFN', 'DIR', 'DIV', 'DL', 'DT', 'EM', 'FIELDSET', 'FONT',
             'FORM', 'FRAME', 'FRAMESET', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
             'HEAD', 'HR', 'HTML', 'I', 'IFRAME', 'IMG', 'INPUT', 'INS',
             'ISINDEX', 'KBD', 'LABEL', 'LEGEND', 'LI', 'LINK', 'MAP', 'MENU',
             'META', 'NOFRAMES', 'NOSCRIPT', 'OBJECT', 'OL', 'OPTGROUP',
             'OPTION', 'P', 'PARAM', 'PRE', 'Q', 'S', 'SAMP', 'SCRIPT', 'SELECT',
             'SMALL', 'SPAN', 'STRIKE', 'STRONG', 'STYLE', 'SUB', 'SUP',
             'TABLE', 'TBODY', 'TD', 'TEXTAREA', 'TFOOT', 'TH', 'THEAD',
             'TITLE', 'TR', 'TT', 'U', 'UL', 'VAR',
             # HTML5 tags
             'ARTICLE', 'ASIDE', 'AUDIO', 'BDI', 'CANVAS', 'COMMAND', 'DATA',
             'DATALIST', 'EMBED', 'FIGCAPTION', 'FIGURE', 'FOOTER', 'HEADER',
             'KEYGEN', 'MAIN', 'MARK', 'MATH', 'METER', 'NAV', 'OUTPUT',
             'PROGRESS', 'RB', 'RP', 'RT', 'RTC', 'RUBY', 'SECTION', 'SOURCE',
             'TEMPLATE', 'TIME', 'TRACK', 'VIDEO', 'WBR',
             # HTML5.1 tags
             'DETAILS', 'DIALOG', 'MENUITEM', 'PICTURE', 'SUMMARY']


class ObserverAlreadyRegistered(Exception):
    pass


class Property(object):

    """
    Property object that implements observer pattern. Use it in Component objects.
    Values are stored in an internal dictionary using component.iid() as key.
    Observers (binded callback functions) are stored in a similar way.
    """
    component = None
    defaultvalue = None
    observers = None  # List of observers
    storage = None

    def __init__(self, *args, **kwargs):
        self.init(args[0])

    def init(self, default):
        self.storage = {}
        self.observers = {}
        self.defaultvalue = default

    def __get__(self, instance, owner):
        # This happens when prop is called from class instead of instance
        if instance is None:
            return self

        iid = instance.iid()
        try:
            return self.storage[iid]
        except:
            if isinstance(self.defaultvalue, list):
                v = list(self.defaultvalue)
            elif isinstance(self.defaultvalue, dict):
                v = dict(self.defaultvalue)
            else:
                v = self.defaultvalue
            self.storage[iid] = v
            return v

        return self.value

    def __set__(self, instance, value):
        pprint(("SET", value, instance))
        iid = instance.iid()
        try:
            oldvalue = self.storage[iid]
        except:
            self.storage[iid] = value
            self.notify_observers(iid, instance, value)
        else:
            # TODO Comparison against old value works only with numbers and strings. Needs different logic
            # for lists and objects
            if value != oldvalue:
                self.storage[iid] = value
                self.notify_observers(iid, instance, value)

    def reg_observer(self, instance, observer):
        iid = instance.iid()
        try:
            if observer in self.observers[iid]:
                raise ObserverAlreadyRegistered()
            pprint("registing observer %s to %s" % (observer, iid))
            self.observers[iid].append(observer)
        except ObserverAlreadyRegistered:
            pprint("Observer", observer, "already registered to", iid)
        except:
            self.observers[iid] = [observer]

    def unreg_observer(self, instance, observer):
        iid = instance.iid()
        try:
            l = self.observers[iid]
            del l[l.index(observer)]
        except:
            pprint("Cannot unregister observer", observer, ". Not registered.")

    def notify_observers(self, iid, instance, value):
        if iid not in self.observers:
            return
        obs_list = self.observers[iid]
        for observer in obs_list:
            observer(value, instance)

    def force_change(self, instance):
        """
        To force a property value change even if the value didn't changed.
        """
        iid = instance.iid()
        v = self.storage[iid] if iid in self.storage else self.defaultvalue
        self.notify_observers(iid, instance, v)


class ObjectWithProperties(object):

    """An object that has properties (Property) and can bind callbacks to it"""

    cnt = 0

    def __init__(self):
        ObjectWithProperties.cnt += 1
        self.cnt = ObjectWithProperties.cnt

    def iid(self):
        return hex(id(self) + self.cnt)

    def bind(self, propname, callback):
        """Bind instance property to callback"""
        cls = self.__class__
        prop = getattr(cls, propname)
        prop.reg_observer(self, callback)

    def unbind(self, propname, callback):
        cls = self.__class__
        prop = getattr(cls, propname)
        prop.unreg_observer(self, callback)

    def update_with_expression(self, property_name, expression, context, obj=None):
        """
        Updates obj.propname with a value resulting from the evaluation of expression each time
        a property referenced in the expression is changed. Those properties belong to context['self'] obj.
        EJ:
        self.update_with_expression('a', 'self.a + self.b', {'self': cat})

        This translates to:
        "self.a = cat.a + cat.b"  executed every time cat.a or cat.b changes.
        Note that 'self' in expression is object cat as stated in context parameter
        If obj is None then obj=self
        """
        if obj is None:
            obj = self
        context_self = context['self']
        cbackp = self.chain_prop_cback(property_name, expression, context, obj)

        for var in match(expression, REGEX_SELF):
            lastprop = var[5:]
            context_self.bind(lastprop, cbackp)

        # Call manually to set an initial value
        self._chain_prop(None, self, property_name, expression, context, obj)

    def chain_prop_cback(self, propname, expression, context, obj=None):
        """returns a proper callback  that updates self.propname with evaluated expression, to be binded to a property.
        """
        return partial(self._chain_prop, propname=propname, expression=expression, context=context, obj=obj)

    def _chain_prop(self, value, instance, propname, expression, context, obj):
        # assign
        v = eval(expression, context)  # TODO security?
        setattr(obj, propname, v)

    def force_change(self, propname):
        getattr(self.__class__, propname).force_change(self)

class Component(ObjectWithProperties):

    """
    Base Component class. All components inherit from it.
    Every Component is linked with a DOMNode element (component.elem) which is present
    in the site's HTML.
    """
    tag = None  # Tag used to identify components in DOM. If None class name is used.
    rendertag = None  # Tag used to render the component in DOM
    template = ""  # Template used to build the internals of the component
    # Template string is parsed and compiled into a set of instructions
    instructions = []
    elem = Property(None)  # DOMNode
    html = Property(None)
    children = None  # Children Components
    # Ids dict to quickly access child comps by their cid
    # (comp.get('child_cid'))
    ids = {}
    parent = None  # Parent Component.
    # Root component (The first component that initiated the mount)
    root = None
    is_mounted = Property(False)

    def __init__(self, domnode=None):
        super(Component, self).__init__()
        cls = self.__class__
        attrs = dir(cls)
        self._prop_list = []
        self.children = []
        self.ids = {}

        # Bind on_property of instance for each prop
        for attr in attrs:
            a = getattr(cls, attr)
            if isinstance(a, Property):
                #self._prop_list.append(a)
                try:
                    callback = getattr(self, "on_%s" % (attr))
                    self.bind(attr, callback)
                except:
                    pass
        # Default callbacks
        callback = getattr(self, "on_elem")
        self.bind("elem", callback)

        callback = getattr(self, "on_html")
        self.bind("html", callback)

        callback = getattr(self, "on_is_mounted")
        self.bind("is_mounted", callback)

        if domnode == None:
            tag = self.tag if self.rendertag is None else self.rendertag
            self.elem = self._create_domelem(tag)
        else:
            self.elem = domnode

    def mount(self, context=None):
        """
        Process the Component (and its children): Parses instructions, binds properties and renders the DOMNode in the site.
        """
        k = time.time()
        pprint("Mounting", self, "Instructions",
               self.instructions, "Context: ", context)
        self.context = {
            "self": self, "root": self.root} if context is None else context
        self.parse_instructions()

        # Setting props from DOM to Component 
        # Grab props from root domnode and use them to initialize component's
        # props
        pprint("Parsing properties values from DOM to Component")
        for attr in self.elem.attributes:
            try:
                name, value = attr.name, attr.value
                if name not in ['cid', 'rd']:

                    if match_search(value, REGEX_BRACKETS) != -1:
                        setattr(self, name, eval(value[1:-1])) 
                    else:
                        setattr(self, name, value)
            except:
                pass
        # mark as mounted
        self._mark_as_mounted()
        pprint("ET Mount %s" % (time.time() - k), force=True)
        return self

    def _mark_as_mounted(self):
        attr_rd = window.document.createAttribute("rd")
        attr_rd.value = '1'
        self.elem.setAttributeNode(attr_rd)
        self.is_mounted = True

    def parse_instructions(self):
        parentcomp = self
        instruction_set = self.instructions
        context_self = self.context['self']

        for instruction in instruction_set:
            type_ = instruction[0]
            cid = None
            if type_ == TEXT:
                txt = instruction[1]
                comp = self.create_component('text', txt)
                comp.is_mounted = True
            else:
                nodename = instruction[1]
                attributes = instruction[2]
                # Get cid if present
                try:
                    cid = [x[1] for x in attributes if x[0] == 'cid'][0]
                except:
                    cid = None

                if nodename not in HTML_TAGS and nodename != VAR:
                    pprint("CREATE custom component, named", nodename)
                    try:
                        comp = Register.get_component_class(nodename)()
                        #comp.elem = self._create_domelem(comp.tag, '')
                        # Set props to DOM
                        for attr in attributes:
                            name, value = attr
                            attr_dom = window.document.createAttribute(name)
                            attr_dom.value = value
                            comp.elem.setAttributeNode(attr_dom)

                        comp.mount()
                    except Exception as e:
                        pprint("Couldnt add component ", nodename, e)

                elif nodename == VAR:
                    comp = self.create_component(nodename)
                    expression = instruction[2]
                    # TODO who is self? Analyze more.
                    # Bind all attributes in expression
                    comp.update_with_expression(
                        'html', expression, self.context, comp)
                    comp.is_mounted = True
                else:  # Components of classic HTML nodes
                    comp = self.create_component(nodename)

                    # Setting props from Component to DOM
                    for attr in attributes:
                        name, value = attr
                        attr_dom = window.document.createAttribute(name)
                        if (match_search(value, REGEX_BRACKETS) != -1):
                            # Dyn
                            pprint("setting dyn attr", name, value)
                            expression = value[2:-2]  # value= "|{expression}|"
                            # TODO who is self? Analyze more.

                            # Check if is event or normal attribute
                            if name not in DOMEVENTS:
                                comp.elem.setAttributeNode(attr_dom)
                                comp.update_with_expression(
                                    name, expression, self.context, comp.elem)
                            else:
                                # Event
                                eventname = name[2:]
                                pprint(
                                    "BINDING DOM Event", eventname, " to expression", expression)
                                comp.elem.bind(
                                    eventname, context_self.domevent_callback(expression, self.context))

                        else:
                            # Normal attr
                            attr_dom.value = value
                            comp.elem.setAttributeNode(attr_dom)

                    child_instructions = instruction[3]
                    comp.instructions = child_instructions
                    comp.mount(context=self.context)
                    #self.parse_instructions(comp, child_instructions)
            pprint("Adding COMP", comp, comp.tag)

            # Add comp to cid dict for quick retrieval
            context_self._add_cid(comp, cid)
            parentcomp.add(comp)

    def create_component(self, tag, text=''):

        dom_elem = self._create_domelem(tag, text)
        c = HTMLComp(tag, dom_elem)
        c.root = self.root
        #c.elem = dom_elem
        return c

    def _create_domelem(self, tag, text=''):
        if tag == 'text':
            dom = document.createTextNode(text)
            dom_elem = window.__BRYTHON__.DOMNode(dom)
        else:
            dom = document.createElement(tag.upper())
            dom_elem = window.__BRYTHON__.DOMNode(dom)
        return dom_elem

    def on_elem(self, value, instance):
        pprint(("dom element", value))

    def on_html(self, value, instance):
        pprint(("html element", value))

    def on_is_mounted(self, value, instance):
        self.on_mount(self)

    def on_mount(self):
        pass

    def render(self, before=None, after=None):
        """Adds self.elem to parent.elem. It's finally rendered on site when parent.elem is added to a DOMNode that is already on site"""
        pprint("Rendedering", self, "domnode", self.elem,
               "to parent", self.parent, "domnode", self.parent.elem)
        if before is not None:
            self.parent.elem.insertBefore(self.elem, before.elem)
        elif after is not None:
            self.parent.elem.insertAfter(self.elem, after.elem)
        else:
            #self.parent.elem <= self.elem
            pass

    def add(self, comp, before=None, after=None):
        """Adds child component"""
        self.children.append(comp)
        comp.parent = self
        # Sometimes comps are not mounted, we should mount them before render
        if not comp.is_mounted:
            comp.root = self.root
            comp.mount()

        comp.render(before, after)

    def _add_cid(self, comp, cid):
        if cid is not None:
            self.ids[cid] = comp

    def get(self, cid):
        """Gets component by its cid"""
        return self.ids[cid]

    def remove(self, component):
        # Remove component
        del self.children[self.children.index(component)]
        # Remove cid association
        comp_k = None
        for k in self.ids:
            if self.ids[k] == component:
                comp_k = k
                break
        if comp_k is not None:
            del self.ids[comp_k]
        # unmount component
        component.unmount()

    def remove_all(self):
        for c in self.children:
            c.unmount()
        self.children = []
        self.ids = {}

    def unmount(self):
        self.parent.elem.removeChild(self.elem)
        del self.elem

    def add_html(self, html):
        """Simplifies adding HTML elements to a component"""
        tp = TemplateProcessor()
        instructions = tp.parse("<HTMLComp>%s</HTMLComp>" % (html))
        old_instructions = self.instructions
        self.instructions = instructions
        # Parse new instructions, this renders and appends new components to
        # self
        self.parse_instructions(self, instructions)
        self.instructions = old_instructions

    # Properties methods

    # Events Logic
    def domevent_callback(self, expression, context):
        """Returns a callback that evals expression using context as globals"""
        return partial(self._domevent_callback, expression=expression, context=context)

    def _domevent_callback(self, event, expression, context):
        pprint("EVENT", event, "expression", expression)
        eval(expression, context)  # TODO security?


class HTMLComp(Component):

    """Component for normal HTML nodes (<a>, <b>, <div>, <p>, etc.)"""
    value = Property('')

    def __init__(self, tag, domnode=None):
        self.tag = tag
        super(HTMLComp, self).__init__(domnode)

    def on_html(self, value, instance):
        self.elem.innerHTML = value

    def mount(self, context=None):
        self.context = {
            "self": self, "root": self.root} if context is None else context
        self.parse_instructions()
        # mark as mounted
        self._mark_as_mounted()
        return self


# From functools
def partial(func, *args, **keywords):
    """New function with partial application of the given arguments
    and keywords.
    """
    if hasattr(func, 'func'):
        args = func.args + args
        tmpkw = func.keywords.copy()
        tmpkw.update(keywords)
        keywords = tmpkw
        del tmpkw
        func = func.func

    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc


def callback(value, instance):
    pprint(("Value", value, "instance", instance))


CONSOLE_ENABLED = False


def pprint(*args, **kwargs):
    force = kwargs['force'] if 'force' in kwargs else False
    if CONSOLE_ENABLED or force:
        pass
        #print(args)

DP = None
try:
    from browser import document, alert, window, html, console
    from javascript import JSConstructor
    import time
    #jq = window.jQuery
    DP = JSConstructor(window.DOMParser)()
    REGEX_SELF = JSConstructor(window.RegExp)("self\.[A-Za-z0-9_]{1,}", 'g')
    REGEX_BRACKETS = JSConstructor(window.RegExp)("\{(.*?)\}", 'g')

    def match(text, regex):
        jstext = JSConstructor(window.String)(text)
        return jstext.match(regex)

    def match_replace(text, regex, replace):
        jstext = JSConstructor(window.String)(text)
        return jstext.replace(regex, replace)

    def match_search(text, regex):
        jstext = JSConstructor(window.String)(text)
        return jstext.search(regex)
except:
    pprint("No brython and javascript libs.", force=True)

    import re

    REGEX_SELF = re.compile("self\.[A-Za-z0-9_]{1,}")
    REGEX_BRACKETS = re.compile("\{(.*?)\}")

    def match(text, regex):
        return re.findall(regex, text)

    def match_replace(text, regex, replace):
        raise Exception

    def match_search(text, regex):
        raise Exception


Main = []


class Register(object):

    """Registers Components"""
    reg = []

    @classmethod
    def add(cls, comp_cls):
        cls.reg.append(comp_cls)

    @classmethod
    def get_component_class(cls, cls_name):
        cls_ = None
        for comp_cls in Register.reg:
            print(comp_cls.__name__)
            if comp_cls.__name__.upper() == cls_name:
                cls_ = comp_cls
                break
        if cls_ is None:
            pprint("Class component %s not found." % (cls_name))
        return cls_


def compile_comps_cls():
    tp = TemplateProcessor()

    for comp_cls in Register.reg:
        pprint("Initializing ", comp_cls)
        # Parsing template
        comp_cls.instructions = tp.parse(comp_cls.template)
        # End parsing
        if comp_cls.tag is None:
            comp_cls.tag = comp_cls.__name__


def render(event):

    for comp_cls in Register.reg:
        pprint("Initializing elements", comp_cls)
        elems = document.get(selector=comp_cls.tag)
        pprint("Elements found:", len(elems))
        for elem in elems:
            try:
                # If has rd then the component is already initialized
                if elem.rd:
                    continue
            except:
                pass
            mc = comp_cls(elem)
            mc.root = mc
            k = time.time()
            mc.mount()
            print("ET MOUNT", time.time() - k)


def init():
    compile_comps_cls()
    render()


class TemplateProcessor(object):

    """Parses Component's template into an instructions set """
    dp = DP

    def parse(self, template):
        k = time.time()
        self.instructions = []
        data = template.replace('{', '|{').replace('}', '}|')
        dom = self.dp.parseFromString(data, "text/xml")
        rootnode = window.__BRYTHON__.DOMNode(dom).children[0]
        self.instructions = self.parse_children(rootnode)
        pprint("ET %s" % (time.time() - k))
        return self.instructions

    def parse_children(self, parentnode, level=0):
        pprint("Parsing template")
        pprint("ParentNode", parentnode)
        instructions = []
        for node in parentnode.children:
            if node.nodeType == TEXT:
                pprint("%sFound text node:[%s]" % ('--' * level, node.text))

                texts = node.text.split("|")
                # Separate normal text nodes from dyncamic ones ({})
                for txt in texts:
                    if(match_search(txt, REGEX_BRACKETS) == 0):
                        # Dynamic node
                        d = [ELEMENT, VAR, txt[1:-1]]
                        instructions.append(d)
                    else:
                        # Text node
                        if len(txt):
                            instructions.append((TEXT, txt))
            else:
                pprint("%sFound element:" %
                       ('--' * level), node, "Name:", node.nodeName)
                # Attributes
                attributes = [(x.name, x.value) for x in node.attributes]
                d = [ELEMENT, node.nodeName.upper(), attributes]
                d.append(self.parse_children(node, level + 1))
                instructions.append(d)  # TODO attributes

        pprint("Parsing template Ended.")
        return instructions
