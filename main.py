from sys import exit
from json import loads
from os import name as OSName
from os.path import join, realpath, dirname
from threading import Thread

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import pyqtSlot, Qt
from PIL import Image, ImageDraw, ImageQt, ImageFont

countries = {}
collisionFindResult = False


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        uic.loadUi(join(dirname(realpath(__file__)), 'gui', 'main.ui'), self)

        self.warn = QtWidgets.QMessageBox()

        self.colorNew = None
        self.begTer = self.findChild(QtWidgets.QLineEdit, 'begTer')
        self.countryName = self.findChild(QtWidgets.QLineEdit, 'countryName')
        self.colorView = self.findChild(QtWidgets.QGraphicsView, 'colorView')
        self.createButton = self.findChild(QtWidgets.QPushButton, 'create')
        self.countriesTree = self.findChild(QtWidgets.QTreeWidget, 'countriesTree')
        self.pic = self.findChild(QtWidgets.QLabel, 'pic')
        self.changeStateEntry = self.findChild(QtWidgets.QLineEdit, 'changeStateEntry')
        self.newApply = self.findChild(QtWidgets.QPushButton, 'newApply')
        self.makeEmpty = self.findChild(QtWidgets.QCheckBox, 'makeEmpty')

        json = ''
        try:
            with open(self.ChooseFile()) as f:
                for s in f.readlines():
                    json += s
        except TypeError:
            exit()
        self.config = loads(json)
        self.imageClean = Image.open(self.config['png'])
        self.config.pop('png')

        self.pic.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(self.drawCountriesLabels(self.imageClean))))

        self.show()

    def fillTer(self, ter, rgb):
        for coord in self.config[ter]:
            if type(coord) is list:
                x, y = coord[0], coord[1]
                ImageDraw.floodfill(self.imageClean, (x, y), rgb)
        self.pic.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(self.drawCountriesLabels(self.imageClean))))

    def ChooseFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выбери карту", "",
                                                            "JSON файлы (*.json)", options=options)
        if fileName:
            return fileName

    def drawCountriesLabels(self, imageClean):
        image = imageClean.copy()
        polygons = [[(40, 40), (40, 80), (80, 80), (80, 40)]]
        draw = ImageDraw.Draw(image)
        if OSName == 'posix':
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 24)
            except OSError:
                exit()
        else:
            font = ImageFont.truetype('arialbd.ttf', 24)

        def color(i):
            if len(countries) >= 1 + i:
                return countries[sorted(countries)[i]]['c']
            else:
                return 255, 255, 255, 255

        def text(i):
            if len(countries) >= 1 + i:
                country = sorted(countries)[i]
                res = country
                item = self.countriesTree.findItems(country, Qt.MatchExactly, column=0)[0]
                try:
                    for x in range(int(item.text(2))):
                        res += ' [ЯО]'
                    for x in range(int(item.text(3))):
                        res += ' [АнтиЯО]'
                except ValueError:
                    self.warn.setText('Неправильное заначение ЯО/Анти ЯО у ' + country)
                    self.warn.show()

                return res
            else:
                return ''

        draw.polygon(polygons[0], fill=color(0), outline=(0, 0, 0, 255))
        textPos = (polygons[0][2][0] + 10, polygons[0][0][1])
        draw.text(textPos, text(0), color(0), font=font, encoding='unic')
        for i in range(1, 10):
            polygons += [[]]
            for (x, y) in polygons[0]:
                y += 80 * i
                polygons[i].append((x, y))
            draw.polygon(polygons[i], fill=color(i), outline=(0, 0, 0, 255))
            textPos = (polygons[i][2][0] + 10, polygons[i][0][1])
            draw.text(textPos, text(i), color(i), font=font, encoding='unic')

        return image

    def checkCountryName(self):
        if self.countryName.text() != '' and self.countryName.text() not in countries:
            return True
        else:
            return False

    def checkBegTer(self):
        begTer = self.begTer.text()
        if begTer in self.config and begTer not in [ter for sub in [countries[x]['t'] for x in countries] for ter \
                                                    in sub] and self.begTer.text() in self.config:
            return True
        else:
            return False

    def newValidation(self):
        if self.checkCountryName() and self.colorNew and self.checkBegTer() and len(countries) <= 10:
            self.createButton.setEnabled(True)
        else:
            self.createButton.setEnabled(False)

    @pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def on_countriesTree_itemChanged(self, item, column):
        if column == 2 or column == 3:
            self.pic.setPixmap(QtGui.QPixmap.fromImage(ImageQt.ImageQt(self.drawCountriesLabels(self.imageClean))))
        elif column == 0:
            item.setText(0, item.whatsThis(0))
        elif column == 1:
            item.setText(1, str(len(countries[item.whatsThis(0)]['t'])))

    @pyqtSlot()
    def on_countryName_editingFinished(self):
        if not self.checkCountryName():
            self.countryName.setStyleSheet('color: red;')
        else:
            self.countryName.setStyleSheet('color: black;')
            self.newValidation()

    @pyqtSlot(str)
    def on_begTer_textChanged(self, begTer):
        begTer = begTer.upper()
        self.begTer.setText(begTer)

        if self.checkBegTer():
            self.begTer.setStyleSheet('color: black;')
            self.newValidation()
        else:
            self.begTer.setStyleSheet('color: red;')

    @pyqtSlot()
    def on_selectColor_clicked(self):
        self.colorNew = QtWidgets.QColorDialog.getColor()
        scene = QtWidgets.QGraphicsScene()
        scene.setBackgroundBrush(self.colorNew)
        self.colorView.setScene(scene)

        self.colorNew = (self.colorNew.red(), self.colorNew.green(), self.colorNew.blue(), self.colorNew.alpha())
        if self.colorNew == (0, 0, 0, 255) or self.colorNew == (176, 215, 244, 255) or \
                self.colorNew == (255, 255, 255, 255) or self.colorNew in [countries[x]['c'] for x in countries]:
            self.colorNew = None
        self.newValidation()

    @pyqtSlot()
    def on_create_clicked(self):
        name = self.countryName.text()
        item = QtWidgets.QTreeWidgetItem(self.countriesTree, [name, '1', '0', '0'])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setWhatsThis(0, name)
        self.countriesTree.addTopLevelItem(item)
        countries[name] = {'t': [self.begTer.text()], 'c': self.colorNew}
        self.fillTer(self.begTer.text(), self.colorNew)

        self.countryName.setText('')
        self.begTer.setText('')
        self.colorNew = None
        scene = QtWidgets.QGraphicsScene()
        scene.setBackgroundBrush(QtGui.QColor.fromRgb(255, 255, 255))
        self.colorView.setScene(scene)
        self.createButton.setEnabled(False)

    @pyqtSlot(str)
    def on_changeStateEntry_textChanged(self, text):
        self.changeStateEntry.setText(text.upper())
        self.createButton.setEnabled(False)

    def newTerValidation(self):
        terras = self.changeStateEntry.text().split()
        if not terras:
            return False
        item = self.countriesTree.currentItem()

        if item is not None:
            country = item.text(0)
        elif not self.makeEmpty.isChecked():
            return None

        def havePorts():
            for i in terras:
                for x in self.config[i]:
                    if type(x) is bool:
                        return True
            return False

        def countryHavePorts():
            if item is not None:
                for ter in countries[country]['t']:
                    for x in self.config[ter]:
                        if type(x) is bool:
                            return True
                return False
            else:
                return False

        def checkCollisions():
            r = []
            for ter in terras:
                r.append(not self.haveCollision(countries[country]['c'], ter))
            return not any(r)

        haveCol = checkCollisions()

        if terras and (self.makeEmpty.isChecked() or all(e in list(self.config) for e in list(terras))
                       and not any(e in terras for e in countries[country]['t']) and (not havePorts() and haveCol) or
                       (havePorts() and countryHavePorts() or (havePorts() and haveCol))):
            return True
        else:
            return False

    def country_fromColor(self, color):
        for country in countries:
            if countries[country]['c'] == color:
                return country

    @pyqtSlot()
    def on_newApply_clicked(self):
        if not self.newTerValidation():
            self.warn.setText('Невозможно присвоить/очистить территории!')
            self.warn.show()
            return False

        def coords_fromTer(terr):
            for x in self.config[terr]:
                if type(x) == list:
                    return tuple(x)

        def setTerCount(country, add):
            item = self.countriesTree.findItems(country, Qt.MatchExactly, column=0)[0]
            index = self.countriesTree.indexFromItem(item).row()
            if item.text(0) == country:
                count = str(int(item.text(1)) + add)
                if count == '0':
                    self.countriesTree.takeTopLevelItem(index)
                    return False
                item.setText(1, str(int(item.text(1)) + add))
                return True

        terras = self.changeStateEntry.text().split()
        if self.makeEmpty.isChecked():
            for ter in terras:
                selColor = self.imageClean.getpixel(coords_fromTer(ter))
                if selColor != (255, 255, 255, 255):
                    countryMinusTer = self.country_fromColor(selColor)
                    countries[countryMinusTer]['t'].pop(countries[countryMinusTer]['t'].index(ter))
                    if not setTerCount(countryMinusTer, -1):
                        countries.pop(countryMinusTer, None)
                self.fillTer(ter, (255, 255, 255, 255))
        else:
            item = self.countriesTree.currentItem()
            country = item.text(0)
            for ter in terras:
                selColor = self.imageClean.getpixel(coords_fromTer(ter))
                if selColor != (255, 255, 255, 255):
                    countryMinusTer = self.country_fromColor(selColor)
                    countries[countryMinusTer]['t'].pop(countries[countryMinusTer]['t'].index(ter))
                    if not setTerCount(countryMinusTer, -1):
                        countries.pop(countryMinusTer, None)
                self.fillTer(ter, countries[country]['c'])
            countries[country]['t'] += terras
            setTerCount(country, 1)
        self.changeStateEntry.setText('')

    def haveCollision(self, color, terr):
        image = self.imageClean.copy()
        width = image.size[0]
        height = image.size[1]

        transparent = (255, 255, 255, 0)
        centralPixel = None

        for ter in self.config[terr]:
            if type(ter) == list:
                if not centralPixel:
                    centralPixel = ter
                ImageDraw.floodfill(image, (ter[0], ter[1]), transparent)

        begPixelF = (lambda: centralPixel[0] - 200 if centralPixel[0] > 200 else 1,
                     lambda: centralPixel[1] - 200 if centralPixel[1] > 200 else 1)

        endPixelF = (lambda: centralPixel[0] + 200 if centralPixel[0] + 200 <= width else width,
                     lambda: centralPixel[1] + 200 if centralPixel[1] + 200 <= height else height)

        class FindThread(Thread):
            def __init__(self, direction, begPixel, endPixel):
                super(FindThread, self).__init__()
                self.direction = direction
                self.begPixel = begPixel
                self.endPixel = endPixel
                self.found = []

            def run(self):
                # 0 - country color
                # 1 - black
                # 2 - new territory color

                global collisionFindResult
                collisionFindResult = False

                def find(x, y):
                    if image.getpixel((x, y)) == color:
                        if 0 not in self.found:
                            if self.found == [2, 1]:
                                return True
                            self.found.append(0)
                    elif image.getpixel((x, y)) == (255, 255, 255, 0):
                        if 2 not in self.found:
                            if self.found == [0, 1]:
                                return True
                            self.found.append(2)
                    elif image.getpixel((x, y)) == (0, 0, 0, 255):
                        if (2 in self.found or 0 in self.found) and 1 not in self.found:
                            self.found.append(1)
                    else:
                        self.found = []

                if self.direction == 'horizontal':
                    for x in range(self.begPixel[0], self.endPixel[0]):
                        for y in range(self.begPixel[1], self.endPixel[1]):
                            if collisionFindResult:
                                return True
                            if find(x, y):
                                collisionFindResult = True
                                return True

                if self.direction == 'vertical':
                    for y in range(self.begPixel[1], self.endPixel[1]):
                        for x in range(self.begPixel[0], self.endPixel[0]):
                            if collisionFindResult:
                                return True
                            if find(x, y):
                                collisionFindResult = True
                                return True

        workerH = FindThread('horizontal', (begPixelF[0](), begPixelF[1]()), (endPixelF[0](), endPixelF[1]()))
        workerV = FindThread('vertical', (begPixelF[0](), begPixelF[1]()), (endPixelF[0](), endPixelF[1]()))
        workerH.start()
        workerV.start()
        workerH.join()
        workerV.join()

        return collisionFindResult

    @pyqtSlot()
    def on_save_clicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                            "PNG file (*.png)", options=options)
        if fileName:
            if fileName[-4:] != '.png':
                fileName += '.png'
            self.pic.pixmap().toImage().save(fileName, "PNG")
