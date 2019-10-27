from __future__ import with_statement
import Live


from settings import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *

from RecordControl import RecordControl
from TransportControl import TransportControl
from TrackControl import TrackControl
from Metronome import Metronome


class NanoKontrolLooper(ControlSurface):
    __module__ = __name__
    __doc__ = "NanoKontrolLooper controller script"

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._track_controls = []

        with self.component_guard():
            self._metronome = Metronome(self)
            self._record_control = RecordControl(self)
            self._transport_control = TransportControl(self)

            for index in range(track_controls.__len__()):
                self._track_controls.append(TrackControl(self, index))

    def refresh_state(self):
        self._record_control.refresh_state()
        self._transport_control.refresh_state()
        self._metronome.refresh_state()
        for control in self._track_controls:
            control.refresh_state()

    def disconnect(self):
        self._record_control.disconnect()
        self._transport_control.disconnect()
        self._metronome.disconnect()
        for control in self._track_controls:
            control.disconnect()

    def resetTracks(self, slot):
        for control in self._track_controls:
            control.resetTrack(slot)

    def update_display(self):
        with self.component_guard():
            self._task_group.update(0.1)

            self._metronome.update_display()
            self._record_control.update_display()
            self._transport_control.update_display()
            for control in self._track_controls:
                control.update_display()
