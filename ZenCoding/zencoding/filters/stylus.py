import zencoding

@zencoding.filter('stylus')
def process(tree, profile):
    for item in tree.children:
        # CSS properties are always snippets 
        if item.type == 'snippet':
            item.start = item.start.rstrip(';')
        process(item, profile)
    return tree