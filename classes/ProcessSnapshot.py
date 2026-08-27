class ProcessSnapshot:

    def __init__(self, pid, name, cpu, memory, diskRead, diskWrite):

        self.pid = pid
        self.name = name

        self.cpu = cpu
        self.memory = memory

        self.diskRead = diskRead
        self.diskWrite = diskWrite


    def __repr__(self):

        return f"{self.name} | CPU: {self.cpu:.2f}% | RAM: {self.memory:.2f}%"
