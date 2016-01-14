import unittest
from components import ObjectWithProperties, Property

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

class ObjTest(ObjectWithProperties):
    a = Property(0)
    b = Property(0)

if __name__ == '__main__':
    unittest.main()
