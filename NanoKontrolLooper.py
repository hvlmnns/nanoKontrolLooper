from __future__ import with_statement

import Live
from _Framework.ControlSurface import ControlSurface

import settings 
from components.SongTasks import SongTasks
from components.TransportControl import TransportControl
from components.TrackControl import TrackControl

class NanoKontrolLooper(ControlSurface):
  __module__ = __name__
  __doc__ = "NanoKontrolLooper controller script"

  def __init__(self, c_instance):
    ControlSurface.__init__(self, c_instance)

    instance = self.instance_identifier()
    with self.component_guard():
      self.SongTasks = SongTasks(self)
      self.TransportControl = TransportControl(self)
      self.TrackControls = []
      
      for index in range(settings.track_controls[instance].__len__()):
        self.TrackControls.append(TrackControl(self, instance, index))


  def refresh_state(self):
    with self.component_guard():
      self.SongTasks.refresh()
      self.TransportControl.refresh()
      for TrackControl in self.TrackControls:
        TrackControl.refresh()


  def disconnect(self):
    with self.component_guard():
      self.SongTasks.disconnect()
      self.TransportControl.disconnect()
      for TrackControl in self.TrackControls:
        TrackControl.disconnect()

  def update_display(self):
    with self.component_guard():
      self.SongTasks.update()
      self.TransportControl.update()
      for TrackControl in self.TrackControls:
        TrackControl.update()

      with self._is_sending_scheduled_messages():
          self._task_group.update(0.1)
      
