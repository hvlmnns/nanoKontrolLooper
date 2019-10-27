import Live

from settings import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import Task
from _Framework.InputControlElement import *
from datetime import datetime
import time

class Metronome(ControlSurface):
    def __init__(self, parent):
        self._parent = parent
        self._song = self._parent.song()
        self._beatTarget = False
        self._barTarget = False
        self._metronome_state = "off"
        self._last_millis = 0
        self._beat_times = []
        self._beat_times_count = 30

        self.millis = 0
        self.beat_time = 0

        if self._song:
            self._setup()

    def refresh_state(self):
        return

    def update_display(self):
        return

    def disconnect(self):
        Live.Song.Song.remove_current_song_time_listener(self._song, self._song_time_oberver)

        
        
    def _setup(self):
        if not Live.Song.Song.current_song_time_has_listener(self._song, self._song_time_oberver):
            Live.Song.Song.add_current_song_time_listener(self._song, self._song_time_oberver)
        if not Live.Song.Song.tempo_has_listener(self._song, self._reset_beat_time):
            Live.Song.Song.add_tempo_listener(self._song, self._reset_beat_time)

    def _reset_beat_time(self):
        self._last_millis = 0
        self._beat_times = []
    
    def _song_time_oberver(self):
        self._metronome()
        

    def _average(self, lst): 
        return sum(lst) / len(lst)
    
    def _set_beat_time(self):
        self.millis = int(round(time.time() * 1000))
        if self._last_millis != 0:
            if len(self._beat_times) == self._beat_times_count:
                self._beat_times.pop(0)
            self._beat_times.append(self.millis - self._last_millis)

            self.beat_time = self._average(self._beat_times)
        self._last_millis = self.millis

        self._parent.log_message(self._beat_times)
        self._parent.log_message(self.beat_time)
        self._parent.log_message(len(self._beat_times))
        self._parent.log_message("--------------------")

    def _metronome(self):
        if not self._song.is_playing:
            return

        currentTime = self._song.current_song_time 

        if self._beatTarget == False or self._barTarget == False:
            self._beatTarget = currentTime + (1 - (currentTime % 1))
            self._barTarget = currentTime + (4 - (currentTime % 4))

        if currentTime >= (self._barTarget):
            if self._metronome_state != "bar":
                self._metronome_state = "bar"
                self._set_beat_time()
                self._parent._transport_control.switchForwadButtons("bar")
        elif currentTime >= (self._beatTarget):
            if self._metronome_state != "beat":
                self._metronome_state = "beat"
                self._set_beat_time()
                self._parent._transport_control.switchForwadButtons("beat")

        if currentTime >= (self._beatTarget + 0.2):
            if self._metronome_state != "off":
                self._metronome_state = "off"
                self._parent._transport_control.switchForwadButtons("off")

            self._beatTarget = currentTime + (1 - (currentTime % 1))
            self._barTarget = currentTime + (4 - (currentTime % 4))
                
