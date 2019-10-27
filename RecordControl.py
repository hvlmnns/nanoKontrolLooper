import Live

from settings import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import Task
from _Framework.InputControlElement import *
from datetime import datetime

class RecordControl(ControlSurface):
    def __init__(self, parent):
        self.tasks = Task.TaskGroup(auto_kill=False)

        self._parent = parent
        self._recording = False
        self._state = False
        self._song = self._parent.song()
        self.trackControl = False
        self._clip_slot = False
        self._startTime = 0 
        self._length = 4
        self._song.loop_length = self._length

        if self._song:
            self._setup()

    def refresh_state(self):
        return

    def update_display(self):
        self.tasks.update(self._parent._metronome.beat_time)

    def disconnect(self):
        Live.Song.Song.remove_current_song_time_listener(self._song, self._song_time_oberver)

    def addTask(self, delay_in_ticks, callback, parameter=None):
        if delay_in_ticks <= 0:
            return
        if not callable(callback):
            return

        def message(delta):
            if parameter:
                callback(parameter)
            else:
                callback()

        delay_in_ticks and self.tasks.add(Task.sequence(Task.delay(delay_in_ticks), message))
        
        
    def _setup(self):
        if not Live.Song.Song.current_song_time_has_listener(self._song, self._song_time_oberver):
            Live.Song.Song.add_current_song_time_listener(self._song, self._song_time_oberver)
        if not Live.Song.Song.data_has_listener(self._song, self._data_listener):
            Live.Song.Song.add_data_listener(self._song, self._data_listener)


    def _data_listener(self):
        
        surface = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl.surface", False)

        if surface:
            if surface != id(self._parent):
                self._startTime = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl._startTime", 0)
                self._recording = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl._recording", False)
                self._state = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl._state", False)
                self._length = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl._length", 4)
                track_control_id = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl.trackControl", False)
                if track_control_id:
                    self.trackControl = self._parent._track_controls[track_control_id]
                else:
                    self.trackControl = False

        type = Live.Song.Song.get_data(self._song, "NanoKontrolLooperRecordControl.type", "stopped")

        if (type == "queued"):
            self._parent._transport_control.tasks.clear()
            self._parent._transport_control.startRecordBlink()
        elif (type == "started"):
            if self.trackControl:
                self.trackControl.stopRecordBlink()
                self.trackControl.enableRecordButton()
            self._parent._transport_control.stopRecordBlink()
            self._parent._transport_control.enableRecordButton()
        elif (type == "stopped"):
            self._parent._transport_control.stopRecordBlink()
        

    def startRecording(self):
        if self._state != False:
            return

        self._recording = True
        
        self._parent._transport_control.stopRecordBlink()
        self._parent._transport_control.startRecordBlink()
        if self.trackControl:
            self.trackControl.stopRecordBlink()
            self.trackControl.startRecordBlink()

        self._update_data("queued")

    def stopRecording(self):
        if self._state != False:
            return

        self._recording = False
        self._parent._transport_control.stopRecordBlink()
        self._update_data("stopped")

    def isRecording(self):
        return self._recording

    def isRunning(self):
        return self._state

    def getLength(self):
        return self._length

    def setTrackControl(self, trackControl):
        self.trackControl = trackControl
        self._clip_slot = trackControl._clip_slot
        self.trackControl.stopRecordBlink()
        self.trackControl.startRecordBlink()
        if self.isRecording():
            self._parent._transport_control.stopRecordBlink()
            self._parent._transport_control.startRecordBlink()
        self._update_data(False)

    def unsetTrackControl(self):
        self.trackControl = False
        self._clip_slot = False

    def resetLength(self):
        if self._state:
            return
        self._length = 4
        self._validateLength("bar")

    def addBar(self):
        if self._state:
            return
        self._length += 4
        self._validateLength("bar")

    def removeBar(self):
        if self._state:
            return
        self._length -= 4
        self._validateLength("bar")

    def addBeat(self):
        if self._state:
            return
        self._length += 1
        self._validateLength("beat")

    def removeBeat(self):
        if self._state:
            return

        self._length -= 1
        self._validateLength("beat")

    def _validateLength(self, type):
        if type == "bar":
            if self._length < 4:
                self._length = 4
        if type == "beat":
            if self._length < 1:
                self._length = 1

        self._song.loop_length = self._length
        self._update_data(False)


    def _update_data(self, type):
        if type:
            Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl.type", type)

        Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl.now", str(datetime.now()))
        Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl.surface", id(self._parent))
        Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl._startTime", self._startTime)
        Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl._recording", self._recording)
        Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl._state", self._state)
        Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl._length", self._length)
        if self.trackControl:
            Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl.trackControl", self.trackControl._trackindex)
        else:
            Live.Song.Song.set_data(self._song, "NanoKontrolLooperRecordControl.trackControl", None)

    def _song_time_oberver(self):
        if not self._clip_slot:
            return

        if self._recording == True and self._recording:
            preDelay = 0.2
            timeToNextBar = 4 - (self._song.current_song_time % 4)
            current = self._song.current_song_time 
            target = current + timeToNextBar - preDelay

            if current >= target and self._state == False:
                self._parent._transport_control.enableRecordButton()
                self.trackControl.stopRecordBlink()
                self.trackControl.enableRecordButton()
                self._startTime = current
                self._state = True
                self._clip_slot.fire()
                self._update_data("started")

            if current >= self._startTime + self._length and self._state == True:
                self._clip_slot.fire()
                self._state = False
                self._recording = False
                self.trackControl._record_state = False
                self.unsetTrackControl()
                self._parent._transport_control.refresh_state()
                self._update_data("stopped")