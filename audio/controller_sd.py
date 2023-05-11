# -*-coding:utf-8-*-
import sys
import wave
import logging
from queue import Queue
import time as tm

# import noisereduce as nr
import numpy as np
from scipy import fftpack
# from scipy.io import wavfile
import sounddevice as sd

# from tqdm import tqdm
import opuslib


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class AudioController:
    _bit_dict = {'int32': 4, 'int16': 2, 'int8': 1, 'float32': 4}

    @classmethod
    def device_info(cls, kind):
        """
        返回输入设备信息

        :param kind: 输入(input) 或 输出(output)
        :return:
        """

        device_list = []
        for device_id, info in enumerate(sd.query_devices()):
            if not kind or info['max_' + kind + '_channels'] > 0:
                hostapi_info = sd.query_hostapis(info['hostapi'])
                if hostapi_info['name'] == 'MME':
                    device_list.append((device_id, info['name'], hostapi_info['name']))
        return device_list

    def __init__(self, channels: int, rate: int, frames_per_buffer: int = 960, input_device_index=None,
                 output_device_index=None, bit_format: str = 'int16', threshold=0, delay=30, opus_rate=None):
        """

        :param channels: 通道
        :param rate: 采样率
        :param frames_per_buffer: 每个缓存区块大小
        :param input_device_index: 输入设备
        :param output_device_index: 输出设备
        :param bit_format: 采样大小(float32, int32, int16, int8)
        :param threshold: 麦克风阈值（为0关闭，streaming为False时无效）
        :param delay: 延迟静音（帧）
        :param opus_rate: opus编码采样率（默认跟rate相关）
        :param sock: udp socket
        """

        self._channels = channels
        self._rate = rate
        self._chunk_size = frames_per_buffer
        self._bit_format = bit_format
        self._input_device_index = input_device_index
        self._output_device_index = output_device_index
        self._threshold = threshold
        self._delay = delay

        self._sample_size = self._bit_dict[bit_format]
        self._frames_per_second = 1

        self._frames = []
        self._stream_file = None
        self._record_flag = True
        self._input_active = False
        self._zero_encoded = None

        self._input_delay_counter = delay

        self._encoder = None
        self._decoder = None

        self._noise = False
        self._noise_sample = None

        self._dtype_dict = {'int16': np.int16, 'int8': np.int8, 'int32': np.int32,
                            'float32': np.float32}
        self._dtype = self._dtype_dict[bit_format]

        self._stationary = False
        self._prop_decrease = 1

        if opus_rate not in [8000, 12000, 16000, 24000, 48000] and opus_rate is not None:
            raise ValueError('opus_rate must be in [8000, 12000, 16000, 24000, 48000]')
        self._opus_rate = opus_rate if opus_rate else self._get_opus_rate()
        self._n_frames = channels * self._sample_size * frames_per_buffer

        self.stream = None
        self._header = 'dplcz'
        self._sock = None
        self._destination_addr = None
        self._zip_frames = None
        self._current_seq = 0
        self._output_queue = None

        self._mic_flag = True

        self._logger = logging.getLogger(__name__)

    def _judge_voice(self, indata: np.ndarray) -> bool:
        """
        麦克风检测(快速傅里叶变换)

        :param indata: 输入音频数据
        :return:
        """
        fft_temp_data = fftpack.fft(indata, indata.size, overwrite_x=True)
        fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
        if sum(fft_data) // len(fft_data) > self._threshold:
            self._input_delay_counter = 0
            if not self._input_active:
                self._change_input_active()
        elif self._input_delay_counter >= self._delay:
            if self._input_active:
                self._change_input_active()
            return False
        else:
            self._input_delay_counter += 1
        return True

    # def _data_reduce_noise(self, in_data, stationary, prop_decrease=1,
    #                        n_fft=512, n_jobs=1) -> np.ndarray:
    #     """
    #     音频降噪
    #
    #     :param in_data: 要降噪的数据
    #     :param stationary: 是否稳态降噪
    #     :param prop_decrease: 降噪率
    #     :param n_fft: fft滑动窗口（语音使用512最优）
    #     :param n_jobs: cpu限制（-1为全部）
    #     :return: 降噪后的数据
    #     """
    #     if len(in_data) > 1:
    #         in_data = np.concatenate(in_data, axis=None).flatten()
    #     # in_data = np.frombuffer(data, dtype=np.int16).flatten()
    #     output = nr.reduce_noise(y=in_data, sr=self._rate, stationary=stationary, y_noise=self._noise_sample,
    #                              prop_decrease=prop_decrease, n_fft=n_fft, n_jobs=n_jobs)
    #     return output

    def _opus_encode(self, data) -> bytes:
        """
        opus编码

        :param data:
        :return:
        """
        # TODO 方案一 分段编码
        enc_data = b''
        for i in range(len(data) // self._n_frames):
            enc_data += (self._encoder.encode(data[i * self._n_frames:(i + 1) * self._n_frames],
                                              self._chunk_size) + '{}'.format(self._header).encode('utf-8'))
        return enc_data

    def _opus_decode(self, data, save=False, concat=False):
        """
        opus解码

        :param data:
        :return:
        """
        if save:

            try:
                if concat:
                    temp = []
                    for frame in data:
                        temp.append(self._decoder.decode(frame, self._chunk_size))
                    if not self._output_queue.full():
                        self._output_queue.put(self._concat_frames(temp[0], temp[1]))
                else:
                    if self._header.encode('utf-8') in data:
                        data = data.split('{}'.format(self._header).encode('utf-8'))
                        for i in data:
                            dec_data = self._decoder.decode(i, self._chunk_size)
                            if not self._output_queue.full():
                                self._output_queue.put(dec_data)
                    else:
                        dec_data = self._decoder.decode(data, self._chunk_size)
                        if not self._output_queue.full():
                            self._output_queue.put(dec_data)
            except opuslib.exceptions.OpusError:
                pass

        else:
            dec_data = self._decoder.decode(data, self._chunk_size)
            return dec_data

    def _concat_frames(self, frame1, frame2):
        if len(frame1) == 0 and len(frame2) == 0:
            return b'\x00' * self._chunk_size
        f1_wave_data = np.frombuffer(frame1, dtype=self._dtype)
        f2_wave_data = np.frombuffer(frame2, dtype=self._dtype)

        if len(frame1) > len(frame2):
            length = len(frame1) - len(frame2)
            temp_array = np.zeros(length, dtype=self._dtype)
            rf1_wave_data = np.concatenate((f1_wave_data, temp_array))
            rf2_wave_data = f2_wave_data
        elif len(frame1) < len(frame2):
            length = len(frame2) - len(frame1)
            temp_array = np.zeros(length, dtype=self._dtype)
            rf2_wave_data = np.concatenate((f2_wave_data, temp_array))
            rf1_wave_data = f1_wave_data
        else:
            rf1_wave_data = f1_wave_data
            rf2_wave_data = f2_wave_data
        new_wave_data = rf1_wave_data + rf2_wave_data
        new_wave = new_wave_data.tobytes()
        return new_wave

    def _change_input_active(self):
        """
        修改麦克风输入状态

        :return:
        """
        self._input_active = not self._input_active
        if self._input_active:
            # self._logger.info('开始收音')
            pass
        else:
            pass
            # self._logger.info('关闭收音')

    def _get_opus_rate(self) -> int:
        """
        获取最匹配的编码采样率

        :return:
        """
        fs = [8000, 12000, 16000, 24000, 48000]
        fs_index = 4
        temp_min = 999999
        for i in range(len(fs)):
            temp = abs(self._rate - fs[i])
            fs_index = i if temp < temp_min else fs_index
            temp_min = temp if temp < temp_min else temp_min

        return fs[fs_index]

    def _stream_send(self, encode_data):
        timestamp = int(tm.time() * 1000).to_bytes(6, 'big')
        cur_seq = self._current_seq.to_bytes(2, 'big')
        encode_data = cur_seq + timestamp + encode_data
        addr_temp = self._destination_addr.list_set()
        try:
            if len(addr_temp) > 0:
                for addr in addr_temp:
                    self._logger.debug(len(encode_data))
                    self._sock.sendto(encode_data, addr)
                if self._current_seq == 999:
                    self._current_seq = 0
                self._current_seq += 1
        except OSError:
            self._logger.error('end stream')
            raise sd.CallbackStop

    def _stream_callback(self, indata, outdata, frames, time, status):
        array = False
        if isinstance(indata, np.ndarray):
            in_data = indata.flatten()
            array = True
        else:
            in_data = indata[:]
        try:
            if self._mic_flag:
                if self._threshold > 0:
                    if self._judge_voice(in_data):
                        pass
                    else:
                        in_data[:] = 0
            else:
                in_data[:] = 0
            # if self._noise:
            #     if self._zip_frames >= 1:
            #         self._frames.append(in_data)
            #         if len(self._frames) == self._zip_frames:
            #             in_data = self._data_reduce_noise(self._frames, self._stationary, self._prop_decrease,
            #                                               n_fft=512)
            #             in_data = in_data.tobytes()
            #             enc_data = self._opus_encode(in_data)
            #             self._stream_send(enc_data)
            #             self._frames.clear()
            #     else:
            #         in_data = self._data_reduce_noise(in_data, self._stationary, self._prop_decrease, n_fft=512)
            #         in_data = in_data.tobytes()
            #         enc_data = self._opus_encode(in_data)
            #         self._stream_send(enc_data)
            # else:
            #     if array:
            #         in_data = in_data.tobytes()
            #     enc_data = self._encoder.encode(in_data, self._chunk_size)
            #     self._stream_send(enc_data)
            if array:
                in_data = in_data.tobytes()
            enc_data = self._encoder.encode(in_data, self._chunk_size)
            self._stream_send(enc_data)
        except ConnectionResetError:
            # raise sd.CallbackStop()
            pass

        temp = []
        destination_addr = self._destination_addr.items()
        for addr in destination_addr:
            try:
                temp.append(addr[1].get(block=False))
            except Exception as e:
                continue
        if len(temp) == 2:
            self._opus_decode(temp, save=True, concat=True)
        elif len(temp) == 1:
            self._opus_decode(temp[0], save=True, concat=False)
        if not self._output_queue.empty():
            if array:
                temp = np.frombuffer(self._output_queue.get(),
                                     dtype=self._dtype).reshape(
                    (self._chunk_size, self._channels))
                outdata[:] = temp
            else:
                outdata[:] = self._output_queue.get()
        else:
            if array:
                outdata.fill(0)
            else:
                outdata[:] = b'\x00' * self._n_frames

    # def _record_callback(self, indata, frames, time, status):
    #     # 检测麦克风音量大小
    #     if isinstance(indata, np.ndarray):
    #         in_data = indata.flatten()
    #     else:
    #         in_data = indata[:]
    #     if self._threshold > 0:
    #         if self._judge_voice(in_data):
    #             if self._encoder:
    #                 self._stream_file.write(self._zero_encoded)
    #             else:
    #                 self._stream_file.writeframes(b'\x00' * self._n_frames)
    #         else:
    #             return
    #     if self._noise:
    #         self._frames.append(in_data)
    #         if len(self._frames) == self._frames_per_second:
    #             in_data = self._data_reduce_noise(self._frames, self._stationary, self._prop_decrease, n_fft=1024)
    #             in_data = in_data.tobytes()
    #             self._frames.clear()
    #         else:
    #             return
    #     if self._encoder:
    #         in_data = self._opus_encode(in_data)
    #         self._stream_file.write(in_data)
    #     else:
    #         self._stream_file.writeframes(in_data)
    #     if not self._record_flag:
    #         raise sd.CallbackStop()

    # def play_file(self, filename, opus=False):
    #     """
    #     播放文件
    #
    #     :param filename: 文件名
    #     :param opus: 是否为opus编码
    #     :return:
    #     """
    #     args = {'samplerate': self._rate, 'blocksize': self._chunk_size, 'channels': self._channels,
    #             'dtype': self._bit_format, 'device': self._output_device_index}
    #
    #     if opus and self._decoder is None:
    #         self._decoder = opuslib.Decoder(self._opus_rate, self._channels)
    #
    #     with open(filename, 'rb') if opus else wave.open(filename, 'rb') as wf:
    #         self.stream = sd.RawOutputStream(**args)
    #         self.stream.start()
    #         if opus:
    #             data = wf.read().split(b'dplcz')
    #             for i in data:
    #                 dec_data = self._opus_decode(i)
    #                 self.stream.write(dec_data)
    #         else:
    #             while True:
    #                 data = wf.readframes(self._chunk_size)
    #                 if len(data) == 0:
    #                     break
    #                 self.stream.write(data)
    #         self.stream.stop()

    # def record_to_file(self, filename, seconds=None, successive=False, noise=False, prop_decrease=1, stationary=False,
    #                    noise_samples='noise.wav', opus=False):
    #     """
    #     录音到wav文件
    #
    #     :param filename: 文件名
    #     :param seconds: (当successive为False生效)录音时间（秒）
    #     :param successive: 是否持续录音
    #     :param noise: 是否降噪
    #     :param prop_decrease: 降噪比例，默认为1(100%)
    #     :param stationary: （当noise为True时生效）是否稳态降噪
    #     :param noise_samples: (当stationary为True时生效)噪音样本，默认为noise.wav(电流噪音)
    #     :param opus: 是否进行编码
    #     :return:
    #     """
    #     args = {'samplerate': self._rate, 'blocksize': self._chunk_size, 'channels': self._channels,
    #             'dtype': self._bit_format, 'device': self._input_device_index}
    #
    #     # 初始化降噪
    #     if noise:
    #         if stationary:
    #             self._stationary = True
    #             _, noise_sample = wavfile.read(noise_samples)
    #             self._noise_sample = np.frombuffer(noise_sample, dtype=self._dtype).flatten()
    #         self._noise = True
    #         self._prop_decrease = prop_decrease
    #     # 初始化opus编码器
    #     if opus and self._encoder is None:
    #         self._encoder = opuslib.Encoder(self._opus_rate, self._channels, 'audio')
    #         self._zero_encoded = self._opus_encode(b'\x00' * self._n_frames)
    #     if successive:
    #         self._logger.info('start record')
    #         self._logger.info('press enter to stop')
    #         with open('{}.opus'.format(filename), 'wb') if opus else wave.open('{}.wav'.format(filename),
    #                                                                            'wb') as self._stream_file:
    #             if not opus:
    #                 self._stream_file.setnchannels(self._channels)
    #                 self._stream_file.setsampwidth(self._bit_dict[self._bit_format])
    #                 self._stream_file.setframerate(self._rate)
    #
    #             args['callback'] = self._record_callback
    #             if self._threshold > 0 or noise:
    #                 with sd.InputStream(**args) as self.stream:
    #                     sys.stdin.readline()
    #             else:
    #                 with sd.RawInputStream(**args) as self.stream:
    #                     sys.stdin.readline()
    #             self._record_flag = False
    #         self._logger.info('finish record')
    #     elif seconds:
    #         with open('{}.opus'.format(filename), 'wb') if opus else wave.open('{}.wav'.format(filename),
    #                                                                            'wb') as wf:
    #             if self._threshold > 0 or noise:
    #                 self.stream = sd.InputStream(**args)
    #             else:
    #                 self.stream = sd.RawInputStream(**args)
    #             self._logger.info('start record')
    #             self.stream.start()
    #             with tqdm(total=seconds) as bar:
    #                 frame_noisy = []
    #                 for i in range(0, self._frames_per_second * (seconds + 1)):
    #                     if i % self._frames_per_second == 0 and i != 0:
    #                         bar.update()
    #                         if noise:
    #                             temp_frame = self._data_reduce_noise(frame_noisy, stationary,
    #                                                                  prop_decrease, n_fft=1024).tobytes()
    #                             frame_noisy = []
    #                     elif noise:
    #                         frame_noisy.append(self.stream.read(self._chunk_size)[0])
    #                         continue
    #                     else:
    #                         temp_frame = self.stream.read(self._chunk_size)[0]
    #                     if self._encoder:
    #                         temp_frame = self._opus_encode(temp_frame)
    #
    #                     self._frames.append(temp_frame)
    #                 self.stream.stop()
    #             if opus:
    #                 wf.write(b''.join(self._frames))
    #             else:
    #                 wf.setnchannels(self._channels)
    #                 wf.setsampwidth(self._bit_dict[self._bit_format])
    #                 wf.setframerate(self._rate)
    #                 wf.writeframes(b''.join(self._frames))
    #         self._logger.info('finish record')

    def init_stream(self, sock, header, destination, zip_frames: int, event, noise=False, stationary=False,
                    noise_samples='noise.wav', logger=None):
        """
        初始化输入输出流

        :param sock: 传递udp套接字对象
        :param header: 协议头
        :param destination: 目的地址
        :param zip_frames: 压缩帧
        :param event: 线程事件对象
        :param noise: 是否降噪
        :param stationary: 是否稳态降噪
        :param noise_samples: 噪音样本（stationary为True时生效）
        :param logger: 日志对象
        :return:
        """

        self._sock = sock
        self._header = header
        self._destination_addr = destination
        self._zip_frames = zip_frames
        self._output_queue = Queue(maxsize=zip_frames * 2)
        self._noise = noise
        # if stationary:
        #     self._stationary = True
        #     _, noise_sample = wavfile.read(noise_samples)
        #     self._noise_sample = np.frombuffer(noise_sample, dtype=self._dtype).flatten()

        self._encoder = opuslib.Encoder(self._opus_rate, self._channels, 'voip')
        self._decoder = opuslib.Decoder(self._opus_rate, self._channels)

        if logger:
            self._logger = logger
        args = {'samplerate': self._rate, 'blocksize': self._chunk_size, 'channels': self._channels,
                'dtype': self._bit_format, 'callback': self._stream_callback, 'finished_callback': event.set}

        if self._input_device_index is not None:
            sd.default.device[0] = self._input_device_index
        if self._output_device_index is not None:
            sd.default.device[1] = self._output_device_index

        if self._noise or self._threshold > 0:
            with sd.Stream(**args) as self.stream:
                event.wait()
        else:
            with sd.RawStream(**args) as self.stream:
                event.wait()

    def change_mic(self, flag):
        self._mic_flag = flag


if __name__ == '__main__':
    print(AudioController.device_info('input'))
    print(AudioController.device_info('output'))
