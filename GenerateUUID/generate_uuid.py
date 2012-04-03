import sublime_plugin
import uuid

class GenerateUuidCommand(sublime_plugin.TextCommand):
    """
    Generate a UUID version 4.
    Plugin logic for the 'generate_uuid' command.

    Author: Eric Hamiter    
    Seealso: https://github.com/ehamiter/Sublime-Text-2-Plugins
    """
    def run(self, edit):
        u = str(uuid.uuid4())
        for r in self.view.sel():
            self.view.replace(edit, r, u)

class GenerateUuidListenerCommand(sublime_plugin.EventListener):
    """
    Expand 'uuid' and 'uuid4' to a random uuid (uuid4) and 
    'uuid1' to a uuid based on host and current time (uuid1).

    Author: Rob Cowie
    Seealso: https://github.com/SublimeText/GenerateUUID/issues/1
    """
    def on_query_completions(self, view, prefix, locations):
        if prefix in ('uuid', 'uuid4'): # random
            val = uuid.uuid4()
        elif prefix == 'uuid1':         # host and current time
            val = uuid.uuid1()
        else:
            return []
        return [(prefix, prefix, str(val))] if val else []
