from datetime import datetime

class ProcessSnapshot:

    def __init__(self, pid, name, path, drive, cpu, memory, diskRead, diskWrite):

        self.pid = pid
        self.name = name

        self.path = path
        self.drive = drive

        self.cpu = cpu
        self.memory = memory

        self.diskRead = diskRead
        self.diskWrite = diskWrite

        self.time = datetime.now()

    def __repr__(self):

        return f"{self.name} | CPU: {self.cpu:.2f}% | RAM: {self.memory:.2f}%"
