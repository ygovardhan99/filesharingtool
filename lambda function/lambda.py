import json
import boto3

# Initialize SES client
ses_client = boto3.client('ses', region_name='us-east-1')

def lambda_handler(event, context):
    # Extract info
    file_url = event['file_url']
    email_addresses = event['email_addresses']
    
    if not isinstance(email_addresses, list):
        email_addresses = [email_addresses]

    # Send email
    for email in email_addresses:
        try:
            response = ses_client.send_email(
                Source='gyalavar@uab.edu',
                Destination={
                    'ToAddresses': [email]
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': f'A file has been sent to you. Please access the file using the link here: {file_url}',
                        }
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': 'File Received Notification',
                    },
                }
            )
            print(f'Successfully sent Email to {email}. Here is the MessageId: {response["MessageId"]}')
        except Exception as e:
            print(f'Error sending email to {email}: {str(e)}')

    return {
        'statusCode': 200,
        'body': json.dumps('Emails sent successfully')
    }