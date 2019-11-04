import Live
from functools import partial

from .. import settings

from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.Task import Task
from _Framework.InputControlElement import *

def __add_btn_task(cls, delay_in_ticks, callback, parameter=None):
    if delay_in_ticks <= 0 or not callable(callback):
      return
    def message(delta):
      if parameter:
        callback(parameter)
      else:
        callback()
    delay_in_ticks and cls._btn_tasks.add(Task.sequence(Task.delay(delay_in_ticks), message))

# overwrites some mehtods of the all buttons (_btns) in the passed cls
def prepare_btns(cls):
  for btn in cls._btns.values():

    def turn_on(self):
      self.send_value(127, True)

    def turn_off(self):
      self.send_value(0, True)

    btn.turn_on = partial(turn_on, btn)
    btn.turn_off = partial(turn_off, btn)
  
    
# adds value listeners to all buttons (_btns) in the passed cls
# functions must be called "_on_<name>_btn_down" or "_on_<name>_btn_up"
def add_btn_value_listeners(cls):
  btn_tasks = getattr(cls, "_btn_tasks", False)
  update = getattr(cls, "update", False)
  if not btn_tasks:
    cls._btn_tasks = Task.TaskGroup(auto_kill=False)
    cls._add_btn_task = __add_btn_task
    def update_override():
      cls._btn_tasks.update(0.1)
      update()
    cls.update = update_override

  for name in cls._btns:
    btn = cls._btns[name]
    def callback(cls, name, value):
      assert isinstance(value, int)
      assert isinstance(btn, ButtonElement)
      if value == 127:
        down_handler = getattr(cls, "_on_" + name + "_btn_down", False)
        if callable(down_handler):
          down_handler()
    
        hold_handler = getattr(cls, "_on_" + name + "_btn_hold", False)
        if callable(hold_handler):
          cls._add_btn_task(cls, settings.btn_hold_down_ticks, hold_handler)

      else:
        cls._btn_tasks.clear()
        up_handler = getattr(cls, "_on_" + name + "_btn_up", False)
        if callable(up_handler):
          up_handler()

    btn.add_value_listener(partial(callback, cls, name))
    
# adds value listeners to all sliders (_sliders) in the passed cls
# function must be called "_on_<name>_slider_change"
def add_slider_value_listeners(cls):
  for name in cls._sliders:
    slider = cls._sliders[name]
    def callback(cls, name, value):
      assert isinstance(value, int)
      assert isinstance(slider, SliderElement)
      handler = getattr(cls, "_on_" + name + "_slider_change", False)
      if callable(handler):
        handler(value)

    slider.add_value_listener(partial(callback, cls, name))
    
# adds value listeners to all knobs (_knobs) in the passed cls
# function must be called "_on_<name>_knob_change"
def add_knob_value_listeners(cls):
  for name in cls._knobs:
    knob = cls._knobs[name]
    def callback(cls, name, value):
      assert isinstance(value, int)
      assert isinstance(knob, EncoderElement)
      handler = getattr(cls, "_on_" + name + "_knob_change", False)
      if callable(handler):
        handler(value)

    knob.add_value_listener(partial(callback, cls, name))
      
# turns all buttons (_btns) off within in the passed cls
def turn_btns_off(cls):
  for btn in cls._btns.values():
    btn.send_value(0, True)

# sets data to the song obj
def set_data(cls, key, value):
  Live.Song.Song.set_data(cls.song, "_NKL_." + key, value)

# gets data from the song obj
def get_data(cls, key, default):
  return Live.Song.Song.get_data(cls.song, "_NKL_." + key, default)