import psutil
import time

from collections import deque

from SnapshotManager import getProcessSnapShot, combineProcesses
from PerformanceAnalyzer import compareSnapShots, getSnapShotCPUAverage, getSnapShotMEMORYAverage

#basic system info to show sucessful connection
def printSystemUsage():

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\").percent

    print("CPU:", cpu, "%")
    print("RAM:", memory, "%")
    print("Disk:", disk, "%")


#Start menu for the program
def startMenu():

    while True:

        print()
        print("Welcome to Lamellar! Please select an option from below")
        print("1. Analyze a program's performance")
        print("2. Optimize a program's performance")
        print("3. Exit")

        try:

            choice = int(input("Choice: "))

        except ValueError:

            print("Please enter a number.")
            continue

        if choice == 1 or choice == 2:

            print()
            print("Programs currently using more than 1% memory:")
            memorySortedPrograms()

            processes = getProcessSnapShot()
            combinedProcesses = combineProcesses(processes)

            targetProcess = assignTargetProgram(combinedProcesses)

            return targetProcess

        elif choice == 3:

            print("Exiting program")
            time.sleep(1)

            return None

        else:

            print("Invalid option.")
            time.sleep(1)


# get one specific program to monitor closer than the others
def assignTargetProgram(programSnapShot):

    while True:

        findOption = input("Type program name here: ")

        for programName, process in programSnapShot.items():

            if programName.lower() == findOption.lower():

                print("Process Found!")
                time.sleep(1)

                print(
                    "Now use the process for some time and allow "
                    "performance changes to occur."
                )

                return process

        print("Program not found, try again.")


# sort processes by memory to better help user choose a process
def memorySortedPrograms():

    programs = {}

    for process in psutil.process_iter(["name", "memory_percent"]):

        try:

            name = process.name()
            memory = process.memory_percent()

            if name in programs:
                programs[name] += memory

            else:
                programs[name] = memory

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):

            continue

    sortedPrograms = sorted(
        programs.items(),
        key=lambda program: program[1],
        reverse=True
    )

    for name, memory in sortedPrograms:

        if memory > 1:

            print(
                name,
                f"{memory:.2f}%"
            )

    return programs


def monitorSystem(targetProcess):
    systemEvents = {}
    path = ""

    for pid in targetProcess.pids:
        try:
            process = psutil.Process(pid)
            path = process.exe()

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    targetdir = path[0:2]
    print(targetdir)
    disk = psutil.disk_usage(f"{targetdir}\\").percent


    if cpu > 80:
        print(f"HIGH SYSTEM CPU USAGE {disk}%")
        systemEvents["Cpu"] = cpu
    if memory > 80:
        print(f"HIGH SYSTEM MEMORY USAGE {memory}%")
        systemEvents["Memory"] = memory
    if disk > 80:
        print(f"HIGH DISK USAGE {disk}%")
        systemEvents["Disk"] = disk
    time.sleep(1)





# recursive monitor system.  takes 2 snapshots objects, combine multiple if same process then put it in deque.
# then compares changes and does multple average checks
def monitorPrograms(targetProcess):

    snapShotDeque = deque(maxlen=300)

    while True:

        separatedSnapShot = getProcessSnapShot()
        combinedSnapShot = combineProcesses(separatedSnapShot)

        snapShotDeque.append(combinedSnapShot)

        dequeLength = len(snapShotDeque)

        if dequeLength >= 2:

            previous = snapShotDeque[-2]
            current = snapShotDeque[-1]

            compareSnapShots(previous, current)

        if dequeLength % 5 == 0:

            targetName = targetProcess.name

            fiveCpuAverage = getSnapShotCPUAverage(snapShotDeque, targetName)
            fiveMemoryAverage = getSnapShotMEMORYAverage(snapShotDeque,targetName)

            current = snapShotDeque[-1]

            if targetName not in current:

                print(f"{targetName} is no longer running.")
                return

            currentTarget = current[targetName]

            print()
            print(
                f"Program: {currentTarget} | "
                f"5 Second CPU Average: {fiveCpuAverage:.2f}% | "
                f"5 Second Memory Average: {fiveMemoryAverage:.2f}%"
            )
        time.sleep(1)


