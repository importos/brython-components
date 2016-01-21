import tester as unittest
from components import ObjectWithProperties, Property, HTMLComp, Component, TemplateProcessor, BrowserDOMRender, Register, compile_expr, RefMap, get_props2bind
from browser import document

class ObjTest(ObjectWithProperties):
    a = Property(0)
    b = Property(0)

    def other_func(self):
        return self.a * 10

class TestProperties(unittest.TestCase):
    
    def test_bind_callback(self):
        """Tests that a property change calls the binded callback"""
        obj = ObjTest()
        result = [0]

        def callback(value, instance):
            result[0] = value

        obj.bind('a', callback)
        obj.a = 1
        self.assertEqual(result[0], 1)

    def test_duplicate_bind(self):
        """Tests that a second bind of a callback to a property does nothing (no multiple binding)"""
        obj = ObjTest()
        result = [0]
        def callback(value, instance):
            result[0] = result[0] + 1

        obj.bind('a', callback)
        obj.a = 1

        self.assertEqual(result[0], 1)


    def test_update_with_expression_self_parent_root(self):
        obj_self = ObjTest()
        obj_parent = ObjTest()
        obj_root = ObjTest()

        expr = 'self.b + parent.a + root.a + 10' #Since we're updating obj_self.a we don't use self.a in expr to avoid infinite recursion
        context = {'self': RefMap.get_ref(obj_self), 'parent': RefMap.get_ref(obj_parent),'root': RefMap.get_ref(obj_root),'this': RefMap.add(None)}
        exprc = compile_expr(expr)

        props2bind = get_props2bind(expr)
        obj_self.update_with_expression('a', exprc, context,
                props2bind=props2bind)
        
        obj_parent.a = 1
        self.assertEqual(obj_self.a, 11)
        obj_root.a = 2
        self.assertEqual(obj_self.a, 13)
        obj_self.b = 3
        self.assertEqual(obj_self.a, 16)

    def test_force_change(self):
        obj = ObjTest()
        result = [0]
        def callback(value, instance):
            result[0] = result[0] + 1
        obj.bind('a', callback)
        getattr(obj.__class__, 'a').force_change(obj)

        self.assertEqual(result[0], 1)

