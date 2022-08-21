import json
import charts.main_sr_chart as main_sr_chart
import config
import requests
import datetime
import calendar
import pandas
from pandas import DataFrame
from dateutil.relativedelta import relativedelta


class MonthReportData:
    def __init__(self, month):
        self.full_data = None
        self.month_sr = None
        self.load_month = month
        self.load_data()

    def load_data(self):
        with open('data/month-report-data.json', 'r', encoding='utf-8') as fp:
            json_data = json.load(fp)
            self.full_data = json_data
            self.month_sr = json_data['monthSR']

    def dump_data(self):
        with open('data/month-report-data.json', 'w', encoding='utf-8') as fp:
            json.dump(self.full_data, fp, ensure_ascii=False)


class ParseExcelData:
    def __init__(self, month):
        self.month = month
        self.month_sr = []

    def download_excel(self):
        date = datetime.datetime.strptime(self.month, '%Y/%m')
        first_day, last_day = self.get_month_first_day_and_last_day(date.year, date.month)
        header = {
            'Authorization': config.itms_authorization}
        var = config.itms_report_get_url
        var = var.replace('%s', first_day.strftime('%Y%m%d') + last_day.strftime('%Y%m%d'))
        response = requests.get(
            url=var,
            headers=header)
        filename = response.json().get('msg')
        itms_report_download_url = config.itms_report_download_url.replace('%s', filename)
        header['Content-Type'] = 'multipart/form-data;charset=utf-8'
        r = requests.get(itms_report_download_url)
        with open(filename, 'wb') as f:
            f.write(r.content)
            f.close()
        return filename, first_day.strftime('%Y-%m-%d')

    def get_month_first_day_and_last_day(self, year=None, month=None):
        """

        """
        if year:
            year = int(year)
        else:
            year = datetime.date.today().year
        if month:
            month = int(month)
        else:
            month = datetime.date.today().month
        # 获取当月第一天的星期和当月的总天数
        first_day_weekday, month_range = calendar.monthrange(year, month)
        # 获取当月第一天
        first_day = datetime.date(year, month, 1)
        # 获取当月最后一天
        last_day = datetime.date(year, month, month_range)
        return first_day, last_day

    def parse_data(self):
        month_report_data = MonthReportData('2022/02')
        filename, first_day = self.download_excel()
        month_complete_sheet = DataFrame(pandas.read_excel(filename, sheet_name='本月完成的需求'))
        month_complete = month_complete_sheet[(month_complete_sheet['系统分析员'] == '后援支持系统开发中心') & (
                (month_complete_sheet['需求类型'] == '数据获取') | (month_complete_sheet['需求类型'] == '功能开发'))]
        month_complete_num = month_complete.shape[0]
        month_unfinished_sheet = DataFrame(pandas.read_excel(filename, sheet_name='所有未完成的需求数量'))
        month_unfinished = month_unfinished_sheet[(month_unfinished_sheet['系统分析员'] == '后援支持系统开发中心') & (
                (month_unfinished_sheet['需求类型'] == '数据获取') | (month_unfinished_sheet['需求类型'] == '功能开发')) & (
                                                          month_unfinished_sheet['工作内容'] != '需求提交') & (
                                                          month_unfinished_sheet['工作内容'] != '需求审核') & (
                                                          month_unfinished_sheet['工作内容'] != '需求分析')]
        month_unfinished_num = month_unfinished.shape[0]
        month_receive_num = month_complete[month_complete['系统分析开始时间'] >= first_day].shape[0] + \
                            month_unfinished[month_unfinished['系统分析开始时间'] >= first_day].shape[0]
        load_month_flag = True
        for item in month_report_data.month_sr:
            if item['month'] == month_report_data.load_month[2:]:
                load_month_flag = False
                item['finished'] = month_complete_num
                item['receive'] = month_receive_num
                item['unfinished'] = month_unfinished_num
        if load_month_flag:
            month_report_data.month_sr.append(
                {"month": month_report_data.load_month[2:], "finished": month_complete_num,
                 "receive": month_receive_num, "unfinished": month_unfinished_num})
        month_report_data.full_data['monthSR'] = month_report_data.month_sr
        month_report_data.dump_data()
        month_report_data.load_data()
        load_month = datetime.datetime.strptime('2022/02', '%Y/%m')
        data_list = [(load_month - relativedelta(months=i)).strftime('%Y/%m')[2:] for i in range(12)]
        for month in data_list:
            for item in month_report_data.month_sr:
                if item['month'] == month:
                    self.month_sr.insert(0, item)


if __name__ == '__main__':
    parser = ParseExcelData('2022/02')
    parser.parse_data()
    main_sr_chart = main_sr_chart.MainSrChart(parser.month_sr)
    main_sr_chart.make_chart()
