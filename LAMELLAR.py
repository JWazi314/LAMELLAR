import psutil 
import time
from collections import deque
from ProcessSnapshot import *


cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory().percent
disk = psutil.disk_usage("C:\\").percent

print("CPU: " , cpu , "%")
print("RAM: " , memory , "%")
print("Disk: " , disk , "%")

def startMenu():
    print("Welcome to Lamellar! Please select an option from below")
    print("Would you like to -")
    print("1. analyze a programs performance")
    print("2. optomize a programs performance")
    print("3. exit")
    choice = int(input())

    if choice == 1 or choice == 2:
        print("Awesome! Please type the process name")
        memorySortedPrograms()
        processes = getProcessSnapShot()
        combinedProcesses = combineProcesses(processes)
        targetProcess = assignTargetProgram(combinedProcesses)

        return targetProcess

    if choice == 3:
        print("exiting program")
        time.sleep(1)
        return 0
    
    else: 
        print("Invalid option")
        time.sleep(1)
        startMenu()

    return None

def assignTargetProgram(programSnapShot):

    programs = programSnapShot

    while True:

        findOption = input("Type Program name here: ")

        for programName, process in programs.items():

            if programName.lower() == findOption.lower():

                print("Process Found!")
                time.sleep(1)
                print("Now, use the process for some time, allow for performance errors to happen a few times if possible")

                return process

        print("Program not found, try again.")

def memorySortedPrograms():
    programs = {}

    for process in psutil.process_iter(["name" , "memory_percent"]):

        try:
            name = process.name()
            memory = process.memory_percent()

            if name in programs:
                programs[name] += memory
            else:
                programs[name] = memory
        except:
            pass

    sortedPrograms = sorted(
    programs.items(),
    key = lambda program: program[1],
    reverse = True
    )
    
    for name, memory in sortedPrograms:
        if memory > 1:
            print(name, f"{memory:.2f}%")
    return programs


def monitorPrograms():

    snapShotDeque = deque(maxlen=300)

    while True:
        
        seperatedSnapShot = getProcessSnapShot()
        combinedSnapShot = combineProcesses(seperatedSnapShot)

        snapShotDeque.append(combinedSnapShot)

        if len(snapShotDeque) >= 2:
            previous = snapShotDeque[-2]
            current = snapShotDeque[-1]

            compareSnapShots(previous,current)

        time.sleep(1)



