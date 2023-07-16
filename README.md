# WikiAPI

This program utilizes the Wikipedia API to fetch the top 100 viewed pages for a specific day and stores the data in a BigQuery dataset.

## Requirements

Before using the program, ensure that you have installed the required dependencies. You can do this by running the following command:
```shell
pip install -r requirements.txt
```

## How to Use

To use the program, follow these steps:

1. Grant write permissions for the BigQuery API. You can do this by visiting the [Google Cloud Console](https://console.cloud.google.com/), enabling the BigQuery API, and ensuring you have the necessary permissions.

2. Download the credential JSON file for the API:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Navigate to your project and go to the "Credentials" section.
   - Click on "Create Credentials" and select "Service Account Key".
   - Choose the appropriate service account and key type, then click "Create".
   - Save the JSON file to your local machine.

3. Place the downloaded credential file into the `WikiAPI/credentials/` folder.

4. Inside the `WikiAPI.py` file, locate the following line:
   
   ```python 
   self.credentialsFile = os.path.join(current_dir, 'credentials', 'alpine-theory-392312-43b3aee89989.json') 
Replace 'alpine-theory-392312-43b3aee89989.json' with the filename of the credential file you downloaded in the previous step.

5. Inside the WikiAPI.py file, locate the following line:
6. `If you want to change the number of data fetched, modify the `count_` variable in the code to your desired value.`

## Backfilling Data

To backfill the data into the BigQuery dataset, run the `backfill.py` script. This will add all the data to the dataset.

## Running the Program Daily

To run the program daily at 00:00, you can set up cronjobs on your server. Here are the steps:

1. Open the cronjob configuration file using the command `crontab -e`.
2. Add the following line to the file:

```shell
0 0 * * * /path/to/python /path/to/main.py
```
Replace `/path/to/python` with the path to your Python executable and `/path/to/main.py` with the full path to the `main.py` file of the program.

Save the file, and the program will run automatically every day at midnight.

## Author

- Ian Cheng (https://github.com/iancheng135)