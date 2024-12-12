#!/usr/bin/python3

import random
import naive_parser
import unicodedata
from config import Config
from logToFile import Logger
import os


def remove_accents(inputNames):
    output_names = []
    for name in inputNames:
        try:
            nfkd_form = unicodedata.normalize('NFKD', name)
            name = u"".join(
                [c for c in nfkd_form if not unicodedata.combining(c)])
            if any(c.isdigit() for c in name):
                continue
            name = name.encode('utf-8').decode('ascii')
            output_names.append(name)
        except UnicodeEncodeError:
            pass
        except UnicodeDecodeError:
            pass
    return output_names


def clunky_string_split(string):
    outputs = []
    current_output = ""
    quoted = False

    for char in string:
        if char == '"':
            quoted = not quoted
        elif char == " " and not quoted:
            outputs.append(current_output)
            current_output = ""
        else:
            current_output += char

    if current_output != "":
        outputs.append(current_output)
    return outputs


def stringlist_drill(*args):
    output = []
    the_strings = naive_parser.drill(*args)
    if the_strings:
        for line in the_strings['']:
            output += clunky_string_split(line)
    return output


def template_fill(data, filename, writefilename):
    for key in data:
        if isinstance(data[key], list):
            newdata = ""
            for entry in data[key]:
                newdata += '"{}" '.format(entry)
            data[key] = newdata

    filedata = open(filename).read()
    for key in data:
        filedata = filedata.replace(key, data[key])

    output = open(writefilename, 'w', encoding="utf-8")
    output.write(filedata)


def make_name_list(tag, destFolder):

    include_generic_unit_names = True

    names_path = Config().get_modded_hoi4_file("common/names/01_names.txt")
    if not names_path:
        names_path = Config().get_modded_hoi4_file("common/names/00_names.txt")
    Logger().log("info", "Reading names from " + names_path)
    names = naive_parser.parse_save_file(names_path)

    mod_unit_names_path = Config().get_modded_hoi4_file(
        "common/units/names/01_names.txt")
    if mod_unit_names_path:
        Logger().log("info", "Reading unit names from modded " + mod_unit_names_path)
        unitnames = naive_parser.parse_save_file(mod_unit_names_path)
        include_generic_unit_names = False
    else:
        special_unit_name_path = Config().get_modded_hoi4_file(
            "common/units/names/00_" + tag + "_names.txt")
        if not special_unit_name_path:
            special_unit_name_path = Config().get_modded_hoi4_file(
                "common/units/names/00_names.txt")
        Logger().log("info", "Reading unique unit names from " + special_unit_name_path)
        unitnames = naive_parser.parse_save_file(special_unit_name_path)

    malenames = stringlist_drill(names, tag, "male", "names")
    femalenames = stringlist_drill(names, tag, "female", "names")
    surnames = stringlist_drill(names, tag, "surnames")

    subs = stringlist_drill(unitnames, tag, "submarine", "unique")
    destroyers = stringlist_drill(unitnames, tag, "destroyer", "unique")
    light_cruisers = stringlist_drill(
        unitnames, tag, "light_cruiser", "unique")
    heavy_cruisers = stringlist_drill(
        unitnames, tag, "heavy_cruiser", "unique")
    battle_cruisers = stringlist_drill(
        unitnames, tag, "battle_cruiser", "unique")
    battleships = stringlist_drill(unitnames, tag, "battleship", "unique")
    carriers = stringlist_drill(unitnames, tag, "carrier", "unique")

    if include_generic_unit_names:
        subs += stringlist_drill(unitnames, tag, "submarine", "generic")
        destroyers += stringlist_drill(unitnames, tag, "destroyer", "generic")
        light_cruisers += stringlist_drill(unitnames,
                                           tag, "light_cruiser", "generic")
        heavy_cruisers += stringlist_drill(unitnames,
                                           tag, "heavy_cruiser", "generic")
        battle_cruisers += stringlist_drill(unitnames,
                                            tag, "battle_cruiser", "generic")
        battleships += stringlist_drill(unitnames,
                                        tag, "battleship", "generic")
        carriers += stringlist_drill(unitnames, tag, "carrier", "generic")

    planetnames = subs
    ships = destroyers + light_cruisers + heavy_cruisers + \
        battle_cruisers + battleships + carriers

    # Leave this in until I work out what accents Stellaris can't take
    ships = remove_accents(ships)
    planetnames = remove_accents(planetnames)
    malenames = remove_accents(malenames)
    femalenames = remove_accents(femalenames)
    surnames = remove_accents(surnames)

    if len(planetnames) < 20:
        extraplanets = ships[:]
        random.shuffle(extraplanets)
        planetnames += extraplanets

    Logger().log("debug", len(planetnames))

    template_data = {}
    template_data["&TAG&"] = tag
    template_data["&SHIPNAMES&"] = ships
    template_data["&PLANETNAMES&"] = planetnames
    template_data["&MALENAMES&"] = malenames
    template_data["&FEMALENAMES&"] = femalenames
    template_data["&SURNAMES&"] = surnames

    template_fill(template_data, 
                 os.path.join("files", "stellaris_name_list_template.txt"),
                 os.path.join(destFolder, f"{tag}_test.txt"))
