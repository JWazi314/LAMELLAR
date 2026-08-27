from classes import PerformanceEvent


def cpuCheck(previous, current):

    events = []

    for processName, newProcess in current.items():

        if newProcess.name == "System Idle Process":
            continue

        if processName not in previous:
            continue

        oldProcess = previous[processName]

        cpuChange = newProcess.cpu - oldProcess.cpu
        severity = getSeverity(cpuChange)

        if abs(cpuChange) > 5:

            cpuEvent = PerformanceEvent(
                newProcess.pids,
                newProcess.name,
                "CPU Change",
                oldProcess.cpu,
                newProcess.cpu,
                severity
            )

            events.append(cpuEvent)

    return events



def memoryCheck(previous, current):

    events = []

    for processName, newProcess in current.items():

        if newProcess.name == "System Idle Process":
            continue

        if processName not in previous:
            continue

        oldProcess = previous[processName]

        memoryChange = newProcess.memory - oldProcess.memory
        severity = getSeverity(memoryChange)

        if abs(memoryChange) > 0.5:

            memoryEvent = PerformanceEvent(
                newProcess.pids,
                newProcess.name,
                "Memory Change",
                oldProcess.memory,
                newProcess.memory,
                severity
            )

            events.append(memoryEvent)

    return events



def getSeverity(change):

    change = abs(change)

    if change < 10:
        return "Small"

    elif change < 30:
        return "Medium"

    else:
        return "Large"



def compareSnapShots(previous, current):

    cpuEvents = cpuCheck(previous, current)
    memoryEvents = memoryCheck(previous, current)

    for event in cpuEvents:

        print(
            event.name,
            event.eventType,
            f"{event.oldValue:.2f}%",
            "->",
            f"{event.newValue:.2f}%",
            event.severity
        )

    for event in memoryEvents:

        print(
            event.name,
            event.eventType,
            f"{event.oldValue:.2f}%",
            "->",
            f"{event.newValue:.2f}%",
            event.severity
        )



def getSnapShotCPUAverage(monitorDq, targetProgram, sampleCount=5):

    recentSnapshots = list(monitorDq)[-sampleCount:]

    cpuValues = []

    for snapshot in recentSnapshots:

        if targetProgram in snapshot:

            cpuValues.append(
                snapshot[targetProgram].cpu
            )

    if not cpuValues:
        return 0

    cpuAverage = sum(cpuValues) / len(cpuValues)

    return cpuAverage



def getSnapShotMEMORYAverage(monitorDq, targetProgram, sampleCount=5):

    recentSnapshots = list(monitorDq)[-sampleCount:]

    memoryValues = []

    for snapshot in recentSnapshots:

        if targetProgram in snapshot:

            memoryValues.append(
                snapshot[targetProgram].memory
            )

    if not memoryValues:
        return 0

    memoryAverage = sum(memoryValues) / len(memoryValues)

    return memoryAverage





