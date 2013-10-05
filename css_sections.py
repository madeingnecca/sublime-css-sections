import sublime
import sublime_plugin
import re


class CssSectionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # @TODO: ensure it's a css/less/sass file.
        sections = []
        quicklist = []

        regions = self.view.find_all('\* (=+)\s*([^\*]+)$', sublime.IGNORECASE)
        for r in regions:
            line = self.view.substr(self.view.line(r))
            # find_all only returns one extraction per match,
            # so we need to re-scan the line.
            match = re.search('(=+)\s*([^\*]+)', line)
            depth = len(match.group(1))
            sect = match.group(2)

            sections.append({'depth': depth, 'name': sect, 'region': r})

            # @TODO: it could be useful to add comments
            # as a second level of the quicklist.
            quicklist.append('({0}) {1}'.format(depth, sect))

        def quick_panel_done(index):
            if index is not -1:
                item = sections[index]
                self.view.sel().clear()
                self.view.sel().add(item['region'])
                self.view.show(item['region'])

        self.view.window().show_quick_panel(quicklist, quick_panel_done)
