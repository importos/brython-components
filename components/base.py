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

DYNODE = 'DYNODE'
NORMAL_ATTR, EVENT_ATTR, DYN_ATTR = 1, 2, 3

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

class RefMap(object):
    """Holds references to all components"""
    ref = {}
    
    @classmethod
    def add(cls, obj):
        id_ = id(obj)
        if id_ in RefMap.ref and obj is not RefMap.ref[id_]:
            print("WARNING Refmap already has object ", obj, "it'll be dereferenced because of", RefMap.ref[id_])

        RefMap.ref[id_] = obj
        return id_

    @classmethod
    def remove(cls, obj):
        id_ = id(obj)
        if id_ in RefMap.ref:
            del RefMap.ref[id_]

    @classmethod
    def get_ref(cls, obj):
        return id(obj)
    
    @classmethod
    def get(cls, id_):
        if id_ not in RefMap.ref:
            raise Exception("RefMap does not contain id: ", id_)
        return RefMap.ref[id_]

class ObserverAlreadyRegistered(Exception):
    pass


class Property(object):

    """
    Property object that implements observer pattern. Use it in Component objects.
    Values are stored in an internal dictionary using object.iid as key.
    Observers (binded callback functions) are stored in a similar way.
    """
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
        # when instance is none is because it's called from class instead of
        # instance
        if instance is None:
            return self

        iid = instance.iid
        if iid in self.storage:
            return self.storage[iid]
        else:
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
        iid = instance.iid
        if iid in self.storage:
            oldvalue = self.storage[iid]
            # TODO Comparison against old value works only with numbers and strings. Needs different logic
            # for lists and objects
            if value != oldvalue:
                self.storage[iid] = value
                self.notify_observers(iid, instance, value)

        else:
            self.storage[iid] = value
            self.notify_observers(iid, instance, value)

    def reg_observer(self, instance, observer):
        iid = instance.iid
        if iid in self.observers:
            if observer not in self.observers[iid]:
                self.observers[iid].append(observer)
        else:
            self.observers[iid] = [observer]

    def unreg_observer(self, instance, observer):
        iid = instance.iid
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
        iid = instance.iid
        v = self.storage[iid] if iid in self.storage else self.defaultvalue
        self.notify_observers(iid, instance, v)


class ObjectWithProperties(object):

    """An object that has properties (Property) and can bind callbacks to it"""

    cnt = 0
    iid = None
    _mro_idx = 1 # Position of ObjectWithProperties class in __mro__,
                 # For Component _mro_idx = 2 TODO This can be problematic
                 # if _mro_ changes with inheritance. Maybe _mro_idx can be calculated

    def __init__(self):
        self.cnt = ObjectWithProperties.cnt
        self.iid = self._calc_iid()
        ObjectWithProperties.cnt += 1
        self._mro_idx = 1 

        RefMap.add(self)

    def _calc_iid(self):
        # return hex(id(self) + self.cnt)
        return self.cnt

    def bind(self, propname, callback):
        """Bind instance property to callback"""
        cls = self.__class__
        prop = getattr(cls, propname)
        prop.reg_observer(self, callback)

    def unbind(self, propname, callback):
        cls = self.__class__
        prop = getattr(cls, propname)
        prop.unreg_observer(self, callback)

    def update_with_expression(self, property_name, expression, context, obj=None, props2bind=None):
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
            obj = RefMap.get_ref(self)
        else:
            obj = RefMap.add(obj)

        cbackp = self.chain_prop_cback(property_name, expression, context, obj)

        for prop in props2bind:
            try:
                objname, propname = prop
                RefMap.get(context[objname]).bind(propname, cbackp)
            except Exception as e:
                print("error binding", e)

        # Call manually to set an initial value
        self._chain_prop(None, self, property_name, expression, context, obj)

    def chain_prop_cback(self, propname, expression, context, objref=None):
        """returns a proper callback  that updates self.propname with evaluated expression, to be binded to a property.
        """
        return partial(self._chain_prop, propname=propname, expression=expression, context=context, objref=objref)

    def _chain_prop(self, value, instance, propname, expression, context, objref):
        # assign
        context_root= RefMap.get(context['root'])
        context_parent= RefMap.get(context['parent'])
        context_self = RefMap.get(context['self'])
        context_this= RefMap.get(context['this'])
        v = expression(context_root, context_parent, context_self, context_this)

        setattr(RefMap.get(objref), propname, v)

    def force_change(self, propname):
        getattr(self.__class__, propname).force_change(self)

    def _get_attr(self, attrname):
        return getattr(self, attrname)

