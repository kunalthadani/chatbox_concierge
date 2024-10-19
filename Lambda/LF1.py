import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Initialize the Lex client
    print(event)
    lex = boto3.client('lexv2-runtime')
    sqs = boto3.client('sqs')
    
    
    # Extract the input from the Lex event
    intent = event['interpretations'][0]['intent']['name']
    slots = event['interpretations'][0]['intent']['slots']
    session_attributes = event.get('sessionState', {}).get('sessionAttributes', {})
    
    # Handle different intents
    if intent == 'GreetingIntent':
        return handle_greeting(session_attributes)
    elif intent == 'ThankYouIntent':
        return handle_thank_you(session_attributes)
    elif intent == 'DiningSuggestionsIntent':
        return handle_dining_suggestions(slots, session_attributes, sqs)
    else:
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close'
                },
                'intent': {
                    'name': intent,
                    'state': 'Fulfilled'
                },
                'sessionAttributes': session_attributes
            },
            'messages': [{
                'contentType': 'PlainText',
                'content': "I'm not sure how to handle that request. Can you try again?"
            }]
        }

def handle_greeting(session_attributes):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': 'GreetingIntent',
                'state': 'Fulfilled'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [{
            'contentType': 'PlainText',
            'content': "Hi there! How can I help you today?"
        }]
    }

def handle_thank_you(session_attributes):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': 'ThankYouIntent',
                'state': 'Fulfilled'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [{
            'contentType': 'PlainText',
            'content': "You're welcome! Have a great day!"
        }]
    }

def handle_dining_suggestions(slots, session_attributes,sqs):
    # Extract slot values
    location = get_slot_value(slots, 'location', session_attributes)
    cuisine = get_slot_value(slots, 'Cuisine', session_attributes)
    dining_time = get_slot_value(slots, 'Time', session_attributes)
    num_people = get_slot_value(slots, 'number_people', session_attributes)
    email = get_slot_value(slots, 'Email', session_attributes)
    
    # Update session attributes
    session_attributes.update({
        'Location': location,
        'Cuisine': cuisine,
        'Time': dining_time,
        'number_people': num_people,
        'Email': email
    })
    
    # Validate all required slots are filled
    required_slots = ['location', 'Cuisine', 'Time', 'number_people', 'Email']
    if not all([location, cuisine, dining_time, num_people, email]):
        for slot_name in required_slots:
                if not slot_filled(slots, slot_name,session_attributes):
                    missing_slot = slot_name
        
        print(missing_slot)
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'slotToElicit': missing_slot
                },
                'intent': {
                    'name': 'DiningSuggestionsIntent',
                    'state': 'InProgress'
                },
                'sessionAttributes': session_attributes
            },
            'messages': [{
                'contentType': 'PlainText',
                'content': f"I still need some more information. Can you provide your {missing_slot}?"
            }]
        }
    
    # All slots are filled, push to SQS
    
    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/911167929377/AssignmentQueue',  # Replace with your SQS queue URL
        MessageBody=json.dumps({
            'location': location,
            'cuisine': cuisine,
            'dining_time': dining_time,
            'num_people': num_people,
            'email': email
        })
    )
    
        
        
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': 'DiningSuggestionsIntent',
                'state': 'Fulfilled'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [{
            'contentType': 'PlainText',
            'content': f"Thank you for providing your preferences. I've received your request for {cuisine} cuisine in {location} for {num_people} people at {dining_time}. I'll send restaurant suggestions to {email} shortly!"
        }]
    }
    
def get_slot_value(slots, slot_name, session_attributes):
    # Try to get the value from the current slot
    slot_value = None
    if slots and slot_name in slots:
        slot = slots[slot_name]
        if slot and 'value' in slot and 'interpretedValue' in slot['value']:
            slot_value = slot['value']['interpretedValue']
    
    # If not found, try to get from session attributes
    if not slot_value:
        slot_value = session_attributes.get(slot_name)
    
    return slot_value
    
def slot_filled(slots, slot_name,session_attributes):
    value = get_slot_value(slots,slot_name,session_attributes)
    if value: 
        return True
    return False
