from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import GROQ_API_KEY, MODEL_NAME
import json


llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0.3
    )

def analyze_email(email_data: dict) -> dict:
    """
    Analyze email content and determine response strategy.
    
    Args:
        email_data: Dict with 'sender', 'subject', 'body'
        
    Returns:
        dict: Analysis with 'should_respond', 'tone', 'key_points', 'urgency'
    """

    system_prompt = """You are an email analysis assistant. Analyze the given email and provide:
    1. should_respond: (true/false) - Should this email get a response?
    2. tone: (formal/casual/friendly) - Appropriate tone for response
    3. key_points: List of main points to address
    4. urgency: (high/medium/low) - How urgent is this email?
    5. category: (question/request/information/greeting/spam)

    Respond ONLY in JSON format.
    Example response format:
    {
        "should_respond": true,
        "tone": "formal",
        "key_points": ["point 1", "point 2"],
        "urgency": "medium",
        "category": "question"
    }"""


    # Truncate body to prevent token overflow
    body_preview = email_data['body'][:2000]

    email_text = f"""
    From: {email_data['sender']}
    Subject: {email_data['subject']}
    Body: {body_preview}
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=email_text)
    ]

    try:
        # Step 3: Get response
        response = llm.invoke(messages)
        response_text = response.content
        
        # Step 4: Parse JSON
        # Sometimes LLM adds markdown, so clean it
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            # Case 2: ``` ... ```
            response_text = response_text.split("```")[1].split("```")[0]
        
        analysis = json.loads(response_text.strip())
        return analysis
        
    except Exception as e:
        print(f"Error in analyze_email: {e}")
        return {
            "should_respond": False,
            "tone": "formal",
            "key_points": [],
            "urgency": "low",
            "category": "error"
        }


def generate_response(email_data: dict, analysis: dict) -> str:
    """
    Generate email response based on analysis.
    
    Args:
        email_data: Original email data
        analysis: Analysis from analyze_email()
        
    Returns:
        str: Generated email response
    """

    tone = analysis.get('tone', 'professional')
    key_points = analysis.get('key_points', [])

    system_prompt = f"""You are a professional email response writer. 
    Generate a {tone} email response that:
    - Addresses these key points: {', '.join(key_points)}
    - Matches the urgency level: {analysis['urgency']}
    - Is concise and clear
    - Ends with appropriate sign-off

    Do not include subject line, just the body."""

    context = f"""
    Original Email:
    From: {email_data['sender']}
    Subject: {email_data['subject']}
    Body: {email_data['body'][:500]}  # Limit to avoid token overflow
    """

    messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=context)
    ]

    try:
        response = llm.invoke(messages)
        return response.content  # Just return the text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Thank you for your email. I'll get back to you soon."
    

