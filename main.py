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
import sys
import os
import re

# IMPORT / GUI, SETTINGS AND WIDGETS
# ///////////////////////////////////////////////////////////////
# Packages
from app.packages.pyside_or_pyqt import *  # Qt
from app.packages.widgets import *  # Widgets
# GUIs
from app.uis.login.ui_login import Ui_Login  # Login / Splash Screen
from app.uis.main_window.ui_main import Ui_MainWindow  # MainWindow
from app.uis.add.ui_add_server import Ui_Add_Dialog
from app.uis.add.ui_set_voice import Ui_Voice_Dialog
from app.uis.add.ui_test_dialog import Ui_Test_Dialog
from app.uis.chat.page_messages import Chat  # Chat Widget
# Modules
import app.modules.ui_functions.functions as ui_functions
from app.modules.app_settings.settings import *
from app.modules.datamodel.tools import *

from client import UDPClient
from conf.config import Conf
from client import get_net_nat

# GLOBALS
# ///////////////////////////////////////////////////////////////
counter = 0
number_pattern = re.compile('\d+')


class MyThread(QThread):
    add_msg_signal = Signal(tuple)
    add_statistics_signal = Signal(tuple)
    result_signal = Signal(tuple)

    def __init__(self, target, *args):
        super().__init__()
        self._func = target
        self.args = args

    def run(self):
        temp = self._func(*self.args)
        if temp:
            self.result_signal.emit(temp)


