class CombinedSnapshot:
    def __init__(self, name, cpu, memory, pids, diskRead, diskWrite):

        self.name = name
        self.pids = pids

        self.cpu = cpu
        self.memory = memory

        self.diskRead = diskRead
        self.diskWrite = diskWrite


    def __repr__(self):

        return f"{self.name} | CPU: {self.cpu:.2f}% | RAM: {self.memory:.2f}%"
