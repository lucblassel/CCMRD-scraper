## Python scraper to extract compound info from CCMRD
This program scrapes [ccmrd.org](http://www.ccmrd.org) to extract data from chemical compounds.  
It is written in python 3.8.5  

it depends on the following packages: 
- requests (2.24.0)
- beautifulsoup4 (4.9.1)

The following `conda` command will install the correct environment: 
```shell
conda create -n ccmrdScraper \
    python=3.8.5 \
    requests=2.24.0 \
    beautifulsoup4=4.9.1
```

To run it, activate the `conda` environment and run the script:
```shell
conda activate ccmrdScraper && python scrapeWebsite.py
```

It will output a `.json` file with all found compound info.

