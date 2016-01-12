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
            self.storage[iid] = self.defaultvalue
            return self.defaultvalue

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


class Component(object):
    """
    Base Component class. All components inherit from it.
    Every Component is linked with a DOMNode element (component.elem) which is present
    in the site's HTML.
    """
    tag = None  # Tag used to identify components in DOM. If None class name is used.
    rendertag = None  # Tag used to render the component in DOM
    template = "" # Template used to build the internals of the component
    instructions = [] # Template string is parsed and compiled into a set of instructions
    elem = Property(None) #DOMNode
    html = Property(None)
    children = None # Children Components
    ids = {} # Ids dict to quickly access child comps by their cid (comp.get('child_cid'))
    parent = None # Parent Component.
    root = None # Root component (The first component that initiated the mount)
    is_mounted = Property(False)

    def __init__(self, domnode=None):
        cls = self.__class__
        attrs = dir(cls)
        self._prop_list = []
        self.children = []
        self.ids = {}

        # Bind on_property of instance for each prop
        for attr in attrs:
            a = getattr(cls, attr)
            if isinstance(a, Property):
                self._prop_list.append(a)
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

        # Setting props from DOM to Component (only if it's not HTML Comp)
        # Grab props from root domnode and use them to initialize component's
        # props
        if not isinstance(self, HTMLComp):
            for attr in self.elem.attributes:
                try:
                    name, value = attr.name, attr.value
                    print("name", name, "value", value)
                    if name not in ['cid']:
                        setattr(self, name, value)
                except:
                    pass
        # mark as rendered
        attr_rd = window.document.createAttribute("rd")
        attr_rd.value = '1'
        self.elem.setAttributeNode(attr_rd)
        pprint("ET Mount %s" % (time.time() - k), force=True)
        self.is_mounted = True
        return self

    def parse_instructions(self):
        parentcomp = self
        instruction_set = self.instructions
        context_self = self.context['self']
        context_cls = context_self.__class__

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
                    eval_expr = [expression, self.context]

                    # Bind all attributes in expression
                    for var in match(expression, REGEX_SELF):
                        context_self.bind(
                            var[5:], comp.chain_prop('html', expression=eval_expr, obj=comp))
                    # force update of chained prop by firing any prop in the
                    # expression
                    getattr(context_cls, var[5:]).force_change(context_self)
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
                            eval_expr = [expression, self.context]

                            # Check if is event or normal attribute
                            if name not in DOMEVENTS:
                                # Bind all attributes in expression
                                for var in match(expression, REGEX_SELF):
                                    # We use comp.elem because we're binding
                                    # domnode attributes
                                    context_self.bind(
                                        var[5:], comp.chain_prop(name, expression=eval_expr, obj=comp.elem))
                                comp.elem.setAttributeNode(attr_dom)
                                # force update of chained prop by firing any
                                # prop in the expression
                                getattr(context_cls, var[5:]).force_change(
                                    context_self)
                            else:
                                # Event
                                eventname = name[2:]
                                comp.elem.bind(
                                    eventname, context_self.domevent_callback(eval_expr))

                        else:
                            # Normal attr
                            attr_dom.value = value
                            comp.elem.setAttributeNode(attr_dom)

                    child_instructions = instruction[3]
                    comp.instructions = child_instructions
                    comp.mount(context=self.context)
                    #self.parse_instructions(comp, child_instructions)
            pprint("Adding COMP", comp)

            # Add comp to cid dict for quick retrieval
            context_self._add_cid(comp, cid)
            parentcomp.add(comp)

    def create_component(self, tag, text=''):

        dom_elem = self._create_domelem(tag, text)
        c = HTMLComp(tag, dom_elem)
        c.root = self.root
        #c.elem = dom_elem
        return c

    def _create_domelem(self, tag, text):
        if tag == 'text':
            dom = document.createTextNode(text)
            dom_elem = window.__BRYTHON__.DOMNode(dom)
        else:
            dom = document.createElement(tag.upper())
            dom_elem = window.__BRYTHON__.DOMNode(dom)
        return dom_elem

    def bind(self, propname, callback):
        """Bind instance property to callback"""
        cls = self.__class__
        prop = getattr(cls, propname)
        prop.reg_observer(self, callback)

    def unbind(self, propname, callback):
        cls = self.__class__
        prop = getattr(cls, propname)
        prop.unreg_observer(self, callback)

    def iid(self):
        return hex(id(self))

    def on_elem(self, value, instance):
        pprint(("dom element", value))

    def on_html(self, value, instance):
        pprint(("html element", value))

    def on_is_mounted(self, value, instance):
        pass

    def render(self):
        """Adds self.elem to parent.elem. It's finally rendered on site when parent.elem is added to a DOMNode that is already on site"""
        for c in self.children:
            c.render()
        self.parent.elem <= self.elem

    def add(self, comp):
        """Adds child component"""
        self.children.append(comp)
        comp.parent = self
        # Sometimes comps are not mounted, we should mount them before render
        if not comp.is_mounted:
            comp.root = self.root
            print("ROOT is", self.root)
            comp.mount()
        comp.render()

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
        self.elem.removeChild(component.elem)

    def add_html(self, html, tag):
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
    def chain_prop(self, propname, expression=None, obj=None):
        """returns a proper callback to be binded to a property change. This callback updates obj.propname internally.
        obj can be the component (self) or the dom node (self.elem)
        """
        return partial(self._chain_prop, propname=propname, expression=expression, obj=obj)

    def _chain_prop(self, value, instance, propname, expression, obj):
        if expression is None:
            setattr(obj, propname, value)
        else:
            # assign
            eval_str, globals_ = expression
            v = eval(eval_str, globals_)  # TODO security?
            setattr(obj, propname, v)

    # Events Logic
    def domevent_callback(self, expression):
        """Links a domevent to an instance callback"""
        return partial(self._domevent_callback, expression=expression)

    def _domevent_callback(self, event, expression):
        pprint("EVENT", event, "expression", expression[0])
        eval_str, globals_ = expression
        eval(eval_str, globals_)  # TODO security?


