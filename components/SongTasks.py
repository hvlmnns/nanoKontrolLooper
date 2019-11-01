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
    if Live.Song.Song.current_song_time_has_listener(self.song, self._song_time_oberver):
      Live.Song.Song.remove_current_song_time_listener(self.song, self._song_time_oberver)
    if Live.Song.Song.tempo_has_listener(self.song, self._song_tempo_observer):
      Live.Song.Song.remove_tempo_listener(self.song, self._song_tempo_observer)
    if Live.Song.Song.is_playing_has_listener(self.song, self._song_playing_observer):
      Live.Song.Song.remove_is_playing_listener(self.song, self._song_playing_observer)
    if not Live.Song.Song.data_has_listener(self.song, self._song_data_observer):
      Live.Song.Song.remove_data_listener(self.song, self._song_data_observer)
      
  def _setup(self):
    self._song_tasks = {}
    self._reset()

    if not Live.Song.Song.current_song_time_has_listener(self.song, self._song_time_oberver):
      Live.Song.Song.add_current_song_time_listener(self.song, self._song_time_oberver)
    if not Live.Song.Song.tempo_has_listener(self.song, self._song_tempo_observer):
      Live.Song.Song.add_tempo_listener(self.song, self._song_tempo_observer)
    if not Live.Song.Song.is_playing_has_listener(self.song, self._song_playing_observer):
      Live.Song.Song.add_is_playing_listener(self.song, self._song_playing_observer)
    if not Live.Song.Song.data_has_listener(self.song, self._song_data_observer):
      Live.Song.Song.add_data_listener(self.song, self._song_data_observer)

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

  def getBeatTime(self):
    return self._beat_time
  
  def isRunning(self):
    return self.song.is_playing


# observers
  def _song_tempo_observer(self):
    self._reset_beat_time()
  
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
    self._beat_times = []
    self._beat_times_count = 30
    self.millis = 0
    self._beat_time = 0

  # adds a task to the type
  def _add_task(self, type, callback, delay=0):
    if type not in self._song_tasks:
      self._song_tasks[type] = []

    if not callable(callback):
      return
    
    self._song_tasks[type].append({
      "delay": delay,
      "callback": callback
    })

  def _handle_tasks(self):    
    if self._beat_target_time == False or self._bar_target_time == False:
      self._set_target_times()
  
    largest_delay = 0
    for type in self._song_tasks:
      if type == "start" or type == "stop":
        continue

      if type == "beat":
        tasks = self._song_tasks[type]
        for task in tasks:
          if largest_delay < task["delay"]:
            largest_delay = task["delay"]
          if self._current_time >= self._beat_target_time + task["delay"]:
            task["callback"]()
  
      if type == "bar":
        tasks = self._song_tasks[type]
        for task in tasks:
          if largest_delay < task["delay"]:
            largest_delay = task["delay"]
          if self._current_time >= self._bar_target_time + task["delay"]:
            task["callback"]()
              
    if self._current_time >= self._beat_target_time + largest_delay:
      self._set_target_times()
    
  # executes tasks of a given type, mostly used for statics like start/stop
  def _execute_tasks(self, type):
    if not type in self._song_tasks:
      return

    for task in self._song_tasks[type]:
      task["callback"]()
    
  # sets the target times for the next occouring beat
  def _set_target_times(self):
    self._beat_target_time = self._current_time + (1 - (self._current_time % 1))
    self._bar_target_time = self._current_time + (4 - (self._current_time % 4))  
      
  def _reset_beat_time(self):
    self._last_millis = 0
    self._beat_times = []
  
  def _set_beat_time(self):
    self.millis = int(round(time.time() * 1000))
    if self._last_millis != 0:
      if len(self._beat_times) == self._beat_times_count:
        self._beat_times.pop(0)
      self._beat_times.append(self.millis - self._last_millis)
      self._beat_time = self.average(self._beat_times)

    self._last_millis = self.millis
    
              
# helpers
  def average(self, lst): 
    return sum(lst) / len(lst)
  
  def log(self, msg): 
    self.parent.log_message(msg)
    