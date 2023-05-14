#!/usr/bin/python3

import math
import yaml
import numpy

import naive_parser
import getCountryNames
import properties
from config import Config
from logToFile import Logger


class Event:
    def __init__(self, event_type, *tags):
        self.event_type = event_type
        self.tags = tags

    def __str__(self):
        printstring = self.event_type + " "
        for tag in self.tags:
            printstring += tag + " "
        return printstring

    def __eq__(self, other):
        return self.event_type == other.event_type

    def __lt__(self, other):
        return self.event_type < other.event_type


class Empire:
    def __init__(self, nation):
        self.nation = nation
        self.tag = self.nation.tag
        self.score = self.nation.points
        self.population = self.nation.population
        self.industry = self.nation.industry
        self.government = self.nation.government
        self.ideology = self.nation.ideology
        self.climate = self.nation.climate
        self.culture = self.nation.culture
        self.nuclear = False
        self.color = "Red"

        self.planet_class = "pc_arid"
        self.penalty = 0
        self.planet_size = 10
        self.planet_population = 1
        self.tile_blockers = 8

    def long_tag(self):
        return self.tag + "_" + self.government

    def go_into_space(self):
        if self.industry > 0.6:
            self.planet_class = "pc_continental"
        elif self.industry > 0.4:
            if self.climate in ["pc_arid", "pc_desert", "pc_savannah"]:
                self.planet_class = "pc_tropical"
            else:
                self.planet_class = "pc_ocean"
        else:
            self.planet_class = self.climate

        popweight = (self.population + self.population + self.industry) / 3.0
        indweight = (self.population + self.industry + self.industry) / 3.0
        self.planet_size = 10 + math.floor(10 * popweight)
        self.planet_population = max(1, math.floor(8 * self.population))
        self.tile_blockers = 10 - (9 * math.floor(indweight))

        if self.score < 0.1:
            self.penalty = 4
        elif self.score < 0.2:
            self.penalty = 3
        elif self.score < 0.4:
            self.penalty = 2
        elif self.score < 0.6:
            self.penalty = 1

    def __str__(self):
        printstring = self.tag + ": "
        printstring += self.planet_class + ". "
        printstring += "Size {}, population {}, {} tile blockers. {}0% penalty.".format(
            self.planet_size, self.planet_population, self.tile_blockers, self.penalty)

        return (printstring)


