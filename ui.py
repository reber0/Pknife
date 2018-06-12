#!/usr/bin/env python
# -*- coding: utf-8 -*-
# code by reber
# 1070018473#qq.com

from PyQt4 import QtCore
from PyQt4 import QtGui

class addNewShell(QtGui.QDialog):  # 添加shell时的窗口
    def __init__(self):
        super(addNewShell, self).__init__()
        self.setWindowTitle("AddShell")
        self.setupUi()

    def setupUi(self): # 添加shell时的弹窗界面
        self.lbl_url = QtGui.QLabel('URL:')
        self.urlEdit = QtGui.QLineEdit('http://')
        self.urlEdit.adjustSize()
        self.passEdit = QtGui.QLineEdit()
        self.add_btn = QtGui.QPushButton('Add',self)
        self.add_btn.clicked.connect(self.close)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.lbl_url,1,0)
        grid.addWidget(self.urlEdit,1,1)
        grid.addWidget(self.passEdit,1,2)
        grid.addWidget(self.add_btn,3,1)

        self.setLayout(grid)


class editShell(QtGui.QDialog):  # 修改shell时的窗口
    def __init__(self, url, pwd):
        super(editShell, self).__init__()
        self.url = url
        self.pwd = pwd
        self.setWindowTitle("EditShell")
        self.setupUi()

    def setupUi(self):
        self.lbl_url = QtGui.QLabel('URL:')
        self.urlEdit = QtGui.QLineEdit(self.url)
        self.urlEdit.adjustSize()
        self.passEdit = QtGui.QLineEdit(self.pwd)
        self.edit_btn = QtGui.QPushButton('Edit',self)
        self.edit_btn.clicked.connect(self.close)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.lbl_url,1,0)
        grid.addWidget(self.urlEdit,1,1)
        grid.addWidget(self.passEdit,1,2)
        grid.addWidget(self.edit_btn,3,1)

        self.setLayout(grid)

class editFile(QtGui.QDialog):
    """docstring for editFile"""
    def __init__(self, text):
        super(editFile, self).__init__()
        self.setWindowTitle('EditFile')
        self.resize(500,400)
        self.text = text

        self.fileEdit = QtGui.QTextEdit()
        self.fileEdit.append(self.text)
        self.btn = QtGui.QPushButton('Save',self)
        self.btn.clicked.connect(self.close)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.fileEdit,1,0)
        grid.addWidget(self.btn,2,0)

        self.setLayout(grid)

class NewFile(QtGui.QDialog):
    """docstring for NewFile"""
    def __init__(self):
        super(NewFile, self).__init__()
        self.setWindowTitle('NewFile')
        self.resize(500,400)
        
        self.lbl_name = QtGui.QLabel('Name: ')
        self.text_name = QtGui.QLineEdit()
        self.content = QtGui.QTextEdit()
        self.btn = QtGui.QPushButton('Create',self)
        self.btn.clicked.connect(self.close)

        gird = QtGui.QGridLayout()
        gird.setSpacing(10)
        gird.addWidget(self.lbl_name,1,0)
        gird.addWidget(self.text_name,1,1)
        gird.addWidget(self.content,2,0,1,2)
        gird.addWidget(self.btn,3,0)

        self.setLayout(gird)

class AddCmdTab(QtGui.QTabWidget):
    """docstring for CmdClass"""
    def __init__(self, url, pwd):
        super(AddCmdTab, self).__init__()
        self.setWindowTitle('Cmd')
        self.url = url
        self.pwd = pwd
        self.content = ''
        self.prefix = '>'

        self.init_UI()

    def init_UI(self):
        self.command = QtGui.QPlainTextEdit(self)
        self.command.appendPlainText('xxxxxxxxxxxx')
    def sendmsg(self):
        print 'ssss'
        print self.command.toPlainText()

    def keyPressEvent(self,event):
        k = QtGui.QKeyEvent(event)
        print k.key()
        print k.text()


        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    addshell = addNewShell()
    addshell.show()
    # editshell = editShell('http://www.xx.com/q.php', '123456')
    # editshell.show()
    app.exec_()