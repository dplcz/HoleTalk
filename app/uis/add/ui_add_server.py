# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_server.ui'
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
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Add_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    def setupUi(self, Add_Dialog):
        if not Add_Dialog.objectName():
            Add_Dialog.setObjectName(u"Add_Dialog")
        Add_Dialog.resize(300, 500)
        Add_Dialog.setMinimumSize(QSize(300, 500))
        Add_Dialog.setMaximumSize(QSize(300, 500))
        Add_Dialog.setStyleSheet(u"#bg {\n"
"	background-color: rgb(50, 50, 50);\n"
"	border-radius: 10px;\n"
"}\n"
"QLabel {\n"
"	color:  rgb(121, 121, 121);\n"
"	padding-left: 10px;\n"
"	padding-top: 20px;\n"
"}\n"
".QLineEdit {\n"
"	border: 3px solid rgb(128, 50, 128);\n"
"	border-radius: 15px;\n"
"	background-color: rgb(47, 48, 50);\n"
"	color: rgb(121, 121, 121);\n"
"	padding-left: 10px;\n"
"	padding-right: 10px;\n"
"	background-repeat: none;\n"
"	background-position: left center;\n"
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
" .QPushButton {	\n"
"	background-position: center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	outline: none;\n"
"	border-radius: 8px;\n"
"	text-align: left;\n"
"}\n"
"#close_app_btn:hover { background-color: rgb(255, 0, 127); }\n"
"#close_app_btn:pressed { background-color: rg"
                        "b(172, 229, 0); }")
        self.horizontalLayout = QHBoxLayout(Add_Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.central = QWidget(Add_Dialog)
        self.central.setObjectName(u"central")
        self.verticalLayout_2 = QVBoxLayout(self.central)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.bg = QFrame(self.central)
        self.bg.setObjectName(u"bg")
        self.bg.setFrameShape(QFrame.NoFrame)
        self.bg.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.bg)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.logo = QFrame(self.bg)
        self.logo.setObjectName(u"logo")
        self.logo.setEnabled(True)
        self.logo.setMinimumSize(QSize(0, 260))
        self.logo.setAutoFillBackground(False)
        self.logo.setStyleSheet(u"#logo {\n"
"	border-radius: 10px;\n"
"	background-image: url(:/images_svg/images/images_svg/logo.svg);\n"
"	background-position: center;\n"
"	background-repeat: no-repeat;\n"
"}")
        self.logo.setFrameShape(QFrame.NoFrame)
        self.logo.setFrameShadow(QFrame.Raised)
        self.close_app_btn = QPushButton(self.logo)
        self.close_app_btn.setObjectName(u"close_app_btn")
        self.close_app_btn.setGeometry(QRect(210, 0, 28, 28))
        self.close_app_btn.setMinimumSize(QSize(28, 28))
        self.close_app_btn.setMaximumSize(QSize(28, 28))
        self.close_app_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_app_btn.setFocusPolicy(Qt.NoFocus)
        self.close_app_btn.setStyleSheet(u"background-image: url(:/icons_svg/images/icons_svg/icon_close.svg);")
        self.close_app_btn.setIconSize(QSize(20, 20))
        self.user_description = QLabel(self.logo)
        self.user_description.setObjectName(u"user_description")
        self.user_description.setGeometry(QRect(0, 260, 240, 36))
        self.user_description.setStyleSheet(u"background: transparent;")

        self.verticalLayout.addWidget(self.logo)

        self.servername = QLineEdit(self.bg)
        self.servername.setObjectName(u"servername")
        self.servername.setMinimumSize(QSize(0, 30))
        self.servername.setMaximumSize(QSize(16777215, 40))

        self.verticalLayout.addWidget(self.servername)

        self.address = QLineEdit(self.bg)
        self.address.setObjectName(u"address")
        self.address.setMinimumSize(QSize(0, 30))
        self.address.setMaximumSize(QSize(16777215, 40))

        self.verticalLayout.addWidget(self.address)

        self.password = QLineEdit(self.bg)
        self.password.setObjectName(u"password")
        self.password.setMinimumSize(QSize(0, 30))
        self.password.setMaximumSize(QSize(16777215, 40))

        self.verticalLayout.addWidget(self.password)


        self.verticalLayout_2.addWidget(self.bg)


        self.horizontalLayout.addWidget(self.central)


        self.retranslateUi(Add_Dialog)

        QMetaObject.connectSlotsByName(Add_Dialog)
    # setupUi

    def retranslateUi(self, Add_Dialog):
        Add_Dialog.setWindowTitle(QCoreApplication.translate("Add_Dialog", u"Dialog", None))
#if QT_CONFIG(tooltip)
        self.close_app_btn.setToolTip(QCoreApplication.translate("Add_Dialog", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.close_app_btn.setText("")
        self.user_description.setText(QCoreApplication.translate("Add_Dialog", u"Add Server Info", None))
        self.servername.setPlaceholderText(QCoreApplication.translate("Add_Dialog", u"Servername", None))
        self.address.setPlaceholderText(QCoreApplication.translate("Add_Dialog", u"Address", None))
        self.password.setPlaceholderText(QCoreApplication.translate("Add_Dialog", u"Password", None))
    # retranslateUi

