# File Templates for SublimeText 2

This Package enables you and other Package Developers to include File Templates.
A File Template is basically a snippet, a filename, a default path and optional arguments.


# Demo

http://www.youtube.com/embed/M4isYen7_Z4

## Installation

### Package Control

The easiest way to install this is with Package Control.

If you just went and installed Package Control, you probably need to restart Sublime Text 2 before doing this next bit.

- Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
- Select "Package Control: Install Package" (it'll take a few seconds)
- Select FileTemplates when the list appears.

Package Control will automatically keep FileTemplates up to date with the latest version.

### Clone from GitHub

    git clone http://github.com/mneuhaus/SublimeFileTemplates

## Usage

Bring up the Command Palette and select "Create File From Template" or set up some key bindings as
explained below.


### Templates

The Templates are files with the extension ".file-template"

Here's a basic example 

```xml
<template>
  <!-- You can us this to specifiy the content for the Template -->
  <!-- <content><![CDATA[ ${0:Hello World} ]]></content> -->

  <!-- Or you set a path to a seperate Template File here -->
  <file>jQueryPlugin.js</file>

  <!-- The filename for the new File, you can use the arguments to make it dynamic -->
  <filename>jquery.$name.js</filename>

  <!-- Default Path to create the new file inside your current Project -->
  <!-- you can use the arguments to make it dynamic -->
  <path>js/</path>

  <!-- Optional: Add as much arguments as you need, they will be asked in the order specified -->
  <arguments>
    <name>Name:</name>
  </arguments>
</template>
```

## Key bindings

The plugin does not install any key bindings automatically. You can set up
your own key bindings like this:

    { "keys": ["super+ctrl+n"], "command": "create_file_from_template" }

If you are using Vintage mode and want to use sequences of non-modifier keys,
you can restrict the key bindings to command mode like this:

    { "keys": [" ", "n"], "command": "create_file_from_template", "context": [{"key": "setting.command_mode"}] }


## Thanks

This Package was forked from [SublimeQuickFileCreator](https://github.com/noklesta/SublimeQuickFileCreator) because it provided the best base for my needs and a good starting point to learn from :)

## Licence

All of SublimeFileTemplates is licensed under the MIT licence.

  Copyright (c) 2012 Anders Nøklestad

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.