import Live

from settings import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import Task
from _Framework.InputControlElement import *


class TransportControl(ControlSurface):
    def __init__(self, parent):
        self.tasks = Task.TaskGroup(auto_kill=False)

        self._midichannel = transport_midi_channel
        self._parent = parent
        self._momentary = True
        self._song = self._parent.song()
        self.set_down = False
        self.set_left_down = False
        self.set_right_down = False

        self._metronome = "left"


        self._setup()
        self._add_listeners()

    def refresh_state(self):
        if self._initialized:
            self._parent._record_control._length = self._song.loop_length
            if self._song.is_playing:
                self._stop_button.turn_on()
                self._play_button.turn_off()
            else:
                self._stop_button.turn_off()
                self._play_button.turn_on()

            if self._parent._record_control.getLength() != 4:
                self._cycle_button.turn_on()
            else:
                self._cycle_button.turn_off()

    def update_display(self):
        self.tasks.update(self._parent._metronome.beat_time)

    def disconnect(self):
        self.tasks.clear()

        self._track_left_button.remove_value_listener(self._handle_track_left_button)
        self._track_right_button.remove_value_listener(self._handle_track_right_button)
        self._cycle_button.remove_value_listener(self._handle_cycle_button)
        self._set_button.remove_value_listener(self._handle_set_button)
        self._set_left_button.remove_value_listener(self._handle_set_left_button)
        self._set_right_button.remove_value_listener(self._handle_set_right_button)
        self._rewind_button.remove_value_listener(self._handle_rewind_button)
        self._forward_button.remove_value_listener(self._handle_forward_button)
        self._stop_button.remove_value_listener(self._handle_stop_button)
        self._play_button.remove_value_listener(self._handle_play_button)
        self._record_button.remove_value_listener(self._handle_record_button)

        self._track_left_button.turn_off()
        self._track_right_button.turn_off()
        self._cycle_button.turn_off()
        self._set_button.turn_off()
        self._set_left_button.turn_off()
        self._set_right_button.turn_off()
        self._rewind_button.turn_off()
        self._forward_button.turn_off()
        self._stop_button.turn_off()
        self._play_button.turn_off()
        self._record_button.turn_off()

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

    

# setup
    def _setup(self):
        self._track_left_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, track_left_button)
        self._track_right_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, track_right_button)
        self._cycle_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, cycle_button)
        self._set_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, set_button)
        self._set_left_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, set_left_button)
        self._set_right_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, set_right_button)
        self._rewind_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, rewind_button)
        self._forward_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, forward_button)
        self._stop_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, stop_button)
        self._play_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, play_button)
        self._record_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, record_button)

        self._track_left_button.add_value_listener(self._handle_track_left_button)
        self._track_right_button.add_value_listener(self._handle_track_right_button)
        self._cycle_button.add_value_listener(self._handle_cycle_button)
        self._set_button.add_value_listener(self._handle_set_button)
        self._set_left_button.add_value_listener(self._handle_set_left_button)
        self._set_right_button.add_value_listener(self._handle_set_right_button)
        self._rewind_button.add_value_listener(self._handle_rewind_button)
        self._forward_button.add_value_listener(self._handle_forward_button)
        self._stop_button.add_value_listener(self._handle_stop_button)
        self._play_button.add_value_listener(self._handle_play_button)
        self._record_button.add_value_listener(self._handle_record_button)

        self._initialized = True
        self.refresh_state()

    def _add_listeners(self):
        if self._song:
            if not Live.Song.Song.is_playing_has_listener(self._song, self.refresh_state):
                Live.Song.Song.add_is_playing_listener(self._song, self.refresh_state)
            if not Live.Song.Song.loop_length_has_listener(self._song, self.refresh_state):
                Live.Song.Song.add_loop_length_listener(self._song, self.refresh_state)

# handlers
    def _handle_track_left_button(self, value):
        if value != 127:
            return
        self._parent._record_control.removeBeat()
        self.refresh_state()

    def _handle_track_right_button(self, value):
        if value != 127:
            return
        self._parent._record_control.addBeat()
        self.refresh_state()

    def _handle_cycle_button(self, value):
        if value != 127:
            return
        self._parent._record_control.resetLength()
        self.refresh_state()

    def _handle_set_button(self, value):
        if value != 127:
            self.set_down = False
            return
        self.set_down = True

    def _handle_set_left_button(self, value):
        if value != 127:
            self.set_left_down = False
            return
        self.set_left_down = True

    def _handle_set_right_button(self, value):
        if value != 127:
            self.set_right_down = False
            return
        self.set_right_down = True

    def _handle_rewind_button(self, value):
        if value != 127:
            return
        self._parent._record_control.removeBar()
        self.refresh_state()

    def _handle_forward_button(self, value):
        if value != 127:
            return
        self._parent._record_control.addBar()
        self.refresh_state()

    def _handle_stop_button(self, value):
        if value != 127:
            return
        if self._song.is_playing:
            self._song.stop_playing()
            self._play_button.turn_on()
            self._stop_button.turn_off()
            self.switchForwadButtons("off")
            self.addTask(1,self.reset_metronome)

    def reset_metronome(self):
        self._parent._metronome._barTarget = False
        self._parent._metronome._beatTarget = False
        self._parent._metronome._metronome_state = "off"
        self._metronome = "left"
        self.switchForwadButtons("off")

    def _handle_play_button(self, value):
        if value != 127:
            return
        if not self._song.is_playing:
            self._song.start_playing()
            self._stop_button.turn_on()
            self._play_button.turn_off()

    def _handle_record_button(self, value):
        if value != 127:
            return

        if self._parent._record_control.isRunning():
            return

        if self._parent._record_control.isRecording():
            self._parent._record_control.stopRecording()
            self.stopRecordBlink()
        else:
            self.startRecordBlink()
            self._parent._record_control.startRecording()
            

    def switchForwadButtons(self, type):
        if type == "beat":
            if self._metronome == "left":
                self._metronome = "right"
                self._rewind_button.turn_off()
                self._forward_button.turn_on()
            else:
                self._metronome = "left"
                self._rewind_button.turn_on()
                self._forward_button.turn_off()
        if type == "bar":
            self._rewind_button.turn_on()
            self._forward_button.turn_on()
        if type == "off":
            self._rewind_button.turn_off()
            self._forward_button.turn_off()
        

    def enableStopButton(self):
        self._stop_button.turn_on()

    def enableRecordButton(self):
        self.tasks.clear()
        self._record_button.turn_on()

    def stopRecordBlink(self):
        self.tasks.clear()
        self._record_button.turn_off()

    def startRecordBlink(self):
        self._record_button.turn_on()
        for i in range(7):
            if i == 0:
                continue

            if i == 6:
                self.addTask(i, self.startRecordBlink)
                break

            if i % 3 == 0:
                self.addTask(i, self._record_button.turn_on)

            if i % 1.5 == 0:
                self.addTask(i, self._record_button.turn_off)
