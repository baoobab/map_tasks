import sys
import requests

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

toponym_longitude = 37.623069
toponym_lattitude = 55.752591
delta = 0.006
pt = ''
z = 8
lays = ['map', 'sat', 'sat,skl']
counter = 0
geocoder_api_server = "http://static-maps.yandex.ru/1.x/"


class Window2(QWidget):
    def __init__(self):
        super(Window2, self).__init__()
        self.setGeometry(700, 300, 400, 200)
        self.setWindowTitle('Спарвка')
        self.label = QLabel(self)
        self.label.move(15, 15)
        self.label.setText('Увеличить масштаб - PgUp\n'
                           'Уменьшить масштаб - PgDn\n'
                           'Передвижение - стрелки\n'
                           'Смена слоёв - Ctrl')


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 300, 600, 500)
        self.setWindowTitle("Yandex Maps 0.08")
        self.image = QLabel(self)
        self.image.move(0, 60)
        self.image.resize(600, 400)
        self.pixmap = QPixmap('map №1.png')
        self.image.setPixmap(self.pixmap)
        self.pixmap.loadFromData(main())

        self.label = QLabel(self)
        self.label.move(50, 15)
        self.label.setText('Поиск')
        self.line_edit = QLineEdit(self)
        self.line_edit.move(120, 15)
        self.line_edit.resize(170, 40)
        self.grabKeyboard()
        self.button = QPushButton(self)
        self.button.setText('Искать')
        self.button.move(320, 15)
        self.button.resize(70, 40)
        self.button.clicked.connect(self.search)
        self.button2 = QPushButton(self)
        self.button2.setText('Сбросить поиск')
        self.button2.move(420, 15)
        self.button2.resize(140, 40)
        self.button2.clicked.connect(self.reset)
        self.button3 = QPushButton(self)
        self.button3.setText('?')
        self.button3.move(560, 15)
        self.button3.resize(40, 40)
        self.button3.clicked.connect(self.show_window_2)

        self.adress = QLabel(self)
        self.adress.setText('')
        self.adress.move(5, 461)
        self.adress.resize(600, 39)
        self.reset()

    def show_window_2(self):
        self.w2 = Window2()
        self.w2.show()

    def reset(self):
        global pt, toponym_longitude, toponym_lattitude
        self.line_edit.setText("")
        self.adress.clear()
        pt = ''
        toponym_longitude = 37.623069
        toponym_lattitude = 55.752591
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(main())
        self.image.setPixmap(self.pixmap)

    def search(self):
        global pt, toponym_longitude, toponym_lattitude
        text = self.line_edit.text()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": text,
            "format": "json"}
        try:
            response = requests.get(geocoder_api_server, params=geocoder_params)
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            self.adress.setText(toponym_address)
        except Exception:
            print('Некорректный запрос')
        toponym_longitude, toponym_lattitude = float(toponym_longitude), float(toponym_lattitude)
        pt = f'{toponym_longitude},{toponym_lattitude},comma'

        self.pixmap = QPixmap()
        self.pixmap.loadFromData(main())
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        global delta, toponym_lattitude, toponym_longitude, z, counter
        if event.key() == Qt.Key_Right:
            toponym_longitude += delta * 2.9
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(main())
            self.image.setPixmap(self.pixmap)
            self.update()
        elif event.key() == Qt.Key_Left:
            toponym_longitude -= delta * 2.9
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(main())
            self.image.setPixmap(self.pixmap)
            self.update()
        elif event.key() == Qt.Key_Up:
            toponym_lattitude += delta * 1.2
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(main())
            self.image.setPixmap(self.pixmap)
            self.update()
        elif event.key() == Qt.Key_Down:
            toponym_lattitude -= delta * 1.2
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(main())
            self.image.setPixmap(self.pixmap)
            self.update()
        else:
            self.line_edit.keyPressEvent(event)

        if event.nativeVirtualKey() == 17:
            if counter + 1 > len(lays) - 1:
                counter = 0
            else:
                counter += 1

        if event.nativeVirtualKey() == 33:
            if z < 20:
                z += 1

        if event.nativeVirtualKey() == 34:
            if z > 2:
                z -= 1
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(main())
        self.image.setPixmap(self.pixmap)
        self.update()


def main():
    global toponym_longitude, toponym_lattitude, delta, lays, counter, z

    params = {
        "ll": ",".join([str(toponym_longitude), str(toponym_lattitude)]),
        # "spn": ",".join([str(delta), str(delta)]), # если строку расокмментарить, то приближение почему-то перестает работать
        'z': z,
        "l": lays[counter],
        "pt": pt
    }
    response = requests.get(geocoder_api_server, params=params)

    if not response:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
    return response.content


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())
