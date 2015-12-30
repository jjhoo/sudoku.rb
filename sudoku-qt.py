#!/usr/bin/python

from PySide import QtCore, QtGui, QtUiTools

class SudokuGrid(QtGui.QWidget):
    def __init__(self, *args, **kw):
        super(SudokuGrid, self).__init__(*args, **kw)
        self.cell_sz = 64
        self.box_sz = 3 * self.cell_sz
        self.grid_sz = 9 * self.cell_sz

        self.solved = {}
        self.candidates = {}

        self.solved[(1, 1)] = 9

        self.pixmap = QtGui.QPixmap(600, 600)
        self.pixmap.fill(self, 0, 0)
        painter = QtGui.QPainter(self.pixmap)
        painter.initFrom(self)
        self.paint(painter)
        painter.end()

    def paint_grid(self, painter):
        pen0 = QtGui.QPen()
        pen1 = QtGui.QPen()
        pen2 = QtGui.QPen()

        pen0.setWidth(3)
        pen1.setWidth(2)
        pen2.setWidth(1)

        painter.setPen(pen0)
        painter.drawRect(QtCore.QRect(0, 0, self.grid_sz, self.grid_sz))

        for i in range(0, self.grid_sz + 1, self.cell_sz):
            if i % self.box_sz == 0:
                painter.setPen(pen1)
            else:
                painter.setPen(pen2)

            painter.drawLine(i, 0, i, self.grid_sz)
            painter.drawLine(0, i, self.grid_sz, i)

    def paint_cands(self, painter):
        num_sz = self.cell_sz / 3
        font_sz = num_sz - 5
        painter.setFont(QtGui.QFont("Times", font_sz))

        for row in range(0, 9):
            for col in range(0, 9):
                # skip cell if solved

                x0 = row * self.cell_sz
                y0 = col * self.cell_sz
                x = x0
                y = y0
                for n in range(1, 10):
                    if (row + 1, col + 1) in self.solved:
                        continue
                    # skip a number if removed

                    rect = QtCore.QRectF(x, y, num_sz, num_sz)
                    painter.drawText(rect, QtCore.Qt.AlignCenter, "%d" % n)
                    if n % 3 == 0:
                        x = x0
                        y += num_sz
                    else:
                        x += num_sz

    def paint_solved(self, painter):
        font_size = 40
        painter.setFont(QtGui.QFont("Times", font_size))

        for row in range(0, 9):
            for col in range(0, 9):
                try:
                    num = self.solved[row + 1, col + 1]
                    x0 = row * self.cell_sz
                    y0 = col * self.cell_sz
                    rect = QtCore.QRectF(row * self.cell_sz, col * self.cell_sz,
                                         self.cell_sz, self.cell_sz)

                    painter.drawText(rect, QtCore.Qt.AlignCenter, "%d" % num)
                except KeyError:
                    pass

    def paint(self, painter):
        self.paint_grid(painter)
        self.paint_cands(painter)
        self.paint_solved(painter)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setClipRegion(event.region())
        painter.drawPixmap(0, 0, self.pixmap)
        painter.end()

def load_ui(filename, parent=None):
    loader = QtUiTools.QUiLoader()
    loader.registerCustomWidget(SudokuGrid)
    uifile = QtCore.QFile(filename)
    uifile.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uifile, parent)
    uifile.close()
    return ui

def asdf(selffi):
    def cb(*args):
        print "Here"
    return cb

class SudokuApp(QtGui.QApplication):
    def __init__(self, args):
        super(SudokuApp, self).__init__(args)
        self.ui = load_ui("sudoku.ui")

        self.paint_area = self.ui.findChild(SudokuGrid, "paint_area")
        self.ui.setFixedSize(610, 840)

    def show(self):
        self.ui.show()
        self.ui.raise_()

    @QtCore.Slot(int, int, int, int)
    def paint_event(x, y, w, h):
        pass

if __name__ == "__main__":
    import sys
    # app = QtGui.QApplication(sys.argv)
    # mainw = load_ui("sudoku.ui")
    # mainw.show()
    app = SudokuApp(sys.argv)
    app.show()
    app.exec_()

    # paintarea = mainw.findChild(QtGui.QWidget, "paint_area")
    # paintarea.repaint.connect()
    # print dir(paintarea)
    # sys.exit(app.exec_())
