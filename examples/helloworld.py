TITLE = "HelloWorld"
CODE = ['''from components import Register, Component, Property
from browser import alert

class MyComponent(Component):
    template = """<MyComponent>
    <input cid='name' placeholder='Type your name' type='text'/>
    <button onclick='{self.hello()}'>Click me</button>
    </MyComponent>"""
  
    def hello(self):
        alert("Hello %s"%(self.get('name').elem.value))

Register.add(MyComponent)
'''
,

'''<MyComponent></MyComponent>''']
