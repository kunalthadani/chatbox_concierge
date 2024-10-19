import json
import boto3
import random
import string

lex_client = boto3.client('lexv2-runtime')


def lambda_handler(event, context):
    messages = event["messages"]
    print(event)
    
    
    bot_id = 'LMTFB9QVXA'
    locale_id = 'en_US'  # Change based on your locale

    for message in messages:
        session_id = generate_session_id()
        if message['unstructured']['id'] is not None:
            session_id = message['unstructured']['id'] 
        
        response = lex_client.recognize_text(
                botId=bot_id,
                botAliasId='RU5VIQMPJ9',
                localeId=locale_id,
                sessionId=session_id,
                text=message['unstructured']['text']
            )
        print(response)
        replies = list()
        body = {}
        reply_messages = []
        if 'messages' in response.keys():
            reply_messages = response["messages"]
        
        for msg in reply_messages:
            reply = {}
            reply['type'] = 'unstructured'
            unstructured = {}
            unstructured["text"] = msg['content']
            unstructured["id"] = session_id
            reply['unstructured'] = unstructured
            replies.append(reply)
        
        body['messages'] = replies
        return body

# Helper function to generate a random session ID if not provided
def generate_session_id(length=12):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))