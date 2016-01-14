TITLE = "Filtered List 2"
CODE = ['''
from custom import FilteredList
from components import Register, Component, Property


# Filter list using input text

class MyComponent(Component):
  template = """<MyComponent>
  <input cid='search' placeholder='Type search' onkeyup='{self.filter()}' type='text'/>
  <FilteredList cid='fl'></FilteredList>
  <div>{self.numitems} items</div>
  </MyComponent>"""
  initial_items = Property([])
  items = Property([])
  numitems = Property(0)
  
  def filter(self):
    value = self.get('search').elem.value.lower()
    newitems = [x for x in self.initial_items if value in x.lower() or not len(value)]
    self.get('fl').items = newitems
    
  def on_initial_items(self, value, instance):
    print("initial items")
    self.get('fl').bind('items', self.update_numitems)
    self.get('fl').initial_items = value
    
  
  def update_numitems(self, value, instance):
    self.numitems = len(value)
  
Register.add(MyComponent)'''
,
'''
<MyComponent initial_items="['Apples', 'Pears', 'Oranges', 'Bananas', 'Papayas', 'Mangos', 'Grapes']"></MyComponent>''' ]
