#!/usr/bin/python

import os
import math
import re
import colorsys

import naive_parser
import config
from logToFile import Logger


def color_distance(hsv1, hsv2):

    hue_distance = min(abs(hsv2[0] - hsv1[0]), 1 - abs(hsv2[0] - hsv1[0]))
    sat_distance = abs(hsv2[1] - hsv1[1])
    val_distance = abs(hsv2[2] - hsv1[2])

    return math.sqrt(hue_distance * hue_distance + sat_distance * sat_distance + val_distance * val_distance)


def get_colors():
    hoi4_color_data = naive_parser.parse_save_file(
        config.Config().get_modded_hoi4_file("common/countries/colors.txt"))
    stellaris_grey_data = {
        "grey": [0.65, 0.05, 0.35],
        "dark_grey": [0.65, 0.05, 0.22],
        "black": [0.5, 0.3, 0.05]
    }
    stellaris_color_data = {
        "grey": [0.65, 0.05, 0.35],
        "dark_grey": [0.65, 0.05, 0.22],
        "black": [0.5, 0.3, 0.05],
        "dark_brown": [0.07, 0.6, 0.23],
        "brown": [0.07, 0.6, 0.4],
        "beige": [0.1, 0.4, 0.6],
        "yellow": [0.11, 0.8, 0.8],
        "light_orange": [0.09, 1.0, 0.8],
        "orange": [0.06, 0.9, 0.7],
        "red_orange": [0.01, 0.75, 0.7],
        "red": [0.0, 0.95, 0.5],
        "burgundy": [0.95, 0.8, 0.35],
        "pink": [0.88, 0.61, 0.5],
        "purple": [0.74, 0.65, 0.61],
        "dark_purple": [0.74, 0.71, 0.37],
        "indigo": [0.71, 0.85, 0.5],
        "dark_blue": [0.64, 0.85, 0.45],
        "blue": [0.64, 0.7, 0.6],
        "light_blue": [0.6, 0.6, 0.7],
        "turquoise": [0.49, 0.6, 0.6],
        "dark_teal": [0.5, 0.6, 0.3],
        "teal": [0.42, 0.6, 0.5],
        "light_green": [0.35, 0.5, 0.60],
        "green": [0.32, 0.6, 0.40],
        "dark_green": [0.33, 0.6, 0.27],
    }

    hsv_set = {}
    name_set = {}
    for tag in hoi4_color_data:
        color = naive_parser.drill(hoi4_color_data, tag, "color", "")
        rgb = ("." not in color)
        if color == "":
            color = "255 255 255"
        color = [float(x) for x in color.replace("  ", " ").split(" ")]

        if rgb:
            color = list(colorsys.rgb_to_hsv(*color))
            color[2] = color[2] / 255

        hsv_set[tag] = color

        min_dist = 9999
        best_color = "red"

        if color[1] < 0.2:
            color_data = stellaris_grey_data
        else:
            color_data = stellaris_color_data

        for stellaris_color in color_data:
            stellaris_hsv = color_data[stellaris_color]
            new_dist = color_distance(color, stellaris_hsv)
            if new_dist < min_dist:
                min_dist = new_dist
                best_color = stellaris_color

        name_set[tag] = best_color

    return name_set


def get_states():
    state_map = {}

    statepath = config.Config().get_modded_hoi4_file("history/states/")
    for filename in os.listdir(statepath):
        state_data = open(statepath + filename).read()

        state_data = state_data.replace("=\n{", "={")
        state_data = state_data.replace("=\n\t{", "={")
        state_data = state_data.replace("=\n\t\t{", "={")
        state_data = state_data.replace("=\n\t\t\t{", "={")
        state_data = state_data.replace("=\n\t\t\t\t{", "={")

        state_data = re.sub(r"#[^\n]*?\n", r"\n", state_data)

        if not state_data:
            continue

        state = naive_parser.parse_save_data(state_data)

        if 0 == len(state.keys()):
            Logger().log(
                "warning", f"\"{statepath}{filename} +\" could not be parsed. Skipping.")
            continue
        state_id = int(naive_parser.drill(state, "state", "id"))
        provinces = naive_parser.drill(
            state, "state", "provinces", "").split(" ")

        province_ids = []
        for province in provinces:
            if not province:
                continue
            province_ids.append(int(province))

        for province in province_ids:
            state_map[province] = state_id

    return state_map


def get_climates():

    climate_map = {}
    state_map = get_states()

    strategic_regions_path = config.Config().get_modded_hoi4_file("map/strategicregions/")
    for filename in os.listdir(strategic_regions_path):
        climate_data = naive_parser.parse_save_file(
            strategic_regions_path + filename)
        provinces = naive_parser.drill(
            climate_data, "strategic_region", "provinces", "").split(" ")
        periodses = naive_parser.drill(
            climate_data, "strategic_region", "weather")
        if "period" not in periodses:
            continue
        periods = periodses["period"]
        year_temperatures = []
        year_rain = []
        year_snow = []
        year_sand = []

        if len(periods) == 0:
            continue

        for period in periods:
            temperature_range = naive_parser.drill(
                period, "temperature", "").split(" ")
            max_temp = temperature_range[1].replace("\"", "")
            min_temp = temperature_range[0].replace("\"", "")
            temperature = float(max_temp) - float(min_temp)
            year_temperatures.append(temperature)

            light_rain = naive_parser.unquote(
                naive_parser.drill(period, "rain_light"))
            heavy_rain = naive_parser.unquote(
                naive_parser.drill(period, "rain_heavy"))
            snow = naive_parser.unquote(naive_parser.drill(period, "snow"))
            blizzard = naive_parser.unquote(
                naive_parser.drill(period, "blizzard"))
            sandstorm = naive_parser.unquote(
                naive_parser.drill(period, "sandstorm"))

            year_rain.append(float(light_rain) + float(heavy_rain) * 2)
            year_snow.append(float(snow) + float(blizzard) * 3)
            year_sand.append(float(sandstorm))

        avg_temp = sum(year_temperatures) / len(year_temperatures)
        avg_rain = sum(year_rain) / len(year_rain)
        avg_snow = sum(year_snow) / len(year_snow)
        avg_sand = sum(year_sand) / len(year_sand)

        climate = "pc_arid"
        if avg_sand > 0.05:
            climate = "pc_desert"
        elif avg_snow > 0.3:
            climate = "pc_arctic"
        elif avg_snow > 0.1:
            climate = "pc_tundra"
        elif avg_temp > 10.0:
            climate = "pc_arid"
        elif avg_temp < 4.7:
            climate = "pc_savannah"
        else:
            climate = "pc_alpine"

        for province in provinces:
            if not province:
                continue
            provinceId = int(province)
            if provinceId in state_map:
                stateId = state_map[provinceId]
                climate_map[stateId] = climate

    return climate_map


if __name__ == "__main__":
    c = get_states()
