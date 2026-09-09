from LAMELLAR import printSystemUsage, startMenu, monitorPrograms
from DatabaseManager import createTables, getDBinfo


def main():

    createTables()
    getDBinfo()
    printSystemUsage()

    targetProcess = startMenu()

    if targetProcess is None:
        return

    monitorPrograms(targetProcess)


if __name__ == "__main__":

    main()
