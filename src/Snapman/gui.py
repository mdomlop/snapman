import time
from Snapman.section import Section, Snapshot, settings
from Snapman.about import *
from Snapman.quit import *  # include os, sys


class TableWidget(QWidget):
    def __init__(self):
        super(TableWidget, self).__init__()
        self.mbox = QMessageBox()

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterKeyColumn(0)  # 0 is PATH

        self.proxyView = QTableView()
        self.proxyView.setModel(self.proxyModel)
        self.proxyView.setSortingEnabled(True)
        self.proxyView.verticalHeader().setVisible(False)
        self.proxyView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.proxyView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.proxyView.sortByColumn(0, Qt.AscendingOrder)  # 0 is PATH
        self.proxyView.selectionModel().selectionChanged.connect(
            self.itemSelected)

        self.filterPatternLineEdit = QLineEdit()
        self.filterPatternLineEdit.setClearButtonEnabled(True)
        self.filterPatternLineEdit.textChanged.connect(
            self.filterRegExpChanged)

        self.filterPatternLabel = QLabel("&Filter:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)

        self.filterSyntaxComboBox = QComboBox()
        self.filterSyntaxComboBox.addItem("Fixed string", QRegExp.FixedString)
        self.filterSyntaxComboBox.addItem("Wildcard", QRegExp.Wildcard)
        self.filterSyntaxComboBox.addItem("Regular expression", QRegExp.RegExp)
        self.filterSyntaxComboBox.currentIndexChanged.connect(
            self.filterRegExpChanged)

        self.filterColumnComboBox = QComboBox()
        self.filterColumnComboBox.currentIndexChanged.connect(
            self.filterColumnChanged)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.filterColumnComboBox, 0, 0)
        mainLayout.addWidget(self.filterPatternLineEdit, 0, 1)
        mainLayout.addWidget(self.filterSyntaxComboBox, 0, 2)
        mainLayout.addWidget(self.proxyView, 1, 0, 1, 3)
        self.setLayout(mainLayout)

    def filterRegExpChanged(self):
        syntax_nr = self.filterSyntaxComboBox.itemData(
            self.filterSyntaxComboBox.currentIndex())
        syntax = QRegExp.PatternSyntax(syntax_nr)

        regExp = QRegExp(self.filterPatternLineEdit.text(),
                         Qt.CaseInsensitive, syntax)
        self.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        self.proxyModel.setFilterKeyColumn(
            self.filterColumnComboBox.currentIndex() + 1)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def getTableViewValue(self, row, column, widget):
        coordinates = widget.model().index(row, column)
        return(widget.model().data(coordinates))

    def reloadTable(self):
        app.setOverrideCursor(Qt.WaitCursor)
        oldindex = self.proxyView.currentIndex().row()
        if not oldindex:
            oldindex = 0
        self.setSourceModel(self.createModel())
        self.proxyView.resizeColumnsToContents()
        self.proxyView.setCurrentIndex(
            self.proxyView.model().index(max(oldindex, 0), 0))
        app.restoreOverrideCursor()


