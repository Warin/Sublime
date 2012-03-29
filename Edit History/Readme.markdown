Edit History
============

Navigate back and forward between edit locations in the current file.

"Rules"
-------

* A new edit location is only created if it is greater than 5 lines away from the previous saved edit location. ( number customizable via settings file )
* When you go back to a point and then create a new edit location all the "future" locations are cleared, as in a web-browser.

Commands
--------

Edit history provides three commands: `previous_edit`, `next_edit` and `clear_edits`

Keybindings
-----------

No default keybindings are provided as I couldn't find defaults that I liked that didn't override existing ones. I suggest `super+[` on Mac and `ctrl+[` on Linux and Windows. This overrides unindent and indent (I use Tab and Shift+Tab for this functionality). You can add the following to your User Keybindings:

Mac

```
  { "keys": ["super+["], "command": "previous_edit" },
  { "keys": ["super+]"], "command": "next_edit" }
```

Linux/Windows

```
  { "keys": ["ctrl+["], "command": "previous_edit" },
  { "keys": ["ctrl+]"], "command": "next_edit" }
```

Context Menu
------------

Edit History adds "Back" and "Forward" entries to the context/right-click menu.