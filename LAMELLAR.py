import psutil
import time
import sys

from collections import deque

from classes import PerformanceEvent
from SnapshotManager import getProcessSnapShot, combineProcesses
from PerformanceAnalyzer import compareSnapShots, getNewAverage
from DatabaseManager import (
    savePrograms,
    savePerformanceEvents,
    saveProgramHistory,
    loadProgramAverages,
    getProgramBaseline
)


def printSystemUsage():

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\").percent

    print("CPU:", cpu, "%")
    print("RAM:", memory, "%")
    print("Disk:", disk, "%")


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


def stopRequested():

    if sys.platform != "win32":
        return False

    try:
        import msvcrt
    except ImportError:
        return False

    if not msvcrt.kbhit():
        return False

    key = msvcrt.getwch()
    return key.lower() == "q" or key in ("\r", "\n")


def waitForInterval(seconds):

    deadline = time.monotonic() + seconds

    while time.monotonic() < deadline:

        if stopRequested():
            return True

        time.sleep(0.1)

    return False


def systemSeverity(value):

    if value >= 90:
        return "Large"

    return "Medium"


def checkSystem(targetProcess):

    events = []

    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent

    drive = targetProcess.drive or "C:"

    try:
        disk = psutil.disk_usage(f"{drive}\\").percent
    except (OSError, ValueError):
        disk = psutil.disk_usage("C:\\").percent

    if cpu > 80:

        print(f"HIGH SYSTEM CPU USAGE {cpu:.1f}%")
        events.append(
            PerformanceEvent(
                [],
                "SYSTEM",
                "System CPU",
                80,
                cpu,
                systemSeverity(cpu)
            )
        )

    if memory > 80:

        print(f"HIGH SYSTEM MEMORY USAGE {memory:.1f}%")
        events.append(
            PerformanceEvent(
                [],
                "SYSTEM",
                "System Memory",
                80,
                memory,
                systemSeverity(memory)
            )
        )

    if disk > 80:

        print(f"HIGH DISK USAGE {disk:.1f}% on {drive}")
        events.append(
            PerformanceEvent(
                [],
                "SYSTEM",
                "System Disk",
                80,
                disk,
                systemSeverity(disk)
            )
        )

    return events, cpu, memory, disk


def printScanSummary(
    targetName,
    duration,
    samples,
    stillRunning,
    stopReason,
    peakCpu,
    peakMemory,
    avgCpu,
    avgMemory,
    baselineCpu,
    baselineMemory,
    severityCounts,
    targetEventCount,
    systemHighCpu,
    systemHighMemory,
    systemHighDisk
):

    print()
    print("=== Scan complete ===")
    print(f"Target: {targetName}")
    print(f"Duration: {duration:.1f}s")
    print(f"Samples: {samples}")
    print(f"Still running: {'Yes' if stillRunning else 'No'}")
    print(f"Stopped because: {stopReason}")

    baselineCpuText = (
        f"{baselineCpu:.2f}%" if baselineCpu is not None else "none"
    )
    baselineMemoryText = (
        f"{baselineMemory:.2f}%" if baselineMemory is not None else "none"
    )

    print(
        f"CPU  avg {avgCpu:.2f}%  peak {peakCpu:.2f}%  "
        f"stored baseline {baselineCpuText}"
    )
    print(
        f"RAM  avg {avgMemory:.2f}%  peak {peakMemory:.2f}%  "
        f"stored baseline {baselineMemoryText}"
    )
    print(
        f"Events: {sum(severityCounts.values())} "
        f"(Large: {severityCounts.get('Large', 0)}, "
        f"Medium: {severityCounts.get('Medium', 0)}, "
        f"Small: {severityCounts.get('Small', 0)})"
    )
    print(f"Target events: {targetEventCount}")
    print(
        f"System high samples — CPU: {systemHighCpu}, "
        f"RAM: {systemHighMemory}, Disk: {systemHighDisk}"
    )


