import sublime
import sublime_plugin


class OpenRecentFilesCommand(sublime_plugin.WindowCommand):
    def run(self):
        w = sublime.active_window()
        counter = 0
        numViews = len(w.views())
        while (counter < 20):
            w.run_command('open_recent_file', {"index": counter})
            if numViews < len(w.views()):
                break
            counter += 1
