from .. import settings

import Live
from _Framework.ControlSurface import ControlSurface

class SongTasks(ControlSurface):
  def __init__(self, parent):
    self.parent = parent
    self.song = self.parent.song()
    self.initialized = False
    if self.song and not self.initialized:
      self._setup()

  def refresh(self):
    return

  def update(self):
    return

  def disconnect(self):
    self._song_tasks = {}
    if self.song.current_song_time_has_listener(self._song_time_oberver):
      self.song.remove_current_song_time_listener(self._song_time_oberver)
    if self.song.is_playing_has_listener(self._song_playing_observer):
      self.song.remove_is_playing_listener(self._song_playing_observer)
    if not self.song.data_has_listener(self._song_data_observer):
      self.song.remove_data_listener(self._song_data_observer)
      
  def _setup(self):
    self._song_tasks = {}
    self._reset()

    if not self.song.current_song_time_has_listener(self._song_time_oberver):
      self.song.add_current_song_time_listener(self._song_time_oberver)
    if not self.song.is_playing_has_listener(self._song_playing_observer):
      self.song.add_is_playing_listener(self._song_playing_observer)
    if not self.song.data_has_listener(self._song_data_observer):
      self.song.add_data_listener(self._song_data_observer)

    self.initialized = True
    

# public
  def addStartTask(self, callback):
    self._add_task("start", callback)

  def addStopTask(self, callback):
    self._add_task("stop", callback)
    
  def addDataTask(self, callback):
    self._add_task("data", callback)
    
  def addBeatTask(self, callback, delay=0):
    self._add_task("beat", callback, delay)

  def addBarTask(self, callback, delay=0):
    self._add_task("bar", callback, delay)

  def isRunning(self):
    return self.song.is_playing


# observers  
  def _song_time_oberver(self):
    if not self.song.is_playing:
      return
    self._current_time = self.song.current_song_time
    self._handle_tasks()
    
  def _song_playing_observer(self):
    if not self.song.is_playing and self._play_state:
      self._play_state = False
      self._execute_tasks("stop")
      self._reset()
    if self.song.is_playing and not self._play_state:
      self._play_state = True
      self._execute_tasks("start")

  def _song_data_observer(self):
    self._execute_tasks("data")

# private        
  def _reset(self):
    self._beat_target_time = False
    self._bar_target_time = False
    self._play_state = False
    self._last_millis = 0
    self.millis = 0

  # adds a task to the type
  def _add_task(self, type, callback, delay=0):
    if type not in self._song_tasks:
      self._song_tasks[type] = []
    if not callable(callback):
      return
    self._song_tasks[type].append({
      "delay": delay,
      "callback": callback,
      "executed": False
    })

  def _handle_tasks(self):    
    if self._beat_target_time == False or self._bar_target_time == False:
      self._set_target_times()
    largest_delay = 0
    for type in self._song_tasks:
      if type == "start" or type == "stop":
        continue
      if type == "beat":
        tasks = self._song_tasks["beat"]
        for task in tasks:
          if largest_delay < task["delay"]:
            largest_delay = task["delay"]
          if self._current_time >= self._beat_target_time + task["delay"]:
            if not task["executed"]:
              self.parent.schedule_message(1, task["callback"])
              self._is_resetted = False
              task["executed"] = True
      if type == "bar":
        tasks = self._song_tasks["bar"]
        for task in tasks:
          if largest_delay < task["delay"]:
            largest_delay = task["delay"]
          if self._current_time >= self._bar_target_time + task["delay"]:
            if not task["executed"]:
              self.parent.schedule_message(1, task["callback"])
              self._is_resetted = False
              task["executed"] = True
    reset_target_time = self._beat_target_time + largest_delay + 0.1
    if self._current_time >= reset_target_time and not self._is_resetted:
      self._is_resetted = True
      tasks = self._song_tasks["beat"]
      for task in tasks:
        task["executed"] = False
      tasks = self._song_tasks["bar"]
      for task in tasks:
        task["executed"] = False
      self._set_target_times()
    
  # executes tasks of a given type, mostly used for statics like start/stop
  def _execute_tasks(self, type):
    if not type in self._song_tasks:
      return
    for task in self._song_tasks[type]:
      self.parent.schedule_message(1, task["callback"])
    
  # sets the target times for the next occouring beat
  def _set_target_times(self):
    self._beat_target_time = self._current_time + (1 - (self._current_time % 1))
    self._bar_target_time = self._current_time + (4 - (self._current_time % 4))  
              
# helpers
  def log(self, msg): 
    self.parent.log_message(msg)
    