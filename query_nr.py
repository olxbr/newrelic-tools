'''
Module created to query the New Relic API and extract the results to insert them into a database.
'''
import datetime
import json
import os
import time

import requests

from prometheus_client import Gauge, start_http_server


g = Gauge('Cost_of_APP', 'Cost of using new relic per application', labelnames=['appName'])

def run_nrquery(select_statement):
    """"
    Run the query against the New Relic GraphQL API and return the response as a string.
    """
    url = "https://api.newrelic.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "API-Key": os.environ["NEWRELIC_API_KEY"],
    }

    full_query = {
                    "query": f"""{{actor {{
                                    account(id: {os.environ["NEWRELIC_ACCOUNT_ID"]}) {{
                                        nrql(query: "{select_statement}") {{
                                            results
                                            }}
                                     }}
                                    }}
                                }}"""
                }
    response = requests.post(url, headers=headers, json=full_query)
    return response.text

def extract_results(json_content):
    """
    Extract the results from the response and return them as a list of dictionaries.
    """
    output = json.loads(json_content)['data']['actor']['account']['nrql']['results']
    return output

#def generate_db_insert(list_of_dicts, current_time):
#    """"
#    Generate a list of SQL INSERT statements from the list of dictionaries.
#    """
#    query_list = []
#    for item in list_of_dicts:
#        insert_query=f"INSERT INTO app_usage (date, appName, cost) VALUES ('{current_time}', '{item['appName']}', {item['Cost']});"
#        query_list.append(insert_query)
#
#    return query_list


select_statements=[
    #Transaction and TransactionError

    "SELECT bytecountestimate() / 10e8 * 24 * 30 * 12 * 0.30 * 5.15 as 'Cost' FROM `Transaction`, `TransactionError` FACET appName LIMIT 400 SINCE 1 hour ago",

    #Metric
    "SELECT bytecountestimate() / 10e8 * 24 * 30 * 12 * 0.30 * 5.15 as 'Cost' FROM `Metric` WHERE newrelic.source = 'agent' AND instrumentation.provider != 'kentik' AND instrumentation.provider != 'pixie' FACET appName LIMIT 400 SINCE 1 hour ago",

    #Tracing
    "SELECT bytecountestimate() / 10e8 * 24 * 30 * 12 * 0.30 * 5.15 as 'Cost' FROM `Span`, `ErrorTrace`, `SqlTrace` WHERE instrumentation.provider != 'pixie' FACET appName LIMIT 400 SINCE 1 hour ago",

    #Log
    "SELECT bytecountestimate() / 10e8 * 24 * 30 * 12 * 0.30 * 5.15 as 'Cost' FROM `Log`, `LogExtendedRecord` WHERE instrumentation.proviver != 'kentik' facet  entity.name or namespace_name as 'appName' LIMIT 400 since 1 hour ago",

]

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    for select_statement in select_statements:
        #Run the query and extract the results
        list_of_results=extract_results(run_nrquery(select_statement))

        
        for item in list_of_results:
            #import ipdb
            #ipdb.set_trace()
            g.labels(appName=item['appName']).set(item['Cost'])


        #Generate the list of SQL INSERT statements
    #    list_of_inserts=generate_db_insert(list_of_results, current_time)

    #    for insert in list_of_inserts:
    #        print  (insert)

start_http_server(8000)

while True:
    main()
#    import ipdb
#    ipdb.set_trace()
    time.sleep(100)
