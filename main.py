import datetime

from WikiApi.WikiApi import WikiApi


def main():
    # get yesterday
    yesterday = datetime.date.today()- datetime.timedelta(days=1)
    day = yesterday.day
    if day == 1:
        # get previous day
        yesterday = yesterday - datetime.timedelta(days=1)
        day = yesterday.day
    month = yesterday.month
    year = yesterday.year
    
    # get yesterdays data and store it in bigquery
    # print(missingDates)
    wikiApi = WikiApi(day,month,year)
    wikiApi.run()
    # check if there are any missing dates
    missingDates = wikiApi.checkMissingDates()
    
    # if there are missing dates, get the data and store it in bigquery
    for i in missingDates:
        day = i.day
        month = i.month
        year = i.year
        print(f"Getting data for {day}/{month}/{year}")
        wikiApi = WikiApi(day,month,year)
        wikiApi.run()

if __name__ == "__main__":
    main()