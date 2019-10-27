# midi channel index starts at 0 so substract 1

# Transprot Controls
transport_midi_channel = 2

track_left_button = 100
track_right_button = 101
cycle_button = 102
set_button = 103
set_left_button = 104
set_right_button = 105
rewind_button = 106
forward_button = 107
stop_button = 108
play_button = 109
record_button = 110

# Quantization
# 0:  none
# 1:  8 bars
# 2:  4 bars
# 3:  2 bars
# 4:  bar
# 5:  half
# 6:  half triplet
# 7:  quarter
# 8:  quarter triplet
# 9:  eight
# 10: eight triplet
# 11: sixtenth
# 12: sixtenth triplet
# 13: thirtytwoth
play_quantization = 4
record_quantization = 7

max_mixer_value = 0.75 # percent

# index starts at 0 so substract 1
input_track = 17

# [
#   track index,
#   midi channel,
#   start,
#   monitor,
#   record,
#   knob,
#   volume,
# ]
track_controls = [

  # KORG - Midi Channel 1 - Track 1 - 8
  [ 0,  0,  10, 11, 12, 13, 14],
  [ 1,  0,  20, 21, 22, 23, 24],
  [ 2,  0,  30, 31, 32, 33, 34],
  [ 3,  0,  40, 41, 42, 43, 44],
  [ 4,  0,  50, 51, 52, 53, 54],
  [ 5,  0,  60, 61, 62, 63, 64],
  [ 6,  0,  70, 71, 72, 73, 74],
  [ 7,  0,  80, 81, 82, 83, 84],

  # KORG - Midi Channel 2 - Track 9 - 16
  [ 8,  1,  10, 11, 12, 13, 14],
  [ 9,  1,  20, 21, 22, 23, 24],
  [ 10, 1,  30, 31, 32, 33, 34],
  [ 11, 1,  40, 41, 42, 43, 44],
  [ 12, 1,  50, 51, 52, 53, 54],
  [ 13, 1,  60, 61, 62, 63, 64],
  [ 14, 1,  70, 71, 72, 73, 74],
  [ 15, 1,  80, 81, 82, 83, 84],

  # KORG - Midi Channel 3 - Track 17 - 24
  # [ 17, 3,  10, 11, 12, 14],
  # [ 18, 3,  20, 21, 22, 24],
  # [ 19, 3,  30, 31, 32, 34],
  # [ 20, 3,  40, 41, 42, 44],
  # [ 21, 3,  50, 51, 52, 54],
  # [ 22, 3,  60, 61, 62, 64],
  # [ 23, 3,  70, 71, 72, 74],
  # [ 24, 3,  80, 81, 82, 84],
]