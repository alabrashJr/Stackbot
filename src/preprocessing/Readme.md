## **Preprocessing package**

Contains some functions used for cleaning and parsing xml data dumps 

## parse_xml_rows.py

Parses given xml file into given format

##### Run:

```
usage: parse_xml_rows.py [-h] -i INPUT_FILE [-o OUTPUT_FILE] [-f {csv,json}]
                           [-c CSV_COLUMNS [CSV_COLUMNS ...]]

arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Path of the file to be processed
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Path of the file to be written to
  -f {csv,json}, --output-format {csv,json}
                        Processing format
  -c CSV_COLUMNS [CSV_COLUMNS ...], --csv-columns CSV_COLUMNS [CSV_COLUMNS ...]
                        List of csv headers
```


## initialize_db.py

Transfers data into mongodb database for more flexible processing

#### Run:

```
usage: initialize_db.py [-h] -p FILES_PATH [-n DB_NAME]
                        [-f FILES_LIST [FILES_LIST ...]]

arguments:
  -h, --help            show this help message and exit
  -p FILES_PATH, --files-path FILES_PATH
                        Path of the files to be processed
  -n DB_NAME, --db-name DB_NAME
                        Path of the file to be written to
  -f FILES_LIST [FILES_LIST ...], --files-list FILES_LIST [FILES_LIST ...]
                        List of the files to be parsed and added to db
```



