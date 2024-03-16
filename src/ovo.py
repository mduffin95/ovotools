from datetime import date, timedelta, datetime
from ovoenergy.ovoenergy import OVOEnergy
import asyncio
import boto3
from botocore.config import Config


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def milli_time(time: datetime) -> str:
    return str(int(round(time.timestamp() * 1000)))


def write_records(write_client, records):
    write_client.write_records(
        DatabaseName="home",
        TableName="electricity",
        Records=records,
        CommonAttributes={})


def load():
    # Create a Systems Manager ovo_client
    ssm = boto3.client('ssm', region_name='eu-west-1')

    # Get a parameter
    user_param = ssm.get_parameter(Name='OVO_USER', WithDecryption=True)
    pass_param = ssm.get_parameter(Name='OVO_PASS', WithDecryption=True)

    # Print the parameter value
    user = user_param['Parameter']['Value']
    password = pass_param['Parameter']['Value']

    ovo_client = OVOEnergy()
    authenticated = asyncio.run(ovo_client.authenticate(user, password))

    if authenticated:
        print("authenticated")

        single_date = date.today() - timedelta(days=1)
        session = boto3.Session()
        write_client = session.client(
            'timestream-write',
            config=Config(read_timeout=20, max_pool_connections=5000, retries={'max_attempts': 10}))

        string_date = single_date.strftime("%Y-%m-%d")
        half_hourly_usage = asyncio.run(ovo_client.get_half_hourly_usage(string_date))
        electricity = half_hourly_usage.electricity

        dimensions = [
            {'Name': 'supplier', 'Value': 'ovo'},
            {'Name': 'postcode', 'Value': 'BN16HL'},
        ]
        records = []
        for half_hour in electricity:
            end_time = half_hour.interval.end
            # if end_time < (datetime.now() - timedelta(days=1)):
            #     continue
            record = {
                'Dimensions': dimensions,
                'MeasureName': 'consumption',
                'MeasureValue': str(half_hour.consumption),
                'MeasureValueType': 'DOUBLE',
                'Time': milli_time(end_time)
            }
            records.append(record)
            if len(records) == 100:
                try:
                    write_records(write_client, records)
                    records = []

                except write_client.exceptions.RejectedRecordsException as err:
                    print("Error:", err)
                except Exception as err:
                    print("Error:", err)

        if len(records) > 0:
            write_records(write_client, records)


if __name__ == "__main__":
    load()
