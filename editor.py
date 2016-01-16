"""
Editor component to edit and render Components code
"""
from components import Component, Property, Register
from browser import document, window



class ComponentEditor(Component):
    tag = "ComponentEditor"
    template = """<ComponentEditor>
                  <div class='panel'>
                      <div><h3>Brython</h3><CodeMirror cid='e1' mode='python'></CodeMirror></div>
                      <div><h3>HTML</h3><CodeMirror cid='e2'></CodeMirror>
                      <button onclick="{self.render_code()}">Render</button>
                      <button onclick="{self.share_code()}">Share</button>
                      <input type='text' cid='link' />
                      </div>
                  </div>

                  <div class='panel'>
                      <h3>Result</h3><ResultComponent cid='result'></ResultComponent>
                  </div>
                  </ComponentEditor>"""

    t= 0
    def on_is_mounted(self, value, instance):
        print("Editors")
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


    def render_code(self):
        self.t+=1
        self.get('result').ifrm_source = 'editor_result.html?v=%s'%(self.t)

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
    
    def mount_editor(self):
        cm = window.CodeMirror
        self.cm = cm(self.elem, {"lineNumbers": True,"indentUnit": 4, "mode": self.mode})
        #self.cm = cm.fromTextArea(self.get('txt').elem, {"value": self.value, "lineNumbers": False, "mode": self.mode})
    def get_code(self):
        return self.cm.getValue()

class ResultComponent(Component):
    tag = "ResultComponent"
    ifrm_source = Property('editor_result.html')
    template = "<ResultComponent><iframe src='{self.ifrm_source}'></iframe></ResultComponent>"
    
Register.add(CodeMirror)
Register.add(ResultComponent)
Register.add(ComponentEditor)
