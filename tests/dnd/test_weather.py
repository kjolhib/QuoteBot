import pytest
import os

import classes.weather_data as wd
from exceptions.dnd import negative_count_error, weather_empty_error, weather_exists_error, weather_missing_error

"""
weather: testing the weather command, specifically dict operations
"""

TMP_PATH = os.path.join(os.path.dirname(__file__), "tmp_weather_probabilities.json")

@pytest.fixture
def weather():
  w = wd.WeatherData({"a": 0, "b": 0, "c": 0}, TMP_PATH)
  wd.save_weather(w, fp=TMP_PATH)
  return wd.load_weather(fp=TMP_PATH)

@pytest.fixture
def empty_weather():
  w = wd.WeatherData({}, fp=TMP_PATH)
  wd.save_weather(w, fp=TMP_PATH)
  return wd.load_weather(fp=TMP_PATH)

@pytest.fixture(autouse=True)
def cleanup():
  # before tests
  
  yield # test runs
  
  # after tests
  print("Cleaning up...")
  os.remove(TMP_PATH)

"""
increment_val
"""
def test_inc__valid(weather: wd.WeatherData):
  weather.increment_val("a")
  assert weather.data["a"] == 1

def test_inc__missing_invalid(weather: wd.WeatherData):
  with pytest.raises(weather_missing_error.WeatherMissingError):
    weather.increment_val("z")

def test_inc__missing_empty_invalid(empty_weather: wd.WeatherData):
  with pytest.raises(weather_missing_error.WeatherMissingError):
    empty_weather.increment_val("a")

"""
select_weighted_random
"""
def test_random__valid(weather: wd.WeatherData):
  chosen = weather.select_weighted_random()
  weather.increment_val(chosen)
  assert 1 in weather.data.values()

def test_random__empty_invalid(empty_weather: wd.WeatherData):
  with pytest.raises(weather_empty_error.WeatherEmptyError):
    empty_weather.select_weighted_random()

"""
load_weather
"""
def test_load_weather__valid():
  data = wd.load_weather(fp=TMP_PATH) # should assign the init data to this new temp file
  assert data.data == wd.get_init_data().data
    
def test_load_weather__valid_already_exists(weather: wd.WeatherData):
  tmp_ = os.path.join(os.path.dirname(__file__), "tmp_weather_probabilities2.json")
  new_data = wd.load_weather(fp=tmp_)
  chosen = new_data.select_weighted_random() # select something just so it will be different from init data
  new_data.increment_val(chosen)
  assert 1 in new_data.data.values()
  wd.save_weather(new_data, fp=tmp_)
  
  updated_data = wd.load_weather(fp=tmp_)
  assert 1 in updated_data.data.values()
  assert weather.data != updated_data.data

  os.remove(tmp_)

"""
save_weather
"""
def test_save_weather__valid(weather: wd.WeatherData):
  old = wd.load_weather(TMP_PATH).data
  chosen = weather.select_weighted_random()
  weather.increment_val(chosen)
  assert chosen in weather.data.keys() # we chose some random key
  assert weather.data[chosen] == 1 # some chosen key has value 1
  wd.save_weather(weather, fp=TMP_PATH) # save the newly updated json
  new = wd.load_weather(TMP_PATH).data
  assert 1 in new.values()
  assert old != new

"""
reset_json
"""
def test_reset_weather__valid(weather: wd.WeatherData):
  # sim a roll
  chosen = weather.select_weighted_random()
  weather.increment_val(chosen)
  wd.save_weather(weather, fp=TMP_PATH)
  old = wd.load_weather(fp=TMP_PATH)
  
  # reset
  wd.reset_json(fp=TMP_PATH)
  new = wd.load_weather(fp=TMP_PATH)

  assert old.data != new.data

"""
reset_data
"""
def test_reset_data__valid(weather: wd.WeatherData):
  # get old data before resetting data
  chosen = weather.select_weighted_random()
  weather.increment_val(chosen)
  old_data = weather.data

  weather.reset_data()

  # get new data after resetting data
  new_data = weather.data
  assert old_data != new_data
  assert 1 in old_data.values()
  assert 1 not in new_data.values()


"""
add_new_weather
"""
def test_add_weather__valid(empty_weather: wd.WeatherData):
  empty_weather.add_new_weather("a")
  assert empty_weather.data
  assert empty_weather.data["a"] == 0

@pytest.mark.parametrize("s", ["a", "b", "c"])
def test_add_weather__exists_invalid(weather: wd.WeatherData, s: str):
  with pytest.raises(weather_exists_error.WeatherExistsError):
    weather.add_new_weather(s)


"""
remove_weather
"""
def test_remove_weather__valid(weather: wd.WeatherData):
  weather.remove_weather("a")
  assert len(weather.data.keys()) == 2 # ["b": 0, "c": 0]
  assert "a" not in weather.data.keys()

def test_remove_weather__missing_invalid(weather: wd.WeatherData):
  with pytest.raises(weather_missing_error.WeatherMissingError):
    weather.remove_weather("f")

"""
modify_data
"""
def test_modify_data__valid(weather: wd.WeatherData):
  weather.modify_weather("a", 100)
  assert weather.data["a"] == 100

def test_modify_data__negative_invalid(weather: wd.WeatherData):
  with pytest.raises(negative_count_error.NegativeCountError):
    weather.modify_weather("a", -5)

def test_modify_data__missing_invalid(empty_weather: wd.WeatherData):
  with pytest.raises(weather_missing_error.WeatherMissingError):
    empty_weather.modify_weather("a", 40)

"""
statistics
"""
def test_statistics__valid(weather: wd.WeatherData):
  chosen = weather.select_weighted_random()
  weather.increment_val(chosen)
  s = weather.statistics()
  assert s.total_rolls != 0
  assert s.most_common != "N/A"
  assert s.least_common != "N/A"

def test_statistics__empty_valid(empty_weather: wd.WeatherData):
  s = empty_weather.statistics()
  assert s.total_rolls == 0
  assert not s.percentages
  assert s.most_common == "N/A"
  assert s.least_common == "N/A"

