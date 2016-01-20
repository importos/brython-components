TITLE = "Filtered list"
CODE = ['''
from components import Register, Component, Property


# Filter list using input text

class FilteredList(Component):
    template = """<FilteredList>
    <input cid='search' placeholder='Type search' onkeyup='{self.filter()}' type='text'/>
    <ul cid='list'></ul>
    <div>{self.itemslen} items</div>
    </FilteredList>"""
    items = Property([])
    initial_items = None
    itemslen = Property(0)
    
    def filter(self):
        value = self.get('search').elem.value.lower()
        newitems = [x for x in self.initial_items if value in x.lower() or not len(value)]
        self.items = newitems
        
    
    def on_items(self, value, instance):
        if self.initial_items is None and len(value):
            self.initial_items = value
        self.itemslen = len(value)
        ulist = self.get('list')
        # Remove all existing children and create new ones according to list. This is not optimal 
        ulist.remove_all()
        for i in value:
            li = ListItem()
            li.text = i
            ulist.add(li)

class ListItem(Component):
    template = "<ListItem>{self.text}</ListItem>"
    rendertag = "li" # Use <li> instead of <ListItem> to render
    text = Property('')

Register.add(FilteredList)
Register.add(ListItem)
'''
,

'''<FilteredList items="{['Apples', 'Pears', 'Oranges', 'Bananas', 'Papayas', 'Mangos', 'Grapes']}" ></FilteredList>''']
