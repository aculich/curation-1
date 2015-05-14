import psycopg2
import pandas as pd
import sys, os, time
from config import conn as c
import re
import csv

DATA_DIR = os.path.expanduser('~/curation/data/transcodes/')

sqlQuery = "SELECT * FROM transcode LEFT JOIN asset ON (transcode.asset = asset.id);"

def makeConnection():
    try:
        conn = psycopg2.connect(dbname=c._DEV_CREDENTIALS['db'], 
                                user=c._DEV_CREDENTIALS['u'],
                                host=c._DEV_CREDENTIALS['host'],
                                password=c._DEV_CREDENTIALS['p'])
    except Exception as e:
        print("Unable to connect to database. Exception: %s" % str(e), file=sys.stderr)

    return conn.cursor()

def getData(cursor):
    try:
        cursor.execute(sqlQuery)
    except Exception as e:
        print("Query for everything failed. Exception: %s" % str(e), file=sys.stderr)
    rows = cursor.fetchall()
    return rows

def filterErrors(data:list) -> dict:
    terrors = {d[9]:[] for d in data}
    pattern = re.compile(r'\[(\w+)\s@\s\w+\](.*)')
    for d in data:
        if d[7] != None:
            logtext = d[7]
            if "incomplete frame" in logtext:
                logtext = str.replace(logtext, "incomplete frame\n", "incomplete frame: ")
            loglines = logtext.split('\n')
            for line in loglines:
                m = re.match(pattern, line) 
                if m:
                    terrors[d[9]].append({'asset': d[1], 
                                          'msg_group': m.group(1).strip(), 
                                          'msg':m.group(2).strip()})
    return terrors

def filteredDataFrame(fdata:dict):
    flattened = []
    for k in fdata:
        for f in fdata[k]:
            f['vol'] = k
            flattened.append(f)
    return pd.DataFrame(flattened)

def outputFilteredCSV(fdata:dict):
    DATA_FNAME = "transcode_errors_" + str(int(time.time())) + '.csv'
    output_path = DATA_DIR + DATA_FNAME
    #with open(output_path, 'w+') as dfile:
    with open(DATA_FNAME, 'w+') as dfile:
        dfile_writer = csv.writer(dfile)
        head = ["volume", "asset", "error_text", "codec"]
        dfile_writer.writerow(head)
        for d in fdata:
            for i in fdata[d]:
                row = [d, i["asset"], i["msg"], i["msg_group"]]
                dfile_writer.writerow(row)

def errorsByVolume(errors):
    for k in sorted(errors):
        print("%s: %s" % (k, len(errors[k])))

def librarySummary(fd:dict):
    pass

def errorSummary(fd:dict):
    pass

def volumeSummary(fd:dict):
    pass

def generateReport(fd:dict):
    pass



'''notes: 1) incomplete frame is followed by a new line and Error while decoding stream ??
          2) Mutiple frames in a packet from stream _ not begining with memory location
          3) what kind of reports do we need
                - aggregate '''
          