class Universe:
    def __init__(self, savefile):
        self.savefile = savefile
        self.hoi4path = Config().get_hoi4_path()
        with open("files/Events.yml", encoding="utf-8") as stream:
            self.event_strings = yaml.safe_load(stream)

    def load(self):
        parser = naive_parser.Parser(self.savefile)
        self.top_nations = parser.get_top_nations()
        self.small_nations = parser.get_small_nations()
        self.gini = parser.get_gini_coeff()
        self.total_score = parser.get_total_score()

        self.seed = int(naive_parser.drill(self.savefile, "game_unique_seed"))
        current_date = naive_parser.drill(self.savefile, "date")
        current_date = current_date.replace('"', '')
        self.current_date = [int(n) for n in current_date.split(".")]

        self.defcon = Config().defcon_results
        if self.defcon:
            self.create_events_from_defcon()
        else:
            self.create_events()

    def create_events_from_defcon(self):
        self.events = []
        climate_change = 0
        self.earth_owned_by = ""
        self.climate_authority = ""
        self.earth_type = "pc_continental"

        self.empires = []
        for nation in self.top_nations:
            self.empires.append(Empire(nation))

        self.nuclear_war = 2

        nuclear_tags = []
        for empire in self.empires:
            if empire.tag in self.defcon.keys():
                empire.nuclear = True
                # No need to add population penalties here - the parser's already taken care of that
                nuclear_tags.append(empire.tag)

        self.events.append(Event("DefconColdWar"))
        self.events.append(Event("DefconNuclearWar"))

        self.add_climate_events()

    def create_events(self):
        self.events = []
        climate_change = 0
        self.nuclear_war = 0
        self.earth_owned_by = ""
        self.climate_authority = ""
        self.earth_type = "pc_continental"

        self.empires = []
        for nation in self.top_nations:
            self.empires.append(Empire(nation))

        if len(self.empires) == 1:
            self.events.append(Event("Hegemon", self.empires[0].tag))
            self.earth_owned_by = self.empires[0].long_tag()
            self.climate_authority = self.empires[0].tag

        elif self.empires[0].score / self.total_score > 0.5:  # largest nation has 50%

            # next largest is pretty big
            if self.empires[1].score / self.empires[0].score > 0.5:
                self.events.append(
                    Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                self.events.append(
                    Event("MinorNuclearWar", self.empires[0].tag, self.empires[1].tag))
                self.events.append(
                    Event("MinorNuclearWarLose", self.empires[1].tag))
                self.events.append(
                    Event("MinorNuclearWarWin", self.empires[0].tag))

                self.nuclear_war = 1
                self.earth_owned_by = self.empires[0].long_tag()
                self.empires[0].nuclear = True
                self.empires[1].nuclear = True
                self.empires[1].population *= 0.25

            else:  # next largest is pretty small
                self.events.append(
                    Event("EconomicCollapse", self.empires[1].tag))
                self.empires[1].industry *= 0.75
                self.events.append(Event("Hegemon", self.empires[0].tag))
                self.earth_owned_by = self.empires[0].long_tag()

        else:  # largest nation does not have 50%

            if self.empires[0].score / self.total_score > 0.3:  # someone's large-ish
                # next largest is pretty big
                if self.empires[1].score / self.empires[0].score > 0.5:
                    if len(self.empires) == 2:  # only two nations
                        self.events.append(
                            Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                    # and next after that is pretty big too
                    elif (self.empires[2].score / self.empires[1].score > 0.5):
                        self.events.append(
                            Event("EconomicProblems", self.empires[2].tag))
                        self.empires[2].industry *= 0.9
                        self.events.append(
                            Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                        self.events.append(
                            Event("ColdWarStaysCold", self.empires[0].tag, self.empires[1].tag))
                        self.events.append(Event("Squabbling"))
                    else:  # and next after that is pretty small
                        self.events.append(
                            Event("EconomicCollapse", self.empires[2].tag))
                        self.empires[2].industry *= 0.75
                        self.events.append(
                            Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                        if self.empires[0].government == self.empires[1].government and self.empires[0].government != "fascist":
                            self.events.append(
                                Event("ColdWarStaysCold", self.empires[0].tag, self.empires[1].tag))
                            self.events.append(Event("Squabbling"))
                        else:
                            self.events.append(
                                Event("NuclearWar", self.empires[0].tag, self.empires[1].tag))
                            self.nuclear_war = 2
                            self.events.append(
                                Event("NuclearWarLose", self.empires[0].tag, self.empires[1].tag))
                            self.empires[0].nuclear = True
                            self.empires[1].nuclear = True
                            self.empires[0].population *= 0.25
                            self.empires[1].population *= 0.25

                else:  # next largest is pretty small
                    self.events.append(
                        Event("EconomicCollapse", self.empires[1].tag))
                    self.empires[1].industry *= 0.75
                    self.events.append(Event("Hegemon", self.empires[0].tag))
                    self.earth_owned_by = self.empires[0].long_tag()

            else:  # everyone's tiny
                self.events.append(Event("Squabbling"))

        self.add_climate_events()

    def add_climate_events(self):
        climate_change = 0
        if self.gini > 0.4:
            if self.climate_authority:
                self.events.append(
                    Event("GovernmentClimateControl", climateAuthority))
            elif self.gini > 0.6:
                climate_change = 2
            else:
                climate_change = 1
        else:
            self.events.append(Event("CleanIndustrialization"))

        self.events.append(Event("Migrations"))

        if self.nuclear_war == 2:
            self.events.append(Event("TombWorld"))
            self.events.append(Event("EscapeLaunches"))
            self.earth_type = "pc_nuked"
        elif self.nuclear_war == 1:
            if climate_change == 0:
                self.events.append(Event("NuclearWinter"))
                self.events.append(Event("EscapeLaunches"))
                self.earth_type = "pc_arctic"
            elif climate_change == 1:
                self.events.append(Event("SeaLevelsRise"))
                self.events.append(Event("Launches"))
                self.earth_type = "pc_ocean"
            elif climate_change == 2:
                self.events.append(Event("NuclearIndustrialDesert"))
                self.events.append(Event("EscapeLaunches"))
                self.earth_type = "pc_desert"
        else:
            if climate_change == 0:
                self.earth_type = "pc_continental"
                self.events.append(Event("Launches"))
                pass
            elif climate_change == 1:
                self.events.append(Event("SeaLevelsRise"))
                self.events.append(Event("Launches"))
                self.earth_type = "pc_ocean"
            elif climate_change == 2:
                self.events.append(Event("GlobalWarming"))
                self.events.append(Event("EscapeLaunches"))
                self.earth_type = "pc_arid"

        # for event in self.events:
        #    print(event)

        color_map = properties.get_colors()

        for empire in self.empires:

            if empire.tag in color_map:
                empire.color = color_map[empire.tag]

            empire.go_into_space()

        # for empire in self.empires:
        #    print(empire)

    def get_history(self):

        tag_to_name = {}
        tag_to_adj = {}
        city_names = getCountryNames.get_city_names()
        country_names = getCountryNames.get_country_names()
        for empire in self.top_nations + self.small_nations:
            tag_blank = empire.long_tag()
            tag_def = empire.long_tag() + "_DEF"
            tag_adj = empire.long_tag() + "_ADJ"

            if tag_def in country_names:
                name = country_names[tag_def]
            else:
                name = country_names[tag_blank]
            name = name.replace("The", "the")
            tag_to_name[empire.tag] = name

            if tag_adj in country_names:
                adj = country_names[tag_adj]
            else:
                adj = country_names[tag_blank]
            tag_to_adj[empire.tag] = adj

        numpy.random.seed(self.seed)

        start_year = self.current_date[0] + 5
        end_year = 2200

        year_range = end_year - start_year
        event_count = numpy.random.randint(8, 12)

        nation_count = len(self.top_nations) + len(self.small_nations)
        if nation_count == 1:  # only one nation - so events about "nations" won't make much sense
            delete_keys = []
            for key in self.event_strings:
                if "nation" in self.event_strings[key].lower():
                    delete_keys.append(key)
            for key in delete_keys:
                del self.event_strings[key]

        real_events = []
        for event in self.events:
            if event.event_type in self.event_strings:
                real_events.append(Event(event.event_type, *event.tags))

            if event.event_type + "0" in self.event_strings:
                real_events.append(Event(event.event_type + "0", *event.tags))

            for i in range(1, 10):
                if event.event_type + str(i) in self.event_strings and (numpy.random.random() < 0.7):
                    real_events.append(
                        Event(event.event_type + str(i), *event.tags))

        random_event_count = event_count - len(real_events)

        random_event_keys = []
        for event_key in sorted(self.event_strings):
            if "Random" in event_key:
                random_event_keys.append(event_key)

        random_events = []
        skips = 0
        while len(random_events) < random_event_count:
            skips += 1
            if skips > 100:
                break
            chosen_event = Event(numpy.random.choice(random_event_keys))
            if chosen_event not in random_events:
                random_events.append(chosen_event)
        random_events.sort()

        if random_event_count > 0:
            jump = event_count // random_event_count
            insert_point = 2 - jump
            if jump == 1:
                insert_point = 0
            for random_event in random_events:
                insert_point += jump
                real_events.insert(insert_point, random_event)

        # Tried just having linear gaps between years; it doesn't feel right. We
        # need a pretty dense cold-war 20th century and a pretty sparse 22nd
        # century. Log scales to the rescue!
        log_nudge = 80
        year_log_scale = numpy.logspace(
            numpy.log10(log_nudge), numpy.log10(
                year_range + log_nudge), num=len(real_events) + 1)

        year_log_scale = [x - log_nudge for x in year_log_scale]

        defcon_results_text = ""
        if self.defcon:
            def score_sort(tag):
                try:
                    return self.defcon[tag].score
                except AttributeError:
                    return 0

            survivor_tags = []
            ok_tags = []
            oblit_tags = []
            for tag in sorted(self.defcon, key=score_sort):
                if not type(tag) is str:
                    continue
                survivors = float(naive_parser.drill(
                    self.defcon, tag, "survivors"))
                if survivors > 80:
                    survivor_tags.append(tag)
                elif survivors > 40:
                    ok_tags.append(tag)
                else:
                    oblit_tags.append(tag)

            # We've only got 3 "survived" messages and 2 "is basically ok" messages.
            while len(survivor_tags) > 3:
                ok_tags.append(survivor_tags.pop())
            while len(ok_tags) > 2:
                ok_tags.pop()

            def name_of_tag_or_faction(name):
                if name in tag_to_name:
                    return tag_to_name[name]
                return "the "+name.title()

            for n in range(len(survivor_tags)):
                nation_name = "the "+survivor_tags[n]
                if survivor_tags[n] in tag_to_name:
                    nation_name = tag_to_name[survivor_tags[n]]

                defcon_results_text += self.event_strings["DefconSurvive"+str(
                    n+1)] + " "
                defcon_results_text = defcon_results_text.replace(
                    "&NATION_1&", name_of_tag_or_faction(survivor_tags[n]))

            for n in range(len(ok_tags)):
                defcon_results_text += self.event_strings["DefconOk"+str(
                    n+1)] + " "
                defcon_results_text = defcon_results_text.replace(
                    "&NATION_1&", name_of_tag_or_faction(ok_tags[n]))

            if len(oblit_tags) == 1:
                defcon_results_text += self.event_strings["DefconObliterated1"] + " "
                defcon_results_text = defcon_results_text.replace(
                    "&NATION_1&", name_of_tag_or_faction(oblit_tags[0]))
            elif len(oblit_tags) > 1:
                for n in range(len(oblit_tags)-1):
                    defcon_results_text += name_of_tag_or_faction(
                        oblit_tags[n]) + ", "
                defcon_results_text += "and " + \
                    self.event_strings["DefconObliteratedPl1"]
                defcon_results_text = defcon_results_text.replace(
                    "&NATION_1&", name_of_tag_or_faction(oblit_tags[-1]))

        history_string = ""

        for e in range(len(real_events)):
            year = int(numpy.floor(start_year + year_log_scale[e]))
            yearJump = (year_log_scale[e + 1] - year_log_scale[e]) // 2
            if yearJump > 1:
                year += numpy.random.randint(-yearJump // 2, yearJump // 2)
            if year < start_year:
                year = start_year + 1
            if year > end_year:
                year = end_year - 1
            event = real_events[e]
            Logger().log("debug", event)

            replaces = {}
            replaces["&YEAR&"] = str(year)
            replaces["&DECADE&"] = str(year // 10) + "0s"
            replaces["&NATION_1&"] = tag_to_name[event.tags[0]] if len(
                event.tags) > 0 else ""
            replaces["&NATION_2&"] = tag_to_name[event.tags[1]] if len(
                event.tags) > 1 else ""
            replaces["&NATION_3&"] = tag_to_name[event.tags[2]] if len(
                event.tags) > 2 else ""
            replaces["&NATION_4&"] = tag_to_name[event.tags[3]] if len(
                event.tags) > 3 else ""
            replaces["&NATION_5&"] = tag_to_name[event.tags[4]] if len(
                event.tags) > 4 else ""
            replaces["&NATION_6&"] = tag_to_name[event.tags[5]] if len(
                event.tags) > 5 else ""
            replaces["&NATION_1_ADJ&"] = tag_to_adj[event.tags[0]] if len(
                event.tags) > 0 else ""
            replaces["&NATION_2_ADJ&"] = tag_to_adj[event.tags[1]] if len(
                event.tags) > 1 else ""
            replaces["&NATION_3_ADJ&"] = tag_to_adj[event.tags[2]] if len(
                event.tags) > 2 else ""
            replaces["&NATION_4_ADJ&"] = tag_to_adj[event.tags[3]] if len(
                event.tags) > 3 else ""
            replaces["&NATION_5_ADJ&"] = tag_to_adj[event.tags[4]] if len(
                event.tags) > 4 else ""
            replaces["&NATION_6_ADJ&"] = tag_to_adj[event.tags[5]] if len(
                event.tags) > 5 else ""
            replaces["&DEFCONRESULTS&"] = defcon_results_text
            if len(city_names) > 0:
                replaces["&RANDOM_SMALL_CITY&"] = numpy.random.choice(
                    city_names)
            else:
                replaces["&RANDOM_SMALL_CITY&"] = "Vienna"

            if len(self.small_nations) > 0:
                replaces["&RANDOM_SMALL_NATION&"] = tag_to_name[numpy.random.choice(
                    self.small_nations).tag]
            else:
                replaces["&RANDOM_SMALL_NATION&"] = "Secret Denmark"

            eventline = self.event_strings[event.event_type]
            for replace_string in replaces:
                eventline = eventline.replace(
                    replace_string, replaces[replace_string])
            history_string += eventline + "\n"

        history_string = history_string.replace(". the", ". The")
        history_string = history_string.replace(": the", ": The")

        Logger().log("info", history_string)
        return history_string

    def get_earth_type_flag(self):
        if self.nuclear_war == 2:
            return "nuclear_war"
        elif self.earth_owned_by:
            return "give_planet"
        else:
            return "un_bureaucracy"

    def get_earth_owner(self):
        return self.earth_owned_by

    def get_earth_class(self):
        return self.earth_type

    def get_earth_entity(self):
        if self.earth_type == "pc_desert":
            return "variable_earth_desert_entity"
        if self.earth_type == "pc_arid":
            return "variable_earth_arid_entity"
        if self.earth_type == "pc_savannah":
            return "variable_earth_savannah_entity"
        if self.earth_type == "pc_tropical":
            return "variable_earth_tropical_entity"
        if self.earth_type == "pc_ocean":
            return "variable_earth_ocean_entity"
        if self.earth_type == "pc_tundra":
            return "variable_earth_tundra_entity"
        if self.earth_type == "pc_arctic":
            return "variable_earth_arctic_entity"
        if self.earth_type == "pc_alpine":
            return "variable_earth_alpine_entity"
        if self.earth_type == "pc_nuked":
            return "nuked_planet"
        return "continental_planet_earth_entity"

    def get_empires(self):
        return self.empires


if __name__ == "__main__":
    savefile = naive_parser.parse_save_file("postwar_1948_06_16_01.hoi4")

    universe = Universe(savefile)
    universe.load()

    for empire in universe.get_empires():
        print(empire)