class DOMRender(object):
    """Class used to render DOM"""
    pass


class BrowserDOMRender(DOMRender):
    direct = False

    def render(self, comp, before=None, after=None):
        if BrowserDOMRender.direct:
            self._render(None, comp, before, after)
        else:
            window.requestAnimationFrame(
                partial(self._render, comp=comp, before=before, after=after))

    def _render(self, ev, comp, before=None, after=None):
        if before is not None:
            comp.parent.elem.insertBefore(comp.elem, before.elem)
        elif after is not None:
            comp.parent.elem.insertAfter(comp.elem, after.elem)
        else:
            comp.parent.elem <= comp.elem


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
    _prop_list = []

    style = Property("")
    _rendered_style = Property("")
    _style_comp = None

    dom_renderer = BrowserDOMRender()

    cls_initialized = False

    def __init__(self, domnode=None):
        super(Component, self).__init__()
        self.children = []
        self.ids = {}
        self._mro_idx = 2
        # Bind on_property of instance for each prop
        for propname in self._prop_list:
            try:
                callback = getattr(self, "on_%s" % (propname))
                self.bind(propname, callback)
            except:
                pass
        # Default callbacks
        callback = getattr(self, "on_elem")
        self.bind("elem", callback)

        callback = getattr(self, "on_html")
        self.bind("html", callback)


        try:
            callback = getattr(self, "on_style")
            self.bind("style", callback) #bind will fail if self.style is not Property
        except:
            pass 

        if domnode == None:
            tag = self.tag if self.rendertag is None else self.rendertag
            self.elem = self._create_domelem(tag)
        else:
            self.elem = domnode

    def __repr__(self):
        return "%s tag: %s id: %s iid: %s"%(self.__class__.__name__, self.tag, id(self), self.iid)

    def set_context(self, root):
        self.context = {"self": RefMap.add(self), "this": RefMap.add(self.elem), "root": RefMap.add(root), "parent": RefMap.add(self.parent)}

    def mount(self):
        """
        Process the Component (and its children): Parses instructions, binds properties and renders the DOMNode in the site.
        """
        if self.elem is None: # Create DOM elem if needed
            tag = self.tag if self.rendertag is None else self.rendertag
            self.elem = self._create_domelem(tag)
        self._dom_newattr("id", "%s_%s" % (self.__class__.__name__, self.iid))

        self.set_context(self.root)

        # Create style comp and add it
        if len(self.style):
            self._mount_style()

        pprint("Mounting", self, "Instructions",
               self.instructions, "Context: ", self.context)

 
        self.parse_instructions()

        # If this is root comp (no parent) then set props from DOM attributes
        # Grab props from root domnode and use them to initialize component's
        # props
        if self.parent is None:
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
        self.on_mount()
        return self

    def _mount_style(self):
        self._rendered_style = self.style.replace(
            ":host", "#%s" % (self.elem.id))
        if self._style_comp is None:
            self._style_comp = HTMLComp(tag='style')
            self.add(self._style_comp)
        self._style_comp.html = self._rendered_style

    def _mark_as_mounted(self):
        self._dom_newattr("rd", "1")
        self.is_mounted = True

    def _dom_newattr(self, name, value):
        self.elem.setAttribute(name, value)

    def parse_instructions(self):
        parentcomp = self
        instruction_set = self.instructions
        context_root = RefMap.get(self.context['root'])

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
                if nodename not in HTML_TAGS and nodename != DYNODE:
                    pprint("CREATE custom component, named", nodename)
                    try:
                        comp = Register.get_component_class(nodename)()
                        # TODO We don't set domnode attributes based on template, only comp,, should we?
                        comp.root = comp #Custom comps are their own root
                        comp.parent = self

                        comp.mount()

                        # For attributes from DOM template to Comp use normal root for context
                        comp.set_context(root=self.root)

                        # Once mounted Set Comp's props initial values  from DOM template
                        for attr in attributes:
                            name, value, type_ = attr[0:3]
                            if name == "cid":
                                continue
                            if (type_ == DYN_ATTR):
                                expression = value
                                props2bind = attr[3]
                                comp.update_with_expression(name, expression, comp.context, comp, props2bind)
                            else:
                                setattr(comp, name, value)

                        #Restore context
                        comp.set_context(root=comp.root)

                    except Exception as e:
                        pprint("Couldnt add component ", nodename, e)

                elif nodename == DYNODE:
                    comp = self.create_component(nodename)
                    expression = instruction[2]
                    props2bind = instruction[3]
                    # Bind all attributes in expression
                    comp.update_with_expression(
                        'html', expression, comp.context, comp, props2bind)
                    comp.is_mounted = True
                else:  # Components of classic HTML nodes
                    comp = self.create_component(nodename)

                    # Setting props from Component to DOM
                    for attr in attributes:
                        name, value, type_ = attr[0:3]

                        if (type_ == DYN_ATTR):
                            # Dyn

                            # Check if is event or normal attribute
                            expression = value
                            if name not in DOMEVENTS:
                                comp._dom_newattr(name, '')
                                props2bind = attr[3]
                                comp.update_with_expression(
                                    name, expression, comp.context, comp.elem, props2bind)
                            else:
                                eventname = name[2:]
                                comp.elem.bind(
                                    eventname, comp.domevent_callback(expression, comp.context))

                        else:
                            # Normal attr
                            comp._dom_newattr(name, value)

                    child_instructions = instruction[3]
                    comp.instructions = child_instructions
                    comp.mount()
            pprint("Adding COMP", comp, comp.tag)

            # Add comp to cid dict for quick retrieval
            context_root._add_cid(comp, cid)
            parentcomp.add(comp)

    def create_component(self, tag, text=''):

        dom_elem = self._create_domelem(tag, text)
        c = HTMLComp(tag, dom_elem)
        c.parent = self
        c.root = self.root
        c.set_context(c.root)
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

    def on_style(self, value, instance):
        if self.is_mounted:
            self._mount_style()


    def on_mount(self):
        pass
    
    def on_unmount(self):
        self.is_mounted = False

    def render(self, before=None, after=None):
        return self.dom_renderer.render(self, before, after)

    def add(self, comp, before=None, after=None):
        """Adds child component"""
        self.children.append(comp)
        comp.parent = self
        # Sometimes comps are not mounted, we should mount them before render
        if not comp.is_mounted:
            comp.root = self.root if isinstance(comp, HTMLComp) else comp #Custom comps are their own root
            comp.mount()

        comp.render(before, after)

    def _add_cid(self, comp, cid):
        if cid is not None:
            self.ids[cid] = comp

    def get(self, cid):
        """Gets component by its cid"""
        return self.ids[cid]

    def remove(self, component):
        # unmount DOM first
        component.unmount()

        # Remove component
        self.children.remove(component)
        # Remove cid association
        comp_k = None
        for k in self.ids:
            if self.ids[k] == component:
                comp_k = k
                break
        if comp_k is not None:
            del self.ids[comp_k]

        RefMap.remove(component) #TODO removing comp from refmap will cause error in its binded events

    def remove_all(self):
        torem = [c for c in self.children if c is not self._style_comp]
        for c in torem:
            self.remove(c)
        self.ids = {}

    def unmount(self):
        self.parent.elem.removeChild(self.elem)
        RefMap.remove(self.elem)
        del self.elem
        self.elem = None
        # TODO Unmount binds to DOM and from DOM
        self.on_unmount()

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

    # Events Logic
    def domevent_callback(self, expression, context):
        """Returns a callback that evals expression using context as globals"""
        return partial(self._domevent_callback, expression=expression, context=context)

    def _domevent_callback(self, event, expression, context):
        pprint("EVENT", event, "expression", expression)
        real_context = {'self': RefMap.get(context['self']),'parent': RefMap.get(context['parent']),'root':RefMap.get(context['root']),'this': RefMap.get(context['this'])}
        eval(expression, real_context)  # TODO security?


