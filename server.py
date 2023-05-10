# -*-coding:utf-8-*-
import queue
import socket
import logging
import json
import threading
import time
from queue import Queue

from utils.TTLDict import TTLDict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class UDPServer:
    def __init__(self, host='127.0.0.1', port=9999, max_connections=2, max_channel=2, addr_expire_time=30,
                 head='dplcz'):
        """
        初始化服务器

        :param host: 绑定ip
        :param port: 绑定端口
        :param max_connections: 最大连接数
        :param max_channel: 最大频道
        :param addr_expire_time: 地址过期时间
        :param head: 请求或响应头
        """

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._head = head

        self._sock.bind((host, port))
        self._q_msg = Queue(maxsize=10)
        self._q_check = Queue(maxsize=5)

        self._address_set = set()
        self._address_dict = TTLDict(self._address_set)
        self._address_checked = TTLDict()

        self._channel_dict = {}
        self._max_channel = max_channel + 1
        for i in range(1, max_channel + 1):
            self._channel_dict[i] = TTLDict()

        self._address_expire_time = addr_expire_time

        self._logger = logging.getLogger()

    def _create_response(self, operation: str, data: str) -> bytes:
        """
        创建响应

        :param operation: 操作
        :param data: 数据
        :return:
        """
        return '{}\r\n{}\r\n{}'.format(self._head, operation, data).encode('utf-8')

    def _solve_request(self, body: bytes):
        """
        处理请求

        :param body: 请求body
        :return:
        """
        try:
            temp = body.decode('utf-8')
            if self._head in temp:
                return temp.split('\r\n')
            return None
        except Exception:
            return None

    def _sock_send(self, operation: str, data: str, addr):
        """
        发送数据

        :param operation: 操作
        :param data: 数据
        :param addr: 目的地址
        :return:
        """
        send_data = self._create_response(operation, data)
        self._sock.sendto(send_data, addr)

    def _get_free_channel(self):
        """
        获取当前的空频道

        :return:
        """

        for i in range(1, self._max_channel):
            if len(self._channel_dict[i].items()) == 0:
                return i

    def _op_ping(self, data, addr):
        """
        处理ping命令

        :param data: 数据
        :param addr: 来源地
        :return:
        """
        self._logger.debug('ping from {}:{}'.format(addr[0], addr[1]))
        nat, channel, username = data.split(' ')
        channel = int(channel)
        if channel > 0:
            self._channel_dict[channel].set_expire(addr, self._address_expire_time, [int(nat), username])
            if addr in self._address_dict.list_set():
                self._address_dict.pop(addr)
        else:
            self._address_dict.set_expire(addr, self._address_expire_time, [int(nat), username])

    def _op_hole(self, data, addr, channel=0):
        """
        处理打洞请求

        :param data: 接收数据
        :param addr: 来源地
        :param channel: 加入频道(为0则程序分配)
        :return:
        """

        ip, port = data.split(' ')
        destination = (ip, int(port))
        if channel == 0:
            # for i in range(1, self._max_channel):
            #     if len(self._channel_dict[i].items()) == 0:
            #         channel = i
            #         break
            nat_flag = self._address_dict[destination][0] + self._address_dict[addr][0]
        else:
            try:
                nat_flag = self._address_dict[addr][0] + self._channel_dict[channel][destination][0]
            except KeyError:
                nat_flag = self._channel_dict[channel][addr][0] + self._channel_dict[channel][destination][0]

        if nat_flag == 0:
            self._logger.debug(
                'trying udp hole punching between {} --- {} (common)'.format(addr, destination))
            if channel == 0:
                channel = self._get_free_channel()
            self._sock_send('common', '{} {} {}'.format(addr[0], addr[1], channel), destination)
        elif nat_flag == 1:
            self._logger.debug(
                'trying udp hole punching between {} --- {} (sequence)'.format(addr, destination))
            if channel == 0:
                if self._address_dict[addr][0] < self._address_dict[destination][0]:
                    destination, addr = addr, destination
                channel = self._get_free_channel()
            else:
                try:
                    if self._address_dict[addr][0] < self._channel_dict[channel][destination][0]:
                        destination, addr = addr, destination
                except KeyError:
                    if self._channel_dict[channel][addr][0] < self._channel_dict[channel][destination][0]:
                        destination, addr = addr, destination

            send_data = self._create_response('sequence', '{} {} {}'.format(addr[0], addr[1], channel))
            self._sock.sendto(send_data, destination)
            self._sock_send('sequence', '{} {} {}'.format(addr[0], addr[1], channel), destination)
        else:
            self._logger.debug(
                'trying udp hole punching between {} --- {} (double sequence)'.format(addr, destination))
            if channel == 0:
                channel = self._get_free_channel()
            self._sock_send('sequence2', '{} {} {}'.format(addr[0], addr[1], channel), destination)
        wait_times = 0
        while wait_times < 10:
            try:
                source_data, new_addr = self._q_check.get(timeout=10)
                # self._logger.info(source_data)
                data = self._solve_request(source_data)
                if nat_flag <= 1:
                    if data[1] == 'check' and new_addr == destination:
                        self._address_checked.set_expire(new_addr, 10, None)
                        self._logger.debug('get check from {}'.format(new_addr))
                        self._sock_send('recheck', '{} {} {}'.format(destination[0],
                                                                     destination[1],
                                                                     channel), addr)
                        self._logger.debug('send recheck to {}'.format(addr))
                        break
                    else:
                        self._q_msg.put((source_data, addr), block=False)
                        wait_times += 1
                else:
                    if data[1] == 'check' and new_addr == destination:
                        self._address_checked.set_expire(new_addr, 10, None)
                        self._logger.debug('get check from {} first'.format(new_addr))
                        self._logger.debug('send hole request to {}'.format(addr))
                        self._sock_send('sequence', '{} {} {}'.format(destination[0], destination[1], channel),
                                        addr)
                        break
                    else:
                        self._q_msg.put((source_data, addr), block=False)
                        wait_times += 1

            except queue.Empty:
                self._logger.debug("can't receive check msg")
                break
            except Exception:
                pass

    def _op_join(self, addr, channel):
        """
        处理加入频道操作

        :param addr: 来源地址
        :param channel: 频道号
        :return:
        """

        self._logger.debug('get join {} channel request from {}'.format(channel, addr))
        temp_keys = list(self._channel_dict[channel].keys())
        for i in range(len(temp_keys)):
            self._op_hole('{} {}'.format(temp_keys[i][0], temp_keys[i][1]), (addr[0], addr[1]), channel)
            time.sleep(4)
        # self._sock_send('join', json.dumps(temp_keys), addr)

    def start(self):
        """
        开始监听

        :return:
        """

        self._logger.info('start listen')
        self._sock.settimeout(1)

        while True:
            try:
                if self._q_msg.empty():
                    source_data, addr = self._sock.recvfrom(1024)
                else:
                    source_data, addr = self._q_msg.get(block=False)
                data = self._solve_request(source_data)
                if data:
                    # 心跳检测
                    if data[1] == 'ping':
                        self._op_ping(data[2], addr)
                    # 服务器注册
                    elif data[1] == 'register':
                        self._logger.debug('registered {}:{} nat--username:{}'.format(addr[0], addr[1], data[2]))
                        nat_type, username = data[2].split(' ')
                        self._address_dict.set_expire(addr, self._address_expire_time, [int(nat_type), username])
                        temp = []
                        for i in self._channel_dict.items():
                            temp_length = len(i[1].items())
                            if temp_length > 1:
                                temp.append({'channel': i[0], 'count': temp_length})
                        for i in self._address_dict.list_set():
                            if i != addr:
                                temp.append({'ip': i[0], 'port': i[1], 'username': self._address_dict[addr][1]})
                        send_data = self._create_response('list', json.dumps(temp))
                        self._sock.sendto(send_data, addr)
                    # 打洞请求
                    elif data[1] == 'hole':
                        t_hole = threading.Thread(target=self._op_hole, args=(data[2], addr))
                        t_hole.start()
                    elif data[1] == 'channel':
                        self._op_hole(data[2], addr, int(data[3]))
                    elif data[1] == 'join':
                        channel = int(data[2])
                        t_join = threading.Thread(target=self._op_join, args=(addr, channel))
                        t_join.start()
                    elif data[1] == 'check':
                        checked_addr = list(self._address_checked.keys())
                        if addr not in checked_addr:
                            self._q_check.put((source_data, addr), block=False)

            except socket.timeout:
                pass
            except Exception as e:
                self._logger.error(e)


if __name__ == '__main__':
    server = UDPServer('0.0.0.0', addr_expire_time=15)
    server.start()
