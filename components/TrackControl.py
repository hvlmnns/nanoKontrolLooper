from .. import settings
import _utils
import _track_utils

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import *
from _Framework.Task import Task


class TrackControl(ControlSurface):
  def __init__(self, parent, instance, index):
    self.instance = instance
    self.index = index
    self.trackIndex = (8 * instance) + index
    self.parent = parent
    self.song = self.parent.song()
    self.SongTasks = self.parent.SongTasks
    self.initialized = False
    if self.song and not self.initialized:
      self._setup()

  def update(self):
    return

  def refresh(self):
    return

  def disconnect(self):
    _utils.turn_btns_off(self)
  
  def _setup(self):
    self._mapping = settings.track_controls[self.instance][self.index]
    self._midichannel = self._mapping[1]
    self._play_btn = self._mapping[2]
    self._monitor_btn = self._mapping[3]
    self._record_btn = self._mapping[4]
    self._value_knob = self._mapping[5]
    self._volume_slider = self._mapping[6]
    self._btns = {
      "play": ButtonElement(False, MIDI_CC_TYPE, self._midichannel, self._play_btn),
      "monitor": ButtonElement(False, MIDI_CC_TYPE, self._midichannel, self._monitor_btn),
      "record": ButtonElement(False, MIDI_CC_TYPE, self._midichannel, self._record_btn),
    }
    _utils.prepare_btns(self)
    _utils.turn_btns_off(self)
    _utils.add_btn_value_listeners(self)
    self._sliders = {
      "volume": SliderElement(MIDI_CC_TYPE, self._midichannel, self._volume_slider),
    }
    _utils.add_slider_value_listeners(self)
    self._knobs = {
      "value": EncoderElement(MIDI_CC_TYPE, self._midichannel, self._value_knob, Live.MidiMap.MapMode.relative_two_compliment),
    }
    _utils.add_knob_value_listeners(self)
    self._add_tasks()
    self._init()
    
  def _init(self):
    self._selected_track = None
    self._selected_clip_slot = None
    self._is_play_triggered = False
    self._is_playing = False
    self._is_record_triggered = False
    self._is_recording = False
    self._monitor_held_down = False
    self._track_wants_mute_change = False
    self._track_is_muted = False
    self.initialized = True

#tasks
  def _add_tasks(self):
    self.SongTasks.addStopTask(self._on_song_stop)
    self.SongTasks.addDataTask(self._on_data_change)
    self.SongTasks.addBarTask(self._on_bar_predelayed, -0.49)
    self.SongTasks.addBarTask(self._on_bar)
    self.SongTasks.addBeatTask(self._on_beat_predelayed, -0.4)
    self.SongTasks.addBeatTask(self._on_beat)
    self.SongTasks.addBeatTask(self._on_beat_delayed, 0.2)
    return
    
