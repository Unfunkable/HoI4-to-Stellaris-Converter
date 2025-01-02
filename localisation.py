import os
import numpy
import getCountryNames
from config import Config


class Localisation:
    def __init__(self, theUniverse):
        self.savefile = Config().get_save_data()
        self.hoi4path = Config().get_hoi4_path()
        self.universe = theUniverse
        self.parser = Config().get_parser()

        self.localise()

    def localise(self):

        self.empire_names = {}

        country_names = getCountryNames.get_country_names()
        for empire in self.universe.empires:
            longtag = empire.long_tag()
            empire_name = country_names[longtag]
            empire_name = empire_name.replace("Empire", "Star Empire")
            if " " not in empire_name:
                if empire.government == "communism":
                    govs = [
                        "People's Republic of &",
                        "People's Republic of &",
                        "Socialist Republic",
                        "People's Democratic Republic of &",
                        "Planetary Republic",
                        "Democratic People's Republic",
                        "Republic of &",
                        "Union",
                        "Alliance of ^ Planets",
                        "&",
                        "Space &"]
                elif empire.government == "democratic":
                    govs = [
                        "Republic",
                        "Republic",
                        "Commonwealth",
                        "Union",
                        "United ^ Planets",
                        "Empire",
                        "United Worlds",
                        "Planetary Republic",
                        "Alliance of ^ Planets",
                        "&",
                        "Space &"]
                elif empire.government == "fascism":
                    govs = [
                        "Empire",
                        "Empire",
                        "Greater ^ Empire",
                        "Star Empire",
                        "Imperium",
                        "Hegemony",
                        "&",
                        "Space &",
                        "Planetary Empire"]
                else:
                    govs = [
                        "Empire",
                        "United Worlds",
                        "Planetary Alliance",
                        "Empire of ^ Planets",
                        "Alliance of ^ Planets",
                        "&",
                        "Space &"]

                country_name = empire_name
                country_adj = country_names[longtag + "_ADJ"]
                empire_name = numpy.random.choice(govs)
                if "&" in empire_name:
                    empire_name = empire_name.replace("&", country_name)
                elif "^" in empire_name:
                    empire_name = empire_name.replace("^", country_adj)
                else:
                    empire_name = country_adj + " " + empire_name
            self.empire_names[longtag] = empire_name

    def write_localisation(self):
        base = open(os.path.join(Config().converter_dir, "files", "convertertest_l_english.yml"),
                    encoding="utf-8").read()
        localisation = base
        for tag in self.empire_names:
            localisation += ' {}:0 "{}"\n'.format(tag, self.empire_names[tag])
        localisation += "\n"

        for tag in self.empire_names:
            localisation += ' NAME_{}:0 "{}"\n'.format(
                tag, self.empire_names[tag])
        localisation += "\n"

        for tag in self.empire_names:
            smalltag = tag.split("_")[0]
            localisation += ' name_list_{}_names:0 "{}"\n'.format(
                smalltag, self.empire_names[tag])
        localisation += "\n"

        history = self.universe.get_history()
        history = history.replace("\n", "\\n")
        localisation += ' START_SCREEN_CONVERTED:0 "{}"\n\n'.format(history)

        open("output/" + Config().get_mod_name() + "/localisation/convertertest_l_english.yml",
             "w", encoding="utf-8-sig").write(localisation)

    def write_synced_localisation(self):
        synced = "l_default:\n"
        for tag in self.empire_names:
            synced += ' NAME_{}: "{}"\n'.format(tag, self.empire_names[tag])
        synced += "\n"
        synced_file = open("output/" + Config().get_mod_name() +
                           "/localisation_synced/converter_names.yml", "w", encoding="utf-8-sig")
        # syncedFile.write(u'\ufeff')
        synced_file.write(synced)