# LOGIN
# ///////////////////////////////////////////////////////////////
class LoginWindow(QMainWindow):
    conn = AppDataModel()

    def __init__(self):
        QMainWindow.__init__(self)
        # GET WIDGETS FROM "ui_login.py"
        # Load widgets inside LoginWindow
        # ///////////////////////////////////////////////////////////////

        self.ui = Ui_Login()
        self.ui.setupUi(self)

        # REMOVE TITLE BAR
        # ///////////////////////////////////////////////////////////////
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # IMPORT CIRCULAR PROGRESS
        # ///////////////////////////////////////////////////////////////
        self.progress = CircularProgress()
        self.progress.width = 240
        self.progress.height = 240
        self.progress.value = 0
        self.progress.setFixedSize(self.progress.width, self.progress.height)
        self.progress.font_size = 20
        self.progress.add_shadow(True)
        self.progress.progress_width = 4
        self.progress.progress_color = QColor("#bdff00")
        self.progress.text_color = QColor("#E6E6E6")
        self.progress.bg_color = QColor("#222222")
        self.progress.setParent(self.ui.preloader)
        self.progress.show()

        # ADD DROP SHADOW
        # ///////////////////////////////////////////////////////////////
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.ui.bg.setGraphicsEffect(self.shadow)

        # QTIMER
        # ///////////////////////////////////////////////////////////////
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

        # KEY PRESS EVENT
        # ///////////////////////////////////////////////////////////////
        self.ui.username.keyReleaseEvent = self.check_login
        self.ui.password.keyReleaseEvent = self.check_login

        self.show()

    # CHECK LOGIN
    # ///////////////////////////////////////////////////////////////
    def check_login(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            username = self.ui.username.text()
            password = self.ui.password.text()

            def open_main(cur_user):
                # SHOW MAIN WINDOW
                self.main = MainWindow(self.conn, cur_user, username)
                self.main.top_user.label_user.setText(username.capitalize())
                self.main.show()
                self.close()

            status, cur_user = self.conn.check_user(username, password)
            if status == OperationStatus.Login_SUCCESS:
                self.ui.user_description.setText(f"Welcome {username}!")
                self.ui.user_description.setStyleSheet("#user_description { color: #bdff00 }")
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid #bdff00; }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid #bdff00; }")
                QTimer.singleShot(1200, lambda: open_main(cur_user))
            elif status == OperationStatus.Register_SUCCESS:
                self.ui.user_description.setText(f"Register Successful! Welcome {username}!")
                self.ui.user_description.setStyleSheet("#user_description { color: #bdff00 }")
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid #bdff00; }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid #bdff00; }")
                QTimer.singleShot(1200, lambda: open_main(cur_user))
            else:
                # SET STYLESHEET
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid rgb(255, 0, 127); }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                self.shacke_window()

    def shacke_window(self):
        # SHACKE WINDOW
        actual_pos = self.pos()
        QTimer.singleShot(0, lambda: self.move(actual_pos.x() + 1, actual_pos.y()))
        QTimer.singleShot(50, lambda: self.move(actual_pos.x() + -2, actual_pos.y()))
        QTimer.singleShot(100, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(150, lambda: self.move(actual_pos.x() + -5, actual_pos.y()))
        QTimer.singleShot(200, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(250, lambda: self.move(actual_pos.x() + -2, actual_pos.y()))
        QTimer.singleShot(300, lambda: self.move(actual_pos.x(), actual_pos.y()))

    # UPDATE PROGRESS BAR
    # ///////////////////////////////////////////////////////////////
    def update(self):
        global counter

        # SET VALUE TO PROGRESS BAR
        self.progress.set_value(counter)

        # CLOSE SPLASH SCREEN AND OPEN MAIN APP
        if counter >= 100:
            # STOP TIMER
            self.timer.stop()
            self.animation_login()

        # INCREASE COUNTER
        counter += 1

    # START ANIMATION TO LOGIN
    # ///////////////////////////////////////////////////////////////
    def animation_login(self):
        # ANIMATION
        self.animation = QPropertyAnimation(self.ui.frame_widgets, b"geometry")
        self.animation.setDuration(1500)
        self.animation.setStartValue(QRect(0, 70, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
        self.animation.setEndValue(QRect(0, -325, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()


# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class MainWindow(QMainWindow):
    def __init__(self, conn, cur_user, username):
        QMainWindow.__init__(self)
        # GET WIDGETS FROM "ui_main.py"
        # Load widgets inside MainWindow
        # ///////////////////////////////////////////////////////////////

        self.img_list = ['images/users/cat.png', 'images/users/mouse.png']

        self.conn: AppDataModel = conn
        self.cur_user = cur_user
        self.username = username

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.close_app_btn.clicked.connect(self.close_all)

        self.dlg = Ui_Add_Dialog()
        self.dlg.setWindowFlag(Qt.FramelessWindowHint)
        self.dlg.setAttribute(Qt.WA_TranslucentBackground)

        self.dlg.servername.keyReleaseEvent = self.add_server
        self.dlg.address.keyReleaseEvent = self.add_server
        self.dlg.password.keyReleaseEvent = self.add_server

        self.dlg.close_app_btn.released.connect(lambda: self.dlg.close())

        self.set = Ui_Voice_Dialog()
        self.set.setWindowFlag(Qt.FramelessWindowHint)
        self.set.setAttribute(Qt.WA_TranslucentBackground)
        self.set.focusOutEvent = lambda x: self.set.close()

        self.set.close_app_btn.clicked.connect(lambda: self.set.close())
        self.set.out_slider.valueChanged.connect(self.change_volume)
        self.set.check_slider.valueChanged.connect(self.change_threshold)

        self.test_dlg = Ui_Test_Dialog()
        self.test_dlg.setWindowFlag(Qt.FramelessWindowHint)
        self.test_dlg.setAttribute(Qt.WA_TranslucentBackground)
        self.test_dlg.close_app_btn.clicked.connect(lambda: self.test_dlg.close())

        # 麦克风和音频
        self.mic = True
        self.voice = True

        self._connect_flag = False

        self.context_menu = QMenu(self)
        self.action_delete = QAction('删除', self)
        self.action_delete.triggered.connect(self.delete_server)
        self.context_menu.addAction(self.action_delete)

        self.context_menu.setStyleSheet('''
            QMenu {
                background-color: rgb(50, 50, 50);
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                
            }
            QMenu::item {
                padding: 5px 30px 5px 30px;
                border-radius: 10px;
                background-color: transparent;
                color: #fff;
            }
            QMenu::item:selected {
                background-color: #BA55D3;
                color: #fff;
            }
        ''')

        # SET DEFAULT PAGE
        # ///////////////////////////////////////////////////////////////
        self.ui.app_pages.setCurrentWidget(self.ui.home)

        # LOAD DICT SETTINGS FROM "settings.json" FILE
        # ///////////////////////////////////////////////////////////////
        self.settings = Settings()

        self.custom_btn_top = LeftMenuButton(
            self,
            "custom_btn_top",
            "images/icons_svg/icon_add_user.svg",
            "Add new server"
        )
        self.custom_btn_bottom_1 = LeftMenuButton(
            self,
            "custom_btn_bottom_1",
            "images/icons_svg/icon_more_options.svg",
            "Test your nat type"
        )
        self.custom_btn_bottom_2 = LeftMenuButton(
            self,
            "custom_btn_bottom_2",
            "images/icons_svg/icon_settings.svg",
            "Open settings"
        )
        self.ui.top_menus_layout.addWidget(self.custom_btn_top)
        self.ui.bottom_menus_layout.addWidget(self.custom_btn_bottom_1)
        self.ui.bottom_menus_layout.addWidget(self.custom_btn_bottom_2)

        # DEBUG
        self.custom_btn_top.released.connect(self.add_dialog)
        self.custom_btn_bottom_2.released.connect(self.set_dialog)
        # self.custom_btn_top.released.connect(lambda: print(f"{self.custom_btn_top.objectName()}: released"))
        self.custom_btn_bottom_1.released.connect(self.test_nat_type)

        def switch2connect():
            if self.ui.chat_layout.count() > 0:
                self.ui.app_pages.setCurrentWidget(self.ui.chat)
            else:
                self.ui.app_pages.setCurrentWidget(self.ui.home)

        def switch2home():
            self.ui.app_pages.setCurrentWidget(self.ui.home)

        self.ui.connect_page.clicked.connect(switch2connect)
        self.ui.home_page.clicked.connect(switch2home)

        # TOP USER BOX
        # Add widget to App
        # ///////////////////////////////////////////////////////////////
        self.top_user = TopUserInfo(self.ui.left_messages, 8, 64, self.username, "Writing your description")
        self.top_user.setParent(self.ui.top_user_frame)
        self.top_user.status.connect(self.status_change)

        # SET UI DEFINITIONS
        # Run set_ui_definitions() in the ui_functions.py
        # ///////////////////////////////////////////////////////////////
        ui_functions.UiFunctions.set_ui_definitions(self)

        # ADD MESSAGE BTNS / FRIEND MENUS
        # Add btns to page
        # ///////////////////////////////////////////////////////////////
        self.setup_servers()

        self.client = None
        self._client_thread = None
        self._text_thread = None
        self._test_thread = None
        self.conf = Conf()

        self._start_threshold = 4000
        self._start_volume = 8
        # SHOW MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        self.show()

    def close_all(self):
        if self._client_thread:
            self.client.handle_stop_all()
            self._client_thread.wait()
        if self._text_thread:
            self._connect_flag = False
            self._text_thread.wait()
        self.close()

    def setup_servers(self):
        cur_server = None
        if getattr(self, 'chat', None):
            cur_server = self.chat.cur_server
        while self.ui.messages_layout.count():
            item = self.ui.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                self.ui.messages_layout.removeItem(item)
                widget.deleteLater()
        add_server = self.conn.get_server_list(self.cur_user)

        self.menu = ServerButton

        def add_menus(self, parameters):
            index = 0
            for parameter in parameters:
                server_id = parameter['server_id']
                server_image = parameter['img_path'] if parameter['img_path'] else self.img_list[index % 2]
                server_addr = parameter['address']
                server_name = parameter['name']
                server_pass = parameter['password']
                server_desc = parameter['description']
                status = 'busy' if str(server_id) != cur_server else 'online'
                unread_messages = 0
                is_active = False

                self.menu = ServerButton(
                    server_id, server_image, server_addr, server_name, server_pass, server_desc, status,
                    unread_messages, is_active
                )
                self.menu.clicked.connect(self.btn_clicked)
                self.menu.setContextMenuPolicy(Qt.CustomContextMenu)
                self.menu.customContextMenuRequested.connect(self.show_context_menu)

                self.ui.messages_layout.addWidget(self.menu)
                index += 1

        add_menus(self, add_server)

    # SET USERNAME TO MAIN WINDOW
    # ///////////////////////////////////////////////////////////////
    def set_user_and_description(self, username):
        self.top_user.user_name = username
        print(f"User: {username} are logged!")

    # PRINT STATUS
    # ///////////////////////////////////////////////////////////////
    def status_change(self, status):
        print(f"send signal: {status}")

    # GET BTN CLICKED
    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self):
        # GET BT CLICKED
        btn = self.sender()
        if getattr(self, 'chat', None):
            if btn.objectName() == self.chat.cur_server:
                if self.ui.app_pages.currentWidget() != self.ui.chat:
                    self.ui.app_pages.setCurrentWidget(self.ui.chat)
                return
            else:
                self.client.handle_stop_all()
                self._client_thread.wait()
                self._connect_flag = False
                self._text_thread.wait()

            # UNSELECT CHATS
        ui_functions.UiFunctions.deselect_chat_message(self, btn.objectName())

        # SELECT CLICKED
        if btn.objectName():
            btn.reset_unread_message()
            ui_functions.UiFunctions.select_chat_message(self, btn.objectName())

        # LOAD CHAT PAGE
        if btn.objectName():
            # REMOVE CHAT
            for chat in reversed(range(self.ui.chat_layout.count())):
                self.ui.chat_layout.itemAt(chat).widget().deleteLater()

            for i in range(self.ui.messages_layout.count()):
                item = self.ui.messages_layout.itemAt(i)
                widget = item.widget()
                widget.change_status_color('busy')
                widget.update()

            # START CONNECT
            addr, port = btn.address.split(':')
            self.client = UDPClient(addr,
                                    int(port),
                                    self.conf.get_item('server', 'beat_time'),
                                    head=self.conf.get_item('server', 'head'),
                                    username=self.top_user.user_name,
                                    nat_type=self.conf.get_item('client', 'nat'),
                                    queue_max_size=5, ui=True)

            self.chat = None

            # SET CHAT WIDGET
            self.chat = Chat(btn.server_image, btn.server_name, btn.server_description,
                             self.top_user.user_name, self.conn, self.cur_user, btn.objectName(),
                             self.client.text_input)

            self.chat.page.btn_mic_top.clicked.connect(self.change_mic)
            self.chat.page.btn_voice_top.clicked.connect(self.change_voice)
            self.chat.page.btn_delete_top.clicked.connect(self.delete_history)

            # ADD WIDGET TO LAYOUT
            self.ui.chat_layout.addWidget(self.chat)

            # JUMP TO CHAT PAGE
            self.ui.app_pages.setCurrentWidget(self.ui.chat)

            self.client.init_audio(channels=self.conf.get_item('client', 'channels'),
                                   rate=self.conf.get_item('client', 'samplerate'),
                                   frames_per_buffer=self.conf.get_item('client', 'frame'),
                                   bit_format=self.conf.get_item('client', 'bit_format'),
                                   input_device=self.conf.get_item('client', 'input_device'),
                                   output_device=self.conf.get_item('client', 'output_device'),
                                   threshold=self._start_threshold,
                                   delay=self.conf.get_item('client', 'delay'), )

            self._connect_flag = True

            self._client_thread = MyThread(self.start_connect, btn)
            self._client_thread.add_msg_signal.connect(self.add_msg)
            self._client_thread.start()

            self._text_thread = MyThread(self.get_server_text)
            self._text_thread.add_msg_signal.connect(self.add_msg)
            self._text_thread.add_statistics_signal.connect(self.set_statistics_info)
            self._text_thread.start()
            # self.client.start_connect(registry=False)

        # DEBUG
        # print(f"Button {btn.objectName()}, clicked!")

    def start_connect(self, btn):
        if self.client.list_addr_active(show=True) is not None:
            btn.change_status_color('online')
            btn.update()
            self._client_thread.add_msg_signal.emit(("enter 'wait' or USER(CHANNEL) NUMBER", True, True, False))
            while self._connect_flag:
                try:
                    text = self.client.text_input.get(timeout=0.5)
                    if text == 'wait':
                        self._client_thread.add_msg_signal.emit(
                            ('start to wait for connecting...', True, True, False))
                        self.client.start_connect(None, True)
                        break
                    else:
                        self.client.text_input.put(text)
                        self._client_thread.add_msg_signal.emit(('start to connect...', True, True, False))
                        self.client.start_connect(True, True)
                        break
                except Exception:
                    pass
        else:
            btn.change_status_color('invisible')
            btn.update()
            self._connect_flag = False

    def get_server_text(self):
        while self._connect_flag:
            try:
                text = self.client.text_output.get(timeout=0.5)
                if text[1] == 'info' or text[1] == 'error':
                    self._text_thread.add_msg_signal.emit(text)
                elif text[1] == 'statistics':
                    self._text_thread.add_statistics_signal.emit(text)
                elif text[1] == 'connect_error':
                    self._text_thread.add_statistics_signal.emit(text)
            except Exception:
                continue

    def add_msg(self, text):
        if text[2]:
            self.chat.send_by_friend('server', text[0], save=True if len(text) < 4 else text[3])

    def set_statistics_info(self, text):
        numbers = re.findall(number_pattern, text[0])
        if len(numbers) != 0:
            self.ui.label_top.setText('D:{}ms J:{}ms C:{}'.format(numbers[0], numbers[1], numbers[3]))
        else:
            self.ui.label_top.setText(text[0])

    def show_context_menu(self, pos):
        # 显示上下文菜单
        button = self.sender()

        # 显示上下文菜单
        self.action_delete.setData(button.objectName())
        self.context_menu.exec(button.mapToGlobal(pos))

    def delete_server(self):
        sender = self.sender()
        if self.conn.delete_server(self.cur_user, sender.data()) == OperationStatus.DELETE_SUCCESS:
            self.setup_servers()
            try:
                if sender.data() == self.chat.cur_server:
                    for chat in reversed(range(self.ui.chat_layout.count())):
                        self.ui.chat_layout.itemAt(chat).widget().deleteLater()
                    self.ui.app_pages.setCurrentWidget(self.ui.home)
            except AttributeError:
                pass

    def delete_history(self):
        if self.conn.delete_history(self.cur_user, self.chat.cur_server) == OperationStatus.DELETE_SUCCESS:
            while self.chat.page.chat_messages_layout.count():
                item = self.chat.page.chat_messages_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.chat.page.chat_messages_layout.removeItem(item)
                    widget.deleteLater()

    # RESIZE EVENT
    # Whenever the window is resized, this event will be triggered
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        ui_functions.UiFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

    def add_dialog(self):
        self.dlg.exec()

    def add_server(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            servername = self.dlg.servername.text()
            address = self.dlg.address.text()
            password = self.dlg.password.text()

            def after_enter():
                if self.conn.add_server(self.cur_user, servername, address, password) == OperationStatus.ADD_SUCCESS:
                    self.dlg.servername.setText('')
                    self.dlg.address.setText('')
                    self.dlg.password.setText('')
                    self.setup_servers()
                    self.dlg.close()
                else:
                    self.dlg.servername.setStyleSheet("#servername:focus { border: 3px solid rgb(255, 0, 127); }")
                    self.dlg.address.setStyleSheet("#address:focus { border: 3px solid rgb(255, 0, 127); }")
                    self.dlg.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                    self.shacke_window()

            if servername != '' and address != '' and password != '':
                try:
                    server, port = address.split(':')
                except Exception:
                    self.dlg.servername.setStyleSheet("#servername:focus { border: 3px solid rgb(255, 0, 127); }")
                    self.dlg.address.setStyleSheet("#address:focus { border: 3px solid rgb(255, 0, 127); }")
                    self.dlg.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                    self.shacke_window()
                else:
                    self.dlg.user_description.setText(f"Add Server Successfully!")
                    self.dlg.user_description.setStyleSheet("#user_description { color: #bdff00 }")
                    self.dlg.servername.setStyleSheet("#servername:focus { border: 3px solid #bdff00; }")
                    self.dlg.address.setStyleSheet("#address:focus { border: 3px solid #bdff00; }")
                    self.dlg.password.setStyleSheet("#password:focus { border: 3px solid #bdff00; }")
                    QTimer.singleShot(1200, lambda: after_enter())
            else:
                self.dlg.servername.setStyleSheet("#servername:focus { border: 3px solid rgb(255, 0, 127); }")
                self.dlg.address.setStyleSheet("#address:focus { border: 3px solid rgb(255, 0, 127); }")
                self.dlg.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                self.shacke_window()

    def shacke_window(self):
        # SHACKE WINDOW
        actual_pos = self.dlg.pos()
        QTimer.singleShot(0, lambda: self.dlg.move(actual_pos.x() + 1, actual_pos.y()))
        QTimer.singleShot(50, lambda: self.dlg.move(actual_pos.x() + -2, actual_pos.y()))
        QTimer.singleShot(100, lambda: self.dlg.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(150, lambda: self.dlg.move(actual_pos.x() + -5, actual_pos.y()))
        QTimer.singleShot(200, lambda: self.dlg.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(250, lambda: self.dlg.move(actual_pos.x() + -2, actual_pos.y()))
        QTimer.singleShot(300, lambda: self.dlg.move(actual_pos.x(), actual_pos.y()))

    def set_dialog(self):
        self.set.setFocus()
        self.set.show()

    def change_mic(self):
        self.mic = not self.mic
        if self.mic:
            self.chat.page.btn_mic_top.setStyleSheet('background-image: url(:/icons_svg/images/icons_svg/mic.svg);')
            self.client.audio.change_mic(self.mic)
        else:
            self.chat.page.btn_mic_top.setStyleSheet(
                'background-image: url(:/icons_svg/images/icons_svg/ic_mic_off.svg);')
            self.client.audio.change_mic(self.mic)

    def change_voice(self):
        self.voice = not self.voice
        if self.voice:
            self.chat.page.btn_voice_top.setStyleSheet('background-image: url(:/icons_svg/images/icons_svg/voice.svg);')
            self.client.audio.change_voice(self.voice)
        else:
            self.chat.page.btn_voice_top.setStyleSheet(
                'background-image: url(:/icons_svg/images/icons_svg/voice_quite.svg);')
            self.client.audio.change_voice(self.voice)

    def change_volume(self):
        slider = self.sender()
        if self.client:
            self.client.audio.change_volume(slider.value())
        else:
            self._start_volume = slider.value()

    def change_threshold(self):
        slider = self.sender()
        if self.client:
            self.client.audio.change_threshold(slider.value() * 800)
        else:
            self._start_threshold = slider.value() * 800

    def test_nat_type(self):
        self.test_dlg.close_app_btn.hide()
        self.test_dlg.show()

        def solve_result(result):
            self.test_dlg.testText.setText('Finished')
            self.test_dlg.resultText.setText(result[0])
            if 'Symmetric' in result[0]:
                self.conf.set_section('client', 'nat', '1')
            else:
                self.conf.set_section('client', 'nat', '0')
            self.test_dlg.close_app_btn.show()

        self._test_thread = MyThread(target=get_net_nat)
        self._test_thread.result_signal.connect(solve_result)
        self._test_thread.start()


# SETTINGS WHEN TO START
# Set the initial class and also additional parameters of the "QApplication" class
# ///////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # APPLICATION
    app = QApplication()
    app.setWindowIcon(QIcon("icon.ico"))
    window = LoginWindow()
    sys.exit(app.exec())
