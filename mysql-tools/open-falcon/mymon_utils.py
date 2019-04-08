#! /bin/env python
# coding:gbk
# author:xucl


def map_value(value):
    if value == 'ON' or value == 'Yes':
        return 1
    elif value == 'OFF' or value == 'No':
        return 0
    else:
        return int(value)


def generate_metric(endpoint, metric, ts, step, value, type, tags):
    metric_dict = {}
    metric_dict['endpoint'] = endpoint
    metric_dict['metric'] = metric
    metric_dict['timestamp'] = ts
    metric_dict['step'] = step
    metric_dict['value'] = value
    metric_dict['counterType'] = type
    metric_dict['tags'] = tags
    return metric_dict


def get_var_metric(self, variables, data_dict, ts):
    metric_list = []
    for var in variables:
        try:
            value = map_value(data_dict[var])
        except:
            value = -1
        metric = generate_metric(self.endpoint, var, ts, 60, value, "GAUGE", self.tags)
        metric_list.append(metric)
    return metric_list


def get_sta_metric(self, status, data_dict, ts, type):
    metric_list = []
    for sta in status:
        try:
            value = map_value(data_dict[sta])
        except:
            value = -1
        metric = generate_metric(self.endpoint, sta, ts, 60, value, type, self.tags)
        metric_list.append(metric)
    return metric_list


def get_statusdiff_metric(self, data_dict1, data_dict2, ts):
    metric_list = []
    try:
        qps_value = map_value(data_dict2['Queries']) - map_value(data_dict1['Queries'])
        tps_value = map_value(data_dict2['Handler_commit']) - map_value(data_dict1['Handler_commit']) + map_value(data_dict2['Handler_rollback']) - map_value(data_dict2['Handler_rollback'])
    except:
        qps_value = -1
        tps_value = -1
    qps = generate_metric(self.endpoint, "qps", ts, 60, qps_value, "GAUGE", self.tags)
    tps = generate_metric(self.endpoint, "tps", ts, 60, tps_value, "GAUGE", self.tags)
    metric_list.append(qps)
    metric_list.append(tps)
    return metric_list


def get_innodb_metric(self, innodb_status_format, ts):
    metric_list = []
    for item in innodb_status_format:
        if "Log sequence number" in item:
            value = map_value(item.split(' ')[3])
            metric = generate_metric(self.endpoint, "loglsn", ts, 60, value, "GAUGE", self.tags)
            metric_list.append(metric)
        if "Log flushed up to" in item:
            value = map_value(item.split(' ')[6])
            metric = generate_metric(self.endpoint, "logflushlsn", ts, 60, value, "GAUGE", self.tags)
            metric_list.append(metric)
        if "Last checkpoint at" in item:
            value = map_value(item.split(' ')[4])
            metric = generate_metric(self.endpoint, "checkpointlsn", ts, 60, value, "GAUGE", self.tags)
            metric_list.append(metric)
        elif "History list length" in item:
            value = map_value(item.split(' ')[3])
            metric = generate_metric(self.endpoint, "historylength", ts, 60, value, "GAUGE", self.tags)
            metric_list.append(metric)
    return metric_list


def get_slave_metric(self, slave_status_format, ts):
    metric_list = []
    if slave_status_format:
        metric_name = "role"
        value = 0
    else:
        metric_name = "role"
        value = 1
    metric = generate_metric(self.endpoint, metric_name, ts, 60, value, "GAUGE", self.tags)
    metric_list.append(metric)

    if slave_status_format:
        for item in ['Slave_IO_Running', 'Slave_SQL_Running', 'Seconds_Behind_Master']:
            value = map_value(slave_status_format[item])
            metric = generate_metric(self.endpoint, item, ts, 60, value, "GAUGE", self.tags)
            metric_list.append(metric)
    return metric_list


def get_other_metric(self, metric_name, value, ts):
    metric_list = []
    metric = generate_metric(self.endpoint, metric_name, ts, 60, value, "GAUGE", self.tags)
    metric_list.append(metric)
    return metric_list
