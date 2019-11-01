from functools import partial

import Live

def get_current_track(cls):
  song = cls.parent.song()
  trackLength = song.tracks.__len__()
  if cls.index < trackLength:
    track = song.tracks[cls.index]
    song.view.selected_track = track
    _register_observers(cls, track, False, False)
    return track
  return False

def track_has_clips(track):
  for clip_slot in track.clip_slots:
    if clip_slot.has_clip:
      return True
  return False

def get_last_available_clip_slot(self):
  self._clip_slot = False

  for clip_slot in self._track.clip_slots:
    if clip_slot.has_clip == False:
      self._clip_slot = clip_slot
      self._view.highlighted_clip_slot = self._clip_slot
      break

def get_playing_clip_slot(cls):
  track = get_current_track(cls)
  if track:
    for clip_slot in track.clip_slots:
      if clip_slot:
        if clip_slot.has_clip and clip_slot.clip.is_playing:
          clip = clip_slot.clip
          cls.song.view.highlighted_clip_slot = clip_slot
          _register_observers(cls, track, clip_slot, clip)
          return clip
  return False

def get_recording_clip_slot(self):
  self._clip = False
  self._clip_slot = False
  for clip_slot in self._track.clip_slots:
    if clip_slot.has_clip and clip_slot.clip.is_recording:
      self._clip_slot = clip_slot
      self._clip = self._clip_slot.clip
      self._view.highlighted_clip_slot = self._clip_slot
      self._add_listeners()
      break

def get_previous_clip_slot(self):
  self._clip = False
  self._clip_slot = False
  prev_slot = False
  for clip_slot in self._track.clip_slots:
    if clip_slot:
      if clip_slot.has_clip:
        if clip_slot == self._view.highlighted_clip_slot:
          break
        prev_slot = clip_slot

  if prev_slot:
    self._clip_slot = prev_slot
    self._clip = self._clip_slot.clip
    self._view.highlighted_clip_slot = self._clip_slot
    self._add_listeners()

def get_next_clip_slot(self):
  self._clip = False
  self._clip_slot = False
  was_highlighted_clip = False
  for clip_slot in self._track.clip_slots:
    if clip_slot:
      if clip_slot.has_clip:
        if clip_slot == self._view.highlighted_clip_slot:
          was_highlighted_clip = True
          continue
        if was_highlighted_clip:
          self._clip_slot = clip_slot
          self._clip = self._clip_slot.clip
          self._view.highlighted_clip_slot = self._clip_slot
          self._add_listeners()
          return

def get_last_clip(cls):
  track = get_current_track(cls)
  clip = False
  if track:
    for clip_slot in track.clip_slots:
      if clip_slot.has_clip:
        clip = clip_slot.clip
        cls.song.view.highlighted_clip_slot = clip_slot
  _register_observers(cls, track, clip_slot, clip)
  return clip


def _register_observers(cls, track, clip_slot, clip):
  handler = getattr(cls, "_on_state_change", False)
  if callable(handler):
    partial(handler, track, clip_slot, clip)
    if track:
      if not Live.Track.Track.solo_has_listener(track, partial(handler, track, clip_slot, clip)):
        Live.Track.Track.add_solo_listener( track, partial(handler, track, clip_slot, clip))
    if clip:
      if not Live.Clip.Clip.is_recording_has_listener(clip, partial(handler, track, clip_slot, clip)):
        Live.Clip.Clip.add_is_recording_listener(clip, partial(handler, track, clip_slot, clip))
      if not Live.Clip.Clip.playing_status_has_listener(clip, partial(handler, track, clip_slot, clip)):
        Live.Clip.Clip.add_playing_status_listener(clip, partial(handler, track, clip_slot, clip))
    
        