class TestComponent(unittest.TestCase):
    tp = TemplateProcessor()

    def test_comp_context(self):
        Register.add(SubComponent)
        obj = MyComponent()
        obj.root = obj
        template ="""<comp><li><a><SubComponent></SubComponent></a></li></comp>"""
        obj.instructions = self.tp.parse(template)

        obj.mount()
        comp_li = obj.children[0]
        comp_a = comp_li.children[0]
        comp_sub = comp_a.children[0]
        self.assertEqual(RefMap.get(comp_li.context['self']), comp_li)
        self.assertEqual(RefMap.get(comp_li.context['parent']), obj)
        self.assertEqual(RefMap.get(comp_li.context['root']), obj)
        
        self.assertEqual(comp_li.root, obj)
        self.assertEqual(comp_li.parent, obj)

        self.assertEqual(RefMap.get(comp_a.context['self']), comp_a)
        self.assertEqual(RefMap.get(comp_a.context['parent']), comp_li)
        self.assertEqual(RefMap.get(comp_a.context['root']), obj)

        self.assertEqual(comp_a.root, obj)
        self.assertEqual(comp_a.parent, comp_li)


        self.assertEqual(RefMap.get(comp_sub.context['parent']), comp_a)
        self.assertEqual(RefMap.get(comp_sub.context['root']), comp_sub)

        comp_sub2 = SubComponent()
        obj.add(comp_sub2)
        self.assertEqual(RefMap.get(comp_sub2.context['parent']), obj)
        self.assertEqual(RefMap.get(comp_sub2.context['root']), comp_sub2)


    def test_htmlcomp_dom_creation(self):
        obj = HTMLComp('LI')
        self.assertEqual('LI' , obj.elem.nodeName)

    def test_comp_dom_creation(self):
        obj = MyComponent()
        self.assertEqual(obj.tag.upper() , obj.elem.nodeName)

    def test_comp_add(self):
        obj = MyComponent()
        c = HTMLComp('LI')
        obj.add(c)
        self.assertEqual(obj.children[0], c)
    def test_comp_add_html(self):
        obj = MyComponent()
        obj.root = obj
        obj.mount() # Needed to add self.context
        obj.add_html("<li><b>Test</b></li>")
        lastc = obj.children[-1]
        self.assertEqual(lastc.elem.nodeName, 'LI')
        self.assertEqual(lastc.children[0].elem.nodeName, 'B')

    def test_comp_remove(self):
        obj = MyComponent()
        obj.root = obj
        c = HTMLComp('LI')
        obj.add(c)
        obj.remove(c)
        self.assertEqual(len(obj.children), 0)

    def test_parse_template(self):
        template ="""<comp>Text node<li a='1' b='1'>2</li></comp>"""
        expected = [(3, 'Text node'), [1, 'LI', [('a', '1', 1), ('b', '1', 1)], [(3, '2')]]]
        tp = TemplateProcessor()
        result = tp.parse(template)
        self.assertEqual(result, expected)

    def test_parse_instructions(self):
        obj = MyComponent()
        obj.root = obj
        template ="""<comp>Text node<li a='1' b='{root.b}'>{root.a}</li></comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()
        li_comp = obj.children[1]

        self.assertEqual(len(obj.children), 2) #  textnode, and <li>
        self.assertEqual(obj.children[0].elem.text, "Text node")
        self.assertEqual(li_comp.elem.nodeName, "LI")
        self.assertEqual(li_comp.elem.a, "1")
        self.assertEqual(li_comp.elem.b, "2")
        self.assertEqual(li_comp.children[0].elem.nodeName, "DYNODE")

    def test_render(self):
        obj = MyComponent()
        obj.root = obj
        template ="""<comp>Text node<li a='1' b='{root.b}'>{root.a}</li></comp>"""
        expected = """Text node<li a="1" b="2" rd="1"><dynode>0</dynode></li>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()
        self.assertEqual(obj.elem.html, expected)

    def test_dynode_change(self):
        obj = MyComponent()
        obj.root = obj
        template ="""<comp>{root.a}</comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()
        
        dynode = obj.children[0]
        self.assertEqual(dynode.elem.html, "%s"%(obj.a)) # should be 0
        obj.a = 2
        self.assertEqual(dynode.elem.html, "%s"%(obj.a)) # should be 2

    def test_dom_attr_change(self):
        obj = MyComponent()
        obj.root = obj
        template ="""<comp><li a='{root.a}'></li></comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()

        li_comp = obj.children[0]
        self.assertEqual(li_comp.elem.a, "%s"%(obj.a)) # should be 0
        obj.a = 2
        self.assertEqual(li_comp.elem.a, "%s"%(obj.a)) # should be 2
        
    def test_style_scope(self):
        obj = MyComponent()
        obj.root = obj
        template ="<comp><b>Hello</b></comp>"
        obj.instructions = self.tp.parse(template)
        obj.style = """:host {color: red;}"""

        obj.mount()

        expected = """#%s {color: red;}"""%(obj.elem.id)
        self.assertEqual(obj._rendered_style, expected)
        self.assertEqual(obj._style_comp.html, expected)

    def test_set_subcomp_props_from_templatedom(self):
        """Tests setting initial values to Component's properties based on
        attributes defined in DOM template"""

        obj = MyComponent()
        obj.root = obj
        template ="""<comp><SubComponent cid="sub" a="{1}" b="{root.a+2}"></SubComponent></comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()

        obj2 = obj.get('sub')
        self.assertEqual(obj2.a, 1)
        self.assertEqual(obj2.b, 2) #obj.a is 0
        obj.a = 2
        self.assertEqual(obj2.b, 4)

class MyComponent(Component):
    template="<MyComponent></MyComponent>"
    tag = 'MyComponent'
    a = Property(0)
    b = Property(2)

class SubComponent(Component):
    template="<SubComponent></SubComponent>"
    tag = 'SubComponent'
    a = Property(0)
    b = Property(2)
    

Register.add(SubComponent)
Register.add(MyComponent)
   

BrowserDOMRender.direct = True
TESTS = (TestProperties, TestComponent)
report_html = ''
document['status'].html = "Testing..."
for t in TESTS:
    document['status'].html = "Processing %s"%(t.__name__)
    tester = t()
    report = tester.run()
    report_html += "<br/> <h2>%s</h2>"%(t.__name__) + report.format_html()
document['status'].html = "Testing done"
document['report'].html = report_html
