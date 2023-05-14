#!/usr/bin/python3

import os
import re
import yaml
from config import Config


def get_country_names():
    country_name_yml_path = Config().get_modded_hoi4_file(
        "localisation/english/countries_mod_l_english.yml")
    if not os.path.exists(country_name_yml_path):
        country_name_yml_path = Config().get_modded_hoi4_file(
            "localisation/english/countries_l_english.yml")
        # Prior to HoI4 1.11, localization files for all languages are simply in the localisation/ folder
        if not os.path.exists(country_name_yml_path):
            country_name_yml_path = Config().get_modded_hoi4_file(
                "localisation/countries_mod_l_english.yml")
            if not os.path.exists(country_name_yml_path):
                country_name_yml_path = Config().get_modded_hoi4_file(
                    "localisation/countries_l_english.yml")

    try:
        yml_file = open(country_name_yml_path, encoding="utf-8")
    except BaseException:
        yml_file = open(country_name_yml_path)
    yml_data = yml_file.read()
    yml_data = "\n".join(yml_data.split("\n")[1:])[1:]

    yml_data = re.sub(r':[0-9]*', r':', yml_data)
    yml_data = re.sub(r'\n ', r'\n', yml_data)

    yml_data = yml_data.encode("ascii", errors="ignore")
    country_names = yaml.safe_load(yml_data)

#    if isinstance(countryNames, str):
#        # I have to do everything myself around here
#        countryNames = {}
#        for line in ymlData.split('\n'):
#            print(line)
#            tag = line.split(":")[0]
#            print(tag)
#            quotes = line.split("\"")
#            if len(quotes) == 2:
#                name = line.split("\"")[1]
#                print(name)
#                countryNames[tag] = name

    return country_names


def get_city_names():
    country_name_yml_path = Config().get_modded_hoi4_file(
        "localisation/english/victory_points_l_english.yml")
    if not os.path.exists(country_name_yml_path):
        # Prior to HoI4 1.11, localization files for all languages are simply in the localisation/ folder
        country_name_yml_path = Config().get_modded_hoi4_file(
            "localisation/victory_points_l_english.yml")

    try:
        yml_data = open(country_name_yml_path).read()
    except BaseException:
        data = open(country_name_yml_path, 'rb').read()
        yml_data = data.decode("utf8", "ignore")

    yml_data = "\n".join(yml_data.split("\n")[1:])[1:]

    yml_data = re.sub(r':[0-9]*', r':', yml_data)
    yml_data = re.sub(r'\n ', r'\n', yml_data)

    yml_data = yml_data.encode("ascii", errors="ignore")
    city_names = yaml.safe_load(yml_data)

    return list(city_names.values())
