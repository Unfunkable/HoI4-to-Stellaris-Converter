import os
import naive_parser
from config import Config
from logToFile import Logger


class Dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Events:
    def __init__(self, the_universe):
        self.savefile = Config().get_save_data()
        self.hoi4path = Config().get_hoi4_path()
        self.universe = the_universe
        self.parser = Config().get_parser()

        self.text_start = open(os.path.join(Config().converter_dir, "files", "converter_events_start.txt")).read()
        self.text_planet = open(os.path.join(Config().converter_dir, "files", "converter_events_planet.txt")).read()
        self.text_give_earth = open(
            os.path.join(Config().converter_dir, "files", "converter_events_give_earth.txt")).read()
        self.text_opinion_penalty = open(
            os.path.join(Config().converter_dir, "files", "converter_events_opinionpenalty.txt")).read()
        self.text_new_human = open(
            os.path.join(Config().converter_dir, "files", "converter_events_newhuman.txt")).read()
        self.text_option = open(os.path.join(Config().converter_dir, "files", "converter_events_option.txt")).read()
        self.text_starbase = open(os.path.join(Config().converter_dir, "files", "converter_events_starbase.txt")).read()

    def makeEvents(self):
        event = self.text_start

        empires = self.universe.get_empires()

        self.earth_type_flag = self.universe.get_earth_type_flag()
        self.earth_owner = self.universe.get_earth_owner()
        self.earth_class = self.universe.get_earth_class()
        self.earth_entity = self.universe.get_earth_entity()

        if not self.earth_owner:
            self.earth_owner = "nobody"

        planets_string = ""
        for e in range(len(empires)):
            empire = empires[e]
            planets_string += self.make_planet(empire, e)

        opinion_penalties = ""
        for judged_empire in empires:
            if not judged_empire.nuclear:
                continue
            for opinionated_empire in empires:
                new_penalty = self.text_opinion_penalty
                new_penalty = new_penalty.replace(
                    "&LONGTAG_OPINIONATED&", opinionated_empire.long_tag())
                new_penalty = new_penalty.replace(
                    "&LONGTAG_JUDGED&", judged_empire.long_tag())
                opinion_penalties += new_penalty

        options_string = ""
        for empire in empires:
            option = self.text_option.replace("&LONGTAG&", empire.long_tag())
            options_string += option

        event = event.replace("&EARTH_TYPE_FLAG&", self.earth_type_flag)
        event = event.replace("&EARTH_OWNER_LONGTAG&", self.earth_owner)
        event = event.replace("&EARTH_PC_TYPE&", self.earth_class)
        event = event.replace("&EARTH_ENTITY&", self.earth_entity)
        event = event.replace("&PLANETS&", planets_string)
        event = event.replace("&OPINION_PENALTIES&", opinion_penalties)
        event = event.replace("&OPTIONS&", options_string)

        open("output/" + Config().get_mod_name() +
             "/events/converter_events.txt", "w").write(event)

    def make_planet(self, empire, idnumber):
        if idnumber > 6:
            return ""
        planet = self.text_planet

        '''
            &PLANET_ID& : planet_1_1
            &PLANET_SIZE_DELTA& : -2
            &PLANET_PC_TYPE& : pc_continental
            &OWNER_TAG& : SOV
            &OWNER_LONGTAG& : SOV_communism

            &AUTHORITY& : auth_dictatorial
            &ETHICS& : ethic = "ethic_xenophobe" \n ethic = "ethic_authoritarian" \n ethic = "ethic_materialist"
            &CIVICS& : civic = civic_police_state \n civic = civic_functional_architecture

            &COLOUR& : red
            &MODIFIER& : converted_2_nuclear
            &NEW_HUMANS& : converter_events_newhuman.txt repeated
            &STARBASE& : converter_events_starbase.txt

            &MINERALS& : 1000
            &ENERGY& : 1000
            &FOOD& : 150
            &INFLUENCE& : 500
        '''

        planet_id = "planet_" + \
            str(1 + (idnumber // 3)) + "_" + str(1 + (idnumber % 3))
        planet_size_delta = str(empire.planet_size - 16)
        planet_pc_type = empire.planet_class
        owner_tag = empire.tag
        owner_longtag = empire.long_tag()

        government = self.get_government(empire)

        color = empire.color
        modifier = f"converted_{str(empire.penalty)}_"
        if empire.nuclear:
            modifier += "nuclear"
        else:
            modifier += empire.government
        if empire.culture:
            self.add_culture_modifier(empire.culture)
            culture = f"add_modifier = {{ modifier = \"{empire.culture}\" days = -1 }}"
        else:
            culture = "none"
        humancount = empire.planet_population - 3

        minerals = "100"
        energy = "100"
        food = "200"
        influence = "100"
        alloys = "100"
        goods = "100"

        ethics_string = ""
        for ethic in government.ethics:
            ethics_string += 'ethic = "{}" '.format(ethic)
        civics_string = ""
        for civic in government.civics:
            civics_string += 'civic = "{}" '.format(civic)

        human_string = ""
        for i in range(humancount):
            human_string += self.text_new_human

        starbase_string = ""
        if self.earth_owner != empire.long_tag():
            starbase_string += self.text_starbase

        planet = planet.replace("&PLANET_ID&", planet_id)
        planet = planet.replace("&PLANET_SIZE_DELTA&", planet_size_delta)
        planet = planet.replace("&PLANET_PC_TYPE&", planet_pc_type)
        planet = planet.replace("&OWNER_TAG&", owner_tag)
        planet = planet.replace("&OWNER_LONGTAG&", owner_longtag)
        planet = planet.replace("&AUTHORITY&", government.authority)
        planet = planet.replace("&ETHICS&", ethics_string)
        planet = planet.replace("&CIVICS&", civics_string)
        planet = planet.replace("&COLOUR&", color)
        planet = planet.replace("&MODIFIER&", modifier)
        if culture == "none":
            planet = planet.replace("&CULTURE&", "")
        else:
            planet = planet.replace("&CULTURE&", culture)
        planet = planet.replace("&NEW_HUMANS&", human_string)
        planet = planet.replace("&STARBASE&", starbase_string)
        planet = planet.replace("&MINERALS&", minerals)
        planet = planet.replace("&ENERGY&", energy)
        planet = planet.replace("&FOOD&", food)
        planet = planet.replace("&INFLUENCE&", influence)
        planet = planet.replace("&ALLOYS&", alloys)
        planet = planet.replace("&GOODS&", goods)

        return planet

    def get_government(self, empire):
        government_set = naive_parser.parse_save_file(
            Config().get_government_mapping())

        empire.ideology = empire.ideology.replace("_neutral", "")
        government = Dotdict({})

        if naive_parser.drill(government_set, "governments", empire.ideology):
            government.authority = naive_parser.drill(
                government_set, "governments", empire.ideology, "authority")
            government.ethics = naive_parser.splitstrings(naive_parser.drill(
                government_set, "governments", empire.ideology, "ethics", ""))
            government.civics = naive_parser.splitstrings(naive_parser.drill(
                government_set, "governments", empire.ideology, "civics", ""))

        else:
            Logger().log("warning", "Did not recognise " + empire.long_tag() + "'s \"" +
                  empire.ideology + "\" ideology. Falling back to generic democracy.")

            government.authority = "auth_democratic"
            government.ethics = ["ethic_egalitarian",
                                 "ethic_pacifist", "ethic_xenophobe"]
            government.civics = [
                "civic_parliamentary_system", "civic_environmentalist"]

        return government

    def add_culture_modifier(self, culture):
        static_modifier = f"{culture} = {{}} \n"
        open(f"output/{Config().get_mod_name()}/common/static_modifiers/converted_culture_modifiers.txt",
             "a").write(static_modifier)