class HTMLComp(Component):

    """Component for normal HTML nodes (<a>, <b>, <div>, <p>, etc.)"""
    value = Property('')

    def __init__(self, tag, domnode=None):
        self.tag = tag
        super(HTMLComp, self).__init__(domnode)

    def on_html(self, value, instance):
        self.elem.innerHTML = value

    def mount(self, context=None):
        self.context = {"self": RefMap.add(self), "this": RefMap.add(self.elem), "root": RefMap.add(self.root), "parent": RefMap.add(self.parent)}
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
        print(args)

DP = None
try:
    from browser import document, alert, window, html, console
    from javascript import JSConstructor
    DP = JSConstructor(window.DOMParser)()
    NEW_FUNC = JSConstructor(window.Function)
    REGEX_SELF = JSConstructor(window.RegExp)("(self|parent|root)\.[A-Za-z0-9_]{1,}", 'g')
    REGEX_BRACKETS = JSConstructor(window.RegExp)("\{(.*?)\}", 'g')
    window.RefMap = RefMap.ref

    def match(text, regex):
        jstext = JSConstructor(window.String)(text)
        m = jstext.match(regex)
        if m is None:
            return []
        return m

    def match_replace(text, regex, replace):
        jstext = JSConstructor(window.String)(text)
        return jstext.replace(regex, replace)

    def match_search(text, regex):
        jstext = JSConstructor(window.String)(text)
        return jstext.search(regex)
