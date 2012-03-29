import sublime
import sublime_plugin

HISTORY_KEY = "edit_history"
HISTORY_KEY_PREV = "edit_history_region_prev"
HISTORY_KEY_NEXT = "edit_history_region_next"

# can't save Regions in the view settings(), and regions get reordered to be
# sequential, so store locally
histories = {}

settings = sublime.load_settings('Edit History.sublime-settings')


class Pref:
    def load(self):
        Pref.line_proximity_thresh        = settings.get('line_proximity_thresh', 5)
        Pref.visible_on_view_context_menu = settings.get('visible_on_view_context_menu', True)
Pref = Pref()
Pref.load()
settings.add_on_change('reload', lambda: Pref.load())


class History(object):
    """Object to store the history for a view"""
    def __init__(self, view):
        self.view = view
        self._previous_points = 0
        self._next_points = 0

    def _update_view(self, point=None):
        if not point is None:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
            self.view.show(point)

    # def _set_point(self, key, index, point=None):
    #     if not point is None:
    #         point = sublime.Region(point, point)
    #     self.view.add_regions(key + index, point)

    def _set_previous(self, region, index=-1):
        if index == -1:
            index = self._previous_points

        assert region is not None
        self.view.add_regions(HISTORY_KEY_PREV + str(index), [region], HISTORY_KEY)

    def _set_next(self, region, index=-1):
        if index == -1:
            index = self._next_points

        assert region is not None
        self.view.add_regions(HISTORY_KEY_NEXT + str(index), [region], HISTORY_KEY)

    def back(self):
        # The last element of _previous is the current position, so we need
        # to pop one, and then move to the item before
        if self._previous_points <= 1:
            return False

        # move top of previous to next
        self._next_points += 1
        self._set_next(self.current())
        self._previous_points -= 1

        assert self._previous_points > 0
        # change view to point to new top
        self._update_view(self.current().begin())
        return True

    def forward(self):
        if self._next_points == 0:
            return False

        # move top of next to previous
        self._previous_points += 1
        self._set_previous(self.next())
        self._next_points -= 1

        # change view to point to new current
        self._update_view(self.current().begin())
        return True

    def add(self, point):
        self.clear(True)
        self._previous_points += 1
        self._set_previous(sublime.Region(point))

    def clear(self, only_next=False):
        for n in xrange(1, self._next_points):
            self.view.erase_regions(HISTORY_KEY_NEXT + str(n))
        self._next_points = 0

        if not only_next:
            for n in xrange(1, self._previous_points):
                self.view.erase_regions(HISTORY_KEY_PREV + str(n))
            self._previous_points = 0

    def current(self):
        if self._previous_points <= 0:
            return None
        regions = self.view.get_regions(HISTORY_KEY_PREV + str(self._previous_points))
        if len(regions) > 0:
            return regions[0]

    def previous(self):
        if self._previous_points <= 1:
            return None
        regions = self.view.get_regions(HISTORY_KEY_PREV + str(self._previous_points - 1))
        if len(regions) > 0:
            return regions[0]

    def next(self):
        if self._next_points <= 0:
            return None
        regions = self.view.get_regions(HISTORY_KEY_NEXT + str(self._next_points))
        if len(regions) > 0:
            return regions[0]


def get_history(view):
    view_id = view.id()
    if view_id in histories:
        return histories[view_id]
    else:
        h = History(view)
        histories[view_id] = h
        return h


def get_line_from_region(view, region):
    return view.rowcol(region.begin())[0]


class EditHistory(sublime_plugin.EventListener):

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'):
            return

        history = get_history(view)

        this_edit_point = view.sel()[0].begin()
        this_edit_line = view.rowcol(this_edit_point)[0]

        current = history.current()

        if current is None:
            last_edit_line = -99
        else:
            # get only the last edit line
            last_edit_line = get_line_from_region(view, current)

        if (abs(this_edit_line - last_edit_line) > Pref.line_proximity_thresh):
            history.add(this_edit_point)

    def on_selection_modified(self, view):
        view.set_status(HISTORY_KEY, "")


class ClearEditsCommand(sublime_plugin.TextCommand):
    """Clears the history of edit points"""

    def run(self, edit):
        get_history(self.view).clear()
        self.view.set_status(HISTORY_KEY, "Edit history cleared")


class PreviousEditCommand(sublime_plugin.TextCommand):
    """Moves the cursor to the previous edit in the current file"""

    def run(self, edit, where='unknown'):
        history = get_history(self.view)

        if not history.back():
            self.view.set_status(HISTORY_KEY, "No previous edit history")

    def is_enabled(self):
        return not get_history(self.view).previous() is None

    def is_visible(self, where='unknown'):
        return Pref.visible_on_view_context_menu


class NextEditCommand(sublime_plugin.TextCommand):
    """Moves the cursor to the next edit in the current file"""

    def run(self, edit, where='unknown'):
        history = get_history(self.view)

        if not history.forward():
            self.view.set_status(HISTORY_KEY, "No next edit history")

    def is_enabled(self):
        return not get_history(self.view).next() is None

    def is_visible(self, where='unknown'):
        return Pref.visible_on_view_context_menu
