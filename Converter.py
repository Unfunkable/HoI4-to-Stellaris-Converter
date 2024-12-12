#!/usr/bin/python3
import shutil
import os

from config import Config
import makeNameList
import flagconvert
import localisation
import universe
import events

from logToFile import Logger


class Converter:
    def __init__(self):
        Config().init()

    def convert_everything(self):
        self.make_folders()
        self.get_universe()
        self.convert_flags()
        self.convert_name_lists()
        self.convert_localisation()
        self.convert_events()

    def make_folders(self):
        Logger().log("info", "Laying out folder structure...")
        shutil.rmtree(Config().get_output_path(), True)
        shutil.copytree(Config().get_base_mod_path(),
                        Config().get_output_path())
        shutil.copy(Config().get_descriptor_file(), Config().get_output_path())
        Logger().log("progress", "36%")

    def get_universe(self):
        Logger().log("info", "Creating the universe...")
        self.universe = universe.Universe(Config().get_save_data())
        Logger().log("progress", "45%")
        Logger().log("info", "Establishing history...")
        self.universe.load()
        Logger().log("progress", "54%")

    def convert_flags(self):
        hoi4flagpath = "gfx/flags/"
        top_nations = Config().get_parser().get_top_nations()

        for top_nation in top_nations:
            Logger().log("info", f"Creating flag for {top_nation.tag}...")
            sourcepath = os.path.join(hoi4flagpath, f"{top_nation.tag}_{top_nation.government}.tga")
            source_flag_tga = Config().get_modded_hoi4_file(sourcepath)
            if not source_flag_tga:
                basesourcepath = os.path.join(hoi4flagpath, f"{top_nation.tag}.tga")
                Logger().log("warning",
                             f"Could not find \"{sourcepath}\". Falling back to \"{basesourcepath}\"")
                source_flag_tga = Config().get_modded_hoi4_file(basesourcepath)
            dest_flag_folder = os.path.join(Config().get_output_path(), "flags", "convertedflags")
            flagconvert.compile_flag(source_flag_tga, dest_flag_folder)
        Logger().log("progress", "63%")

    def convert_name_lists(self):
        top_nations = Config().get_parser().get_top_nations()
        for top_nation in top_nations:
            Logger().log("info", f"Creating name list for {top_nation.tag}...")
            dest_name_list_folder = os.path.join("output", Config().get_mod_name(), "common", "name_lists")
            makeNameList.make_name_list(top_nation.tag, dest_name_list_folder)
        Logger().log("progress", "72%")

    def convert_localisation(self):
        Logger().log("info", "Converting localisation...")

        localiser = localisation.Localisation(self.universe)
        Logger().log("progress", "81%")
        Logger().log("info", "Writing localisation...")
        localiser.write_localisation()
        localiser.write_synced_localisation()
        Logger().log("progress", "90%")

    def convert_events(self):
        Logger().log("info", "Creating events...")

        self.events = events.Events(self.universe)
        self.events.makeEvents()
        Logger().log("progress", "99%")


if __name__ == "__main__":
    Logger().log("info", "Beginning conversion...")

    #converter = Converter()
    Converter().convert_everything()

    Logger().log("info", "Conversion successful")
    Logger().log("progress", "100%")
