import Live

from settings import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
import time


class TrackControl(ControlSurface):
    def __init__(self, parent, index):
        self.tasks = Task.TaskGroup(auto_kill=False)

        self._controls = track_controls[index]
        self._trackindex = self._controls[0]
        self._midichannel = self._controls[1]
        self._play_cc = self._controls[2]
        self._monitor_cc = self._controls[3]
        self._record_cc = self._controls[4]
        self._knob_cc = self._controls[5]
        self._volume_cc = self._controls[6]

        self._song = False
        self._view = False
        self._tracks = False
        self._track = False
        self._clip_slot = False
        self._clip = False
        self._record_state = False
        self._play_is_blinking = False
        self._record_is_blinking = False

        self._clip_reset_time = 30

        self._parent = parent
        self._momentary = True
        self._setup_controls()
        self._setup_tracks()
        self._add_listeners()

    def refresh_state(self):
        self._get_current_track()
        self._state_observer()

        self._get_playing_clip_slot()
        if self._clip_slot:
            self._state_observer()
            return

        self._get_recording_clip_slot()
        if self._clip_slot:
            self._state_observer()
            return

    def update_display(self):
        self.tasks.update(self._parent._metronome.beat_time)

    def disconnect(self):
        self.tasks.clear()
        self._play_button.turn_off()
        self._record_button.turn_off()
        self._monitor_button.turn_off()
        self._play_button.remove_value_listener(self._handle_play_button)
        self._record_button.remove_value_listener(self._handle_record_button)
        self._monitor_button.remove_value_listener(self._handle_monitor_button)
        self._control_knob.remove_value_listener(self._handle_control_knob)
        self._volume_slider.remove_value_listener(self._handle_volume_slider)

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

        delay_in_ticks and self.tasks.add(
            Task.sequence(Task.delay(delay_in_ticks), message))

# publics
    def resetTrack(self, slot=None):
        if self._track:
            self._track.arm = False
            self.stopRecordBlink()
            self._record_button.turn_off()

            if self._clip_slot:
                if slot:
                    if slot != self._clip_slot:
                        self._state_observer()
                        self._record_state = False
                else:
                    self._get_playing_clip_slot()  
                    self._state_observer()
            

# setup
    def _setup_tracks(self):
        self._get_current_track()
        if self._track:
            if self._track_has_clips():
                self._track.solo = False
                self._monitor_button.turn_on()
                self._add_listeners()
            else:
                self._monitor_button.turn_off()

    def _setup_controls(self):
        self._play_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, self._play_cc)
        self._record_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, self._record_cc)
        self._monitor_button = ButtonElement(not self._momentary, MIDI_CC_TYPE, self._midichannel, self._monitor_cc)
        self._control_knob = SliderElement(MIDI_CC_TYPE, self._midichannel, self._knob_cc)
        self._volume_slider = SliderElement(MIDI_CC_TYPE, self._midichannel, self._volume_cc)

        self._play_button.add_value_listener(self._handle_play_button)
        self._record_button.add_value_listener(self._handle_record_button)
        self._monitor_button.add_value_listener(self._handle_monitor_button)
        self._control_knob.add_value_listener(self._handle_control_knob)
        self._volume_slider.add_value_listener(self._handle_volume_slider)

# play functionality

    def _fire_clip(self):
        if self._clip:
            self._add_listeners()
            if self._clip.is_recording:
                self._clip.fire()
            elif self._clip.is_playing:
                self._clip.stop()
            else:
                self._clip.fire()

            self.startPlayBlink()

    def _handle_play_button(self, value):
        assert isinstance(value, int)
        assert isinstance(self._play_button, ButtonElement)
        if value != 127:
            return

        


# record functionality

    def _handle_record_button(self, value):
        assert isinstance(value, int)
        assert isinstance(self._record_button, ButtonElement)
        if value != 127:
            return

        if self._parent._record_control.isRunning():
            return

        self._get_current_track()
        self._get_last_available_clip_slot()

        if not self._clip_slot:
            Live.Song.Song.create_scene(self._song, len(self._song.scenes))
            self._get_last_available_clip_slot()

        self._song.clip_trigger_quantization = record_quantization
        self._parent.resetTracks(self._clip_slot)
        self._record_state = not self._record_state

        if self._clip_slot and self._record_state:
            if self._track.can_be_armed:
                self._track.arm = True
                self.startRecordBlink()
                self._add_clip_slot_listener()
                self._parent._record_control.setTrackControl(self)
                self._state_observer()
                self._add_listeners()
        else:
            self._parent._record_control.unsetTrackControl()
            self.stopRecordBlink()
            self._record_button.turn_off()
            self._state_observer()


    

# track listener
    def _add_clip_slot_listener(self):
        if self._clip_slot:
            if not Live.ClipSlot.ClipSlot.has_clip_has_listener(self._clip_slot, self._clip_slot_state_observer):
                Live.ClipSlot.ClipSlot.add_has_clip_listener(
                    self._clip_slot, self._clip_slot_state_observer)

    def _clip_slot_state_observer(self):
        self._add_listeners()

    def _add_listeners(self):
        if self._clip_slot:
            if self._clip_slot.has_clip:
                self._clip = self._clip_slot.clip

        if self._track:
            if not Live.Track.Track.solo_has_listener(self._track, self._state_observer):
                Live.Track.Track.add_solo_listener( self._track, self._state_observer)

        if self._clip:
            if not Live.Clip.Clip.is_recording_has_listener(self._clip, self._state_observer):
                Live.Clip.Clip.add_is_recording_listener( self._clip, self._state_observer)
            if not Live.Clip.Clip.playing_status_has_listener(self._clip, self._state_observer):
                Live.Clip.Clip.add_playing_status_listener( self._clip, self._state_observer)

    def _disableArm(self):
        self._track.arm = False

    def _state_observer(self):
        if self._track:
            if self._track_has_clips():
                if self._track.solo:
                    self._monitor_button.turn_off()
                else:
                    self._monitor_button.turn_on()

        if self._clip_slot:

            if self._clip_slot.has_clip:
                self._clip = self._clip_slot.clip

                if self._clip.is_recording:
                    self._record_button.turn_on()
                    self._play_button.turn_off()
                elif self._clip.is_playing:
                    self.stopPlayBlink()
                    self._play_button.turn_on()
                    self._record_button.turn_off()
                    self.addTask(1, self._disableArm)
                elif self._clip.is_triggered:
                    self.startPlayBlink()
                else:
                    self.stopPlayBlink()
                    self._play_button.turn_off()
                    self._record_button.turn_off()
        else:
            self.stopPlayBlink()
            self._record_button.turn_off()
            self._play_button.turn_off()
            return

    def stopPlayBlink(self):
        self.tasks.clear()
        self._play_is_blinking = False

    def startPlayBlink(self):
        if self._record_is_blinking:
            self.stopRecordBlink()
        self._play_button.turn_on()
        self._play_is_blinking = True
        for i in range(7):
            if i == 0:
                continue

            if i == 6:
                self.addTask(i, self.startPlayBlink)
                break

            if i % 3 == 0:
                self.addTask(i, self._play_button.turn_on)

            if i % 1.5 == 0:
                self.addTask(i, self._play_button.turn_off)

    def enableRecordButton(self):
        self._record_button.turn_on()

    def stopRecordBlink(self):
        self.tasks.clear()
        self._record_is_blinking = False

    def startRecordBlink(self):
        if self._play_is_blinking:
            self.stopPlayBlink()
        self._record_button.turn_on()
        self._record_is_blinking = True
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
