# test_auth.py
# from utils.gmail_auth import get_gmail_service

# service = get_gmail_service()
# print("✅ Authentication successful!")

# # Test by listing labels
# results = service.users().labels().list(userId="me").execute()
# labels = results.get("labels", [])
# print(f"Found {len(labels)} labels in your Gmail")

#  testing gmail_tools.py
# from utils.gmail_auth import get_gmail_service
# from tools.gmail_tools import fetch_unread_emails

# service = get_gmail_service()

# # Test 1: Primary inbox only
# print("=== PRIMARY INBOX ===")
# emails = fetch_unread_emails(service, max_results=3, query='is:unread category:primary')
# for email in emails:
#     print(f"Subject: {email['subject']}")

# # Test 2: Promotions
# print("\n=== PROMOTIONS ===")
# promos = fetch_unread_emails(service, max_results=3, query='is:unread category:promotions')
# for email in promos:
#     print(f"Subject: {email['subject']}")

# # Test 3: All inbox (default behavior you had)
# print("\n=== ALL INBOX ===")
# all_emails = fetch_unread_emails(service, max_results=3, query='is:unread in:inbox')
# for email in all_emails:
#     print(f"Subject: {email['subject']}")

# test_llm.py
# from utils.gmail_auth import get_gmail_service
# from tools.gmail_tools import fetch_unread_emails
# from tools.llm_tools import analyze_email, generate_response

# service = get_gmail_service()
# emails = fetch_unread_emails(service, max_results=1)

# if emails:
#     email = emails[0]
#     print(f"Testing with: {email['subject']}\n")
    
#     analysis = analyze_email(email)
#     print("Analysis:", analysis, "\n")
    
#     draft = generate_response(email, analysis)
#     print("Draft:", draft)