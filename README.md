brython-components
==================

Components for Brython like React, RiotJS and similar. But using Python!


**Experimental status. Work in progress. Please test.**

##Example usage

brython code:
```
from components import Register, Component, Property, init()
from browser import alert

class MyComponent(Component):
  template = """<MyComponent>
  <input cid='name' placeholder='Type your name' type='text'/>
  <button onclick='{self.hello()}'>Click me</button>
  </MyComponent>"""
  
  def hello(self):
    alert("Hello %s"%(self.get('name').elem.value))

Register.add(MyComponent)
init() # Renders registered Components. Call this only once
```

html:
```
<MyComponent></MyComponent>
```
[Test it!](http://45.55.135.188:8000/brython-components/simpletest.html)

##Requisites
- Brython

##Editor

Clone repository in brython/www/brython-components, run Brython server and access http://localhost:8000/brython-components/editor.html

[Live editor](http://45.55.135.188:8000/brython-components/editor.html#WycnJ2Zyb20gY29tcG9uZW50cyBpbXBvcnQgUmVnaXN0ZXIsIENvbXBvbmVudCwgUHJvcGVydHkKZnJvbSBicm93c2VyIGltcG9ydCBhbGVydAoKY2xhc3MgTXlDb21wb25lbnQoQ29tcG9uZW50KToKICB0ZW1wbGF0ZSA9ICIiIjxNeUNvbXBvbmVudD4KICA8aW5wdXQgY2lkPSduYW1lJyBwbGFjZWhvbGRlcj0nVHlwZSB5b3VyIG5hbWUnIHR5cGU9J3RleHQnLz4KICA8YnV0dG9uIG9uY2xpY2s9J3tzZWxmLmhlbGxvKCl9Jz5DbGljayBtZTwvYnV0dG9uPgogIDwvTXlDb21wb25lbnQ+IiIiCiAgCiAgZGVmIGhlbGxvKHNlbGYpOgogICAgYWxlcnQoIkhlbGxvICVzIiUoc2VsZi5nZXQoJ25hbWUnKS5lbGVtLnZhbHVlKSkKClJlZ2lzdGVyLmFkZChNeUNvbXBvbmVudCkKJycnLCAnPE15Q29tcG9uZW50PjwvTXlDb21wb25lbnQ+J10=)

[Examples](http://45.55.135.188:8000/brython-components/)

##Known bugs and limitations
- Not ready for production yet.
- It's slow. Code refactoring is needed.
- It's leaking memory. Needs code refactoring to exterminate leaks.
- Needs better documentation and more examples.
- No scoped styles yet.
- There's not an easy way to create and maintain a list of Components yet.

##Immediate TODO
- Code refactoring for better speed and memory usage.
- Proper Testing suite.
- Documentation improvement.
- Scoped styles (CSS).
- Reported critical issues.

CREDITS
=======
Ideas from kivy, riotjs and react.
Author: Jeyson Molina jeyson.mco at gmail dot com
