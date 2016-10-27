import sublime
import sublime_plugin
from subprocess import Popen, PIPE
from random import random

mmix_status_code = 0
def mmix_show_status(view, text):
    view.set_status("mmix", text)
    mmix_status_code = random()
    sublime.set_timeout(lambda code=mmix_status_code, view=view: view.set_status("mmix", "") if mmix_status_code == code else False, 5000)

class MmixTranslateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command('save')
        file = self.view.file_name()
        if (file == None):
            mmix_show_status(self.view, "✘ MMIX: Can't translate an unsaved file")
        else:
            child = Popen(["mmixal", file], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = child.communicate(b"")
            code = child.returncode
            if code == 0:
                has_output = ""
                if len(out) != 0 or len(err) != 0:
                    has_output = ", check output for more information"
                mmix_show_status(self.view, "✔ MMIX: Translation successful" + has_output)
                # @TODO Hide Status text after some time
            else:
                mmix_show_status(self.view, "✘ MMIX: Translation failed, check output for more information")
            if len(out) != 0 or len(err) != 0:
                panel = self.view.window().get_output_panel("mmixal")
                self.view.window().run_command("show_panel", {"panel": "output.mmixal"})
                panel.run_command('mmix_panel_append', {'content': out.decode("utf-8") + err.decode("utf-8"), 'scroll': True})
            else:
                self.view.window().run_command("hide_panel", {"panel": "output.mmixal"})

# Run and debug open a new view containing the output. Every keypress is sent to STDIN, the cursor is kept at the end.
#class MmixRunCommand(sublime_plugin.TextCommand):
#class MmixDebugCommand(sublime_plugin.TextCommand):
#class MmixTranslateAndRunCommand(sublime_plugin.TextCommand):
#class MmixTranslateAndDebugCommand(sublime_plugin.TextCommand):

# @TODO Kill process if the output window is closed
class MmixKill(sublime_plugin.EventListener):
    def on_close(self, view):
        print(view)


class MmixPanelWriteCommand(sublime_plugin.TextCommand):

    def is_visible(self):
        return False

    def run(self, edit, content=''):
        self.view.set_read_only(False)
        if self.view.size() > 0:
            self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, content)
        self.view.set_read_only(True)


class MmixPanelAppendCommand(sublime_plugin.TextCommand):

    def is_visible(self):
        return False

    def run(self, edit, content='', scroll=False):
        self.view.insert(edit, self.view.size(), content)
        if scroll:
            self.view.show(self.view.size())
