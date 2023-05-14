#!/usr/bin/python

import os
import sys
import shutil
import naive_parser
from logToFile import Logger


class BorgSingleton:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Config(BorgSingleton):
    def __init__(self):
        BorgSingleton.__init__(self)
        if hasattr(self, 'loaded'):
            return
        self.loaded = True

        self.configfile = naive_parser.parse_save_file("configuration.txt")

        if getattr(sys, 'frozen', False):
            # running in a bundle
            self.converter_dir = self.make_sane_path(
                os.path.dirname(sys.executable))
        else:
            # running live
            self.converter_dir = self.make_sane_path(
                os.path.dirname(os.path.realpath(__file__)))

        Logger().log("debug", "Running from: "+self.converter_dir)

        self.save_file_name = naive_parser.unquote(
            naive_parser.drill(self.configfile, "savefile"))
        self.hoi4_path = naive_parser.unquote(
            naive_parser.drill(self.configfile, "HoI4directory"))
        self.hoi4_mod_path = naive_parser.unquote(
            naive_parser.drill(self.configfile, "HoI4ModDirectory"))
        self.stellaris_mod_path = naive_parser.unquote(
            naive_parser.drill(self.configfile, "targetGameModPath"))
        government_mapping = naive_parser.unquote(
            naive_parser.drill(self.configfile, "government_mapping"))
        self.government_mapping_file = f"files/governments/{government_mapping}.txt"

        # HoI4 to DEFCON is busted, so might as well keep this off to make fronter stuff easier for now.
        self.defcon_results = False

        #self.useDefconResults = naive_parser.unquote(naive_parser.drill(self.configfile, "useDefconResults"))
        # if self.useDefconResults == "y" or self.useDefconResults == "yes":
        #     self.defconResults = naive_parser.unquote(naive_parser.drill(self.configfile, "defconResults"))
        # else:
        #     self.defconResults = False

        self.mod_name_human = naive_parser.unquote(
            naive_parser.drill(self.configfile, "output_name"))
        self.mod_name = self.mod_name_human.replace(" ", "_")

        self.base_mod_path = self.converter_dir + "outputMod_base/"
        self.output_path = self.converter_dir + "output/" + self.mod_name + "/"
        self.output_mod_file = self.converter_dir + "output/outputMod.mod"
        self.output_descriptor = self.converter_dir + "files/descriptor.mod"

        shutil.copyfile("files/outputMod.mod", "output/outputMod.mod")
        # Renames the mod and the path inside the modfile, and then renames the modfile.
        with open(self.output_mod_file, "r") as tempfile:
            filedata = tempfile.read()
        filedata = filedata.replace(
            "name=\"ConverterOutput\"", "name=\"" + self.mod_name_human + "\"")
        filedata = filedata.replace(
            "path=\"mod/outputMod\"", "path=\"mod/" + self.mod_name + "\"")
        with open(self.output_mod_file, "w") as tempfile:
            tempfile.write(filedata)
        os.replace("output/outputMod.mod", "output/" + self.mod_name + ".mod")
        # Renames the mod inside the descriptor
        with open(self.output_descriptor, "r") as tempfile:
            filedata = tempfile.read()
        filedata = filedata.replace(
            "name=\"ConverterOutput\"", "name=\"" + self.mod_name_human + "\"")
        with open(self.output_descriptor, "w") as tempfile:
            tempfile.write(filedata)

        if self.stellaris_mod_path:
            self.stellaris_mod_path = self.make_sane_path(
                self.stellaris_mod_path)
            self.final_path = self.stellaris_mod_path + self.mod_name + "/"
            self.final_mod_file = self.stellaris_mod_path + self.mod_name + ".mod"
        else:
            self.final_path = ""
            self.final_mod_file = ""

        if not self.is_sane():
            sys.exit(0)

    def init(self):
        Logger.log(self, "info", "Parsing save file...")
        self.savefile = naive_parser.parse_save_file(self.save_file_name)
        Logger.log(self, "info", "Reading save data...")
        self.parser = naive_parser.Parser(self.savefile)
        Logger.log(self, "info", "Save file parsed.")
        Logger.log(self, "progress", "27%")

    def is_sane(self):
        if self.save_file_name == "":
            Logger().log("error", "No Hearts Of Iron 4 save file specified.")
            return False

        if self.hoi4_path == "":
            Logger().log("error", "No path to Hearts Of Iron 4 specified.")
            return False

        # TODO: some more checking that we're actually pointing at a legit HoI4 installation etc

        self.hoi4_path = self.make_sane_path(self.hoi4_path)
        self.hoi4_mod_path = self.make_sane_path(self.hoi4_mod_path)
        self.stellaris_mod_path = self.make_sane_path(self.stellaris_mod_path)
        self.base_mod_path = self.make_sane_path(self.base_mod_path)
        self.output_path = self.make_sane_path(self.output_path)

        return True

    def make_sane_path(self, path):
        # TODO use pathlib for this

        path = path.replace("\\", "/")
        if path == "":
            return path

        if path[-1] != "/":
            path += "/"
        return path

    def create_directories(self):
        os.makedirs(self.output_path, exist_ok=True)
        shutil.rmtree(self.output_path, True)
        shutil.copytree(self.base_mod_path, outputPath)

    def get_modded_hoi4_file(self, targetPath):
        # TODO make this work with multiple mods at the same time
        path_that_exists = self.hoi4_mod_path + targetPath
        if os.path.exists(path_that_exists):
            return path_that_exists
        path_that_exists = self.hoi4_path + targetPath
        if os.path.exists(path_that_exists):
            return path_that_exists
        Logger().log("warning", "Could not find HoI4 file "+targetPath)
        return ""

    def get_converter_dir(self): return self.converter_dir
    def get_save_path(self): return self.save_file_name
    def get_hoi4_path(self): return self.hoi4_path
    def get_hoi4_mod_path(self): return self.hoi4_mod_path
    def get_stellaris_mod_path(self): return self.stellaris_mod_path
    def get_base_mod_path(self): return self.base_mod_path
    def get_output_path(self): return self.output_path
    def get_output_mod_file(self): return self.output_mod_file
    def get_final_path(self): return self.final_path
    def get_final_mod_file(self): return self.final_mod_file
    def get_mod_name(self): return self.mod_name
    def get_descriptor_file(self): return self.output_descriptor
    def get_government_mapping(self): return self.government_mapping_file

    def get_save_data(self): return self.savefile
    def get_parser(self): return self.parser
    def get_defcon_results(self): return self.defcon_results
