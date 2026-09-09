import sqlite3

from pathlib import Path
from datetime import datetime

DATABASE_PATH = Path(__file__).parent / "lamellar.db"


def getDataConnection():

    connection = sqlite3.connect(DATABASE_PATH)
    return connection


def getDBinfo():

    connection = getDataConnection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM programs")
    count = cursor.fetchone()[0]

    print(f"Known programs in local database: {count}")

    if count:

        cursor.execute("""
            SELECT exeName, cpuAverage, memoryAverage, lastSeen
            FROM programs
            ORDER BY lastSeen DESC
            LIMIT 5
        """)

        print("Recently seen:")

        for name, cpuAverage, memoryAverage, lastSeen in cursor.fetchall():

            print(
                f"  {name} | CPU avg {cpuAverage:.2f}% | "
                f"RAM avg {memoryAverage:.2f}% | last seen {lastSeen}"
            )

    connection.close()


def createTables():

    connection = getDataConnection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programs
        (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exeName TEXT UNIQUE NOT NULL,

            path TEXT,

            cpu REAL DEFAULT 0,
            cpuAverage REAL DEFAULT 0,

            Memory REAL DEFAULT 0,
            memoryAverage REAL DEFAULT 0,

            diskRead INTEGER DEFAULT 0,
            diskWrite INTEGER DEFAULT 0,

            lastSeen TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performanceEvents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exeName TEXT NOT NULL,

            eventType TEXT NOT NULL,

            oldValue REAL,
            newValue REAL,

            severity TEXT,

            timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programHistory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exeName TEXT NOT NULL,

            cpu REAL,
            memory REAL,

            diskRead INTEGER,
            diskWrite INTEGER,

            timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_exeName
        ON performanceEvents(exeName)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_exeName_time
        ON programHistory(exeName, timestamp)
    """)

    connection.commit()
    connection.close()


def loadProgramAverages():

    connection = getDataConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT exeName, cpuAverage, memoryAverage
        FROM programs
    """)

    cpuAverages = {}
    memoryAverages = {}

    for name, cpuAverage, memoryAverage in cursor.fetchall():

        cpuAverages[name] = cpuAverage
        memoryAverages[name] = memoryAverage

    connection.close()

    return cpuAverages, memoryAverages


def getProgramBaseline(exeName):

    connection = getDataConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT cpuAverage, memoryAverage
        FROM programs
        WHERE exeName = ?
    """, (exeName,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None, None

    return row[0], row[1]


def savePrograms(programs, cpuAverages, memoryAverages):

    connection = getDataConnection()
    cursor = connection.cursor()

    timeOfSave = datetime.now().isoformat()

    for name, process in programs.items():

        cpuAverage = cpuAverages[name]
        memoryAverage = memoryAverages[name]

        cursor.execute("""
            INSERT INTO programs(

                exeName,
                path,

                cpu,
                cpuAverage,

                memory,
                memoryAverage,

                diskRead,
                diskWrite,

                lastSeen

            )

            VALUES (?,?,?,?,?,?,?,?,?)

            ON CONFLICT(exeName)
            DO UPDATE SET

                path = excluded.path,

                cpu = excluded.cpu,
                cpuAverage = excluded.cpuAverage,

                memory = excluded.memory,
                memoryAverage = excluded.memoryAverage,

                diskRead = excluded.diskRead,
                diskWrite = excluded.diskWrite,

                lastSeen = excluded.lastSeen
        """, (
            process.name,
            process.path,

            process.cpu,
            cpuAverage,

            process.memory,
            memoryAverage,

            process.diskRead,
            process.diskWrite,

            timeOfSave
        ))

    connection.commit()
    connection.close()


def savePerformanceEvents(events):

    if not events:
        return

    connection = getDataConnection()
    cursor = connection.cursor()

    for event in events:

        cursor.execute("""
            INSERT INTO performanceEvents (
                exeName,
                eventType,
                oldValue,
                newValue,
                severity,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.name,
            event.eventType,
            event.oldValue,
            event.newValue,
            event.severity,
            event.time.isoformat()
        ))

    connection.commit()
    connection.close()


def saveProgramHistory(process):

    connection = getDataConnection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO programHistory (
            exeName,
            cpu,
            memory,
            diskRead,
            diskWrite,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        process.name,
        process.cpu,
        process.memory,
        process.diskRead,
        process.diskWrite,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()
