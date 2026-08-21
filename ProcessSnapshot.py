import psutil
import time
from collections import deque


class ProcessSnapshot:

    def __init__(self,pid,name,cpu,memory, diskRead, diskWrite):
        self.pid = pid
        self.name = name

        self.cpu = cpu
        self.memory = memory

        self.diskRead = diskRead
        self.diskWrite = diskWrite

    def __repr__(self):
        return f"{self.name} | CPU: {self.cpu:.2f}% | RAM: {self.memory}%"

class CombinedSnapshot:

    def __init__(self, name, cpu, memory, pids,diskRead,diskWrite):

        self.name = name
        self.pids = pids

        self.cpu = cpu
        self.memory= memory

        self.diskRead = diskRead
        self.diskWrite = diskWrite


    def __repr__(self):
       return f"{self.name} | CPU: {self.cpu:.2f}% | RAM: {self.memory}%"

class PerformanceEvent:

    def __init__(self,pid,name,eventType,oldValue,newValue,severity):

        self.pid = pid
        self.name = name

        self.oldValue = oldValue
        self.newValue = newValue

        self.eventType = eventType
        self.severity = severity


def getProcessSnapShot():

    processSnapshots = {}

    for process in psutil.process_iter():

        try:

            cpu = process.cpu_percent() / psutil.cpu_count()

            io = process.io_counters()

            snapshot = ProcessSnapshot(
                process.pid,
                process.name(),
                cpu,
                process.memory_percent(),
                io.read_bytes,
                io.write_bytes
            )

            processSnapshots[process.pid] = snapshot
        
        except Exception as error:
            print(error)

    return processSnapshots



def combineProcesses(processSnapshots):

    combined = {}

    for snapshot in processSnapshots.values():

        name = snapshot.name

        if name not in combined:

            combined[name] = CombinedSnapshot(
                name,
                snapshot.cpu,
                snapshot.memory,
                [snapshot.pid],
                snapshot.diskRead,
                snapshot.diskWrite
            )

        else:

            combined[name].cpu += snapshot.cpu
            combined[name].memory += snapshot.memory
            combined[name].pids.append(snapshot.pid)
            combined[name].diskRead += snapshot.diskRead
            combined[name].diskWrite += snapshot.diskWrite

    return combined
        

def cpuCheck(previous , current):

    events = []

    for pid, newProcess in current.items():

        if newProcess.name == "System Idle Process":
            continue
        
        if pid not in previous:
            continue
    
        oldProcess = previous[pid]

        cpuChange = newProcess.cpu - oldProcess.cpu

        severity = getSeverity(cpuChange)
 

        if abs(cpuChange) > 5:
            cpuEvent = PerformanceEvent(
                pid,
                newProcess.name,
                "CPU Change",
                oldProcess.cpu,
                newProcess.cpu,
                severity
            )

            events.append(cpuEvent)

    return events



def memoryCheck(previous , current):

    events = []

    for pid, newProcess in current.items():

        if newProcess.name == "System Idle Process":
            continue
        
        if pid not in previous:
            continue
    
        oldProcess = previous[pid]

        memoryChange = newProcess.memory - oldProcess.memory

        severity = getSeverity(memoryChange)

        if abs(memoryChange) > .5:
            memoryEvent = PerformanceEvent(
                pid,
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




def compareSnapShots(previous,current):

    cpuEvents = cpuCheck(previous,current)
    memoryEvents = memoryCheck(previous,current)

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
 


