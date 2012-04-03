# CSS Less(ish)

This is a [SublimeText 2](http://www.sublimetext.com/2) plugin that facilitates a very very stripped down version of the functionality in LESS css. ([http://lesscss.org](http://lesscss.org))

### CSS Variables

You can store variables within comments using the "@" symbol, then use them anywhere within your css.

    /* @link = "#FF0000" */  
    a { color: @link; }`

produces

    /* @link = "#FF0000" */
    a { color: #FF0000; }

### CSS Nesting

You can nest styles within other blocks to append that selector to all children.

    .header [
        h1 { color:blue }
        a { color:blue }
    ]

produces

    .header h1 { color:blue }
    .header a { color:blue }

### CSS Colours

You can use colour functions when declaring css variables including `lighten`, `darken`, `saturate`, and `desaturate`. You can pass existing variables as arguments too.

    /* 
    @base-colour = #336699
    @link = lighten(@base-colour, 20%) 
    */  
    a { color: @link; }

produces

    a { color: #3d7ab7; }


### Read More

You can [read more on the wiki](https://github.com/kizza/CSS-Less-ish/wiki).
