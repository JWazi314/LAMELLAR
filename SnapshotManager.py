import psutil
import datetime
from pathlib import Path

from classes import ProcessSnapshot
from classes import CombinedSnapshot


def getProcessSnapShot():

    processSnapshots = {}

    for process in psutil.process_iter():

        try:
            
            path = process.exe()
            drive = Path(path).drive

            cpu = process.cpu_percent() / psutil.cpu_count()
            io = process.io_counters()

            snapshot = ProcessSnapshot(
                process.pid,
                process.name(),
                path,
                drive,
                cpu,
                process.memory_percent(),
                io.read_bytes,
                io.write_bytes
            )

            processSnapshots[process.pid] = snapshot

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):

            continue

    return processSnapshots



def combineProcesses(processSnapshots):

    combined = {}

    for snapshot in processSnapshots.values():

        name = snapshot.name

        if name not in combined:

            combined[name] = CombinedSnapshot(
                name,
                snapshot.path,
                snapshot.drive,
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
