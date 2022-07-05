#!/usr/bin/python

import os,sys,shutil
import naive_parser
from logToFile import Logger

class BorgSingleton:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

class Config(BorgSingleton):
    def __init__(self):
        BorgSingleton.__init__(self)
        if hasattr(self, 'loaded'): return
        self.loaded = True

        self.configfile = naive_parser.ParseSaveFile("configuration.txt")

        if getattr( sys, 'frozen', False ) :
            # running in a bundle
            self.converterDir = self.makeSanePath(os.path.dirname(sys.executable))
        else :
            # running live
            self.converterDir = self.makeSanePath(os.path.dirname(os.path.realpath(__file__)))
        
        print("Running from: "+self.converterDir)

        self.savefileName = naive_parser.unquote(naive_parser.drill(self.configfile, "savefile"))
        self.hoi4Path = naive_parser.unquote(naive_parser.drill(self.configfile, "HoI4directory"))
        self.hoi4ModPath = naive_parser.unquote(naive_parser.drill(self.configfile, "HoI4ModDirectory"))
        self.stellarisModPath = naive_parser.unquote(naive_parser.drill(self.configfile, "targetGameModPath"))
        government_mapping = naive_parser.unquote(naive_parser.drill(self.configfile, "government_mapping"))
        self.government_mapping_file = f"files/governments/{government_mapping}.txt"

        self.defconResults = False # HoI4 to DEFCON is busted, so might as well keep this off to make fronter stuff easier for now.
        
        #self.useDefconResults = naive_parser.unquote(naive_parser.drill(self.configfile, "useDefconResults"))
        # if self.useDefconResults == "y" or self.useDefconResults == "yes":
        #     self.defconResults = naive_parser.unquote(naive_parser.drill(self.configfile, "defconResults"))
        # else:
        #     self.defconResults = False

        self.modNameHuman = naive_parser.unquote(naive_parser.drill(self.configfile, "output_name"))
        self.modName = self.modNameHuman.replace(" ", "_")

        self.baseModPath = self.converterDir + "outputMod_base/"
        self.outputPath = self.converterDir + "output/" + self.modName + "/"
        self.outputModFile = self.converterDir + "output/outputMod.mod"
        self.outputDescriptor = self.converterDir + "files/descriptor.mod"

        shutil.copyfile("files/outputMod.mod", "output/outputMod.mod")
        # Renames the mod and the path inside the modfile, and then renames the modfile.
        with open(self.outputModFile, "r") as tempfile:
            filedata = tempfile.read()
        filedata = filedata.replace("name=\"ConverterOutput\"", "name=\"" + self.modNameHuman + "\"")
        filedata = filedata.replace("path=\"mod/outputMod\"", "path=\"mod/" + self.modName + "\"")
        with open(self.outputModFile, "w") as tempfile:
             tempfile.write(filedata)
        os.replace("output/outputMod.mod", "output/" + self.modName + ".mod")
        # Renames the mod inside the descriptor
        with open(self.outputDescriptor, "r") as tempfile:
            filedata = tempfile.read()
        filedata = filedata.replace("name=\"ConverterOutput\"", "name=\"" + self.modNameHuman + "\"")
        with open(self.outputDescriptor, "w") as tempfile:
            tempfile.write(filedata)

        if self.stellarisModPath:
            self.stellarisModPath = self.makeSanePath(self.stellarisModPath)
            self.finalPath = self.stellarisModPath + self.modName + "/"
            self.finalModFile = self.stellarisModPath + self.modName + ".mod"
        else:
            self.finalPath = ""
            self.finalModFile = ""

        if not self.isSane():
            sys.exit(0)

    def Init(self):
        Logger.log(self, "info", "Parsing save file...")
        print("Parsing save file...")
        self.savefile = naive_parser.ParseSaveFile(self.savefileName)
        Logger.log(self, "info", "Reading save data...")
        print("Reading save data...")
        self.parser = naive_parser.Parser(self.savefile)
        Logger.log(self, "info", "Save file parsed.")
        Logger.log(self, "progress", "27%")
        print("Save file parsed.")

    def isSane(self):
        if self.savefileName == "":
            print("No Hearts Of Iron 4 save file specified.")
            return False

        if self.hoi4Path == "":
            print("No path to Hearts Of Iron 4 specified.")
            return False

        # TODO: some more checking that we're actually pointing at a legit HoI4 installation etc

        self.hoi4Path           = self.makeSanePath(self.hoi4Path)
        self.hoi4ModPath        = self.makeSanePath(self.hoi4ModPath)
        self.stellarisModPath   = self.makeSanePath(self.stellarisModPath)
        self.baseModPath        = self.makeSanePath(self.baseModPath)
        self.outputPath         = self.makeSanePath(self.outputPath)

        return True

    def makeSanePath(self, path):
        # TODO use pathlib for this

        path = path.replace("\\","/")
        if path == "": return path

        if path[-1] != "/":
            path += "/"
        return path
        
    def createDirectories(self):
        os.makedirs(self.outputPath, exist_ok=True)
        shutil.rmtree(self.outputPath, True)
        shutil.copytree(self.baseModPath, outputPath)

    def getModdedHoi4File(self, targetPath):
        # TODO make this work with multiple mods at the same time
        pathThatExists = self.hoi4ModPath + targetPath
        if os.path.exists(pathThatExists): return pathThatExists
        pathThatExists = self.hoi4Path + targetPath
        if os.path.exists(pathThatExists): return pathThatExists
        print("Warning: Could not find HoI4 file "+targetPath)
        return ""

    def getConverterDir(self):  return self.converterDir
    def getSavePath(self):      return self.savefileName
    def getHoi4Path(self):      return self.hoi4Path
    def getHoi4ModPath(self):   return self.hoi4ModPath
    def getStellarisModPath(self):    return self.stellarisModPath
    def getBaseModPath(self):   return self.baseModPath
    def getOutputPath(self):    return self.outputPath
    def getOutputModFile(self): return self.outputModFile
    def getFinalPath(self):     return self.finalPath
    def getFinalModFile(self):  return self.finalModFile
    def getModName(self):       return self.modName
    def getDescriptorFile(self):return self.outputDescriptor
    def get_government_mapping(self): return self.government_mapping_file

    def getSaveData(self):      return self.savefile
    def getParser(self):        return self.parser
    def getDefconResults(self): return self.defconResults
