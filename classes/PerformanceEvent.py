class PerformanceEvent:

    def __init__(self, pid, name, eventType, oldValue, newValue, severity):

        self.pid = pid
        self.name = name

        self.oldValue = oldValue
        self.newValue = newValue

        self.eventType = eventType
        self.severity = severity


    def __repr__(self):

        return (
            f"{self.name} | {self.eventType} | "
            f"{self.oldValue:.2f} -> {self.newValue:.2f} | "
            f"{self.severity}"
        )
