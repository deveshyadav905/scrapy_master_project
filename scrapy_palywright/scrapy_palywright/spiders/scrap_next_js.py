import json
import scrapy
import pandas as pd
from os import link



class ScrapNextJsSpider(scrapy.Spider):
    name = "scrap_next_js"
    
    start_urls = ["https://explore.jobs.netflix.net/careers"]

    def parse(self, response):
        
        if response.status == 200:
            js_str = response.xpath('//code[@id="smartApplyData"]/text()').get()
            if not js_str:
                self.logger.error("Could not find the job data in the page.")
                return 
            
            data = json.loads(js_str)
            for keys, values in data.items():
                if keys == 'positions':
                    with open(f'netflix_jobs_{keys}.json', 'w') as f:
                        json.dump(values, f, indent=4)
                    self.logger.info("Job data has been written to netflix_jobs_positions.json")

                # extract facets data to filter jobs on basis of facets
                if keys == 'facets':
                    if isinstance(values, dict):
                        for facet_key, facet_values in values.items():
                            if facet_key=='locations':
                                for location in facet_values:
                                    if location:
                                        api_url = f"https://explore.jobs.netflix.net/api/apply/v2/jobs/?domain=netflix.com&location={location}&sort_by=relevance&triggerGoButton=false"
                                        print(api_url)
                                        yield scrapy.Request(url=api_url, callback=self.parse_api)
                            # print(f"Facet Key: {facet_key}, Facet Value Type: {type(facet_values)}")
                            with open(f'netflix_facets_{facet_key}.json', 'w') as f:
                                json.dump(facet_values, f, indent=4)
                            self.logger.info(f"Facet data for {facet_key} has been written to netflix_facets_{facet_key}.json")
                    else:
                        self.logger.warning(f"Expected 'facets' to be a dict, but got {type(values)}")
        else:
            self.logger.error(f"Failed to retrieve the page, status code: {response.status}")

    def parse_api(self, response):
        if response.status == 200:
            data = response.json()
            positions = data.get('positions', [])
            if positions:
                with open(f'Jobs_By_location/netflix_jobs.csv', 'a') as f:
                    dataframe = pd.DataFrame(positions)
                    dataframe.to_csv(f, header=f.tell()==0, index=False)

                self.logger.info(f"Job data from API has been written to Jobs_By_location/netflix_jobs.csv")
            else:
                self.logger.warning("No positions found in the API response.")
        else:
            self.logger.error(f"Failed to retrieve the API data, status code: {response.status}")