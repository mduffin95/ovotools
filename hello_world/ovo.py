from datetime import date, timedelta, datetime
from ovoenergy.ovoenergy import OVOEnergy
import asyncio
import os
import boto3
import json


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def current_milli_time(time: datetime) -> str:
    return str(int(round(time.timestamp() * 1000)))


def load():

    client = OVOEnergy()
    authenticated = asyncio.run(client.authenticate(
        os.environ["OVO_USER"],
        os.environ["OVO_PASS"]
    ))

    records = []

    if authenticated:

        start_date = date(2024, 2, 8)
        end_date = date(2024, 2, 16)
        for single_date in daterange(start_date, end_date):
            string_date = single_date.strftime("%Y-%m-%d")
            half_hourly_usage = asyncio.run(client.get_half_hourly_usage(string_date))
            electricity = half_hourly_usage.electricity
            for f in electricity:
                record = {
                    'Dimensions': [],
                    'MeasureName': 'electricity_usage',
                    'MeasureValue': f.consumption,
                    'MeasureValueType': 'DOUBLE',
                    'Time': current_milli_time(f.interval.start)
                }
                records.append(record)

            client = boto3.client('timestream-write')

            try:
                result = client.write_records(DatabaseName="home", TableName="electricity",
                                                   Records=records, CommonAttributes={})
                print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
            # except client.exceptions.RejectedRecordsException as err:
            #     _print_rejected_records_exceptions(err)
            except Exception as err:
                print("Error:", err)

    return {
        'statusCode': 200,
        'body': json.dumps('written')
    }
