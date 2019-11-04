from functools import partial
import Live

def get_current_track(cls):
  trackLength = cls.song.tracks.__len__()
  if cls.trackIndex < trackLength:
    track = cls.song.tracks[cls.trackIndex]
    _register_observers(cls, track)
    return track
  return False

def track_has_clips(track):
  for clip_slot in track.clip_slots:
    if clip_slot.has_clip:
      return True
  return False

def get_last_available_clip_slot(cls):
  track = get_current_track(cls)
  for clip_slot in track.clip_slots:
    if clip_slot.has_clip == False:
      cls.song.view.highlighted_clip_slot = clip_slot    
      _register_observers(cls, track)
      return clip_slot
  cls.song.create_scene(len(cls.song.scenes))
  return get_last_available_clip_slot(cls)

def get_playing_clip_slot(cls):
  track = get_current_track(cls)
  if track:
    for clip_slot in track.clip_slots:
      if clip_slot:
        if clip_slot.has_clip and clip_slot.clip.is_playing:
          cls.song.view.highlighted_clip_slot = clip_slot
          _register_observers(cls, track)
          return clip_slot
  return False

def get_recording_clip_slot(cls):
  track = get_current_track(cls)
  for clip_slot in track.clip_slots:
    if clip_slot.has_clip and clip_slot.clip.is_recording:
      cls.song.view.highlighted_clip_slot = clip_slot
      _register_observers(cls, track)
      return clip_slot

def get_first_clip_slot(cls):
  track = get_current_track(cls)
  first_clip_slot = False
  if track:
    for clip_slot in track.clip_slots:
      if clip_slot.has_clip:
        first_clip_slot = clip_slot
        break
  if first_clip_slot:
    cls.song.view.highlighted_clip_slot = first_clip_slot
    _register_observers(cls, track)
  return first_clip_slot

def get_previous_clip_slot(cls):
  track = get_current_track(cls)
  prev_clip_slot = False
  for clip_slot in track.clip_slots:
    if clip_slot.has_clip:
        if clip_slot == cls.song.view.highlighted_clip_slot:
          break
        prev_clip_slot = clip_slot
  if prev_clip_slot:
    cls.song.view.highlighted_clip_slot = prev_clip_slot
    _register_observers(cls, track)
  return prev_clip_slot

def get_next_clip_slot(cls):
  track = get_current_track(cls)
  next_clip_slot = False
  was_highlighted_clip = False
  for clip_slot in track.clip_slots:
    if clip_slot.has_clip:
      if clip_slot == cls.song.view.highlighted_clip_slot:
        was_highlighted_clip = True
        continue
      if was_highlighted_clip:
        next_clip_slot = clip_slot
        break
  if next_clip_slot:
    cls.song.view.highlighted_clip_slot = next_clip_slot
    _register_observers(cls, track)
  return next_clip_slot

def get_last_clip_slot(cls):
  track = get_current_track(cls)
  last_clip_slot = False
  if track:
    for clip_slot in track.clip_slots:
      if clip_slot.has_clip:
        last_clip_slot = clip_slot
  if last_clip_slot:
    cls.song.view.highlighted_clip_slot = last_clip_slot
    _register_observers(cls, track)
  return last_clip_slot

def _register_observers(cls, track):
  on_state_change = getattr(cls, "_on_state_change", False)
  if callable(on_state_change):
    on_state_change()
    if track:
      if not track.solo_has_listener(on_state_change):
        track.add_solo_listener(on_state_change)
      for clip_slot in track.clip_slots:
        if not clip_slot.playing_status_has_listener(on_state_change):
          clip_slot.add_playing_status_listener(on_state_change)
        if not clip_slot.has_clip_has_listener(partial(_register_observers, cls, track)):
          clip_slot.add_has_clip_listener(partial(_register_observers, cls, track))
        if not clip_slot.is_triggered_has_listener(on_state_change):
          clip_slot.add_is_triggered_listener(on_state_change)
        if clip_slot.clip:
          if not clip_slot.clip.is_recording_has_listener(on_state_change):
            clip_slot.clip.add_is_recording_listener(on_state_change)
          if not clip_slot.clip.playing_status_has_listener(on_state_change):
            clip_slot.clip.add_playing_status_listener(on_state_change)
          
    
        