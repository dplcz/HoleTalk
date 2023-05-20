# -*-coding:utf-8-*-
import signal
import sys

import logging
import time
import socket
import json
import threading
from queue import Queue

from stun.cli import get_net_nat
from audio.controller_sd import AudioController
from utils.TTLDict import TTLDict
from conf.config import Conf

CONE_NAT = 0
SYMMETRIC_NAT_SEQUENCE = 1
SYMMETRIC_NAT_RANDOM = 3

# from audio.controller import AudioController

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class UDPClient:
    _retry_delay_time = 1

    def __init__(self, host, port, max_connections: int = 2, addr_expire_time: float = 20, max_retries: int = 5,
                 queue_max_size=5, head='dplcz', username='visitor', nat_type: int = CONE_NAT, beat_time=5, ui=False,
                 thread_class=threading.Thread):
        self._logger = logging.getLogger()
        signal.signal(signal.SIGINT, self.signal_handler)

        self._host = host
        self._port = port
        self._max_retries = max_retries
        self._addr_expire_time = addr_expire_time
        self._head = head
        self._beat_time = beat_time
        self._beat_flag = True
        self._username = username
        self._thread_class = thread_class

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if 0 <= nat_type <= 2:
            self._nat_type = nat_type
        else:
            self._nat_type = 0
            self._logger.warning('nat_type should among [0,1,2] or use default value 0')
        self._test_server = [{'ip': '124.221.228.222', 'port': 9998}, {'ip': '121.4.36.253', 'port': 9999}]

        self._destination_addr = None
        self._connected_set = set()
        self._connected_addr = TTLDict(ttl_set=self._connected_set, max_broken_length=max_connections)
        self._cur_connections_count = 0

        self._hole_request = TTLDict()

        self._activity_addr = []
        self._recheck_flag = False

        self._stream = None
        self._cur_sec = TTLDict()

        self._queue_max_size = queue_max_size
        self._q_msg = Queue(maxsize=10)
        self._q_clear_times = 5

        self._stop_flag = True
        self._cur_channel = 0
        self._beat = None
        self._recv = None
        self._t_operate = None
        self._event = None

        self.audio = None

        self._ui = ui

        if self._ui:
            self.text_input = Queue()
            self.text_output = Queue()

    def init_audio(self, channels=1, rate=12000, frames_per_buffer=960, bit_format: str = 'int16', threshold=5000,
                   delay=30, input_device=None, output_device=None):
        self.audio = AudioController(channels, rate, frames_per_buffer, bit_format=bit_format, threshold=threshold,
                                     delay=delay, input_device_index=input_device, output_device_index=output_device)

    def _create_request(self, operation, data) -> bytes:
        """
        创建请求体

        :param operation: 操作
        :param data: 数据
        :return:
        """

        return '{}\r\n{}\r\n{}'.format(self._head, operation, data).encode('utf-8')

    def _solve_response(self, body: bytes):
        """
        处理响应的body

        :param body:
        :return:
        """

        try:
            temp = body.decode('utf-8')
            if self._head in temp:
                return temp.split('\r\n')
            return None
        except Exception:
            return None

    def _solve_text(self, text, level='debug', server=True):
        if not self._ui:
            if level == 'debug':
                self._logger.debug(text)
            elif level == 'info' or level == 'statistics' or level == 'connect_error':
                self._logger.info(text)
            elif level == 'error':
                self._logger.error(text)
        else:
            self.text_output.put((text, level, server))

    def _solve_input_text(self, text):
        if self._ui:
            return self.text_input.get()
        return input(text)

    def _registry(self):
        """
        向服务器注册信息

        :return:
        """
        retry_times = 0
        self._sock.settimeout(2)
        while True:
            try:
                retry_times += 1
                self._solve_text('try to register at {} {} --- {} time'.format(self._host, self._port, retry_times),
                                 'info')
                send_data = self._create_request('register', '{} {}'.format(self._nat_type, self._username))
                self._sock.sendto(send_data, (self._host, self._port))
                addr_data, _ = self._sock.recvfrom(1024)
                res_data = self._solve_response(addr_data)
                # self._sock.settimeout(None)
                self._solve_text('register successfully', 'info')
                if res_data is not None and res_data[1] == 'list':
                    return json.loads(res_data[2])
                return None
            except (ConnectionResetError, socket.timeout):
                if retry_times >= self._max_retries:
                    self._solve_text("cant register at %s:%s" % (self._host, self._port), 'error')
                    # self._sock.settimeout(None)
                    return None
                time.sleep(self._retry_delay_time)

    def _ping(self, client_addr=None, wait_response=False, channel=0):
        """
        发出ping命令(对服务器或客户端)

        :param client_addr: 对方客户端地址(为空默认向服务器ping)
        :param wait_response: 是否等待响应
        :param channel: 通话频道
        :return:
        """

        retry_times = 0

        host = self._host
        port = self._port
        if client_addr:
            host = client_addr[0]
            port = int(client_addr[1])
        while True:
            try:
                if retry_times > self._max_retries:
                    return None
                retry_times += 1

                self._solve_text('send ping to {}--- {} time'.format((host, port), retry_times), 'debug')
                send_data = self._create_request('ping', '') if client_addr else self._create_request('ping',
                                                                                                      '{} {} {}'.format(
                                                                                                          self._nat_type,
                                                                                                          channel,
                                                                                                          self._username))

                self._sock.sendto(send_data, (host, port))
                if wait_response:
                    wait_times = 0
                    while wait_times < 8:
                        try:
                            if self._recv:
                                data, addr = self._q_msg.get(timeout=2)
                            else:
                                source, addr = self._sock.recvfrom(1024)
                                data = self._solve_response(source)
                            if data[1] == 'pong':
                                if addr == self._destination_addr:
                                    self._solve_text('get pong from {}'.format(addr), 'debug')
                                    # self._sock.settimeout(None)
                                    return True
                                else:
                                    wait_times += 1
                                    self._q_msg.put((data, addr))
                            else:
                                wait_times += 1
                                self._q_msg.put((data, addr))
                        except Exception:
                            wait_times += 1
                else:
                    # self._sock.settimeout(None)
                    return True
            except (ConnectionResetError, socket.timeout):
                if retry_times >= self._max_retries:
                    self._solve_text("can't connect to %s:%s" % (host, port), 'error')
                    # self._sock.settimeout(None)
                    return None
                time.sleep(self._retry_delay_time)

    def _heart_beat(self, addr: TTLDict = None):
        """
        心跳函数

        :param addr: （暂时不需要）
        :return:
        """
        while self._beat_flag:
            time.sleep(self._beat_time)
            # if addr:
            #     for i in addr.list_set():
            #         if not self._ping(i):
            #             self._solve_text('heart beat error!!','error')
            #             self._stop_flag = True
            #             break
            #         time.sleep(0.1)
            if not self._ping(channel=self._cur_channel if self._cur_connections_count > 0 else 0):
                self._solve_text('heart beat error!!', 'error')
                self._stop_flag = False
                break

    def _init_connect(self, addr):
        """
        初始化连接

        :param addr: 连接对象地址
        :return:
        """
        self._connected_addr.set_expire(addr, self._addr_expire_time, Queue(maxsize=self._queue_max_size))
        self._cur_sec.set_expire(addr, self._addr_expire_time, 0)
        self._destination_addr = None
        self._cur_connections_count += 1
        return True

    def _send_check(self, channel):
        send_data = self._create_request('check', '')
        for _ in range(0, 3):
            self._sock.sendto(send_data, (self._host, self._port))
            time.sleep(0.05)
        self._solve_text('send check to server', 'info')
        self._cur_channel = int(channel)

    def _op_common(self, data):
        """
        处理普通型打洞的请求

        :param data: 命令数据
        :return:
        """
        self._solve_text('receive {} hole request (common)'.format(data[2]), 'info')
        ip, port, channel = data[2].split(' ')
        self._destination_addr = (ip, int(port))
        if self._ping((ip, port)):
            self._send_check(channel)

    def _op_sequence(self, data):
        """
        处理对称型打洞的请求（暂时只支持顺序变换的对称型NAT）

        :param data: 命令数据
        :return:
        """
        self._solve_text('receive {} hole request (sequence)'.format(data[2]), 'info')
        ip, port, channel = data[2].split(' ')
        port = int(port)
        self._destination_addr = (ip, None)
        for i in range(port, port + 50):
            try:
                if self._ping((ip, i)):
                    time.sleep(0.07)
            except OverflowError:
                break
        self._send_check(channel)

    def _op_pong(self, addr):
        """
        处理pong命令

        :param addr: 来源地址
        :return:
        """
        if self._destination_addr:
            if self._destination_addr == addr:
                self._solve_text('get pong from {}'.format(addr), 'debug')
                send_data = self._create_request('pong', '')
                self._sock.sendto(send_data, self._destination_addr)
                return self._init_connect(addr)
            elif self._destination_addr[1] is None and self._destination_addr[0] == addr[0]:
                self._solve_text('get pong from {}'.format(addr), 'debug')
                send_data = self._create_request('pong', '')
                self._destination_addr = addr
                self._sock.sendto(send_data, self._destination_addr)
                return self._init_connect(addr)

    def _op_recheck(self, data):
        """
        处理recheck命令

        :param data: 命令数据
        :return:
        """
        ip, port, channel = data[2].split(' ')
        self._destination_addr = (ip, int(port))
        self._solve_text('recheck ping to {}'.format(self._destination_addr), 'info')
        if self._ping(self._destination_addr, wait_response=True):
            self._recheck_flag = True
            self._cur_channel = int(channel)
            return self._init_connect(self._destination_addr)

    def _op_ping(self, addr):
        """
        处理ping命令

        :param addr: 来源地址
        :return:
        """
        if self._destination_addr:
            send_data = self._create_request('pong', '')
            self._sock.sendto(send_data, addr)
            self._solve_text('send pong to {}'.format(addr), 'debug')
            if self._destination_addr == addr:
                return self._init_connect(addr)
            elif self._destination_addr[1] is None and self._destination_addr[0] == addr[0]:
                return self._init_connect(addr)
        elif addr in self._connected_addr.list_set():
            self._solve_text('received ping from {}'.format(addr), 'info')
            self._connected_addr.set_expire(addr, self._addr_expire_time, Queue(maxsize=self._queue_max_size))
            self._cur_sec.set_expire(addr, self._addr_expire_time, 0)
            return True

    def _operate_command(self):
        """
        处理消息队列线程

        :return:
        """

        double_sequence = False
        while self._stop_flag:
            try:
                data, addr = self._q_msg.get(timeout=1)
            except Exception:
                continue
            if data[1] == 'common' and data[2] not in list(self._hole_request.keys()):
                self._op_common(data)
                self._hole_request.set_expire(data[2], 30, None)
            elif data[1] == 'sequence' and data[2] not in list(self._hole_request.keys()):
                self._op_sequence(data)
                self._hole_request.set_expire(data[2], 30, None)
            elif data[1] == 'sequence2' and data[2] not in list(self._hole_request.keys()):
                self._op_sequence(data)
                self._hole_request.set_expire(data[2], 30, None)
                double_sequence = True
            elif data[1] == 'pong':
                if double_sequence:
                    self._init_connect(addr)
                    double_sequence = False
                self._op_pong(addr)
            elif data[1] == 'recheck':
                self._op_recheck(data)
            elif data[1] == 'ping':
                if double_sequence:
                    self._destination_addr = addr
                    if self._ping(addr, wait_response=True):
                        self._init_connect(addr)
                        double_sequence = False
                self._op_ping(addr)

    def _punch_hole(self, destination=None):
        """
        打洞函数,如果destination为None,则接收用户输入选择要连接的对象

        :param destination: 是否进行主动连接
        :return:
        """
        try:
            if destination is None:
                choose_addr = int(self._solve_input_text('输入连接对象序号'))
                # 告诉服务器将要给 destination 打洞
                destination = self._activity_addr[choose_addr]
                if list(destination.keys())[0] == 'channel':
                    send_data = self._create_request('join', destination['channel'])
                    self._solve_text('report server to join channel {}'.format(destination['channel']), 'debug')
                    self._sock.sendto(send_data, (self._host, self._port))
                    return destination
                else:
                    destination = [destination['ip'], destination['port']]
            self._destination_addr = (destination[0], destination[1])
            if self._cur_channel == 0:
                send_data = self._create_request('hole', '{} {}'.format(destination[0], destination[1]))
            else:
                send_data = self._create_request('channel', '{} {}\r\n{}'.format(destination[0], destination[1],
                                                                                 self._cur_channel))
            self._sock.sendto(send_data, (self._host, self._port))
            self._solve_text('report server to hole with {}'.format(destination), 'debug')
            self._sock.settimeout(5)
            return destination
        except (IndexError, ValueError):
            self._solve_text('recheck your choice index of addr', 'error')
            return None

    def _recv_data(self):
        """
        接收数据的线程,音频数据直接存储在用户字典中,操作数据放入消息队列中,在另一个线程中等待处理

        :return:
        """
        temp_times = 0
        reconnect_times = 0
        recv_times = 0
        delay = []
        jitter = []
        sec_error_times = 0
        loss_packet = 0

        report_flag = True

        change_timeout_flag = False
        change_value = 2
        self._sock.settimeout(change_value)
        while self._stop_flag:
            if change_timeout_flag:
                change_value = 5 if change_value == 2 else 2
                self._sock.settimeout(change_value)
                change_timeout_flag = False
            try:
                source_data, addr = self._sock.recvfrom(1400)
                data = self._solve_response(source_data)
                if data:
                    if self._q_msg.full():
                        temp_times += 1
                        if temp_times >= self._q_clear_times:
                            self._q_msg.queue.clear()
                            self._solve_text('clear msg queue', 'debug')
                    self._q_msg.put((data, addr))
                elif self._connected_addr[addr].full():
                    temp_times += 1
                    if temp_times >= self._q_clear_times:
                        self._connected_addr[addr].queue.clear()
                        self._solve_text('clear sound queue', 'debug')
                    continue
                else:
                    self._connected_addr.set_expire(addr, self._addr_expire_time, Queue(maxsize=self._queue_max_size))
                    self._cur_sec.set_expire(addr, self._addr_expire_time, 0)
                    cur_sec, send_time, source_data = int.from_bytes(source_data[0:2], 'big'), int.from_bytes(
                        source_data[2:8], 'big'), source_data[8:]

                    if sec_error_times >= 20:
                        self._cur_sec[addr] = cur_sec
                        sec_error_times = 0
                    if cur_sec < self._cur_sec[addr]:
                        sec_error_times += 1
                        continue
                    elif cur_sec == 999:
                        self._cur_sec[addr] = 0
                    else:
                        temp = self._cur_sec[addr]
                        if temp + 1 != cur_sec:
                            loss_packet += cur_sec - temp
                        self._cur_sec[addr] = cur_sec
                        sec_error_times = 0

                    recv_times += 1
                    receive_time = int(time.time() * 1000)
                    delay.append(abs(receive_time - send_time))
                    jitter.append(max(delay) - min(delay))
                    if recv_times % (100 * self._cur_connections_count) == 0 and cur_sec:
                        temp_length = len(self._connected_addr.list_set())
                        if temp_length < self._cur_connections_count:
                            self._cur_connections_count = temp_length
                        self._solve_text(
                            'avg_delay: {}ms\t--jitter: {}ms\t--connections: {}\t--channel: {}\t--loss: {}'.format(
                                sum(delay) // len(delay),
                                sum(jitter) // len(jitter),
                                self._cur_connections_count, self._cur_channel, loss_packet), 'statistics')
                        loss_packet = 0
                        delay.clear()
                        jitter.clear()
                    self._connected_addr[addr].put(source_data)
            except ConnectionResetError:
                temp_set = self._connected_addr.list_set()
                if len(temp_set) < self._cur_connections_count or 1 <= reconnect_times < 5:
                    if reconnect_times == 0:
                        self._solve_text('connection is break!!', 'error')
                        self._solve_text('disconnection', 'connect_error')
                        self._cur_connections_count = len(temp_set)
                if len(temp_set) == 0:
                    self._cur_channel = 0

            except socket.timeout:
                if report_flag:
                    self._solve_text('timeout', 'error')
                    self._solve_text('timeout', 'connect_error')
                    self._cur_channel = 0
                    report_flag = False

                # TODO change channel
                # if self._reconnect_flag:
                #     broken_addr = self._connected_addr.get_broken_connection()
                #     reconnect_times += 1
                #     self._solve_text('try to reconnect to {} --- {} time'.format(broken_addr, reconnect_times),'info')
                #     self._punch_hole(broken_addr)
                #     change_value = 5
            except KeyError:
                pass
            else:
                if change_value == 5:
                    change_timeout_flag = True
                    reconnect_times = 0
                    report_flag = True
                # self._sock.close()
                # self._stop_flag = True

    def test_nat_type(self):
        """
        测试NAT类型

        :return:
        """
        self._solve_text('start test', 'debug')
        nat_type, external_ip, external_port = get_net_nat()
        self._logger.info(
            'finish test: NAT Type: {} External IP: {} External Port: {}'.format(nat_type, external_ip, external_port))
        if 'Symmetric' in nat_type:

            port_test = []
            for server in self._test_server:
                self._sock.sendto(b'', (server['ip'], server['port']))
                data, _ = self._sock.recvfrom(1024)
                port_test.append(int(data.decode('utf-8').split(',')[-1].strip(') ')))
            if (max(port_test) - min(port_test)) < len(port_test) * 5:
                self._nat_type = 1
                self._solve_text('sequence Symmetric', 'nat')
                return 1
            else:
                self._nat_type = 3
                self._solve_text('random Symmetric(not supported)', 'nat')
                raise KeyboardInterrupt
        else:
            self._nat_type = 0
            self._solve_text('Cone', 'nat')
            return 0

    def list_addr_active(self, show=True, registry=True):
        """
        向服务器注册并返回当前在线客户端

        :param registry: 是否在服务器注册
        :param show: 是否命令行输出
        :return:
        """
        if registry:
            self._solve_text('list active addresses', 'debug')
            addr_active = self._registry()
            if show and addr_active is not None:
                for i in range(len(addr_active)):
                    keys, values = list(addr_active[i].keys()), list(addr_active[i].values())
                    if len(keys) == 2:
                        self._solve_text(
                            '{} --- {}:{} {}:{}'.format(i, keys[0], values[0], keys[1], values[1]), 'info')
                    else:
                        self._solve_text(
                            '{} --- {}:{} {}:{} --- {}'.format(i, keys[0], values[0], keys[1], values[1], values[2]),
                            'info')
            self._activity_addr = addr_active
            return addr_active
        else:
            return True

    def start_connect(self, choose_addr=None, registry=True):
        """
        开始连接

        :param registry: 是否注册服务器
        :param choose_addr: 是否主动选择连接
        :return:
        """
        if self.list_addr_active(show=True, registry=registry) is not None:

            cur_destination = None

            if not self._beat:
                self._beat_flag = True
                self._beat = self._thread_class(target=self._heart_beat)
                self._beat.start()
            if choose_addr:
                while True:
                    cur_destination = self._punch_hole()
                    if cur_destination:
                        self._sock.settimeout(7)
                        break
            else:
                self._sock.settimeout(1)
            sequence = False
            double_sequence = False
            while self._stop_flag:
                try:
                    source_data, addr = self._sock.recvfrom(1024)
                    data = self._solve_response(source_data)
                    if data[1] == 'common' and data[2] not in list(self._hole_request.keys()):
                        self._op_common(data)
                        self._hole_request.set_expire(data[2], 30, None)
                        self._recheck_flag = True
                    elif data[1] == 'sequence' and data[2] not in list(self._hole_request.keys()):
                        self._op_sequence(data)
                        self._hole_request.set_expire(data[2], 30, None)
                        self._recheck_flag = True
                        sequence = True
                    elif data[1] == 'sequence2' and data[2] not in list(self._hole_request.keys()):
                        self._op_sequence(data)
                        self._hole_request.set_expire(data[2], 30, None)
                        sequence = True
                        double_sequence = True
                    elif data[1] == 'pong':
                        if double_sequence:
                            self._init_connect(addr)
                            break
                        if not sequence:
                            if self._op_pong(addr):
                                break
                    elif data[1] == 'recheck':
                        sequence = True
                        if self._op_recheck(data):
                            break
                    elif data[1] == 'ping':
                        if double_sequence:
                            self._destination_addr = addr
                            if self._ping(addr, wait_response=True):
                                self._init_connect(addr)
                                break
                        if self._recheck_flag:
                            self._solve_text(addr, 'info')
                            if self._op_ping(addr):
                                break
                except ConnectionResetError:
                    pass
                except socket.timeout as e:
                    if cur_destination:
                        self._punch_hole(cur_destination)
                        cur_destination = None
                    else:
                        continue
                except KeyboardInterrupt:
                    self._beat_flag = False
                    self._beat.join()
                    return False
            if self._stop_flag:
                self._sock.settimeout(None)
                self._solve_text('have fun', 'info')

                self._recv = self._thread_class(target=self._recv_data)
                self._recv.start()

                self._t_operate = self._thread_class(target=self._operate_command)
                self._t_operate.start()

                self._event = threading.Event()
                self.audio.init_stream(self._sock, self._head, self._connected_addr, 1, self._event,
                                       noise=False, stationary=False, logger=self._logger)

    def signal_handler(self, temp_signal, frame):
        self._beat_flag = False
        self._beat.join()
        sys.exit(0)

    def handle_stop_all(self):
        self._stop_flag = False
        self._beat_flag = False
        if self._recv:
            self._recv.join()
        if self._t_operate:
            self._t_operate.join()
        if self._beat:
            self._beat.join()
        if self._event:
            self._event.set()


if __name__ == '__main__':
    config = Conf()
    client = UDPClient(config.get_item('server', 'host'),
                       config.get_item('server', 'port'),
                       config.get_item('server', 'beat_time'),
                       head=config.get_item('server', 'head'),
                       username=config.get_item('client', 'username'),
                       nat_type=config.get_item('client', 'nat'),
                       queue_max_size=5)
    client.init_audio(channels=config.get_item('client', 'channels'),
                      rate=config.get_item('client', 'samplerate'),
                      frames_per_buffer=config.get_item('client', 'frame'),
                      bit_format=config.get_item('client', 'bit_format'),
                      input_device=config.get_item('client', 'input_device'),
                      output_device=config.get_item('client', 'output_device'),
                      threshold=config.get_item('client', 'threshold'),
                      delay=config.get_item('client', 'delay'), )
    while True:
        print('1.测试网络NAT    2.等待连接     3.连接')
        choose = input('输入指令')
        if choose == '1':
            config.set_section('client', 'nat', str(client.test_nat_type()))
        elif choose == '2':
            if client.start_connect():
                break
        elif choose == '3':
            if client.start_connect(True):
                break
