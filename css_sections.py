import sublime
import sublime_plugin
import re


class CssSectionsCommand(sublime_plugin.TextCommand):

    def build_tree(self, sections, indent):
        sid = 1
        root = {'path': [], 'pid': None, 'sid': 0}
        tree_index = {}
        tree_index[0] = root
        last_by_depth = {}

        tree = []
        for section in sections:
            depth = section['depth']
            name = section['name']

            # Remember the id of the last item with this depth.
            # So it can be retrieved by our children (depth + 1)
            last_by_depth[depth] = sid

            node = {'path': [name], 'pid': 0, 'sid': sid}
            if (depth - 1) in last_by_depth:
                pid = last_by_depth[depth - 1]
                node['pid'] = pid
                node['path'].extend(tree_index[pid]['path'])

            result = (indent * (depth - 1)) + ' / '.join(reversed(node['path']))
            tree.append(result)

            tree_index[sid] = node
            sid += 1

        return tree

    def run(self, edit):
        sections = []
        quicklist = []

        # @TODO: make regexes configurable.
        matching_regions = self.view.find_all('\* (=+)\s*([^\*]+)$', sublime.IGNORECASE)

        for r in matching_regions:
            line = self.view.substr(self.view.line(r))
            # "find_all" only returns one extraction per match,
            # so we need to re-scan the line.
            match = re.search('(=+)\s*([^\*]+)', line)
            depth = len(match.group(1))
            sect = match.group(2)

            # Flat list of sections.
            sections.append({'depth': depth, 'name': sect, 'region': r})

        # Process sections so every item of the quicklist
        # contains the "path" to the section.
        quicklist = self.build_tree(sections, indent='   ')

        def goto_section(index):
            if index is not -1:
                item = sections[index]
                self.view.sel().clear()
                self.view.sel().add(item['region'])
                self.view.show(item['region'])

        self.view.window().show_quick_panel(quicklist, goto_section)
