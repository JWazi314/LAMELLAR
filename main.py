from LAMELLAR import printSystemUsage, startMenu, monitorPrograms, monitorSystem


def main():

    printSystemUsage()

    targetProcess = startMenu()

    if targetProcess is None:
        return
    monitorSystem(targetProcess)
    monitorPrograms(targetProcess)



if __name__ == "__main__":

    main()
