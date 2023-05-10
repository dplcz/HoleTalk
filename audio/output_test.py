# -*-coding:utf-8-*-
from controller_sd import *

audio = AudioController(2, 12000, frames_per_buffer=960)

audio.play_file('test1.opus', opus=True)
# audio.play_file('temp.wav')
