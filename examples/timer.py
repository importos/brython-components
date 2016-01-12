['''
from components import Register, Component, Property
from browser import timer

class MyComponent(Component):
  template = """<MyComponent>Seconds elapsed {self.time}</MyComponent>"""
  time = Property(0)
  
  def on_is_mounted(self, value, instance):
    self._timer = timer.set_interval(self.tick,1000)
  
  def tick(self):
    self.time += 1
    
Register.add(MyComponent)
'''
,

'''<MyComponent></MyComponent>''']
