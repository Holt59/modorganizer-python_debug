"""An example of embedding a RichJupyterWidget in a PyQT Application.

This uses a normal kernel launched as a subprocess. It shows how to shutdown
the kernel cleanly when the application quits.

To run:

    python3 embed_qtconsole.py
"""
import json
import os
import site

from pathlib import Path
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

import mobase
import moprivate

site.addsitedir(os.path.join(os.path.dirname(__file__), "lib"))

from pyqtconsole.commandhistory import CommandHistory  # noqa: E402
from pyqtconsole.console import PythonConsole  # noqa: E402

history_file = Path(__file__).parent.joinpath("history.json")


class PersistentCommandHistory(CommandHistory):

    _json: List[str]

    def __init__(self, parent):
        super().__init__(parent)

        self._json = []
        if history_file.exists():
            with open(history_file, "r") as fp:
                self._json = json.load(fp)
                for command in self._json:
                    super().add(command)

    def add(self, str_):
        super().add(str_)

        if str_:
            if str_ in self._json:
                self._json.remove(str_)
            self._json.append(str_)

            # Keep only the 100 last lines:
            self._json = self._json[-100:]
            with open(history_file, "w") as fp:
                json.dump(self._json, fp, indent=2)


class InfinitePythonConsole(PythonConsole):
    def __init__(self, *args, **kwargs):

        oldps = self._show_ps
        self._show_ps = lambda *args: None

        super().__init__(*args, **kwargs)

        self.command_history = PersistentCommandHistory(self)

        styles = self.pbar.highlighter.styles
        self.pbar.highlighter.rules = [
            # Match the prompt incase of a console
            (QtCore.QRegExp(r"In[^\:]*"), 0, styles["inprompt"]),
            (QtCore.QRegExp(r"Out[^\:]*"), 0, styles["outprompt"]),
            # Numeric literals
            (QtCore.QRegExp(r"\b[+-]?[0-9]+\b"), 0, styles["numbers"]),
        ]

        self._ps1 = "In [%s]: "
        self._ps2 = "...: "
        self._ps_out = "Out[%s]: "
        self._ps = self._ps1 % self._current_line

        self._show_ps = oldps

        self.interpreter.locals["clear"] = self._clear

    def _clear(self):
        edit = self.edit
        vsb = self.edit.verticalScrollBar()
        fm = QtGui.QFontMetrics(self.edit.font())

        nvislines = min(
            edit.document().lineCount(),
            (edit.height() - edit.document().documentMargin() * 2) // fm.lineSpacing(),
        )

        vsb.setMaximum(vsb.maximum() + nvislines - 1)
        vsb.setValue(vsb.maximum())

    def exit(self):
        self._close()


class IPythonDebugPlugin(mobase.IPluginTool):

    _organizer: mobase.IOrganizer

    def __init__(self):
        super().__init__()  # You need to call this manually.

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer

        # Create the console:
        self._console = InfinitePythonConsole(
            locals={
                "organizer": self._organizer,
                "mobase": mobase,
                "moprivate": moprivate,
                "_plugin": self,
            }
        )
        self._console.resize(840, 680)
        self._setFont()
        self._console._show_ps()
        self._console.eval_in_thread()

        self._organizer.onUserInterfaceInitialized(
            lambda mw: QtWidgets.QShortcut(
                QtGui.QKeySequence(QtCore.Qt.Key_F12), mw
            ).activated.connect(self.display),
        )

        return True

    def name(self) -> str:
        return "Python Debugger"

    def author(self) -> str:
        return "Holt59"

    def description(self) -> str:
        return self._tr("Run Python from MO2")

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 0, 1, mobase.ReleaseType.FINAL)

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            mobase.PluginSetting(
                "font family", "font family for the terminal", "Courier New"
            ),
            mobase.PluginSetting("font size", "font size for the terminal", 10),
        ]

    def displayName(self) -> str:
        return self._tr("Python Debugger")

    def icon(self) -> QtGui.QIcon:
        return QtGui.QIcon(
            os.path.join(os.path.dirname(__file__), "res", "python.webp")
        )

    def tooltip(self) -> str:
        return self._tr("Open the Python debugger")

    def display(self):
        self._console.show()

    def _setFont(self):
        font = self._console.edit.document().defaultFont()
        font.setFamily(self._organizer.pluginSetting(self.name(), "font family"))
        font.setPointSize(self._organizer.pluginSetting(self.name(), "font size"))
        self._console.setFont(font)

    def _tr(self, txt: str) -> str:
        return QtWidgets.QApplication.translate(IPythonDebugPlugin.__name__, txt)


def createPlugin() -> mobase.IPlugin:
    return IPythonDebugPlugin()
