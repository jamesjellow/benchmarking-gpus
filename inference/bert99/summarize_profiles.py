import sys
import pandas as pd

resourcesToReport = ['cpu', 'disk', 'memory', 'gpu']

# grab profiling headers from log file
metricHeaderLine = {
    'cpu': 3,
    'disk': 6,
    'gpu': 1,
    'memory': 2
}

# select metrics to summarize by identifying profiling headers
cpuSummaryHeaders = ['%usr']
diskSummaryHeaders = ['%util']
gpuSummaryHeaders = ['utilization.gpu [%]', 'utilization.memory [%]', 'memory.used [MiB]', 'memory.total [MiB]']
memorySummaryHeaders = ['free', 'cache', 'buff', 'si', 'so', 'bi']

# display headers for selected metrics
cpuHeaders = ['CPU usage (%)']
diskHeaders = ['Disk usage (%)']
gpuHeaders = ['GPU usage (%)', 'GPU memory usage (%)', 'GPU memory used (MiB)', 'GPU memory total (MiB)']
memoryHeaders = ['free, RAM available (KB)', 'cache, RAM cache usage (KB)', 'buff, RAM buffer usage (KB) ', 'si, swap-in rate from disk to RAM (KB/s)', 'so, swap-out rate from RAM to disk (KB/s)', 'bi, disk block reading frequency (blocks/s)']
usageHeader = 'usage (%)'

# header entries
rawHeaders = {}
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

# row clean up
rowRemoval = {
    'cpu': {'CPU': ['CPU']},
    'disk': {'Device': ['Device', 'avg-cpu:']},
    'gpu': {},
    'memory': {'r': ['r']}
}

# aggregated metrics by sub-resources
groupedMetrics = {
    'cpu': 'CPU',
    'disk': 'Device'
}

# metric stats
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

def getTable(logfile, resource):
    # get headers
    if resource in resourcesToReport:
        with open(logfile, 'r') as file:
            lines = file.readlines()
            # extract headers
            rawHeadersLine = lines[metricHeaderLine[resource]-1].strip()
            thisRawHeaders = rawHeadersLine.split()
            rawHeaders[resource] = thisRawHeaders
            
    # load dataframe
    if resource in ['cpu', 'disk']:
        df = pd.read_table(
            logfile,
            skiprows=2,
            delim_whitespace=True,
            names=rawHeaders[resource]
        )
    elif resource == 'memory':
        df = pd.read_table(
            logfile,
            skiprows=2,
            delim_whitespace=True,
            names=rawHeaders[resource],
            comment='p',
            engine='python'
        )
    elif resource == 'gpu':
        df = pd.read_csv(logfile)
        df = df.replace({' %': '', ' MiB': ''}, regex=True)
        df.columns = df.columns.str.strip()

    # remove rows with headers
    rowsToRemove = set()
    for col, rowList in rowRemoval[resource].items():
        for row in rowList:
            rowToRemove = df[df[col] == row].index
            rowsToRemove = rowsToRemove.union(rowToRemove)

            # only for disk
            if resource == 'disk' and col == 'Device' and row == 'avg-cpu:':
                rowsToRemove = rowsToRemove.union(rowToRemove+1)
    df = df.drop(rowsToRemove)

    # convert numerical entries to float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # aggregate
    if resource in ['cpu', 'disk']:
        df = df.groupby(groupedMetrics[resource])[summaryHeaders[resource]].agg(summaryMetrics)
    elif resource == 'memory':
        df = df[memorySummaryHeaders].agg(
            {col: summaryMetrics for col in memorySummaryHeaders
            }
        )
    elif resource == 'gpu':
        df = df[gpuSummaryHeaders].agg(
            {col: summaryMetrics for col in gpuSummaryHeaders
            }
        )

    # rotate if needed
    if resource in ['cpu', 'disk']:
        df = df.T

    # fix row labels and name of group of columns
    df.index = summaryMetricsLabel
    df.columns.name = None

    # select columns
    if resource == 'disk':
        df = df[['dm-0', 'xvda']]

    # rename columns
    if resource == 'cpu':
        df.columns = [f'cpu_{int(col)} {usageHeader}' if str(col).isdigit() else f'cpu_{col} {usageHeader}' for col in df.columns]
    elif resource in ['memory', 'gpu']:
        df.columns = headers[resource]
    elif resource == 'disk':
        df.columns = [f'{col} {usageHeader}' for col in df.columns]

    return df

def getSummary(logfile):
    resource, _, runType = logfile.split("_") #for strategy pattern

    if resource in resourcesToReport:
        df = getTable(logfile, resource)
        return df

    print(f"Error: {resource} needs to be incorporated into the summarize_profiles.py script.")
    return