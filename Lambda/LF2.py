
import boto3
import json
import requests
from boto3.dynamodb.conditions import Key, Attr  # Import Key and Attr
from botocore.exceptions import NoCredentialsError, ClientError


from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth


# Initialize SQS client
sqs = boto3.client('sqs')

# URL of your SQS Queue
queue_url = 'https://sqs.us-east-1.amazonaws.com/911167929377/AssignmentQueue'  # Replace with your actual queue URL

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('yelp-restaurants')

# Initialize AWS services
session = boto3.Session()
credentials = session.get_credentials()
username = "kunalthadani"  # Replace with your OpenSearch username
password = "Devikamohan@123"    # Replace with your OpenSearch password

# OpenSearch configurations
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, session.region_name, 'es', session_token=credentials.token)
host = 'https://search-restaurants-vdxopwnqknskbpvq5envfpxje4.aos.us-east-1.on.aws'  # Replace with your OpenSearch endpoint

ses_client = boto3.client('ses', region_name='us-east-1')  # Replace with your region

# Email parameters
sender_email = "kmt9501@nyu.edu"  # Replace with your sender email (must be verified in SES)
recipient_email = "kmt9501@nyu.edu"  # Replace with recipient email
subject = "Restaurant Recommendations"
# Define email parameters


def lambda_handler(event, context):
    try:
        # Poll messages from SQS
        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['All'],  # To get all available attributes
            MaxNumberOfMessages=10,  # Max allowed is 10 messages at a time
            MessageAttributeNames=['All'],
            WaitTimeSeconds=20  # Enable long polling
        )
        
        # Check if there are messages in the response
        if 'Messages' in response:
            for message in response['Messages']:
                print(f"Message Body: {message['Body']}")
                
                # Process the message body (which is typically JSON)
                message_body = json.loads(message['Body'])
                print(f"Processing message: {message_body}")
                
                url = f'{host}/_search?q={message_body['cuisine']}'
                
                response = requests.get(url, auth=HTTPBasicAuth(username, password))

                # Check if the response is successful
                response.raise_for_status()
        
                # Process the search results
                
                hits = response.json()['hits']['hits']
                results = [hit['_source'] for hit in hits]
                recommendations = []
                place = ""
                for result in results:
                    response_d = table.query(KeyConditionExpression=Key("id").eq(result["id"]))  # Scanning the entire table (for larger tables, use pagination)
                    for item in response_d['Items']:
                        place += f"{item['name']} - {item['address']}<br>"
                        
                

                body_html = f"""
<html>
    <head></head>
    <body>
        Hello! Here are my {message_body['cuisine']} restaurant suggestions:<br>
        {place}
        Enjoy your meal!
    </body>
</html>
"""
                email_params = {
                    'Source': sender_email,
                    'Destination': {
                        'ToAddresses': [
                            recipient_email
                        ]
                    },
                    'Message': {
                        'Subject': {
                            'Data': subject,
                            'Charset': 'UTF-8'
                        },
                        'Body': {
                            'Html': {
                                'Data': body_html,
                                'Charset': 'UTF-8'
                            }
                        }
                    }
                }
                ses_client.send_email(**email_params)

                # After successful processing, delete the message from the queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                print("Message deleted from queue.")
        else:
            print("No messages to process.")
    except Exception as e:
        print(f"Error receiving or processing messages: {e}")