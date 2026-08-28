from LAMELLAR import *
from DatabaseManager import createTables,getDBinfo
from datetime import datetime


def main():

    getDBinfo()
    printSystemUsage()

    createTables()

    targetProcess = startMenu()

    if targetProcess is None:
        return

    monitorSystem(targetProcess)
    monitorPrograms(targetProcess)



if __name__ == "__main__":

    main()
