from .. import settings
import _utils
import _track_utils

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import *


class TrackControl(ControlSurface):
  def __init__(self, parent, index):
    self.index = index
    self.parent = parent
    self.song = self.parent.song()
    self.SongTasks = self.parent.SongTasks
    self.initialized = False
    if self.song and not self.initialized:
      self._setup(self.index)

  def update(self):
    return

  def refresh(self):
    return

  def disconnect(self):
    _utils.turn_btns_off(self)
  
  def _setup(self, index):
    self._mapping = settings.track_controls[index]
    self._midichannel = self._mapping[1]
    self._play_btn = self._mapping[2]
    self._monitor_btn = self._mapping[3]
    self._record_btn = self._mapping[4]
    self._value_knob = self._mapping[5]
    self._volume_slider = self._mapping[6]
    
    self._is_play_triggered = False
    self._is_playing = False
    self._is_recording = False
        
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
    self.initialized = True

#tasks
  def _add_tasks(self):
    self.SongTasks.addBarTask(self._on_bar)
    self.SongTasks.addBeatTask(self._on_beat)
    self.SongTasks.addBeatTask(self._on_beat_delayed, 0.2)
    return
    
#listeners
  def _on_state_change(self, track, clip_slot, clip):      
    if track.solo:
      self._btns["monitor"].turn_off()
    else:
      self._btns["monitor"].turn_on()

    if clip_slot and clip:
      self._is_playing = (clip_slot.is_playing or clip.is_playing)

  def _on_beat(self):
    if self._is_play_triggered or self._is_playing:
      self._btns["play"].turn_on()
    else:
      self._btns["play"].turn_off()

  def _on_beat_delayed(self):
    if self._is_play_triggered:
      self._btns["play"].turn_off()    
      
  def _on_bar(self):
    self._is_play_triggered = False

  def _on_play_btn_down(self):
    track = _track_utils.get_current_track(self)

    # set_down = self._parent._transport_control.set_down
    # set_left_down = self._parent._transport_control.set_left_down
    # set_right_down = self._parent._transport_control.set_right_down
    if track:
      clip = _track_utils.get_playing_clip_slot(self)
      if not clip:
        clip = _track_utils.get_last_clip(self)
      self._fire_clip(clip)
      
      # if set_down:
      #   self._get_playing_clip_slot()
      #   if not self._clip:
      #     self._get_last_clip()

      #   if not self._clip:
      #     self._clip_slot = self._view.highlighted_clip_slot
      #     self._clip = self._clip_slot.clip
      #   # self._state_observer()
      #   # self.addTask(self._clip_reset_time,self.resetTrack,None)
      #   return

      # if set_left_down and set_right_down:
      #   self._get_last_clip()

      #   if not self._clip:
      #     self._clip_slot = self._view.highlighted_clip_slot
      #     self._clip = self._clip_slot.clip
      #   # self._state_observer()
      #   # self.addTask(self._clip_reset_time,self.resetTrack,None)
      #   return

      # if set_left_down:
      #   self._get_previous_clip_slot()
      #   if not self._clip:
      #     self._clip_slot = self._view.highlighted_clip_slot
      #     self._clip = self._clip_slot.clip
      #   # self._state_observer()
      #   # self.addTask(self._clip_reset_time,self.resetTrack,None)
      #   return

      # if set_right_down:
      #   self._get_next_clip_slot()
      #   if not self._clip:
      #     self._clip_slot = self._view.highlighted_clip_slot
      #     self._clip = self._clip_slot.clip
      #   # self._state_observer()
      #   # self.addTask(self._clip_reset_time,self.resetTrack,None)
      #   return

    
  def _on_monitor_btn_down(self):
    track = _track_utils.get_current_track(self)

    if track:
      if _track_utils.track_has_clips(track):
        track.solo = not track.solo
        track.mute = False
        self._clip = False
        self.song.tracks[settings.input_track - 1].solo = True

  def _on_record_btn_down(self):
    self.log("_on_record_btn_down")

  def _on_record_btn_up(self):
    self.log("_on_record_btn_up")
    
  def _on_volume_slider_change(self, value):
    track = _track_utils.get_current_track(self)

    if track:
      value = (float(value) / float(127)) * settings.max_mixer_value
      track.mixer_device.volume.value = value
    
  def _on_value_knob_change(self, value):
    track = _track_utils.get_current_track(self)
    if track:
      device = False
      for trackDevice in track.devices:
        if trackDevice.name == settings.knob_control_device_name:
          device = trackDevice
          break

      if device:
        self.song.view.select_device(device)
        for param in device.parameters:
          if param.name == settings.knob_control_parameter_name:
            param.value = value

# helpers
  def _fire_clip(self, clip):
    if clip:
      if clip.is_recording:
        clip.fire()
      elif clip.is_playing:
        clip.stop()
      else:
        clip.fire()
      self._is_play_triggered = True
            
  def log(self, msg): 
    self.parent.log_message(msg)