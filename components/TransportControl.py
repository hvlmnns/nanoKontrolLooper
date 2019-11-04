from .. import settings
import _utils

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *


class TransportControl(ControlSurface):
  def __init__(self, parent):
    self.parent = parent
    self.song = self.parent.song()
    self.SongTasks = self.parent.SongTasks
    self.initialized = False
    if self.song and not self.initialized:
      self._setup()

  def update(self):
    return

  def refresh(self):
    self._init()

  def disconnect(self):
    _utils.turn_btns_off(self)
  
  def _setup(self):
    self._btns = {
      "trackLeft": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.track_left_button), 
      "trackRight": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.track_right_button), 
      "cycle": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.cycle_button), 
      "set": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.set_button), 
      "setLeft": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.set_left_button), 
      "setRight": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.set_right_button), 
      "rewind": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.rewind_button), 
      "forward": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.forward_button), 
      "stop": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.stop_button), 
      "start": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.start_button), 
      "record": ButtonElement(False, MIDI_CC_TYPE, settings.transport_midi_channel, settings.record_button), 
    }

    _utils.prepare_btns(self)
    _utils.turn_btns_off(self)
    _utils.add_btn_value_listeners(self)
    self._add_tasks()
    self._init()
    
  def _init(self):
    self.initialized = True
    self._wants_stop = False
    self._metronome_enabled = False
    self._btns["record"].turn_off()
    if self.song.is_playing:
      self._btns["stop"].turn_on()
    else:
      self._btns["start"].turn_on()

  def _add_tasks(self):
    self.SongTasks.addStartTask(self._on_song_start)
    self.SongTasks.addStopTask(self._on_song_stop)
    self.SongTasks.addBarTask(self._on_bar_predelayed, -0.3)
    self.SongTasks.addBarTask(self._on_bar)
    self.SongTasks.addBarTask(self._on_bar_delayed, 0.2)
    self.SongTasks.addBeatTask(self._on_beat)
    self.SongTasks.addBeatTask(self._on_beat_delayed, 0.2)
    self.SongTasks.addDataTask(self._on_data_change)
  
#listeners
  def _on_beat(self):
    self._btns["start"].turn_on()

  def _on_beat_delayed(self):
    self._btns["start"].turn_off()    

  def _on_bar_predelayed(self):
    if self._wants_stop:
      self._wants_stop = False
      if self.song.is_playing:
        self.song.stop_playing()
        self._init()

  def _on_bar(self):
    if not self._wants_stop:
      if self._metronome_enabled:
        self._btns["record"].turn_off()
      else:
        self._btns["record"].turn_on()
    
  def _on_bar_delayed(self):
    if self._metronome_enabled:
      self._btns["record"].turn_on()
    else:
      self._btns["record"].turn_off()

  def _on_song_start(self):
    self._btns["stop"].turn_on()
    self._btns["start"].turn_off()
    
  def _on_song_stop(self):
    self._btns["start"].turn_on()
    self._btns["stop"].turn_off()
    
  def _on_data_change(self):
    recordLength = _utils.get_data(self, "recordLength", 4)
    if recordLength != 4:
      self._btns["cycle"].turn_on()
      if recordLength < 1:
        _utils.set_data(self, "recordLength", 1)
    else:
      self._btns["cycle"].turn_off()
      
  def _on_start_btn_down(self):
    if not self.song.is_playing:
      self.song.start_playing()
    
  def _on_stop_btn_hold(self):
    if self.song.is_playing:
      self._wants_stop = True  

  def _on_record_btn_hold(self):
    self.song.metronome = not self.song.metronome
    self._metronome_enabled = self.song.metronome
  
  def _on_cycle_btn_down(self):
    _utils.set_data(self, "recordLength", 4)
  
  def _on_trackLeft_btn_down(self):
    recordLength = _utils.get_data(self, "recordLength", 4)
    _utils.set_data(self, "recordLength", recordLength - 1)
    self._btns["trackLeft"].turn_on()

  def _on_trackLeft_btn_up(self):
    self._btns["trackLeft"].turn_off()

  def _on_trackRight_btn_down(self):
    recordLength = _utils.get_data(self, "recordLength", 4)
    _utils.set_data(self, "recordLength", recordLength + 1)
    self._btns["trackRight"].turn_on()

  def _on_trackRight_btn_up(self):
    self._btns["trackRight"].turn_off()

  def _on_rewind_btn_down(self):
    recordLength = _utils.get_data(self, "recordLength", 4)
    _utils.set_data(self, "recordLength", recordLength - 4)
    self._btns["rewind"].turn_on()

  def _on_rewind_btn_up(self):
    self._btns["rewind"].turn_off()

  def _on_forward_btn_down(self):
    recordLength = _utils.get_data(self, "recordLength", 4)
    _utils.set_data(self, "recordLength", recordLength + 4)
    self._btns["forward"].turn_on()

  def _on_forward_btn_up(self):
    self._btns["forward"].turn_off()

  def _on_set_btn_down(self):
    _utils.set_data(self, "isSetBtnDown", True)

  def _on_set_btn_up(self):
    _utils.set_data(self, "isSetBtnDown", False)    
    
  def _on_setLeft_btn_down(self):
    _utils.set_data(self, "isSetLeftBtnDown", True)
    
  def _on_setLeft_btn_up(self):
    _utils.set_data(self, "isSetLeftBtnDown", False)
    
  def _on_setRight_btn_down(self):
    _utils.set_data(self, "isSetRightBtnDown", True)
    
  def _on_setRight_btn_up(self):
    _utils.set_data(self, "isSetRightBtnDown", False)

# helpers
  def log(self, msg): 
    self.parent.log_message(msg)