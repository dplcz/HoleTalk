# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

# DEFAULT PACKAGES
# ///////////////////////////////////////////////////////////////
import os
import random

# IMPORT / GUI, SETTINGS AND WIDGETS
# ///////////////////////////////////////////////////////////////
# Packages
from app.packages.pyside_or_pyqt import *  # Qt
from app.packages.widgets import *  # Widgets
from app.modules.datamodel.tools import *
# GUI
from app.uis.chat.ui_page_messages import Ui_chat_page  # MainWindow
from app.uis.chat.message import Message  # MainWindow


# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class Chat(QWidget):
    def __init__(
            self,
            user_image,
            user_name,
            user_description,
            my_name,
            conn,
            cur_user,
            cur_server,
            input_queue=None
    ):
        QWidget.__init__(self)

        self.conn = conn
        self.cur_user = cur_user
        self.cur_server = cur_server
        self.input_queue = input_queue

        self.page = Ui_chat_page()
        self.page.setupUi(self)

        # UPDATE INFO
        self.page.user_image.setStyleSheet(
            "#user_image { background-image: url(\"" + os.path.normpath(user_image).replace("\\", "/") + "\") }")
        self.page.user_name.setText(user_name)
        self.page.user_description.setText(user_description)

        # CHANGE PLACEHOLDER TEXT
        format_user_name = user_name.replace(" ", "_").replace("-", "_")
        format_user_name = format_user_name.lower()
        self.page.line_edit_message.setPlaceholderText(f"Message #{str(format_user_name).lower()}")

        # ENTER / RETURN PRESSED
        self.page.line_edit_message.keyReleaseEvent = self.enter_return_release

        # ENTER / RETURN PRESSED
        self.page.btn_send_message.clicked.connect(self.send_message)

        history_msg = self.conn.get_history_list(self.cur_user, self.cur_server)

        # MESSAGES
        # self.messages = [
        #     f"Hi {my_name.capitalize()}, how are you?",
        #     f"Hello {my_name.capitalize()}, how are you today?",
        #     f"{my_name.capitalize()}, do you know if it is going to rain today?",
        #     f"{my_name.capitalize()}, how is your day?",
        #     f"{my_name.capitalize()}, do you remember that you owe me $100? Humm..."
        # ]

        self.messages = history_msg

        # SEND USER MESSAGE
        for i in self.messages:
            if i['send_me'] == 0:
                self.send_by_friend(i['send_info'], i['message'], i['send_time'])
            else:
                self.send_message(i['message'], i['send_time'])

        self.add_line_split()

    # ENTER / RETURN SEND MESSAGE
    def enter_return_release(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message()

    # SEND MESSAGE
    def send_message(self, msg=None, send_time=None):
        if self.page.line_edit_message.text() != "" or msg is not None:
            if msg:
                self.message = Message('" {} "'.format(msg), True, send_time)
            else:
                self.message = Message('" {} "'.format(self.page.line_edit_message.text()), True)

                if self.conn.add_message(self.cur_user, self.cur_server, 'self', self.page.line_edit_message.text(),
                                         send_me=1) != OperationStatus.ADD_SUCCESS:
                    return None
                if self.input_queue:
                    self.input_queue.put(self.page.line_edit_message.text())

            self.page.chat_messages_layout.addWidget(self.message, Qt.AlignCenter, Qt.AlignBottom)
            self.page.line_edit_message.setText("")

            # SCROLL TO END            
            # QTimer.singleShot(10, lambda: self.page.messages_frame.setFixedHeight(
            #     self.page.chat_messages_layout.sizeHint().height()))
            QTimer.singleShot(15, lambda: self.scroll_to_end())

    # SEND MESSAGE BY FRIEND
    def send_by_friend(self, send_info, msg, send_time=None, save=True):
        if send_info == 'server':
            self.message = Message('{} :" {} "'.format(send_info, msg), False, send_time, True)
        else:
            self.message = Message('{} :" {} "'.format(send_info, msg), False, send_time)
        if save:
            if self.conn.add_message(self.cur_user, self.cur_server, 'server', msg,
                                     send_me=0) != OperationStatus.ADD_SUCCESS:
                return None

        self.page.chat_messages_layout.addWidget(self.message, Qt.AlignCenter, Qt.AlignBottom)
        self.page.chat_messages_layout.update()
        # self.page.line_edit_message.setText("")

        # SCROLL TO END            
        # QTimer.singleShot(10, lambda: self.page.messages_frame.setFixedHeight(
        #     self.page.chat_messages_layout.sizeHint().height()))
        QTimer.singleShot(15, lambda: self.scroll_to_end())

    def add_line_split(self):
        self.message = Message('-' * 150, False, server=False, split=True)
        self.page.chat_messages_layout.addWidget(self.message, Qt.AlignCenter, Qt.AlignBottom)
        self.page.chat_messages_layout.update()
        # self.page.line_edit_message.setText("")

        # SCROLL TO END
        # QTimer.singleShot(10, lambda: self.page.messages_frame.setFixedHeight(
        #     self.page.chat_messages_layout.sizeHint().height()))
        QTimer.singleShot(15, lambda: self.scroll_to_end())

    def scroll_to_end(self):
        # SCROLL TO END
        self.scroll_bar = self.page.chat_messages.verticalScrollBar()
        self.scroll_bar.setValue(self.scroll_bar.maximum())
