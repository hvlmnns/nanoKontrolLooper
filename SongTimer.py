import Live

from settings import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import Task
from _Framework.InputControlElement import *
from datetime import datetime
import time

BEAT_STATE = 1
BAR_STATE = 2
OFF_STATE = 3

# time offset for early beat ticks in percent of one 1/4 beat
PREFIRE_OFFSET = 0.075 # 1 == 100%

class SongTimer(ControlSurface):
  def __init__(self, parent):
    self.parent = parent

    self._song = self.parent.song()
    if self._song:
      self._setup()

  def refresh_state(self):
    return

  def update_display(self):
    return

  def disconnect(self):
    if Live.Song.Song.current_song_time_has_listener(self._song, self._song_time_oberver):
      Live.Song.Song.remove_current_song_time_listener(self._song, self._song_time_oberver)
    if Live.Song.Song.tempo_has_listener(self._song, self._song_tempo_observer):
      Live.Song.Song.remove_tempo_listener(self._song, self._song_tempo_observer)
    if Live.Song.Song.is_playing_has_listener(self._song, self._song_playing_observer):
      Live.Song.Song.remove_is_playing_listener(self._song, self._song_playing_observer)
      
  def _setup(self):
    self._reset()

    if not Live.Song.Song.current_song_time_has_listener(self._song, self._song_time_oberver):
      Live.Song.Song.add_current_song_time_listener(self._song, self._song_time_oberver)
    if not Live.Song.Song.tempo_has_listener(self._song, self._song_tempo_observer):
      Live.Song.Song.add_tempo_listener(self._song, self._song_tempo_observer)
    if not Live.Song.Song.is_playing_has_listener(self._song, self._song_playing_observer):
      Live.Song.Song.add_is_playing_listener(self._song, self._song_playing_observer)

    self.initialized = True

# public
    
  def addOnBeatTask(self, func, params=None):
    return

  def addOnBarTask(self, func, params=None):
    return

  def addOnPreBeatTask(self, func, params=None):
    return

  def addOnPreBarTask(self, func, params=None):
    return

  def getBeatTime(self):
    return self._beat_time


# observers
  def _song_tempo_observer(self):
    self._reset_beat_time()
  
  def _song_time_oberver(self):
    if not self._song.is_playing:
      return

    self._current_time = self._song.current_song_time
    self._handle_song_pre_beats()
    self._handle_song_beats()
    
  def _song_playing_observer(self):
    if not self._song.is_playing:
      self._reset()

# private

  def _reset(self):
    self._beat_target_time = False
    self._bar_target_time = False
    self._state = OFF_STATE
    self._pre_state = OFF_STATE
    self._last_millis = 0
    self._beat_times = []
    self._beat_times_count = 30
    self.millis = 0
    self._beat_time = 0

  def _reset_beat_time(self):
    self._last_millis = 0
    self._beat_times = []
  
  def _set_beat_time(self):
    self.millis = int(round(time.time() * 1000))
    if self._last_millis != 0:
      if len(self._beat_times) == self._beat_times_count:
        self._beat_times.pop(0)
      self._beat_times.append(self.millis - self._last_millis)

      self._beat_time = self._average(self._beat_times)
    self._last_millis = self.millis


  # handles the tasks that should fire right before the next beat tick
  def _handle_song_pre_beats(self):
    if self._beat_target_time == False or self._bar_target_time == False:
      self._set_target_times()

    if self._current_time >= (self._bar_target_time - PREFIRE_OFFSET):
      if self._pre_state != BAR_STATE:
        self._pre_state = BAR_STATE
        self._log("pre beat")
        self._log("pre bar")
            
    elif self._current_time >= (self._beat_target_time - PREFIRE_OFFSET):
      if self._pre_state != BEAT_STATE:
        self._pre_state = BEAT_STATE
        self._log("pre beat")

    if self._current_time >= (self._beat_target_time + PREFIRE_OFFSET):
      if self._pre_state != OFF_STATE:
        self._pre_state = OFF_STATE

  # handles the tasks that should fire on or right after the next beat tick
  def _handle_song_beats(self):
    if self._beat_target_time == False or self._bar_target_time == False:
      self._set_target_times()

    if self._current_time >= self._bar_target_time:
      if self._state != BAR_STATE:
        self._state = BAR_STATE
        self._log("beat")
        self._log("bar")
        self._set_beat_time()
            
    elif self._current_time >= self._beat_target_time:
      if self._state != BEAT_STATE:
        self._state = BEAT_STATE
        self._log("beat")
        self._set_beat_time()
            
    if self._current_time >= self._beat_target_time + PREFIRE_OFFSET:
      if self._state != OFF_STATE:
        self._state = OFF_STATE
      self._set_target_times()


  # sets the target times for the next occouring beat
  def _set_target_times(self):
    self._beat_target_time = self._current_time + (1 - (self._current_time % 1))
    self._bar_target_time = self._current_time + (4 - (self._current_time % 4))
              
# helpers
  def _average(self, lst): 
    return sum(lst) / len(lst)
  
  def _log(self, msg): 
    self.parent.log_message(msg)
    