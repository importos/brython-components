import tester as unittest
from components import ObjectWithProperties, Property, HTMLComp, Component, TemplateProcessor, BrowserDOMRender, Register, compile_expr
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

    def test_update_with_expression(self):
        obj1 = ObjTest()
        obj2 = ObjTest()
        expr = 'self.a + self.b'
        context = {'self': obj1}
        exprc = compile_expr(expr)
        obj2.update_with_expression('a', exprc, context, props2bind=('a', 'b'))
        obj1.a = 10
        # At this point obj2.a = obj1.a + obj2.b = 10 + 0 = 10
        self.assertEqual(obj2.a, 10)
        obj1.b = 5
        # At this point obj2.a = obj1.a + obj2.b = 10 + 5 = 15
        self.assertEqual(obj2.a, 15)

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
        obj.mount() # Needed to add self.context
        obj.add_html("<li><b>Test</b></li>")
        lastc = obj.children[-1]
        self.assertEqual(lastc.elem.nodeName, 'LI')
        self.assertEqual(lastc.children[0].elem.nodeName, 'B')

    def test_comp_remove(self):
        obj = MyComponent()
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
        template ="""<comp>Text node<li a='1' b='{self.b}'>{self.a}</li></comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()
        li_comp = obj.children[2]

        self.assertEqual(len(obj.children), 3) # <style> , textnode, and <li>
        self.assertEqual(obj.children[1].elem.text, "Text node")
        self.assertEqual(li_comp.elem.nodeName, "LI")
        self.assertEqual(li_comp.elem.a, "1")
        self.assertEqual(li_comp.elem.b, "2")
        self.assertEqual(li_comp.children[0].elem.nodeName, "DYNODE")

    def test_render(self):
        obj = MyComponent()
        template ="""<comp>Text node<li a='1' b='{self.b}'>{self.a}</li></comp>"""
        expected = """<style rd="1"></style>Text node<li a="1" b="2" rd="1"><dynode>0</dynode></li>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()
        self.assertEqual(obj.elem.html, expected)

    def test_dynode_change(self):
        obj = MyComponent()
        template ="""<comp>{self.a}</comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()
        
        dynode = obj.children[1]
        self.assertEqual(dynode.elem.html, "%s"%(obj.a)) # should be 0
        obj.a = 2
        self.assertEqual(dynode.elem.html, "%s"%(obj.a)) # should be 2
    def test_dom_attr_change(self):
        obj = MyComponent()
        template ="""<comp><li a='{self.a}'></li></comp>"""
        obj.instructions = self.tp.parse(template)
        obj.mount()

        li_comp = obj.children[1]
        self.assertEqual(li_comp.elem.a, "%s"%(obj.a)) # should be 0
        obj.a = 2
        self.assertEqual(li_comp.elem.a, "%s"%(obj.a)) # should be 2
        
    def test_style_scope(self):
        obj = MyComponent()
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
        template ="""<comp><SubComponent cid="sub" a="{1}" b="{self.a+2}"></SubComponent></comp>"""
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