class SectionTable(TableWidget):
    sect_title = Section.info_name.capitalize()
    subv_title = Section.info_subvolume.capitalize()
    count_title = Section.info_count.capitalize()
    quota_title = Section.info_quota.capitalize()
    freq_title = Section.info_frequency.capitalize()
    enabled_title = Section.info_enabled.capitalize()

    def __init__(self):
        super(SectionTable, self).__init__()
        self.selected = set()
        self.filterColumnComboBox.addItem(self.sect_title)
        self.filterColumnComboBox.addItem(self.subv_title)
        self.filterColumnComboBox.addItem(self.count_title)
        self.filterColumnComboBox.addItem(self.quota_title)
        self.filterColumnComboBox.addItem(self.freq_title)
        self.filterColumnComboBox.addItem(self.enabled_title)

    def createModel(self):
        # Column indices:
        PATH, SUBV, NSNAP, QUOTA, FREQUENCY, ENABLED = range(6)

        model = QStandardItemModel(0, 6)
        model.setHeaderData(PATH, Qt.Horizontal, self.sect_title)
        model.setHeaderData(SUBV, Qt.Horizontal, self.subv_title)
        model.setHeaderData(NSNAP, Qt.Horizontal, self.count_title)
        model.setHeaderData(QUOTA, Qt.Horizontal, self.quota_title)
        model.setHeaderData(FREQUENCY, Qt.Horizontal, self.freq_title)
        model.setHeaderData(ENABLED, Qt.Horizontal, self.enabled_title)

        for i in settings.sections:
            x = Section(settings.config[i])
            model.insertRow(0)
            model.setData(model.index(0, PATH), x.name)
            model.setData(model.index(0, SUBV), x.subvolume)
            model.setData(model.index(0, NSNAP), x.count)
            model.setData(model.index(0, QUOTA), x.percent)
            model.setData(model.index(0, FREQUENCY), x.frequency)
            model.setData(model.index(0, ENABLED), x.enabled)
        return model

    def itemSelected(self):
        # Using set() type for prevent repeated
        # values in proxyView.selectedIndexes:
        # TODO: Remember selected if exist
        self.selected = set()
        for i in self.proxyView.selectedIndexes():
            row = i.row()
            item = self.getTableViewValue(row, 0, self.proxyView)
            self.selected.add(item)
        mainWindow.snapshotTable.selected = {}
        mainWindow.snapshotTable.reloadTable()
        mainWindow.snapshotTable.proxyView.setColumnHidden(0, True)
        mainWindow.updateButtons()
        mainWindow.updateStatusBar()

    def new_snapshot(self):
        failed = []
        ok = False
        for s in self.selected:
            x = Section(settings.config[s])
            if x.makesnapshot(force=True):
                ok = True
            else:
                failed.append(s)

        if failed:
            text = 'Failed to create new snapshots for the sections: \n\n' + \
                '\n'.join(failed) + '\
            \n\nMaybe are not you root?'
            title = 'Operation failed'
            self.mbox.warning(self, title, text, self.mbox.Ok)

        if ok:  # Only update table if some change happened
            self.reloadTable()

    def delete(self):
        failed = []
        ok = False
        for s in self.selected:
            x = Section(settings.config[s])
            if x.snapshot_clean():
                ok = True
            else:
                failed.append(s)

        if failed:
            text = 'Failed to clean sections: \n\n' + '\n'.join(failed) + '\
            \n\nMaybe are not you root?'
            title = 'Operation failed'
            self.mbox.warning(self, title, text, self.mbox.Ok)

        if ok:  # Only update table if some were deleted
            self.reloadTable()


