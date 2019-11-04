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
start_button = 109
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

knob_control_device_name = "Multi Map Pro 1.0.0"
knob_control_parameter_name = "Input"

go_back_to_playing_clip_after_beats = 8
btn_hold_down_ticks = 7

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
track_controls = {
  
  0: [
    # # KORG - Midi Channel 1 - Track 1 - 8
    [ 0,  0,  10, 11, 12, 13, 14],
    [ 1,  0,  20, 21, 22, 23, 24],
    [ 2,  0,  30, 31, 32, 33, 34],
    [ 3,  0,  40, 41, 42, 43, 44],
    [ 4,  0,  50, 51, 52, 53, 54],
    [ 5,  0,  60, 61, 62, 63, 64],
    [ 6,  0,  70, 71, 72, 73, 74],
    [ 7,  0,  80, 81, 82, 83, 84],
  ],

  1: [
    # # KORG - Midi Channel 2 - Track 9 - 16
    [ 8,  1,  10, 11, 12, 13, 14],
    [ 9,  1,  20, 21, 22, 23, 24],
    [ 10, 1,  30, 31, 32, 33, 34],
    [ 11, 1,  40, 41, 42, 43, 44],
    [ 12, 1,  50, 51, 52, 53, 54],
    [ 13, 1,  60, 61, 62, 63, 64],
    [ 14, 1,  70, 71, 72, 73, 74],
    [ 15, 1,  80, 81, 82, 83, 84],
  ],

  2: [
    #KORG - Midi Channel 3 - Track 17 - 24
    [ 16, 2,  10, 11, 12, 13, 14],
    [ 17, 2,  20, 21, 22, 23, 24],
    [ 18, 2,  30, 31, 32, 33, 34],
    [ 29, 2,  40, 41, 42, 43, 44],
    [ 20, 2,  50, 51, 52, 53, 54],
    [ 21, 2,  60, 61, 62, 63, 64],
    [ 22, 2,  70, 71, 72, 73, 74],
    [ 23, 2,  80, 81, 82, 83, 84],
  ],
  
  3: [
    #KORG - Midi Channel 4 - Track 25 - 32
    [ 24, 3,  10, 11, 12, 13, 14],
    [ 25, 3,  20, 21, 22, 23, 24],
    [ 26, 3,  30, 31, 32, 33, 34],
    [ 27, 3,  40, 41, 42, 43, 44],
    [ 28, 3,  50, 51, 52, 53, 54],
    [ 29, 3,  60, 61, 62, 63, 64],
    [ 30, 3,  70, 71, 72, 73, 74],
    [ 31, 3,  80, 81, 82, 83, 84],
  ]

}