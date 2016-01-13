from components import Register, Component, Property, HTMLComp, HTML_TAGS

# Filter list using input text

class FilteredList(Component):
    template = """<FilteredList></FilteredList>"""
    items = Property([])
    initial_items = Property([])
    rendertag='ul'
    itemtag='li'
    filtervalue = Property('')
    order = {}

    def on_filtervalue(self, value, instance):
        lvalue = value.lower()  
        newitems = [x for x in self.initial_items if lvalue in x.lower() or not len(value)]
        self.items = newitems
    
    def on_initial_items(self, value, instance):
        self.order = {k: v for v,k in enumerate(value)}
        self.items = list(value)

    def on_items(self, value, instance):
        comp2rm, values2add, current_items = [], list(self.items), []
        for c in self.children:
            if c.value in self.items:
              current_items.append(c.value)
              values2add.remove(c.value)
            else:
              comp2rm.append(c)

        #Remove
        for c in comp2rm:
            self.remove(c)

        # Add 
        ishtml = self.itemtag.upper() in HTML_TAGS
        cls_comp = HTMLComp if ishtml else Register.get_component_class(self.itemtag)

        for c in list(self.children):
            added = []
            for v in values2add:
                if self.order[v] < self.order[c.value]:
                    newcomp = cls_comp(tag=self.itemtag) if ishtml else cls_comp()
                    newcomp.value = v
                    newcomp.html = v
                    self.add(newcomp, before=c)
                    added.append(v)
                else:
                    break

            for a in added: 
                values2add.remove(a)

        # Add remaining
        HTMLComp(tag='li')
        for v in values2add:
            try:
                newcomp = cls_comp(tag=self.itemtag, domnode=None) if ishtml else cls_comp()
                newcomp.value = v
                newcomp.html = v
            except:
                pass
            self.add(newcomp)


class ListItem(Component):
    template = "<ListItem>{self.text}</ListItem>"
    rendertag = "li" # Use <li> instead of <ListItem> to render
    text = Property('')
    value = Property('')
  
Register.add(FilteredList)
Register.add(ListItem)
