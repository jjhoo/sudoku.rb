#!/usr/bin/python
# coding: latin1
#
# Copyright (c) 2015-2016 Jani J. Hakala <jjhakala@gmail.com> Jyväskylä, Finland
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, version 3 of the
#  License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from PySide import QtCore, QtGui, QtUiTools

import os
import perttirpc
import time

class SudokuGrid(QtGui.QWidget):
    def __init__(self, *args, **kw):
        super(SudokuGrid, self).__init__(*args, **kw)
        self.cell_sz = 64
        self.box_sz = 3 * self.cell_sz
        self.grid_sz = 9 * self.cell_sz

        self.num_sz = self.cell_sz / 3
        self.num_font_sz = self.num_sz - 5

        self.reset()

    def reset(self):
        self.solved = {}
        self.candidates = {}

        self.pixmap = QtGui.QPixmap(600, 600)
        self.pixmap.fill(self, 0, 0)
        painter = QtGui.QPainter(self.pixmap)
        painter.initFrom(self)
        self.paint(painter)
        painter.end()
        self.update()

    def get_pixmap_painter(self):
        painter = QtGui.QPainter(self.pixmap)
        painter.initFrom(self)
        return painter

    def paint_grid(self, painter):
        pen0 = QtGui.QPen()
        pen1 = QtGui.QPen()
        pen2 = QtGui.QPen()

        pen0.setWidth(3)
        pen1.setWidth(2)
        pen2.setWidth(1)

        painter.setPen(pen0)
        painter.fillRect(QtCore.QRect(0, 0, self.grid_sz, self.grid_sz),
                         QtCore.Qt.lightGray)
        painter.drawRect(QtCore.QRect(0, 0, self.grid_sz, self.grid_sz))

        for i in range(0, self.grid_sz + 1, self.cell_sz):
            if i % self.box_sz == 0:
                painter.setPen(pen1)
            else:
                painter.setPen(pen2)

            painter.drawLine(i, 0, i, self.grid_sz)
            painter.drawLine(0, i, self.grid_sz, i)

    def paint_cands(self, painter):
        painter.setFont(QtGui.QFont("Times", self.num_font_sz))

        for row in range(1, 10):
            for col in range(1, 10):
                for n in range(1, 10):
                    if (row, col) in self.solved:
                        continue
                    self.paint_cell_candidate(row, col, n, painter)

    def candidate_rect(self, row, column, number):
        num_sz = self.cell_sz / 3
        x = (row - 1) * self.cell_sz
        y = (column - 1) * self.cell_sz

        offset = [2, 0, 1]		# 3, 1, 2
        x += offset[number % 3] * num_sz
        y += (number - 1) / 3 * num_sz

        rect = QtCore.QRectF(x, y, num_sz, num_sz)
        return rect

    def paint_cell_candidate(self, row, column, number, painter):
        # row		1..9
        # column 	1..9

        rect = self.candidate_rect(row, column, number)
        painter.drawText(rect, QtCore.Qt.AlignCenter, "%d" % number)

    def paint_cell_candidates(self, candidates, painter=None):
        if painter is None:
            painter = self.get_pixmap_painter()

        painter.setFont(QtGui.QFont("Times", self.num_font_sz))

        for (row, col), n in candidates:
            self.paint_cell_candidate(row, col, n, painter)

    def cell_rect(self, row, column):
        # row		1..9
        # column 	1..9
        x = (row - 1) * self.cell_sz
        y = (column - 1) * self.cell_sz

        rect = QtCore.QRectF(x, y, self.cell_sz, self.cell_sz)
        return rect

    def update_solved(self, cells, color=None):
        painter = self.get_pixmap_painter()

        for (row, col), num in cells:
            self.solved[row, col] = num
        self.paint_solved(cells, painter, color)

    def paint_solved(self, cells, painter=None, color=QtCore.Qt.black):
        if painter is None:
            painter = self.get_pixmap_painter()

        font_size = 40
        painter.setFont(QtGui.QFont("Times", font_size))
        pen = QtGui.QPen()
        pen.setColor(color)
        painter.setPen(pen)
        for (row, col), num in cells:
            rect = self.cell_rect(row, col)
            self.blank_rect(rect, 2, painter)
            painter.drawText(rect, QtCore.Qt.AlignCenter, "%d" % num)

        self.update()

    def paint(self, painter):
        self.paint_grid(painter)
        # self.paint_cands(painter)
        self.paint_solved(((k, v) for k, v in self.solved.iteritems()), painter)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setClipRegion(event.region())
        painter.drawPixmap(0, 0, self.pixmap)
        painter.end()

    def blank_rect(self, rect, width, painter, color=QtCore.Qt.lightGray):
        rect = QtCore.QRect(rect.x() + width, rect.y() + width,
                            rect.width() - 2 * width, rect.width() - 2 * width)
        painter.fillRect(rect, color)

    def border_rect(self, rect, width, painter, color=QtCore.Qt.lightGray):
        pen = QtGui.QPen()
        pen.setWidth(width)
        pen.setColor(color)
        painter.setPen(pen)

        rect = QtCore.QRect(rect.x() + width, rect.y() + width,
                            rect.width() - 2 * width, rect.width() - 2 * width)
        painter.drawRect(rect)

    def blank_cell(self, row, column, painter):
        # row		1..9
        # column 	1..9
        self.blank_rect(self.cell_rect(row, column), 2, painter)

    def blank_candidate(self, row, column, number, painter):
        rect = self.candidate_rect(row, column, number)

        dx = [-1, 1, 0]		# 3, 1, 2
        dy = [1, 0, -1]
        rect.translate(dx[number % 3], dy[(number - 1)/ 3])
        self.border_rect(rect, 1, painter, QtCore.Qt.red)

    def eliminate(self, eliminated):
        painter = self.get_pixmap_painter()
        for (row, col), num in eliminated:
            self.blank_candidate(row, col, num, painter)
        self.update()

    def mark_cell(self, row, column, painter):
        pass

    def mark_candidate(self, row, column, number, painter):
        pass

    def unmark_cell(self, row, column):
        pass

    def unmark_candidate(self, row, column, number, painter):
        pass

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

        self.grid = self.ui.findChild(SudokuGrid, "paint_area")
        self.ui.setFixedSize(610, 840)
        self.solved = False

        self.step_button = self.ui.findChild(QtGui.QPushButton, "step_button")
        self.step_button.clicked.connect(self.on_step)

        button = self.ui.findChild(QtGui.QPushButton, "reset_button")
        button.clicked.connect(self.on_reset)

        self.connect_rpc()
        # self.rpc = bertrpc.Service('localhost', 7777)
        # self.rpc.request('call').sudoku.init('610320000300400000058600000009503620000040000023801500000006750000004003000058014')

    def connect_rpc(self):
        user = os.getenv('USER')
        self.rpc_sock = perttirpc.connect_unix('/tmp/sudokusocket-' + user + os.sep + 'sudoku.sock')
        self.rpc = perttirpc.Connection(self.rpc_sock)

        self.init_grid()
        # reply = self.rpc.call('sudoku', 'solve', [])
        # reply = self.rpc.call('sudoku', 'solve_singles')
        # print reply
        # sys.exit(1)

    def init_grid(self, grid='610320000300400000058600000009503620000040000023801500000006750000004003000058014'):
        reply = self.rpc.call('sudoku', 'init', grid)
        if not perttirpc.is_ok_reply(reply):
            # Display error
            pass

        reply = self.rpc.call('sudoku', 'get_solved')
        # print reply
        self.grid.update_solved(reply)

        reply = self.rpc.call('sudoku', 'get_candidates')
        # print reply
        self.grid.paint_cell_candidates(reply)

    def on_reset(self):
        self.grid.reset()
        self.init_grid()
        self.step_button.setEnabled(True)

    def on_step(self):
        reply = self.rpc.call('sudoku', 'step')
        status, ngrid, solved, eliminated = reply
        self.grid.eliminate(eliminated)
        self.grid.update_solved(solved, QtCore.Qt.blue)
        # print reply

        if status == 'solved':
            self.step_button.setDisabled(True)

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
