import sys
from time import sleep
from PyQt5.QtCore import QThread
from serial import Serial, SerialException
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPlainTextEdit, QPushButton


class InputThread(QThread):
    def __init__(self, current_com_port, input_label):
        QThread.__init__(self)
        self.flag = True
        self.current_com_port = current_com_port
        self.input_label = input_label

    def run(self) -> None:
        self.auto_read()

    def auto_read(self) -> None:
        while self.flag:
            try:
                input_data = self.current_com_port.readline().decode('UTF-8')
                if len(input_data) > 0:
                    self.input_label.insertPlainText(f'{input_data}\n')
                sleep(1)
            except (OSError, SerialException):
                pass

    def stop(self):
        self.flag = False
        self.current_com_port.close()


class COMPortTransmission(QMainWindow):
    def __init__(self):
        super(COMPortTransmission, self).__init__()
        self.input_thread = None
        self.current_com_port = None
        self.bytes_per_second_speed = [
            '110', '150', '300', '600', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']

        self.setWindowTitle('COM port')
        self.setFixedSize(325, 450)

        self.com_port_label = QLabel(self)
        self.com_port_label.move(10, 10)
        self.com_port_label.setText('COM-порт:')
        self.com_port_label.adjustSize()

        self.com_port_choice = QComboBox(self)
        self.com_port_choice.setGeometry(130, 5, 80, 30)
        self.com_port_choice.setEnabled(False)

        self.output_label_title = QLabel(self)
        self.output_label_title.move(10, 140)
        self.output_label_title.setText('Введите передаваемую информацию:')
        self.output_label_title.adjustSize()

        self.output_label = QLineEdit(self)
        self.output_label.setGeometry(10, 170, 305, 30)
        self.output_label.setReadOnly(True)

        self.input_label_title = QLabel(self)
        self.input_label_title.move(100, 255)
        self.input_label_title.setText('Полученные данные:')
        self.input_label_title.adjustSize()

        self.input_label = QPlainTextEdit(self)
        self.input_label.setGeometry(10, 280, 305, 160)
        self.input_label.setReadOnly(True)

        self.get_com_ports_button = QPushButton(self)
        self.get_com_ports_button.setText('Получить\nдоступные\nCOM-порты')
        self.get_com_ports_button.setGeometry(225, 5, 90, 70)
        self.get_com_ports_button.clicked.connect(self.get_com_ports)

        self.speed_title_label = QLabel(self)
        self.speed_title_label.setText('Скорость, бит/сек:')
        self.speed_title_label.move(10, 50)
        self.speed_title_label.adjustSize()

        self.speed_choice = QComboBox(self)
        self.speed_choice.setGeometry(130, 45, 80, 30)
        self.speed_choice.setEnabled(False)

        self.com_port_connection_button = QPushButton(self)
        self.com_port_connection_button.setText('Образовать соединение')
        self.com_port_connection_button.setGeometry(10, 90, 155, 30)
        self.com_port_connection_button.setEnabled(False)
        self.com_port_connection_button.clicked.connect(self.com_port_connection)

        self.com_port_close_connection_button = QPushButton(self)
        self.com_port_close_connection_button.setText('Прервать соединение')
        self.com_port_close_connection_button.setGeometry(175, 90, 140, 30)
        self.com_port_close_connection_button.setEnabled(False)
        self.com_port_close_connection_button.clicked.connect(self.com_port_close_connection)

        self.clear_button = QPushButton(self)
        self.clear_button.setText('Очистить поле ввода')
        self.clear_button.setGeometry(10, 210, 150, 30)
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_input)

        self.send_button = QPushButton(self)
        self.send_button.setText('Отправить')
        self.send_button.setGeometry(170, 210, 145, 30)
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_data)

    def get_com_ports(self) -> None:
        self.speed_choice.clear()
        self.com_port_choice.clear()
        com_ports = ['COM%s' % i for i in range(1, 257)]
        connection_flag = False
        for com_port_number in com_ports:
            try:
                com_port = Serial(com_port_number)
                com_port.close()
                connection_flag = True
                self.com_port_choice.addItem(com_port_number)
            except (OSError, SerialException):
                pass
        if connection_flag:
            for speed in self.bytes_per_second_speed:
                self.speed_choice.addItem(speed)

            self.speed_choice.setEnabled(True)
            self.com_port_choice.setEnabled(True)
            self.com_port_connection_button.setEnabled(True)

    def com_port_connection(self) -> None:
        try:
            self.current_com_port = Serial(
                port=self.com_port_choice.currentText(),
                baudrate=int(self.speed_choice.currentText()),
                bytesize=8,
                stopbits=1,
                timeout=0)
            self.input_thread = InputThread(self.current_com_port, self.input_label)
            self.input_thread.start()

            self.send_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.com_port_close_connection_button.setEnabled(True)

            self.speed_choice.setEnabled(False)
            self.output_label.setReadOnly(False)
            self.com_port_choice.setEnabled(False)
            self.get_com_ports_button.setEnabled(False)
            self.com_port_connection_button.setEnabled(False)
        except (OSError, SerialException):
            pass

    def com_port_close_connection(self) -> None:
        self.clear_input()
        self.input_thread.stop()
        self.input_thread = None
        self.current_com_port = None

        self.speed_choice.setEnabled(True)
        self.output_label.setReadOnly(True)
        self.com_port_choice.setEnabled(True)
        self.get_com_ports_button.setEnabled(True)
        self.com_port_connection_button.setEnabled(True)

        self.send_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.com_port_close_connection_button.setEnabled(False)

    def clear_input(self) -> None:
        self.output_label.clear()

    def send_data(self) -> None:
        output_data = self.output_label.text().encode()
        self.current_com_port.write(output_data)
        self.clear_input()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = COMPortTransmission()
    main_window.show()
    sys.exit(app.exec_())

# pyinstaller -w -F --onefile --upx-dir=D:\UPX main.py
