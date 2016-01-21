"""
Editor component to edit and render Components code
"""
from components import Component, Property, Register, initialize_comps_classes
from browser import document, window



class ComponentEditor(Component):
    tag = "ComponentEditor"
    template = """<ComponentEditor>
                  <div class='panel'>
                      <div><h3>Brython</h3><CodeMirror cid='e1' mode='python'></CodeMirror></div>
                      <div><h3>HTML</h3><CodeMirror cid='e2'></CodeMirror>
                      <button onclick="{root.render_code()}">Render</button>
                      <button onclick="{root.share_code()}">Share</button>
                      <input type='text' cid='link' />
                      </div>
                  </div>

                  <div class='panel'>
                      <h3>Result</h3><ResultComponent cid='result'></ResultComponent>
                  </div>
                  </ComponentEditor>"""

    style = """
            :host .panel div  button{
                line-height: 30px;
                width: 200px;
                display: inline-block;
                margin: auto;
                margin-top: 20px;
                margin-bottom: 20px;
                font-size: 30px;
                cursor: pointer;
            }
            :host .panel div input{
                line-height:30px;
                width: 100%;
            }
            :host >div {
                width: 45%;
                margin-left: 10px;
                float: left;
            }

            """

    def on_mount(self):
        python_editor = self.get('e1')
        html_editor = self.get('e2')
        python_editor.mount_editor()
        html_editor.mount_editor()
        
        encoded_code = window.location.hash[1:]
        try:
            if len(encoded_code):
                code = window.Base64.decode(encoded_code)
                python_code, html_code = eval(code)
                python_editor.cm.setValue(python_code)
                html_editor.cm.setValue(html_code)
        except Exception as e:
            print ("Error decoding", e, "decode", code)

        window.editor_python = python_editor
        window.editor_html = html_editor

        self.render_code()

    def render_code(self):
        python_editor = self.get('e1')
        html_editor = self.get('e2')
        #Remove old component classes
        for comp_cls in Register.reg:
            if comp_cls not in (CodeMirror, ResultComponent, ComponentEditor):
                Register.remove(comp_cls)
        
        python_code = python_editor.get_code()
        try:
            eval(python_code)
        except Exception as e:
            print("Error evaluating code ", e)
        # Init comp classes again (User must have registered its comps in the code)
        initialize_comps_classes()

        # Add new html with components in it
        result_comp = self.get('result')
        result_comp.remove_all()
        result_comp.add_html(html_editor.get_code())

    def share_code(self):
        python_editor = self.get('e1')
        html_editor = self.get('e2')

        data = "['''%s''', '''%s''']"%(python_editor.get_code(), html_editor.get_code())
        encoded_code = window.Base64.encode(data)
        try:
            url = window.location.href.split('#')[0]
        except:
            url = window.location.href
        self.get('link').elem.value = "%s#%s"%(url, encoded_code)
        

class CodeMirror(Component):
    tag = "CodeMirror"
    mode = Property('xml')
    template="<CodeMirror></CodeMirror>"
    style = """
              :host {
                display: block;
                background-color:  #444;;
                padding: 10px;
            }
            :host .codemirror {min-height: 300px;}
            """
    
    def mount_editor(self):
        cm = window.CodeMirror
        self.cm = cm(self.elem, {"lineNumbers": True,"indentUnit": 4, "mode": self.mode})
        #self.cm = cm.fromTextArea(self.get('txt').elem, {"value": self.value, "lineNumbers": False, "mode": self.mode})
        self.refresh()

    def refresh(self):
        window.requestAnimationFrame(self._refresh)
    
    def _refresh(self, ev):
        self.cm.refresh()

    def get_code(self):
        return self.cm.getValue()

class ResultComponent(Component):
    tag = "ResultComponent"
    template = "<ResultComponent></ResultComponent>"
    style = """
             :host {
                display: block;
                background-color:  #fff;;
                border: 10px solid #444;
                padding: 15px;
                min-height: 700px;
            }
            """
    
Register.add(CodeMirror)
Register.add(ResultComponent)
Register.add(ComponentEditor)
