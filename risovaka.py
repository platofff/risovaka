from sys import argv, exit

from PyQt5.QtWidgets import QApplication

import configurer
import main

if __name__ == '__main__':
    if argv[1] == 'main':
        argv.pop(1)
        app = QApplication(argv)
        window = main.App()
        exit(app.exec_())
    elif argv[1] == 'configurer':
        argv.pop(1)
        app = QApplication(argv)
        window = configurer.App()
        exit(app.exec_())
