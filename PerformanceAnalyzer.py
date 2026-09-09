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

    return cpuEvents + memoryEvents



def getNewAverage(oldAverage,currentValue, alpha = 0.05):

    if oldAverage is None:
        return currentValue

    newAverage = alpha * currentValue + ( 1 - alpha) * oldAverage
    return newAverage





