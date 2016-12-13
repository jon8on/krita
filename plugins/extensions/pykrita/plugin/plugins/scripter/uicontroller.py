from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from scripter.ui_scripter.syntax import syntax, syntaxstyles
from scripter.ui_scripter.editor import pythoneditor
import os
import importlib


class UIController(object):

    def __init__(self, mainWidget):
        self.mainWidget = mainWidget
        self.actionToolbar = QToolBar('toolBar', self.mainWidget)
        self.menu_bar = QMenuBar(self.mainWidget)

        self.actionToolbar.setObjectName('toolBar')
        self.menu_bar.setObjectName('menuBar')

        self.actions = []

        self.mainWidget.setWindowModality(Qt.NonModal)
        self.editor = pythoneditor.CodeEditor()
        self.output = QPlainTextEdit()
        self.statusBar = QLabel('untitled')
        self.highlight = syntax.PythonHighlighter(self.editor.document(), syntaxstyles.DefaultSyntaxStyle())

    def initialize(self, scripter):
        self.scripter = scripter

        self.loadMenus()
        self.loadActions()

        vbox = QVBoxLayout(self.mainWidget)
        vbox.addWidget(self.menu_bar)
        vbox.addWidget(self.editor)
        vbox.addWidget(self.actionToolbar)
        vbox.addWidget(self.output)
        vbox.addWidget(self.statusBar)

        self.mainWidget.resize(400, 500)
        self.mainWidget.setWindowTitle("Scripter")
        self.mainWidget.setSizeGripEnabled(True)
        self.mainWidget.show()
        self.mainWidget.activateWindow()

    def loadMenus(self):
        self.addMenu('File', 'File')
        self.addMenu('Edit', 'Edit')

    def addMenu(self, menuName, parentName):
        parent = self.menu_bar.findChild(QObject, parentName)
        self.newMenu = None

        if parent:
            self.newMenu = parent.addMenu(menuName)
        else:
            self.newMenu = self.menu_bar.addMenu(menuName)

        self.newMenu.setObjectName(menuName)

        return self.newMenu


    def loadActions(self):
        module_path = 'scripter.ui_scripter.actions'
        actions_module = importlib.import_module(module_path)
        modules = []

        for class_path in actions_module.action_classes:
            _module, _klass =  class_path.rsplit('.', maxsplit=1)
            modules.append(dict(module='{0}.{1}'.format(module_path, _module),
                                klass=_klass))

        for module in modules:
            m = importlib.import_module(module['module'])
            action_class = getattr(m, module['klass'])
            obj = action_class(self.scripter)
            parent = self.mainWidget.findChild(QObject, obj.parent)
            self.actions.append(dict(action=obj, parent=parent))

        for action in self.actions:
            action['parent'].addAction(action['action'])

    def invokeAction(self, actionName):
        for action in self.actions:
            if action['action'].objectName() == actionName:
                method = getattr(action['action'], actionName)
                if method:
                    return method()

    def setDocumentEditor(self, document):
        self.editor.clear()

        for line in document.data:
            self.editor.appendPlainText(line)

    def setStatusBar(self, value='untitled'):
        self.statusBar.setText(value)

    def clearEditor(self):
        self.editor.clear()