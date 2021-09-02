import sys
import sqlite3
import datetime
import subprocess

enableBlockTime = datetime.time(9,0)
disableBlockTime = datetime.time(16, 0)

domainsToBlock = ['facebook', 'tumblr'] # type: list[str]

conn = None

def GetDomainIds() -> list:
    # Query the Database for each domain in the domainsToBlock list,
    # and return the id for each.

    condition = "("

    # Build Condition string
    for index, domain in enumerate(domainsToBlock):
        condition += f"domain LIKE '%{domain}%' "

        if index < len(domainsToBlock) - 1:
            condition += "OR "

    # Regex Blacklist
    condition += ") AND type=3"

    cur = conn.cursor()
    cur.execute(f"SELECT id, enabled FROM domainlist WHERE {condition}")

    rows = cur.fetchall()

    ids = [row for row in rows] # type: list[int]

    return ids

def CreateConnection():
    # Create a Database connection to the SQLite
    # database file.

    global conn
    conn = None

    try:
        conn = sqlite3.connect("/etc/pihole/gravity.db")
    except Error as e:
        print(e)
        sys.exit()

    return conn

def CloseConnection():
    conn.close()

def BlockDomain(domain: int, block: bool):
    print(f"Change Blocking state to {int(block)} for domain '{domain}'")

    cur = conn.cursor()
    cur.execute(f"UPDATE domainlist SET enabled={int(block)} where id={domain}")

    conn.commit()

def FlushDNS():
   print(f"Flushing DNS cache")

   subprocess.run(["/usr/local/bin/pihole", "restartdns", "reload"])


def main():
    currentTime = datetime.datetime.now().time()
    print(f"Current time: {currentTime}")

    CreateConnection()
    ids = GetDomainIds()

    enableBlock = (currentTime > enableBlockTime and
        currentTime < disableBlockTime and
        datetime.datetime.now().weekday() <= 4)

    print(f"Inside restricted window: {enableBlock}")

    dnsFlushRequired = False

    for domain in ids:
       if domain[1] != enableBlock:
          dnsFlushRequired = True
          BlockDomain(domain[0], enableBlock)

    if dnsFlushRequired:
       FlushDNS()

    CloseConnection()

if __name__ == '__main__':
    main()
