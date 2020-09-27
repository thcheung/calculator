import sys
import os

import sys
from math import sqrt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QApplication,
                               QLineEdit, QLayout, QLabel,QToolButton,QSizePolicy)
from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5.QtGui import QIcon

class Button(QToolButton):
    def __init__(self, text):
        super(Button, self).__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setText(text)

    def sizeHint(self):
        size = QToolButton.sizeHint(self)
        width = size.height() + 20
        height = max(size.width(), size.height())
        hint = QSize(width, height)
        # print(hint)
        return hint

class Calculator(QWidget):
    def __init__(self, icon):
        super(Calculator, self).__init__()
        self.sum_in_memory = 0
        self.sum_so_far = 0.0
        self.factor_so_far = 0.0
        self.pending_additive_operator = ''  # last + or - operator
        self.pending_multiplicative_operator = ''  # last x or / operator
        self.waiting_for_operand = True

        self.num_buttons = []

        self.label = QLabel('', self)
        self.label.setAlignment(Qt.AlignRight)
        font = self.label.font()
        font.setPointSize(font.pointSize() + 4)
        self.label.setFont(font)

        # create the display
        self.display = QLineEdit('0', self)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMaxLength(15)
        font = self.display.font()
        font.setPointSize(font.pointSize() + 8)
        self.display.setFont(font)

        # create all the buttons
        for i in range(10):
            button = self.create_button(str(i), self.digit_clicked)
            self.num_buttons.append(button)
            button.setShortcut(str(i))
        self.point_button = self.create_button('.',
                                               self.point_clicked)
        self.point_button.setShortcut('.')
        self.sign_button = self.create_button('\u00b1',
                                              self.change_sign_clicked)
        self.plus_button = self.create_button('+',
                                              self.additive_clicked)
        self.plus_button.setShortcut('+')
        self.minus_button = self.create_button('-',
                                               self.additive_clicked)
        self.minus_button.setShortcut('-')
        self.multiply_button = self.create_button('x',
                                                  self.multiplicative_clicked)
        self.multiply_button.setShortcut('x')
        self.divide_button = self.create_button('/',
                                                self.multiplicative_clicked)
        self.divide_button.setShortcut('/')
        self.root_button = self.create_button('\u221a',
                                              self.unary_operator_clicked)
        self.square_button = self.create_button('x\u00b2',
                                                self.unary_operator_clicked)
        self.reciproce_button = self.create_button('1/x',
                                                   self.unary_operator_clicked)
        self.equal_button = self.create_button('=',
                                               self.equal_clicked)
        self.equal_button.setShortcut('Return')
        self.back_button = self.create_button('\u2190',
                                              self.backspace_clicked)
        self.back_button.setShortcut('Backspace')
        self.clear_button = self.create_button('Clear',
                                               self.clear)
        self.clear_all_button = self.create_button('Clear All',
                                                   self.clear_all)
        self.memory_clear = self.create_button('MC',
                                               self.clear_memory)
        self.memory_add = self.create_button('M+',
                                             self.add_to_memory)
        self.memory_read = self.create_button('MR',
                                              self.read_memory)
        self.memory_save = self.create_button('MS',
                                              self.set_memory)
        # create a grid layout
        self.layout = QGridLayout()
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.layout)

        # put the buttons into the setLayout
        self.layout.addWidget(self.label, 0, 0, 1, 6)
        self.layout.addWidget(self.display, 1, 0, 1, 6)
        self.layout.addWidget(self.back_button, 2, 0, 1, 2)
        self.layout.addWidget(self.clear_button, 2, 2, 1, 2)
        self.layout.addWidget(self.clear_all_button, 2, 4, 1, 2)

        for i in range(len(self.num_buttons)):
            if i > 0:
                row = int(((9-i)) / 3) + 3
                col = ((i - 1) % 3) + 1
                self.layout.addWidget(self.num_buttons[i], row, col)
            else:
                self.layout.addWidget(self.num_buttons[0], 6, 2)

        self.layout.addWidget(self.memory_clear, 3, 0)
        self.layout.addWidget(self.memory_save, 4, 0)
        self.layout.addWidget(self.memory_read, 5, 0)
        self.layout.addWidget(self.memory_add, 6, 0)
        self.layout.addWidget(self.divide_button, 3, 4)
        self.layout.addWidget(self.multiply_button, 4, 4)
        self.layout.addWidget(self.minus_button, 5, 4)
        self.layout.addWidget(self.plus_button, 6, 4)
        self.layout.addWidget(self.root_button, 3, 5)
        self.layout.addWidget(self.square_button, 4, 5)
        self.layout.addWidget(self.reciproce_button, 5, 5)
        self.layout.addWidget(self.equal_button, 6, 5)
        self.layout.addWidget(self.sign_button, 6, 1)
        self.layout.addWidget(self.point_button, 6, 3)

        self.setWindowTitle('Calculator')
        window_icon = QIcon(icon)
        self.setWindowIcon(window_icon)
        print(icon)

    @pyqtSlot()
    def digit_clicked(self):
        number = int(self.sender().text())
        # print(self.sender(), self.sender.text())
        if number == 0 and self.display.text() == 0:
            return
        if self.waiting_for_operand:
            self.display.clear()
            self.waiting_for_operand = False
        self.display.setText(self.display.text() + str(number))

    @pyqtSlot()
    def additive_clicked(self):
        text = self.display.text()
        if text[-1].isdigit():
            clicked_operator = self.sender().text()
            self.update_label(text, clicked_operator)
            operand = float(text)
            if self.pending_multiplicative_operator != '':
                if not self.calculate(operand,
                                      self.pending_multiplicative_operator):
                    self.abort_operation('zero_div')
                    return
                self.display.setText(str(self.factor_so_far))
                operand = self.factor_so_far
                self.factor_so_far = 0.0
                self.pending_multiplicative_operator = ''
            if self.pending_additive_operator != '':
                if not self.calculate(operand,
                                      self.pending_additive_operator):
                    self.abort_operation('zero_div')
                    return
                self.display.setText(str(self.sum_so_far))
            else:
                self.sum_so_far = operand
            self.pending_additive_operator = clicked_operator
            self.waiting_for_operand = True
        else:
            self.clear_all()
            self.update_label()

    @pyqtSlot()
    def unary_operator_clicked(self):
        text = self.display.text()
        if text[-1].isdigit():
            button = self.sender()
            operator = button.text()
            operand = float(text)
            result = 0.0
            if operator == '\u221a':
                if operand < 0:
                    self.abort_operation('sqrt')
                else:
                    result = sqrt(operand)
                    self.display.setText(str(result))
                    self.update_label(operator, text, '=', str(result))
            if operator == '1/x':
                if operand == 0:
                    self.abort_operation('zero_div')
                else:
                    result = float(1 / operand)
                    self.display.setText(str(result))
                    self.update_label(f'1/{text}', '=', str(result))
            if operator == 'x\u00b2':
                result = operand**2
                self.display.setText(str(result))
                self.update_label(text, '\u00b2', '=', str(result))
            self.waiting_for_operand = True
        else:
            self.clear_all()
            self.update_label()

    @pyqtSlot()
    def multiplicative_clicked(self):
        text = self.display.text()
        if text[-1].isdigit():
            clicked_operator = self.sender().text()
            operand = float(text)
            self.update_label(text, clicked_operator)
            if self.pending_multiplicative_operator != '':
                if not self.calculate(operand,
                                      self.pending_multiplicative_operator):
                    self.abort_operation('zero_div')
                    return
                self.display.setText(str(self.factor_so_far))
            else:
                self.factor_so_far = operand
            self.pending_multiplicative_operator = clicked_operator
            self.waiting_for_operand = True
        else:
            self.clear_all()
            self.update_label()

    @pyqtSlot()
    def equal_clicked(self):
        text = self.display.text()
        if text[-1].isdigit():
            operand = float(text)
            self.update_label(text)
            if self.pending_multiplicative_operator != '':
                if not self.calculate(operand,
                                      self.pending_multiplicative_operator):
                    self.abort_operation('zero_div')
                    return
                operand = self.factor_so_far
                self.factor_so_far = 0.0
                self.pending_multiplicative_operator = ''
            if self.pending_additive_operator != '':
                if not self.calculate(operand,
                                      self.pending_additive_operator):
                    self.abort_operation('zero_div')
                    return
                self.pending_additive_operator = ''
            else:
                self.sum_so_far = operand
            self.display.setText(str(self.sum_so_far))
            self.update_label('=', self.sum_so_far)
            self.sum_so_far = 0.0
            self.waiting_for_operand = True
        else:
            self.clear_all()

    @pyqtSlot()
    def point_clicked(self):
        if self.waiting_for_operand:
            self.display.setText('0')
        if '.' not in self.display.text():
            self.display.setText(self.display.text() + '.')
            self.waiting_for_operand = False

    @pyqtSlot()
    def change_sign_clicked(self):
        operand = self.display.text()
        if '-' not in operand:
            self.display.setText('-' + operand)
        else:
            self.display.setText(operand[1:])

    @pyqtSlot()
    def backspace_clicked(self):
        if self.waiting_for_operand:
            return
        text = self.display.text()[:len(self.display.text()) - 1]
        if text == '':
            self.display.setText('0')
            self.waiting_for_operand = True
        else:
            self.display.setText(text)

    @pyqtSlot()
    def clear(self):
        if self.waiting_for_operand:
            return
        self.display.setText('0')
        self.waiting_for_operand = True

    @pyqtSlot()
    def clear_all(self):
        self.display.setText('0')
        self.waiting_for_operand = True
        self.sum_so_far = 0
        self.factor_so_far = 0
        self.pending_additive_operator = ''
        self.pending_multiplicative_operator = ''
        self.update_label()

    @pyqtSlot()
    def clear_memory(self):
        self.sum_in_memory = 0

    @pyqtSlot()
    def read_memory(self):
        self.waiting_for_operand = True
        self.display.setText(str(self.sum_in_memory))

    @pyqtSlot()
    def set_memory(self):
        self.equal_clicked()
        self.sum_in_memory = float(self.display.text())

    @pyqtSlot()
    def add_to_memory(self):
        self.equal_clicked()
        self.sum_in_memory += float(self.display.text())

    def create_button(self, text, slot):
        self.new_button = Button(text)
        self.new_button.clicked.connect(slot)
        return self.new_button

    def abort_operation(self, err=None):
        self.clear_all()
        if err is None:
            self.display.setText('Error!')
        if err == 'sqrt':
            self.display.setText('Undefined!')
        if err == 'zero_div':
            self.display.setText('Zero division')

    # calculates a binary operation returns True if possible else False
    def calculate(self, right_operand, pending_operator):
        if pending_operator == '+':
            self.sum_so_far += right_operand
        if pending_operator == '-':
            self.sum_so_far -= right_operand
        if pending_operator == 'x':
            self.factor_so_far *= right_operand
        if pending_operator == '/':
            if right_operand == 0:
                return False
            self.factor_so_far /= right_operand
        return True

    def update_label(self, *args):
        if '=' in self.label.text():
            self.label.setText('')
        if args:
            for i in args:
                self.label.setText(self.label.text() + str(i))
        else:
            self.label.setText('')

    def round_float(self, f):
        if len(str(f)) > 10:
            res = round(f, 8)
            return res
        return f

def resource_path(relative_path):
    """ Get absolute path to resource,
    works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Logo = resource_path("calc_icon.png")
    w = Calculator(Logo)
    w.show()
    sys.exit(app.exec_())