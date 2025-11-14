import base64
from email.mime.text import MIMEText

def fetch_unread_emails(service, max_results=10, query='is:unread category:primary'):
    """
    Fetch unread emails from Gmail inbox.
    
    Args:
        service: Authenticated Gmail service object
        max_results: Maximum number of emails to fetch
        
    Returns:
        list: List of email dictionaries with basic info
    """
    response = service.users().messages().list(
        userId='me',
        q=query,  # Query for unread emails
        maxResults=max_results
    ).execute()
    
    messages = response.get('messages',[])
    
    if not messages:
        print('There are no unread emails.')
        return []
    
    result = [get_email_details(service, msg['id']) for msg in messages]

    return result


# Email structure, it can also have nested parts
{
    'id': 'message_id',
    'threadId': 'thread_id',
    'snippet': 'Preview text...',
    'payload': {
        'headers': [
            {'name': 'From', 'value': 'sender@example.com'},
            {'name': 'Subject', 'value': 'Email subject'},
            {'name': 'Date', 'value': '...'}
        ],
        'body': {'data': 'base64_encoded_content'}
    }
}

#  function to get the details from the email
def get_email_details(service, message_id):
    """
    Get detailed content of a specific email.
    
    Args:
        service: Gmail service
        message_id: Email message ID
        
    Returns:
        dict: Email details including sender, subject, body, date
    """

    email_content = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'  # Get full email content
    ).execute()
    
    result = {}

    result['id'] = message_id
    result['thread_id'] = email_content.get('threadId', '')
    result['snippet'] = email_content.get('snippet', '')

    headers = email_content['payload']['headers']  

    for header in headers:
      if header['name'] == 'From':
        result['sender'] = header['value']
      if header['name'] == 'Subject':
        result['subject'] = header['value']
      if header['name'] == 'To':  
        result['to'] = header['value']

    # Use the robust body extraction helper
    result['body'] = get_email_body(email_content['payload'])
    
    # Fallback to snippet if body is empty
    if not result['body']:
        result['body'] = result['snippet']

    return result


def get_email_body(payload):
    """
    Recursively extract email body from payload.
    Handles simple, multipart, and nested multipart emails.
    """
    body = ''
    
    # Case 1: Body data directly in payload
    if 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    # Case 2: Multipart email - recursively search parts
    if 'parts' in payload:
        for part in payload['parts']:
            # Check mime type - prefer text/plain, fallback to text/html
            mime_type = part.get('mimeType', '')
            
            if mime_type == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            
            # Recursive case: part has nested parts
            if 'parts' in part:
                body = get_email_body(part)
                if body:
                    return body
        
        # If no text/plain found, try text/html
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    
    return body


def mark_as_read(service, message_id):
    """
    Mark an email as read.
    
    Args:
        service: Gmail service
        message_id: Email message ID
    """
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error marking email as read: {e}")
        return False
    

def send_email(service, to, subject, body, thread_id=None):
    """
    Send an email (or reply to a thread).
    
    Args:
        service: Gmail service
        to: Recipient email
        subject: Email subject
        body: Email body content
        thread_id: Optional thread ID for replies
        
    Returns:
        dict: Sent message info
    """
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    # Convert the message object to bytes
    raw_message = message.as_bytes()

    # Encode to base64 URL-safe format
    encoded_message = base64.urlsafe_b64encode(raw_message).decode('utf-8')

    body_payload = {'raw': encoded_message}

    # If replying to a thread, add threadId
    if thread_id:
        body_payload['threadId'] = thread_id

    sent_message = service.users().messages().send(
        userId='me',
        body=body_payload
    ).execute()

    return sent_message

def create_draft(service, to, subject, body, thread_id=None):
    """
    Create a draft email for review.
    
    Args:
        service: Gmail service
        to: Recipient
        subject: Email subject  
        body: Email body
        thread_id: Optional thread ID
        
    Returns:
        dict: Draft info
    """
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    # Convert the message object to bytes
    raw_message = message.as_bytes()

    # Encode to base64 URL-safe format
    encoded_message = base64.urlsafe_b64encode(raw_message).decode('utf-8')

    draft_body = {'message': { 'raw': encoded_message}}

    if thread_id:
       draft_body['message']['thread_id'] = thread_id

    draft = service.users().drafts().create(
        userId='me',
        body=draft_body
    ).execute() 
    
    return draft