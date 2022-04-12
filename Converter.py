#!/usr/bin/python3

import os
import sys
import shutil

from config import Config
import naive_parser
import makeNameList
import flagconvert
import localisation
import universe
import events

from logToFile import Logger


class Converter:
    def __init__(self):
        Config().Init()
    def ConvertEverything(self):
        self.makeFolders()
        self.getUniverse()

        self.convertFlags()
        self.convertNameLists()
        self.convertLocalisation()
        self.convertEvents()

    def makeFolders(self):
        Logger().log("info", "Laying out folder structure...")
        print("Laying out folder structure...")
        converterDir = Config().getConverterDir()
        shutil.rmtree(Config().getOutputPath(), True)
        shutil.copytree(Config().getBaseModPath(), Config().getOutputPath())
        shutil.copy(Config().getDescriptorFile(), Config().getOutputPath())
        Logger().log("progress", "36%")

    def getUniverse(self):
        Logger().log("info", "Creating the universe...")
        print("Creating the universe...")
        self.universe = universe.Universe(Config().getSaveData())
        Logger().log("progress", "45%")
        Logger().log("info", "Establishing history...")
        print("Establishing history...")
        self.universe.Load()
        Logger().log("progress", "54%")

    def convertFlags(self):
        hoi4flagpath = "gfx/flags/"
        topNations = Config().getParser().getTopNations()

        for topNation in topNations:
            Logger().log("info", "Creating flag for " + topNation.tag + "...")
            print("Creating flag for " + topNation.tag + "...")
            sourcepath = hoi4flagpath + topNation.tag + "_" + topNation.government + ".tga"
            sourceFlagTga = Config().getModdedHoi4File(sourcepath)
            if not sourceFlagTga:
                basesourcepath = hoi4flagpath + topNation.tag + ".tga"
                Logger().log("warning", "Could not find \"" + sourcepath + "\". Falling back to \"" + basesourcepath + "\".")
                print("WARNING: Could not find \"" + sourcepath + "\". Falling back to \"" + basesourcepath + "\".")
                sourceFlagTga = Config().getModdedHoi4File(basesourcepath)
            destFlagFolder = Config().getOutputPath() + "flags/convertedflags/"
            flagconvert.CompileFlag(sourceFlagTga, destFlagFolder)
        Logger().log("progress", "63%")

    def convertNameLists(self):
        topNations = Config().getParser().getTopNations()
        for topNation in topNations:
            Logger().log("info", "Creating name list for " + topNation.tag + "...")
            print("Creating name list for " + topNation.tag + "...")
            destNameListFolder = "output/"+ Config().getModName() + "/common/name_lists/"
            makeNameList.MakeNameList(topNation.tag, destNameListFolder)
        Logger().log("progress", "72%")

    def convertLocalisation(self):
        Logger().log("info", "Converting localisation...")
        print("Converting localisation...")

        savefile = Config().getSaveData()
        parser = Config().getParser()
        hoi4path = Config().getHoi4Path()

        localiser = localisation.Localisation(self.universe)
        Logger().log("progress", "81%")
        Logger().log("info", "Writing localisation...")
        print("Writing localisation...")
        localiser.writeLocalisation()
        localiser.writeSyncedLocalisation()
        Logger().log("progress", "90%")

    def convertEvents(self):
        Logger().log("info", "Creating events...")
        print("Creating events...")

        savefile = Config().getSaveData()
        parser = Config().getParser()
        hoi4path = Config().getHoi4Path()

        self.events = events.Events(self.universe)
        self.events.makeEvents()
        Logger().log("progress", "99%")


if __name__ == "__main__":
    Logger().log("info", "Beginning conversion...")
    print("BEGINNING CONVERSION")

    converter = Converter()
    converter.ConvertEverything()

    Logger().log("info", "Conversion successful")
    Logger().log("progress", "100%")
    print("ALL DONE!")
