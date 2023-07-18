import datetime

from WikiApi.WikiApi import WikiApi


def main():
    # start from April 1, 2023

    start_date = datetime.date(2023, 4, 1)
    
    # until yesterday
    end_date = datetime.date.today()- datetime.timedelta(days=1)

    current_date = start_date
    
    # loop through each day and store the results in bigquery dataset
    while current_date <= end_date:
        day = current_date.day
        month = current_date.month
        year = current_date.year
        wikiApi = WikiApi(day,month,year)
        wikiApi.run()
        current_date += datetime.timedelta(days=1)

if __name__ == "__main__":
    main()