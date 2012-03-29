CSSpecific is a [Sublime Text][sublime] plugin which will calculate and display the [CSS Specificity value][spec] of your selectors.

## Installation ## 

Clone the repository into your Sublime Text packages folder:

    git clone https://github.com/spadgos/sublime-csspecific CSSpecific

Don't forget to watch for updates!

*Installation via Package Control coming soon.* 

## Usage ##

Open a file containing CSS (this can include HTML files!), and then activate CSSpecific by hitting the hotkey (default: `Alt+Ctrl+Shift+C`), or using the Command Palette.

If you have nothing selected, then all CSS selectors in the file will be evaluated. If you have one or more non-empty selections, then only the selectors which intersect with your selections will be shown.

## Notes ##

- Actual CSS specificity is not calculated as a single number. For simplicity, the real values are converted to a single number (basically, id = 100, class = 10, tag = 1), which is fine in most circumstances, but will break if you have more than 10 classes or tags referenced in a single selector. If this is the case for you, you have bigger problems to deal with first.

- If you find a bug in the calculations, send me a pull request or report an issue in the [tracker][issues]. Feature requests welcome, too.


[sublime]: http://www.sublimetext.com/
[spec]: http://www.w3.org/TR/CSS2/cascade.html#specificity
[issues]: https://github.com/spadgos/sublime-csspecific/issues