#listeners
  def _on_song_stop(self):
    self._btns["play"].turn_off()
    self._btns["record"].turn_off()

  def _on_state_change(self):
    if self._selected_track:
      if not _track_utils.track_has_clips(self._selected_track):
        self._btns["monitor"].turn_off()
        self._btns["play"].turn_off()
        self._is_play_triggered = False
        self._is_playing = False
      else:
        if not self._track_is_muted:
          if self._selected_track.solo:
            self._btns["monitor"].turn_off()
          else:
            self._btns["monitor"].turn_on()
    if self._selected_clip_slot:
      if self._selected_clip_slot.has_clip:
        clip = self._selected_clip_slot.clip
        self._is_playing = clip.is_playing
        if self._is_playing:
          self._btns["play"].turn_on()
          self._is_play_triggered = False
        else:
          self._btns["play"].turn_off()
        if not self._selected_clip_slot.is_triggered:
          self._is_play_triggered = False


  def _on_data_change(self):
    trackToRecord = _utils.get_data(self, 'trackToRecord', False)
    if trackToRecord != self.trackIndex:
      self._is_record_triggered = False

  def _on_beat_predelayed(self):
    if self._is_recording:
      self._on_recording()
      
  def _on_recording(self):
    isRecording = _utils.get_data(self, 'isRecording', False)
    if not isRecording:
      self._selected_track = _track_utils.get_current_track(self)
      if self._selected_track and self._selected_track.can_be_armed:
        recordLength = _utils.get_data(self, "recordLength", 4)
        _utils.set_data(self, "trackRecordLength", recordLength)
        self._selected_track.arm = True
        self.song.clip_trigger_quantization = settings.record_quantization
        self._selected_clip_slot = _track_utils.get_last_available_clip_slot(self)
        if self._selected_clip_slot:
          self._selected_clip_slot.fire()
        _utils.set_data(self, 'isRecording', True)
      else:
        _utils.set_data(self, 'isRecording', False)
        self._is_recording = False
    trackRecordLength = _utils.get_data(self, "trackRecordLength", 4)
    _utils.set_data(self, "trackRecordLength", trackRecordLength - 1)
    if (trackRecordLength == 0):
      self._selected_track = _track_utils.get_current_track(self)
      self._selected_clip_slot = _track_utils.get_recording_clip_slot(self)
      if self._selected_clip_slot:
          self._selected_clip_slot.fire()
          _utils.set_data(self, 'isRecording', False)
          self._selected_clip_slot = _track_utils.get_playing_clip_slot(self)
      self._is_recording = False
      return

  def _on_beat(self):
    if self._is_play_triggered or self._is_playing:
      self._btns["play"].turn_on()
    else:
      self._btns["play"].turn_off()
    if self._is_record_triggered or self._is_recording:
      self._btns["record"].turn_on()
    else:
      self._btns["record"].turn_off()
    if self._track_is_muted:
      if self._selected_track.solo:
        self._btns["monitor"].turn_on()
      else:
        self._btns["monitor"].turn_off()
    goBackToPlayingTimer = _utils.get_data(self, 'goBackToPlayingTimer' + str(self.trackIndex), -1)
    if goBackToPlayingTimer > 0:
      _utils.set_data(self, 'goBackToPlayingTimer' + str(self.trackIndex), goBackToPlayingTimer - 1)
    elif goBackToPlayingTimer == 0:
      _utils.set_data(self, 'goBackToPlayingTimer' + str(self.trackIndex),-1)
      self._selected_clip_slot = _track_utils.get_playing_clip_slot(self)

  def _on_beat_delayed(self):
    if self._is_play_triggered:
      self._btns["play"].turn_off()
    if self._is_record_triggered:
      self._btns["record"].turn_off()
    if self._track_is_muted:
      if self._selected_track.solo:
        self._btns["monitor"].turn_off()
      else:
        self._btns["monitor"].turn_on()
    isRecording = _utils.get_data(self, 'isRecording', False)
    if not isRecording and self._selected_track:
      self._selected_track.arm = False
  
  def _on_bar(self):
    if self._track_wants_mute_change == True:
      self._track_wants_mute_change = False
      self._selected_track = _track_utils.get_current_track(self)
      self._selected_track.mute = not self._selected_track.mute
      self._track_is_muted = self._selected_track.mute
          
  def _on_bar_predelayed(self):
    if self._is_record_triggered:
      self._is_record_triggered = False
      self._is_play_triggered = True
      self._is_recording = True

  def _on_play_btn_down(self):
    self._selected_track = _track_utils.get_current_track(self)
    set_down = _utils.get_data(self, 'isSetBtnDown', False)
    set_left_down = _utils.get_data(self, 'isSetLeftBtnDown', False)
    set_right_down = _utils.get_data(self, 'isSetRightBtnDown', False)
    got_selected = False
    if self._selected_track:
      if set_down:
        if set_left_down:
          self._selected_clip_slot = _track_utils.get_first_clip_slot(self)
          got_selected = True
          self._delayed_go_back_to_playing()
          got_selected = True
          return
        if set_right_down:
          self._selected_clip_slot = _track_utils.get_last_clip_slot(self)
          got_selected = True
          self._delayed_go_back_to_playing()
          return
        self._selected_clip_slot = _track_utils.get_playing_clip_slot(self)
        if not self._selected_clip_slot or not self._selected_clip_slot.clip:
          self._selected_clip_slot = _track_utils.get_last_clip_slot(self)
          got_selected = True
        return
      if set_left_down:
        self._selected_clip_slot = _track_utils.get_previous_clip_slot(self)
        got_selected = True
        self._delayed_go_back_to_playing()
        return
      if set_right_down:
        self._selected_clip_slot = _track_utils.get_next_clip_slot(self)
        got_selected = True
        self._delayed_go_back_to_playing()
        return
      self._discard_go_back_to_playing()
      if got_selected == False:
        self._selected_clip_slot = _track_utils.get_playing_clip_slot(self)
        if not self._selected_clip_slot:
          self._selected_clip_slot = _track_utils.get_last_clip_slot(self)
      self._selected_clip_slot = self.song.view.highlighted_clip_slot
      self._fire_clip(self.song.view.highlighted_clip_slot.clip)
    
  def _on_monitor_btn_up(self):
    if self._monitor_held_down:
      self._monitor_held_down = False
      return
    self._selected_track = _track_utils.get_current_track(self)
    if self._selected_track:
      if _track_utils.track_has_clips(self._selected_track):
        self._selected_track.solo = not self._selected_track.solo
        self.song.tracks[settings.input_track - 1].solo = True
        
  def _on_monitor_btn_hold(self):
    self._monitor_held_down = True
    self._selected_track = _track_utils.get_current_track(self)
    if self._selected_track:
      if _track_utils.track_has_clips(self._selected_track):
        self._track_wants_mute_change = True
        self.song.tracks[settings.input_track - 1].solo = True
  
  def _on_record_btn_up(self):  
    if self.song.is_playing == False:
      return
    isRecording = _utils.get_data(self, 'isRecording', False)
    if isRecording:
      return
    self._discard_go_back_to_playing()
    if self._is_record_triggered:
      _utils.set_data(self, "trackToRecord", False)
      self._is_record_triggered = False
    else:
      _utils.set_data(self, "trackToRecord", self.trackIndex)
      self._is_record_triggered = True
      self._btns["record"].turn_on()
    
  def _on_volume_slider_change(self, value):
    self._selected_track = _track_utils.get_current_track(self)
    if self._selected_track:
      self.song.view.selected_track = self._selected_track
      value = (float(value) / float(127)) * settings.max_mixer_value
      self._selected_track.mixer_device.volume.value = value
    
  def _on_value_knob_change(self, value):
    self._selected_track = _track_utils.get_current_track(self)
    if self._selected_track:
      self.song.view.selected_track = self._selected_track
      device = False
      for trackDevice in self._selected_track.devices:
        if trackDevice.name == settings.knob_control_device_name:
          device = trackDevice
          break
      if device:
        self.song.view.selected_device = device
        self.song.view.select_device(device)
        for param in device.parameters:
          if param.name == settings.knob_control_parameter_name:
            param.value = value

# helpers
  def _delayed_go_back_to_playing(self):
    _utils.set_data(self, 'goBackToPlayingTimer' + str(self.trackIndex), settings.go_back_to_playing_clip_after_beats)

  def _discard_go_back_to_playing(self):
    _utils.set_data(self, 'goBackToPlayingTimer' + str(self.trackIndex), -1)

  def _fire_clip(self, clip):
    if clip:
      self.song.clip_trigger_quantization = settings.play_quantization
      if clip.is_recording:
        clip.fire()
      elif clip.is_playing:
        clip.stop()
      else:
        clip.fire()
      self._is_play_triggered = True
            
  def log(self, msg): 
    self.parent.log_message(msg)