class SnapshotTable(TableWidget):
    path_title = Snapshot.info_path
    sect_title = Snapshot.info_section
    subv_title = Snapshot.info_subvolume
    wday_title = Snapshot.info_wday
    date_title = Snapshot.info_date
    time_title = Snapshot.info_time
    ts_title = Snapshot.info_timestamp

    def __init__(self):
        super(SnapshotTable, self).__init__()
        self.selected = {}
        self.filterColumnComboBox.addItem(self.sect_title)
        self.filterColumnComboBox.addItem(self.subv_title)
        self.filterColumnComboBox.addItem(self.wday_title)
        self.filterColumnComboBox.addItem(self.date_title)
        self.filterColumnComboBox.addItem(self.time_title)
        self.filterColumnComboBox.addItem(self.ts_title)

    def createModel(self):
        model = QStandardItemModel(0, 7)
        model.setHeaderData(0, Qt.Horizontal, self.path_title)
        model.setHeaderData(1, Qt.Horizontal, self.sect_title)
        model.setHeaderData(2, Qt.Horizontal, self.subv_title)
        model.setHeaderData(3, Qt.Horizontal, self.wday_title)
        model.setHeaderData(4, Qt.Horizontal, self.date_title)
        model.setHeaderData(5, Qt.Horizontal, self.time_title)
        model.setHeaderData(6, Qt.Horizontal, self.ts_title)

        n = 0
        for i in mainWindow.sectionTable.selected:
            x = Section(settings.config[i])
            for j in x.snapshot_paths:
                snap = x.snapshot_info(j, printout=False)
                model.insertRow(n)
                model.setData(model.index(n, 0), j)
                model.setData(model.index(n, 1), x.name)
                model.setData(model.index(n, 2), x.subvolume)
                model.setData(model.index(n, 3), snap.wday)
                model.setData(model.index(n, 4), snap.date)
                model.setData(model.index(n, 5), snap.time)
                model.setData(model.index(n, 6), snap.ts)
            n =+ 1
        return model

    def itemSelected(self):
        self.selected = {}
        for i in self.proxyView.selectedIndexes():
            snap = self.getTableViewValue(i.row(), 0, self.proxyView)
            sect = self.getTableViewValue(i.row(), 1, self.proxyView)
            self.selected.update({snap: sect})

        mainWindow.updateButtons()
        mainWindow.updateStatusBar()

    def delete(self):
        failed = []
        ok = False
        for snap in self.selected:
            sect = self.selected[snap]
            x = Section(settings.config[sect])
            if x.delete(snap):
                ok = True
            else:
                failed.append(snap)

        if failed:
            text = 'Failed to delete snapshots: \n\n' + '\n'.join(failed) + '\
            \n\nMaybe are not you root?'
            title = 'Operation failed'
            self.mbox.warning(self, title, text, self.mbox.Ok)

        if ok:  # Only update table if some were deleted
            mainWindow.sectionTable.reloadTable()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.sectionTable = SectionTable()
        self.snapshotTable = SnapshotTable()
        self.statusPathFocused = QLabel()
        self.aboutDialog = AboutDialog()
        self.helpView = HtmlHelp()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createDockWindows()
        self.createStatusBar()
        self.readSettings()
        self.show()

    def new(self):
        self.newAct.setEnabled(False)
        self.sectionTable.new_snapshot()
        time.sleep(1)  # Wait a prudent time to prevent fails
        self.newAct.setEnabled(True)

    def deleteSection(self):
        self.deleteSectionsAct.setEnabled(False)
        self.sectionTable.delete()
        time.sleep(1)
        self.deleteSectionsAct.setEnabled(True)

    def deleteSnapshot(self):
        self.deleteSnapshotsAct.setEnabled(False)
        self.snapshotTable.delete()
        time.sleep(1)
        self.deleteSnapshotsAct.setEnabled(True)

    def reloadTable(self):
        self.sectionTable.reloadTable()

    def closeEvent(self, event):
        app.quit()
        clean_exit()

    def showAbout(self):
        self.aboutDialog.show()

    def showHelp(self):
        self.helpView.show()

    def updateButtons(self):
        if len(self.sectionTable.selected) == 0:
            self.deleteSectionsAct.setEnabled(False)
            self.newAct.setEnabled(False)
        else:
            self.deleteSectionsAct.setEnabled(True)
            self.newAct.setEnabled(True)

        if len(self.snapshotTable.selected) == 0:
            self.deleteSnapshotsAct.setEnabled(False)
        else:
            self.deleteSnapshotsAct.setEnabled(True)

    def updateStatusBar(self):
        self.statusPathFocused.setText('Selected: ' +
                                  str(len(self.sectionTable.selected)) +
                                  ' sections, ' +
                                  str(len(self.snapshotTable.selected)) +
                                  ' snapshots')

    def createActions(self):
        self.newAct = QAction(QIcon.fromTheme('list-add'), _("&New"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Create new snapshot"),
                               triggered=self.new)

        self.deleteSectionsAct = QAction(QIcon.fromTheme('document-cleanup'),
                                         _("&Clean sections"),
                                        self, shortcut=QKeySequence.Quit,
                                        statusTip=_("Clean selected sessions"),
                                        triggered=self.deleteSection)

        self.deleteSnapshotsAct = QAction(QIcon.fromTheme('edit-delete'), _("&Delete snapshots"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Delete selected snapshots"),
                               triggered=self.deleteSnapshot)

        self.reloadAct = QAction(QIcon.fromTheme('view-refresh'), _("&Reload"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Reload tables"),
                               triggered=self.reloadTable)

        self.exitAct = QAction(QIcon.fromTheme('window-close'), _("E&xit"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Exit the application"),
                               triggered=self.closeEvent)

        self.viewHorizontalAct = QAction(QIcon.fromTheme('view-split-left-right'),
                                         _('&Horizontal align'),
                                         self, shortcut=QKeySequence.Quit,
                                         statusTip=_('Set horizontal alignment'),
                                         triggered=self.viewHorizontal)

        self.viewVerticalAct = QAction(QIcon.fromTheme('view-split-top-bottom'),
                                         _('&Vertical align'),
                                         self, shortcut='Ctrl + V',
                                         statusTip=_('Set vertical alignment'),
                                         triggered=self.viewVertical)

        self.showAboutAct = QAction(QIcon.fromTheme(EXECUTABLE_NAME),
                                    _("&About") + " " + PROGRAM_NAME, self,
                                    statusTip=_("Information about"
                                                " this application"),
                                    triggered=self.showAbout)

        self.aboutQtAct = QAction(QIcon.fromTheme('qtcreator'),
                                  _("About &Qt"), self,
                                  statusTip=_("Show information about"
                                              " the Qt library"),
                                  triggered=QApplication.instance().aboutQt)

        self.showHelpAct = QAction(QIcon.fromTheme('help-browser'),
                                    _("&Help browser"), self,
                                    statusTip=_("Show help"),
                                    triggered=self.showHelp)

    def createMenus(self):
        self.snapmanMenu = self.menuBar().addMenu(PROGRAM_NAME)
        self.snapmanMenu.addAction(self.newAct)
        self.snapmanMenu.addAction(self.reloadAct)
        self.snapmanMenu.addSeparator()
        self.snapmanMenu.addAction(self.deleteSectionsAct)
        self.snapmanMenu.addAction(self.deleteSnapshotsAct)
        self.snapmanMenu.addSeparator()
        self.snapmanMenu.addAction(self.exitAct)

        self.viewMenu = self.menuBar().addMenu(_("&View"))
        self.viewMenu.addAction(self.viewVerticalAct)
        self.viewMenu.addAction(self.viewHorizontalAct)

        self.helpMenu = self.menuBar().addMenu(_("&Help"))
        self.helpMenu.addAction(self.showHelpAct)
        self.helpMenu.addAction(self.showAboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.toolBar = self.addToolBar(_("Toolbar"))
        self.toolBar.addAction(self.newAct)
        self.toolBar.addAction(self.reloadAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.deleteSectionsAct)
        self.toolBar.addAction(self.deleteSnapshotsAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.viewVerticalAct)
        self.toolBar.addAction(self.viewHorizontalAct)

    def createStatusBar(self):
        self.statusBar().addWidget(self.statusPathFocused, Qt.AlignLeft)

    def createDockWindows(self):
        self.sectionsDock = QDockWidget(_("Sections"), self)
        self.sectionsDock.setWidget(self.sectionTable)

        self.snapshot_pathsDock = QDockWidget(_("Snapshots"), self)
        self.snapshot_pathsDock.setWidget(self.snapshotTable)

        self.viewVertical()


    def viewVertical(self):
        self.addDockWidget(Qt.TopDockWidgetArea, self.sectionsDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.snapshot_pathsDock)
        self.viewVerticalAct.setEnabled(False)
        self.viewHorizontalAct.setEnabled(True)

    def viewHorizontal(self):
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sectionsDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.snapshot_pathsDock)
        self.viewHorizontalAct.setEnabled(False)
        self.viewVerticalAct.setEnabled(True)


    def readSettings(self):
        settings = QSettings(PROGRAM_NAME, _("Settings"))
        size = settings.value("size", QSize(700, 600))
        self.resize(size)
        self.setWindowTitle(PROGRAM_NAME)
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))


def run():
    mainWindow.sectionTable.reloadTable()
    sys.exit(app.exec_())


app = QApplication(sys.argv)
mainWindow = MainWindow()