except:
    pprint("No brython and javascript libs.", force=True)

    import re

    REGEX_SELF = re.compile("self\.[A-z0-9_]{1,}")
    REGEX_BRACKETS = re.compile("\{(.*?)\}")

    def match(text, regex):
        return re.findall(regex, text)

    def match_replace(text, regex, replace):
        raise Exception

    def match_search(text, regex):
        raise Exception


class Register(object):

    """Registers Components"""
    reg = []

    @classmethod
    def add(cls, comp_cls):
        if comp_cls not in cls.reg:
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

    @classmethod
    def remove(cls, comp_cls):
        cls.reg.remove(comp_cls)

def initialize_comps_classes():
    tp = TemplateProcessor()

    for comp_cls in Register.reg:
        if comp_cls.cls_initialized:
            continue
        pprint("Initializing ", comp_cls)
        # Parsing template
        comp_cls.instructions = tp.parse(comp_cls.template)
        # End parsing
        if comp_cls.tag is None:
            comp_cls.tag = comp_cls.__name__
        # props list
        comp_cls._prop_list = []
        attrs = dir(comp_cls)
        for attr in attrs:
            a = getattr(comp_cls, attr)
            if isinstance(a, Property):
                comp_cls._prop_list.append(attr)
        pprint("proplist for ", comp_cls, comp_cls._prop_list)
        comp_cls.cls_initialized = True


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
            rootcomp = comp_cls(elem)
            rootcomp.root =  rootcomp
            rootcomp.mount()
            # TODO What happens with root components? Are they garbage collected? Should we store a reference in a global variable?


def init():
    initialize_comps_classes()
    render()


class TemplateProcessor(object):

    """Parses Component's template into an instructions set """
    dp = DP

    def parse(self, template):
        self.instructions = []
        data = template.replace('{', '|{').replace('}', '}|')
        dom = self.dp.parseFromString(data, "text/xml")
        rootnode = window.__BRYTHON__.DOMNode(dom).children[0]
        self.instructions = self.parse_children(rootnode)
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
                    if(match_search(txt, REGEX_BRACKETS) != -1):
                        # Dynamic node
                        props2bind = get_props2bind(txt)
                        compiled_expr = self._compile_expr(txt[1:-1])

                        d = [ELEMENT, DYNODE, compiled_expr, props2bind]
                        instructions.append(d)
                    else:
                        # Text node
                        if len(txt):
                            instructions.append((TEXT, txt))
            else:
                pprint("%sFound element:" %
                       ('--' * level), node, "Name:", node.nodeName)
                # Attributes
                attributes = []

                for attr in node.attributes:
                    name, value = attr.name, attr.value
                    if(match_search(value, REGEX_BRACKETS) != -1):
                        if name not in DOMEVENTS:
                            props2bind = get_props2bind(value)
                            compiled_expr = self._compile_expr(value[2:-2])
                            attributes.append((name, compiled_expr, DYN_ATTR, props2bind))
                        else:
                            #linked DOM event to Comp method
                            attributes.append((name, value[2:-2], DYN_ATTR, None))
                    else:
                        if name not in DOMEVENTS:
                            attributes.append((name, value, NORMAL_ATTR))
                        else:
                            attributes.append((name, value, EVENT_ATTR))
                #attributes = [(x.name, x.value) for x in node.attributes]
                d = [ELEMENT, node.nodeName.upper(), attributes]
                d.append(self.parse_children(node, level + 1))
                instructions.append(d)  # TODO attributes

        pprint("Parsing template Ended.")
        return instructions

    def _compile_expr(self, expression):
        return compile_expr(expression)

def get_props2bind(expression):
    ret = [x.split('.')[0:2] for x in match(expression, REGEX_SELF)]
    return ret

def compile_expr(expression):
    thefunc = "def func(root, parent, self, this):\n    return %s" %(expression)
    try:
        exec(thefunc)
    except:
        raise Exception("Cannot compile expression %s"%(expression))
    else:
        return func #Some IDEs will say func is not defined, but it is defined in exec in this scope
