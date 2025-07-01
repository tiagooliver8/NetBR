# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setMinimumSize(QSize(400, 700))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(0)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.top_box = QWidget(self.centralwidget)
        self.top_box.setObjectName(u"top_box")
        self.top_layout = QVBoxLayout(self.top_box)
        self.top_layout.setSpacing(8)
        self.top_layout.setObjectName(u"top_layout")
        self.top_layout.setContentsMargins(20, 10, 20, 10)
        self.cloud_icon = QLabel(self.top_box)
        self.cloud_icon.setObjectName(u"cloud_icon")

        self.top_layout.addWidget(self.cloud_icon)

        self.top_label = QLabel(self.top_box)
        self.top_label.setObjectName(u"top_label")

        self.top_layout.addWidget(self.top_label)


        self.main_layout.addWidget(self.top_box)

        self.spacer_top = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.main_layout.addItem(self.spacer_top)

        self.button = QPushButton(self.centralwidget)
        self.button.setObjectName(u"button")
        self.button.setMinimumHeight(80)

        self.main_layout.addWidget(self.button)

        self.spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.main_layout.addItem(self.spacer_bottom)

        self.text_box = QWidget(self.centralwidget)
        self.text_box.setObjectName(u"text_box")
        self.text_box_layout = QVBoxLayout(self.text_box)
        self.text_box_layout.setObjectName(u"text_box_layout")
        self.text_box_layout.setContentsMargins(18, 18, 18, 18)
        self.scroll_area = QScrollArea(self.text_box)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.scroll_area.setWidget(self.scrollAreaWidgetContents)

        self.text_box_layout.addWidget(self.scroll_area)


        self.main_layout.addWidget(self.text_box)

        self.progress_bar = QProgressBar(self.centralwidget)
        self.progress_bar.setObjectName(u"progress_bar")

        self.main_layout.addWidget(self.progress_bar)

        self.bottom_box = QWidget(self.centralwidget)
        self.bottom_box.setObjectName(u"bottom_box")
        self.bottom_layout = QVBoxLayout(self.bottom_box)
        self.bottom_layout.setSpacing(8)
        self.bottom_layout.setObjectName(u"bottom_layout")
        self.bottom_layout.setContentsMargins(20, 10, 20, 10)
        self.mersen_logo = QLabel(self.bottom_box)
        self.mersen_logo.setObjectName(u"mersen_logo")

        self.bottom_layout.addWidget(self.mersen_logo)


        self.main_layout.addWidget(self.bottom_box)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"NetBR", None))
        self.top_label.setText(QCoreApplication.translate("MainWindow", u"Nuvem.Test", None))
        self.button.setText(QCoreApplication.translate("MainWindow", u"TESTAR!", None))
    # retranslateUi

