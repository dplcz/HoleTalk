# -*-coding:utf-8-*-
from controller_sd import *

# print(AudioController.in_device_info())

audio = AudioController(2, 12000, input_device_index=1, frames_per_buffer=960)
# audio = AudioController(2, 44100, _output=True)

audio.record_to_file('test1', seconds=5, successive=True, opus=True, noise=True, stationary=True)

# audio.play_file('test.opus', opus=True)
