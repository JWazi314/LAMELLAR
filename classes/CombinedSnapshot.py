from datetime import datetime

class CombinedSnapshot:

    def __init__(self, name, path, drive, cpu, memory, pids, diskRead, diskWrite):

        self.name = name
        self.pids = pids

        self.path = path
        self.drive = drive

        self.cpu = cpu
        self.memory = memory

        self.diskRead = diskRead
        self.diskWrite = diskWrite

        self.time = datetime.now()


    def __repr__(self):

        return f"{self.name} | CPU: {self.cpu:.2f}% | RAM: {self.memory:.2f}%"
