import numpy as np
import pandas as pd

# raw profiling headers
cpuRawHeaders = ['time', 'PM', 'CPU', '%usr', '%nice', '%sys', '%iowait', '%irq', '%soft', '%steal', '%guest', '%gnice', '%idle']
diskRawHeaders = [
    'Device', 'r/s', 'rkB/s', 'rrqm/s', '%rrqm', 'r_await', 'rareq-sz', 'w/s', 'wkB/s', 'wrqm/s', '%wrqm', 'w_await',
    'wareq-sz', 'd/s', 'dkB/s', 'drqm/s', '%drqm', 'd_await', 'dareq-sz', 'aqu-sz', '%util'
    ]
gpuRawHeaders = ['timestamp', 'utilization.gpu [%]', 'utilization.memory [%]', 'memory.used [MiB]', 'memory.total [MiB]']

memoryRawHeaders = ['r', 'b', 'swpd', 'free', 'buff', 'cache', 'si', 'so', 'bi', 'bo', 'in', 'cs', 'us', 'sy', 'id', 'wa', 'st']

# summarized profiling headers
cpuSummaryHeaders = ['%usr']
diskSummaryHeaders = ['%util']
gpuSummaryHeaders = ['utilization.gpu [%]', 'utilization.memory [%]', 'memory.used [MiB]', 'memory.total [MiB]']
memorySummaryHeaders = ['free', 'cache', 'buff', 'si', 'so', 'bi']

# display summarized profiling headers
cpuHeaders = ['CPU usage (%)']
diskHeaders = ['Disk usage (%)']
gpuHeaders = ['GPU usage (%)', 'GPU memory usage (%)', 'GPU memory used (MiB)', 'GPU memory total (MiB)']
memoryHeaders = ['free, RAM available (KB)', 'cache, RAM cache usage (KB)', 'buff, RAM buffer usage (KB) ', 'si, swap-in rate from disk to RAM (KB/s)', 'so, swap-out rate from RAM to disk (KB/s)', 'bi, disk block reading frequency (blocks/s)']

# dictionary entries
rawHeaders = {
    'cpu': cpuRawHeaders,
    'disk': diskRawHeaders,
    'gpu': gpuRawHeaders,
    'memory': memoryRawHeaders
}
summaryHeaders = {
    'cpu': cpuSummaryHeaders,
    'disk': diskSummaryHeaders,
    'gpu': gpuSummaryHeaders,
    'memory': memorySummaryHeaders
}
headers = {
    'cpu': cpuHeaders,
    'disk': diskHeaders,
    'gpu': gpuHeaders,
    'memory': memoryHeaders
}

# hm
metricReadTable = ['cpu', 'disk', 'memory', 'gpu']
metricReadCSV = ['gpu']


rowRemoval = {
    'cpu': {'CPU': ['CPU']},
    'disk': {'Device': ['Device', 'avg-cpu:']},
    'gpu': {},
    'memory': {'r': ['r']}
}

groupedMetrics = {
    'cpu': 'CPU',
    'disk': 'Device'
}

summaryMetrics = [
    'min',
    'max',
    'mean',
    lambda x: x.quantile(0.5),
    lambda x: x.quantile(0.9),
    lambda x: x.quantile(0.95),
    lambda x: x.quantile(0.97),
    lambda x: x.quantile(0.99),
    lambda x: x.quantile(0.999)
]

summaryMetricsLabel = [
    'min',
    'max',
    'mean',
    'percentile_50',
    'percentile_90',
    'percentile_95',
    'percentile_97',
    'percentile_99',
    'percentile_99_9'
]


def getTable(logfile, metricType):
    # load dataframe
    if metricType == 'cpu' or metricType == 'disk':
        df = pd.read_table(
            logfile,
            skiprows=2,
            delim_whitespace=True,
            names=rawHeaders[metricType]
        )
    elif metricType == 'memory':
        df = pd.read_table(
            logfile,
            skiprows=2,
            delim_whitespace=True,
            names=rawHeaders[metricType],
            comment='p',
            engine='python'
        )
    elif metricType == 'gpu':
        df = pd.read_csv(logfile)
        df = df.replace({' %': '', ' MiB': ''}, regex=True)
        df.columns = df.columns.str.strip()

        
    rowsToRemove = set()
    for col, rowList in rowRemoval[metricType].items():
        for row in rowList:
            rowToRemove = df[df[col] == row].index
            rowsToRemove = rowsToRemove.union(rowToRemove)
            
            # only for disk
            if metricType == 'disk' and col == 'Device' and row == 'avg-cpu:':
                rowsToRemove = rowsToRemove.union(rowToRemove+1)
    df = df.drop(rowsToRemove)
    
    
    # convert numerical entries to float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    # aggregate
    if metricType in ['cpu', 'disk']:
        df = df.groupby(groupedMetrics[metricType])[summaryHeaders[metricType]].agg(summaryMetrics)
    elif metricType == 'memory':
        df = df[memorySummaryHeaders].agg(
            {col: summaryMetrics for col in memorySummaryHeaders
            }
        )
    elif metricType == 'gpu':
        df = df[gpuSummaryHeaders].agg(
            {col: summaryMetrics for col in gpuSummaryHeaders
            }
        )

    
    # rotate if needed
    if metricType in ['cpu', 'disk']:
        df = df.T
    
    # fix row labels and name of group of columns
    df.index = summaryMetricsLabel
    df.columns.name = None

    # select columns
    if metricType == 'disk':
        df = df[['dm-0', 'xvda']]
    
    # # rename columns
    if metricType == 'cpu':
        df.columns = [f'cpu_{int(col)}' if str(col).isdigit() else f'cpu_{col}' for col in df.columns]
    elif metricType == 'memory':
        df.columns = memoryHeaders
    elif metricType == 'gpu':
        df.columns = gpuHeaders

    return df



def getSummary(logfile):
     metricType, _, runType = logfile.split("_") #for strategy pattern
     
     if metricType in metricReadTable:
         df = getTable(logfile, metricType)
      
         return df
     return headers
     
