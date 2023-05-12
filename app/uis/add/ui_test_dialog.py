# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
                               QLabel, QPushButton, QSizePolicy, QVBoxLayout,
                               QWidget)


class Ui_Test_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, Test_Dialog):
        if not Test_Dialog.objectName():
            Test_Dialog.setObjectName(u"Test_Dialog")
        Test_Dialog.resize(400, 300)
        Test_Dialog.setMinimumSize(QSize(400, 300))
        Test_Dialog.setMaximumSize(QSize(400, 300))
        Test_Dialog.setLayoutDirection(Qt.LeftToRight)
        Test_Dialog.setAutoFillBackground(False)
        Test_Dialog.setStyleSheet(u"#bg {\n"
                                  "	background-color: rgb(50, 50, 50);\n"
                                  "	border-radius: 10px;\n"
                                  "}\n"
                                  ".QLabel {\n"
                                  "	font: 800 15pt \"Segoe UI\";\n"
                                  "	color: rgb(150, 150, 128);\n"
                                  "}\n"
                                  ".QLineEdit:hover {\n"
                                  "	color: rgb(230, 230, 230);\n"
                                  "	border: 3px solid rgb(62, 63, 66);\n"
                                  "}\n"
                                  ".QLineEdit:focus {\n"
                                  "	color: rgb(230, 230, 230);\n"
                                  "	border: 3px solid rgb(189, 255, 0);\n"
                                  "	background-color: rgb(14, 14, 15);\n"
                                  "}\n"
                                  ".QPushButton {	\n"
                                  "	background-position: center;\n"
                                  "    background-repeat: no-repeat;\n"
                                  "	border: none;\n"
                                  "	outline: none;\n"
                                  "	border-radius: 8px;\n"
                                  "	text-align: left;\n"
                                  "}\n"
                                  "\n"
                                  "#close_app_btn:hover { background-color: rgb(255, 0, 127); }\n"
                                  "#close_app_btn:pressed { background-color: rgb(172, 229, 0); }\n"
                                  "\n"
                                  "\n"
                                  "\n"
                                  "\n"
                                  "")
        self.horizontalLayout = QHBoxLayout(Test_Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(Test_Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.bg = QFrame(self.widget)
        self.bg.setObjectName(u"bg")
        self.bg.setLayoutDirection(Qt.LeftToRight)
        self.bg.setFrameShape(QFrame.NoFrame)
        self.bg.setFrameShadow(QFrame.Raised)
        self.testText = QLabel(self.bg)
        self.testText.setObjectName(u"testText")
        self.testText.setGeometry(QRect(130, 20, 111, 51))
        self.testText.setLayoutDirection(Qt.LeftToRight)
        self.testText.setStyleSheet(u"")
        self.resultText = QLabel(self.bg)
        self.resultText.setObjectName(u"resultText")
        self.resultText.setGeometry(QRect(50, 100, 261, 41))
        self.close_app_btn = QPushButton(self.bg)
        self.close_app_btn.setObjectName(u"close_app_btn")
        self.close_app_btn.setGeometry(QRect(310, 10, 31, 16))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_app_btn.sizePolicy().hasHeightForWidth())
        self.close_app_btn.setSizePolicy(sizePolicy)
        self.close_app_btn.setMaximumSize(QSize(16777215, 16777215))
        self.close_app_btn.setFocusPolicy(Qt.NoFocus)
        self.close_app_btn.setContextMenuPolicy(Qt.NoContextMenu)
        self.close_app_btn.setLayoutDirection(Qt.LeftToRight)
        self.close_app_btn.setStyleSheet(u"background-image: url(:/icons_svg/images/icons_svg/icon_close.svg);")

        self.verticalLayout_2.addWidget(self.bg)

        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(Test_Dialog)

        QMetaObject.connectSlotsByName(Test_Dialog)

    # setupUi

    def retranslateUi(self, Test_Dialog):
        Test_Dialog.setWindowTitle(QCoreApplication.translate("Test_Dialog", u"Voice_Dialog", None))
        self.testText.setText(QCoreApplication.translate("Test_Dialog", u"Testing...", None))
        self.resultText.setText("")
        self.close_app_btn.setText("")
    # retranslateUi
