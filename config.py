import configparser

conf = configparser.RawConfigParser()
conf.read("settings.ini")
selection = conf.sections()
itms_report_get_url = conf.get("itms", "report_get_url")
itms_report_download_url = conf.get("itms", "report_download_url")
itms_authorization = conf.get("itms", "authorization")