def monitorPrograms(targetProcess):

    snapShotDeque = deque(maxlen=300)
    cpuAverages, memoryAverages = loadProgramAverages()

    targetName = targetProcess.name
    baselineCpu, baselineMemory = getProgramBaseline(targetName)

    samples = 0
    peakCpu = 0.0
    peakMemory = 0.0
    sumCpu = 0.0
    sumMemory = 0.0
    targetEventCount = 0
    systemHighCpu = 0
    systemHighMemory = 0
    systemHighDisk = 0
    stillRunning = True
    stopReason = "stopped by user"
    severityCounts = {"Small": 0, "Medium": 0, "Large": 0}

    print()
    print("Starting scan. Press Q or Enter to finish, or Ctrl+C.")
    print("Priming CPU samples...")

    getProcessSnapShot()
    psutil.cpu_percent(interval=None)
    time.sleep(1)

    scanStart = time.monotonic()

    try:

        while True:

            systemEvents, sysCpu, sysMem, sysDisk = checkSystem(targetProcess)
            savePerformanceEvents(systemEvents)

            for event in systemEvents:

                if event.eventType == "System CPU":
                    systemHighCpu += 1
                elif event.eventType == "System Memory":
                    systemHighMemory += 1
                elif event.eventType == "System Disk":
                    systemHighDisk += 1

            separatedSnapShot = getProcessSnapShot()
            combinedSnapShot = combineProcesses(separatedSnapShot)
            snapShotDeque.append(combinedSnapShot)

            for name, process in combinedSnapShot.items():

                if name not in cpuAverages:

                    cpuAverages[name] = process.cpu
                    memoryAverages[name] = process.memory

                else:

                    cpuAverages[name] = getNewAverage(
                        cpuAverages[name],
                        process.cpu
                    )
                    memoryAverages[name] = getNewAverage(
                        memoryAverages[name],
                        process.memory
                    )

            savePrograms(combinedSnapShot, cpuAverages, memoryAverages)

            if len(snapShotDeque) >= 2:

                events = compareSnapShots(snapShotDeque[-2], snapShotDeque[-1])
                savePerformanceEvents(events)

                for event in events:

                    severityCounts[event.severity] = (
                        severityCounts.get(event.severity, 0) + 1
                    )

                    if event.name == targetName:

                        targetEventCount += 1
                        print(
                            event.name,
                            event.eventType,
                            f"{event.oldValue:.2f}%",
                            "->",
                            f"{event.newValue:.2f}%",
                            event.severity
                        )

            if targetName not in combinedSnapShot:

                print(f"{targetName} is no longer running.")
                stillRunning = False
                stopReason = "target process exited"
                break

            currentTarget = combinedSnapShot[targetName]
            saveProgramHistory(currentTarget)

            samples += 1
            peakCpu = max(peakCpu, currentTarget.cpu)
            peakMemory = max(peakMemory, currentTarget.memory)
            sumCpu += currentTarget.cpu
            sumMemory += currentTarget.memory

            print(
                f"Program: {currentTarget} | "
                f"CPUAverage: {cpuAverages[targetName]:.2f} | "
                f"MemoryAverage: {memoryAverages[targetName]:.2f} | "
                f"SYS CPU {sysCpu:.1f}% RAM {sysMem:.1f}% Disk {sysDisk:.1f}%"
            )

            if waitForInterval(1):
                stopReason = "stopped by user"
                break

    except KeyboardInterrupt:

        stopReason = "stopped by user"
        print()

    duration = time.monotonic() - scanStart
    avgCpu = (sumCpu / samples) if samples else 0.0
    avgMemory = (sumMemory / samples) if samples else 0.0

    printScanSummary(
        targetName,
        duration,
        samples,
        stillRunning,
        stopReason,
        peakCpu,
        peakMemory,
        avgCpu,
        avgMemory,
        baselineCpu,
        baselineMemory,
        severityCounts,
        targetEventCount,
        systemHighCpu,
        systemHighMemory,
        systemHighDisk
    )
