import os, time, re
import sublime
import sublime_plugin
import glob
import os
from xml.etree import ElementTree

current_path = None

class CreateFileFromTemplateCommand(sublime_plugin.WindowCommand):
    ROOT_DIR_PREFIX = '[root: '
    ROOT_DIR_SUFFIX = ']'
    INPUT_PANEL_CAPTION = 'File name:'

    def run(self):

        if not self.find_root():
            return

        self.find_templates()
        self.window.show_quick_panel(self.templates, self.template_selected)

    def create_and_open_file(self, path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        
        open(path, 'w')
        
        global template
        template = {
            'content': self.replace_variables(self.get_content(path)),
            'filename': os.path.basename(path),
            'path': os.path.dirname(path)
        }

        global current_path
        
        view = self.window.open_file(path)
        current_path = view.file_name()

        if not view.is_loading():
            populate_file(view)

    def get_content(self, path):
        content = ''

        try:
            content = self.template.find("content").text
        except:
            pass

        try:
            path = os.path.abspath(os.path.join(os.path.dirname(self.template_path), self.template.find("file").text))
            content = open(path).read()
            print content
        except:
            pass

        return content


    def find_root(self):
        folders = self.window.folders()
        if len(folders) == 0:
            sublime.error_message('Could not find project root')
            return False

        self.root = folders[0]
        self.rel_path_start = len(self.root) + 1
        return True

    def construct_excluded_pattern(self):
        patterns = [pat.replace('|', '\\') for pat in self.get_setting('excluded_dir_patterns')]
        self.excluded = re.compile('^(?:' + '|'.join(patterns) + ')$')

    def get_setting(self, key):
        settings = None
        view = self.window.active_view()

        if view:
            settings = self.window.active_view().settings()

        if settings and settings.has('FileTemplates') and key in settings.get('FileTemplates'):
            # Get project-specific setting
            results = settings.get('FileTemplates')[key]
        else:
            # Get user-specific or default setting
            settings = sublime.load_settings('FileTemplates.sublime-settings')
            results = settings.get(key)
        return results
    
    def find_templates(self):
        self.templates = []
        self.template_paths = []

        for root, dirnames, filenames in os.walk(sublime.packages_path()):
            for filename in filenames:
                if filename.endswith(".file-template"):
                    self.template_paths.append(os.path.join(root, filename))
                    self.templates.append(os.path.basename(root) + ": " + os.path.splitext(filename)[0])

    def template_selected(self, selected_index):
        if selected_index != -1:
            self.template_path = self.template_paths[selected_index]
            #print self.template_path
            tree = ElementTree.parse(open(self.template_path))
            self.template = tree
            
            self.construct_excluded_pattern()
            self.build_relative_paths()
            #self.move_current_directory_to_top()
            self.window.show_quick_panel(self.relative_paths, self.dir_selected)

    def build_relative_paths(self):
        self.relative_paths = []

        try:
            path = self.template.find("path").text
        except:
            path = ""

        if len(path) > 0:
            self.relative_paths = [ "Default: " + self.template.find("path").text ]

        self.relative_paths.append( self.ROOT_DIR_PREFIX + os.path.split(self.root)[-1] + self.ROOT_DIR_SUFFIX )

        for base, dirs, files in os.walk(self.root):
            dirs_copy = dirs[:]
            [dirs.remove(dir) for dir in dirs_copy if self.excluded.search(dir)]

            for dir in dirs:
                relative_path = os.path.join(base, dir)[self.rel_path_start:]
                self.relative_paths.append(relative_path)

    def move_current_directory_to_top(self):
        view = self.window.active_view()

        if view:
            cur_dir = os.path.dirname(view.file_name())[self.rel_path_start:]
            for path in self.relative_paths:
                if path == cur_dir:
                    i = self.relative_paths.index(path)
                    self.relative_paths.insert(0, self.relative_paths.pop(i))
                    break

    def dir_selected(self, selected_index):
        if selected_index != -1:
            self.selected_dir = self.relative_paths[selected_index]
            
            filename = ''
            if len(self.template.find("filename").text) > 0:
                filename = self.template.find("filename").text

            try:
                self.arguments = list(self.template.find("arguments"))
            except:
                self.arguments = []
            
            self.variables = {}
            self.next_argument()

    def next_argument(self):
        if len(self.arguments) > 0 :
            self.argument = self.arguments.pop(0)
            caption = self.argument.text
            self.window.show_input_panel(caption, '', self.process_argument, None, None)
        else:
            self.file_name_input()

    def process_argument(self, value):
        self.variables[self.argument.tag] = value
        self.next_argument()

    def replace_variables(self, text):
        for variable in self.variables.keys():
            text = text.replace( "$" + variable, self.variables[variable] )
        return text

    def file_name_input(self):
        file_name = self.template.find("filename").text
        file_name = self.replace_variables(file_name)

        dir = self.selected_dir
        if self.selected_dir.startswith(self.ROOT_DIR_PREFIX):
            dir = ''
        if self.selected_dir.startswith("Default: "):
            dir = self.template.find("path").text
        
        dir = self.replace_variables(dir)

        full_path = os.path.join(self.root, dir, file_name)
        if os.path.lexists(full_path):
            sublime.error_message('File already exists:\n%s' % full_path)
            return
        else:
            self.create_and_open_file(full_path)
            
class FileTemplatesListener(sublime_plugin.EventListener):
    def on_load(self, view):
        global current_path
        if view.file_name() == current_path:
            populate_file(view)
            current_path = None

def populate_file(view):
    global template
    view.run_command("insert_snippet", {'contents': template["content"]})
