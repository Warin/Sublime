import sublime
import sublime_plugin


class DuplicateSelectionsCommand(sublime_plugin.TextCommand):
    def duplicate_regions(self, edit, empty_region, notempty_region):
        notempty_content = self.view.substr(notempty_region)
        self.view.replace(edit, empty_region, notempty_content)

    def run(self, edit, **kwargs):
        empties = []
        notempties = []
        for region in self.view.sel():
            if region:
                notempties.append(region)
            else:
                empties.append(region)

        if not notempties:
            sublime.status_message("No non-empty regions")
            return
        if not empties:
            sublime.status_message("No empty regions")
            return
        if len(notempties) > 1 and len(empties) != len(notempties):
            sublime.status_message("Number of empty regions (%i) does note equal number of non-empty regions (%i)" % (len(empties), len(notempties)))
            return

        e = self.view.begin_edit('duplicate_selections')
        for region_i, empty_region in enumerate(empties):
            if len(notempties) == 1:
                notempty_region = notempties[0]
            else:
                notempty_region = notempties[region_i]

            # adjust regions to the right of empty_region
            for fix_i, fix_region in enumerate(notempties):
                if fix_region.begin() >= empty_region.end():
                    notempties[fix_i] = sublime.Region(fix_region.a + len(notempty_region), fix_region.b + len(notempty_region))
            for fix_i, fix_region in enumerate(empties):
                if fix_region.begin() >= empty_region.end():
                    empties[fix_i] = sublime.Region(fix_region.a + len(notempty_region), fix_region.b + len(notempty_region))

            self.duplicate_regions(edit, empty_region, notempty_region)
        self.view.sel().clear()
        for region in empties:
            self.view.sel().add(region)
        self.view.show_at_center(empties[0])
        self.view.end_edit(e)
