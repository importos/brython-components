import tester as unittest
from components import ObjectWithProperties, Property, HTMLComp, Component
from browser import document

class ObjTest(ObjectWithProperties):
    a = Property(0)
    b = Property(0)

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

        obj2.update_with_expression('a', expr, context)

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

    def test_comp_remove(self):
        obj = MyComponent()
        c = HTMLComp('LI')
        obj.add(c)
        obj.remove(c)
        self.assertEqual(len(obj.children), 0)

class MyComponent(Component):
    template="<MyComponent></MyComponent>"
    tag = 'MyComponent'
    


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
