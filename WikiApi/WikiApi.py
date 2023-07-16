from google.cloud import bigquery
from google.oauth2 import service_account
import requests
import uuid
import os
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))

class WikiApi:
    def __init__(self,day,month,year):
        self.day = int(day)<10 and f"0{day}" or day
        self.month = int(month)<10 and f"0{month}" or month
        self.year = year
        self.credentialsFile = os.path.join(current_dir, 'credentials', 'alpine-theory-392312-43b3aee89989.json')
        self.datasetId = 'wikimedia'

    def run(self):
        rows_pages = []
    
        top_pages = self.getTopWikipediaPages()
        # start count for number of articles
        count_ =0

    
        for item in top_pages:
            page = item[0]
            views = item[1]
            rank = item[2]
            date = item[3]
            # if number of articles are 100 then stop the loop
            if count_ == 100:
                break
            categories = self.getPageCategories(page)
            # if the given article has a category add the page information if not skip it
            if not categories == "":
                page_id = str(uuid.uuid4())  
                rows_pages.append((page_id, page, views,rank,date,categories))
                count_ += 1         
        # call storeInBigQuery To store data in big query
        self.storeInBigquery(rows_pages)


        
    
    def getTopWikipediaPages(self):
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{self.year}/{self.month}/{self.day}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        print(url)

        response = requests.get(url, headers=headers)
        try:
            data = response.json()            
            topPages = []
            # extract data from API response
            for item in data['items'][0]['articles']:
                title = item['article']
                views = item['views']
                rank = item['rank']
                date = f"{self.year}-{self.month}-{self.day}"
                topPages.append((title, views,rank,date))
            return topPages
        except Exception as e:
            raise Exception("An error occurred when retrieving the data.", e)
    

    def getPageCategories(self,pageTitle):
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=categories&titles={pageTitle}"
        response = requests.get(url)
        data = response.json()
        # extract data from API response
        pageId = next(iter(data['query']['pages']))
        pageInfo = data['query']['pages'][pageId]
        categories = pageInfo.get('categories', [])
        
        pageCategories = []
        for category in categories:
            cat = category['title'].replace("Category:", "")
            pageCategories.append(cat)
        return ", ".join(pageCategories)
    
    def storeInBigquery(self,rowResults):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentialsFile,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        
        client = bigquery.Client(credentials=credentials)
        # defince Schema for results table
        resultsSchema = [
            bigquery.SchemaField("PageID", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Page", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Views", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("Rank", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("Date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("Categories", "STRING", mode="REQUIRED"),
        ]   
        tableId = 'results'

        # make a list of dictionaries for each row
        resultsData = [dict(zip(["PageID","Page", "Views",'Rank',"Date","Categories"], row)) for row in rowResults]
        
         # Prepare the data to be loaded into results table
        jobConfig = bigquery.LoadJobConfig()
        jobConfig.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        jobConfig.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
        jobConfig.schema = resultsSchema
        # Insert data into the results table using a load job
        loadJob = client.load_table_from_json(
                        resultsData,
                        f"{client.project}.{self.datasetId}.{tableId}",
                        job_config=jobConfig
                    )
        # Wait for the load job to complete
        loadJob.result()
        # Check the status of the load job
        if loadJob.errors:
            print("Encountered errors while loading pages data:")
            for error in loadJob.errors:
                print(error)
        else:
            print("Pages data imported successfully.")
    
    def checkMissingDates(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentialsFile,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        client = bigquery.Client(credentials=credentials)
        tableId = 'results'
        tableRef = client.dataset(self.datasetId).table(tableId)
        table = client.get_table(tableRef)        
        start_date = datetime(2023, 4, 1).date()
        end_date = datetime.today().date() - timedelta(days=1)

        # Query to get all elements from the table
        query = f"SELECT date FROM `{self.datasetId}.{tableId}`"

        # Run the query
        query_job = client.query(query)
        results = query_job.result()
        
        # Create a set of unique dates from the query results
        existing_dates = set(row.date for row in results)

        # Check for missing dates
        missing_dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date not in existing_dates:
                missing_dates.append(current_date)
            current_date += timedelta(days=1)

        # Print the missing dates, if any
        if missing_dates:
            print("Missing dates:")
            for date in missing_dates:
                print(date)
        else:
            print("No missing dates found.")
        return missing_dates
    