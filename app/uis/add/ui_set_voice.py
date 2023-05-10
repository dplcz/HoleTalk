# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'set_voice.ui'
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
                               QLabel, QPushButton, QSizePolicy, QSlider,
                               QVBoxLayout, QWidget)


class Ui_Voice_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, Voice_Dialog):
        if not Voice_Dialog.objectName():
            Voice_Dialog.setObjectName(u"Voice_Dialog")
        Voice_Dialog.resize(400, 300)
        Voice_Dialog.setMinimumSize(QSize(400, 300))
        Voice_Dialog.setMaximumSize(QSize(400, 300))
        Voice_Dialog.setLayoutDirection(Qt.LeftToRight)
        Voice_Dialog.setAutoFillBackground(False)
        Voice_Dialog.setStyleSheet(u"#bg {\n"
                                   "	background-color: rgb(50, 50, 50);\n"
                                   "	border-radius: 10px;\n"
                                   "}\n"
                                   ".QLabel {\n"
                                   "	font: 800 10pt \"Segoe UI\";\n"
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
        self.horizontalLayout = QHBoxLayout(Voice_Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(Voice_Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.bg = QFrame(self.widget)
        self.bg.setObjectName(u"bg")
        self.bg.setLayoutDirection(Qt.LeftToRight)
        self.bg.setFrameShape(QFrame.NoFrame)
        self.bg.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.bg)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, -1, 20, -1)
        self.close_app_btn = QPushButton(self.bg)
        self.close_app_btn.setObjectName(u"close_app_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_app_btn.sizePolicy().hasHeightForWidth())
        self.close_app_btn.setSizePolicy(sizePolicy)
        self.close_app_btn.setMaximumSize(QSize(16777215, 16777215))
        self.close_app_btn.setContextMenuPolicy(Qt.NoContextMenu)
        self.close_app_btn.setLayoutDirection(Qt.LeftToRight)
        self.close_app_btn.setFocusPolicy(Qt.NoFocus)
        self.close_app_btn.setStyleSheet(u"background-image: url(:/icons_svg/images/icons_svg/icon_close.svg);")

        self.verticalLayout.addWidget(self.close_app_btn)

        self.label = QLabel(self.bg)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(400, 20))

        self.verticalLayout.addWidget(self.label)

        self.input_slider = QSlider(self.bg)
        self.input_slider.setObjectName(u"input_slider")
        self.input_slider.setMaximum(100)
        self.input_slider.setPageStep(5)
        self.input_slider.setValue(50)
        self.input_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.input_slider)

        self.label_2 = QLabel(self.bg)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(400, 20))

        self.verticalLayout.addWidget(self.label_2)

        self.out_slider = QSlider(self.bg)
        self.out_slider.setObjectName(u"out_slider")
        self.out_slider.setMaximum(100)
        self.out_slider.setPageStep(5)
        self.out_slider.setValue(50)
        self.out_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.out_slider)

        self.label_3 = QLabel(self.bg)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(400, 20))

        self.verticalLayout.addWidget(self.label_3)

        self.check_slider = QSlider(self.bg)
        self.check_slider.setObjectName(u"check_slider")
        self.check_slider.setMaximum(100)
        self.check_slider.setPageStep(5)
        self.check_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.check_slider)

        self.verticalLayout_2.addWidget(self.bg)

        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(Voice_Dialog)

        QMetaObject.connectSlotsByName(Voice_Dialog)

    # setupUi

    def retranslateUi(self, Voice_Dialog):
        Voice_Dialog.setWindowTitle(QCoreApplication.translate("Voice_Dialog", u"Voice_Dialog", None))
        self.close_app_btn.setText("")
        self.label.setText(QCoreApplication.translate("Voice_Dialog", u"\u8f93\u5165\u97f3\u91cf", None))
        self.label_2.setText(QCoreApplication.translate("Voice_Dialog", u"\u8f93\u51fa\u97f3\u91cf", None))
        self.label_3.setText(QCoreApplication.translate("Voice_Dialog", u"\u9ea6\u514b\u98ce\u68c0\u6d4b", None))
    # retranslateUi