class HTMLComp(Component):
    """Component for normal HTML nodes (<a>, <b>, <div>, <p>, etc.)"""

    def __init__(self, tag, domnode=None):
        super(HTMLComp, self).__init__(domnode)
        self.tag = tag

    def on_html(self, value, instance):
        self.elem.innerHTML = value


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


def match(text, regex):
    jstext = JSConstructor(window.String)(text)
    return jstext.match(regex)


def match_replace(text, regex, replace):
    jstext = JSConstructor(window.String)(text)
    return jstext.replace(regex, replace)


def match_search(text, regex):
    jstext = JSConstructor(window.String)(text)
    return jstext.search(regex)

CONSOLE_ENABLED = True


def pprint(*args, **kwargs):
    force = kwargs['force'] if 'force' in kwargs else False
    if CONSOLE_ENABLED or force:
        print(args)

try:
    from browser import document, alert, window, html, console
    from javascript import JSConstructor
    import time
    #jq = window.jQuery
    DP = JSConstructor(window.DOMParser)()
    REGEX_SELF = JSConstructor(window.RegExp)("self\.[a-zA-z]{1,}", 'g')
    REGEX_BRACKETS = JSConstructor(window.RegExp)("\{(.*?)\}", 'g')

except:
    pprint("No browser libs.", force=True)


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
            mc.mount()
            Main.append(mc)


def init():
    compile_comps_cls()
    render()


class TemplateProcessor(object):
    """Parses Component's template into an instructions set """
    dp = JSConstructor(window.DOMParser)()

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
                        instructions.append((TEXT, txt))
            else:
                pprint("%sFound element:" %
                       ('--' * level), node, "Name:", node.nodeName)
                # Attributes
                attributes = [(x.name, x.value) for x in node.attributes]
                d = [ELEMENT, node.nodeName.upper(), attributes]
                d.append(self.parse_children(node, level + 1))
                instructions.append(d)  # TODO attributes

        return instructions
