import Live
from functools import partial

from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import *

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
  for name in cls._btns:
    btn = cls._btns[name]
    def callback(cls, name, value):
      assert isinstance(value, int)
      assert isinstance(btn, ButtonElement)
      if value == 127:
        handler = getattr(cls, "_on_" + name + "_btn_down", False)
        if callable(handler):
          handler()
      else:
        handler = getattr(cls, "_on_" + name + "_btn_up", False)
        if callable(handler):
          handler()

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
  Live.Song.Song.set_data(cls._song, "_NKL_." + key, value)

# gets data from the song obj
def get_data(cls, key, default):
  return Live.Song.Song.get_data(cls._song, "_NKL_." + key, default)