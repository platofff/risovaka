from sys import exit
from collections import OrderedDict
from json import dumps
from os.path import join, realpath, dirname
from copy import deepcopy

from PIL import Image, ImageDraw, ImageQt
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QScrollArea, QListWidget, QListWidgetItem
from PyQt5.uic import loadUi

image = None

config = OrderedDict()


def getName(listw):
    if not config:
        key = '1B'
    else:
        key = list(config.keys())[-1]
        if key[-1:] == 'A':
            key = key[:-1] + 'B'
        elif key[-1:] == 'B':
            key = key[:-1] + 'C'
        elif key[-1:] == 'C':
            key = str(int(key[:-1]) + 1) + 'A'
        else:
            key += '_'

    if listw.findItems(key, Qt.MatchExactly):
        key += '_'
    config.update(OrderedDict({key: []}))
    return key


class App(QMainWindow):

    def __init__(self):
        global image
        super(App, self).__init__()
        self.imgpath = self.ChooseFile()

        if self.imgpath is None:
            exit()
        loadUi(join(dirname(realpath(__file__)), 'gui', 'config_generator.ui'), self)

        image = Image.open(self.imgpath)

        imgobj = QPixmap.fromImage(ImageQt.ImageQt(image))

        self.list = self.findChild(QListWidget, 'list')
        self.list.setCurrentRow(0)

        self.scroll = self.findChild(QScrollArea, 'scrollArea_2')
        self.pic = Pic(imgobj, self.list)
        self.scroll.setWidget(self.pic)
        self.show()

    def ChooseFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Выбери карту", "",
                                                  "PNG файлы (*.png)", options=options)
        if fileName:
            return fileName

    def SaveFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "JSON file (*.json)", options=options)
        saveConfig = deepcopy(config)
        if fileName:
            for ter in saveConfig:
                if self.list.findItems(ter, Qt.MatchExactly)[0].checkState() == Qt.Checked:
                    saveConfig[ter] += [True]
            saveConfig['png'] = self.imgpath
            if fileName[-5:] != '.json':
                fileName += '.json'
            with open(fileName, 'w+') as f:
                f.write(dumps(saveConfig))

    @pyqtSlot()
    def on_plus_clicked(self):
        item = QListWidgetItem()
        name = getName(self.list)
        item.setText(name)
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setWhatsThis(name)
        self.list.addItem(item)
        self.list.setCurrentItem(item)

    @pyqtSlot()
    def on_minus_clicked(self):
        cur = self.list.currentItem()
        self.list.takeItem(self.list.currentRow())
        self.list.setCurrentRow(0)

        if config[cur.text()]:
            for (x, y) in config[cur.text()]:
                ImageDraw.floodfill(image, (x, y), (255, 255, 255, 255))
                self.pic.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(image)))

            config.pop(cur.text())

    @pyqtSlot()
    def on_save_clicked(self):
        self.SaveFile()

    @pyqtSlot(str)
    def on_list_currentTextChanged(self, current):
        for ter in config:
            if ter == current:
                for (x, y) in config[ter]:
                    ImageDraw.floodfill(image, (x, y), (50, 205, 50, 255))
                    self.pic.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(image)))
            else:
                print(config)
                for (x, y) in config[ter]:
                    if image.getpixel((x, y)) != (0, 0, 255, 255):
                        ImageDraw.floodfill(image, (x, y), (0, 0, 255, 255))
                        self.pic.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(image)))

    @pyqtSlot(QListWidgetItem)
    def on_list_itemChanged(self, item):
        global config
        oldName = item.whatsThis()
        newName = item.text()
        if newName not in config:
            config = OrderedDict([(newName, v) if k == oldName else (k, v) for k, v in config.items()])
            item.setWhatsThis(newName)
        else:
            item.setText(oldName)


class Pic(QLabel):
    def __init__(self, imgobj, listwid):
        super(Pic, self).__init__()
        self.setPixmap(imgobj)
        self.list = listwid
        self.setMouseTracking(True)

    def mouseDoubleClickEvent(self, e):
        x = e.x()
        y = e.y()

        if image.getpixel((x, y)) == (255, 255, 255, 255):
            ImageDraw.floodfill(image, (x, y), (50, 205, 50, 255))
            self.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(image)))
            curTer = self.list.currentItem().text()
            if curTer not in config:
                config.update(OrderedDict({curTer: [(x, y)]}))
            else:
                config[curTer] += [(x, y)]
            item = self.list.currentItem()
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
