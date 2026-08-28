import sqlite3

from pathlib import Path
from datetime import datetime

DATABASE_PATH = Path(__file__).parent / "lamellar.db"


def getDataConnection():
    
    DATABASEPATH = Path(__file__).parent / "lamellar.db"
    connection = sqlite3.connect(DATABASEPATH)
    return connection

def getDBinfo():

    connection = getDataConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM programs
    """)

    programs = cursor.fetchall()

    for program in programs:
        print(f"{program} \n")
    
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

    connection.commit()
    connection.close()


def savePrograms(programs,cpuAverages,memoryAverages):

    connection = getDataConnection()
    cursor = connection.cursor()

    timeOfSave = datetime.now().isoformat()

    for name, process in programs.items():
        cpuAverage = cpuAverages[name]
        memoryAverage = memoryAverages[name]


        cursor.execute("""
            INSERT INTO PROGRAMS(

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

