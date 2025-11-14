from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional, Annotated
from tools.gmail_tools import fetch_unread_emails, create_draft, mark_as_read
from tools.llm_tools import analyze_email, generate_response
from utils.gmail_auth import get_gmail_service
import operator

class EmailAgentState(TypedDict):
    """State for email automation agent."""
    # In LangGraph, a state is the data object that moves through your graph —
    # it carries everything your app knows or remembers at a given moment in the workflow.
    # Think of it as:
    # “The context that gets updated and passed between nodes.”

    # Defining the state fields

    emails: List[dict]  # All fetched emails
    current_index: int  # Which email we're on

    # Optional[dict] This means:
    # current_email can be a dictionary when an email is selected
    # or None before any email is loaded
    
    current_email: Optional[dict]  # The email being processed
    analysis: Optional[dict]  # LLM analysis
    draft_response: str  # Generated response
    user_approved: bool  # Did user approve?
    messages: Annotated[list, operator.add]  # Status messages (this accumulates)


def fetch_email_node(state : EmailAgentState) -> dict:
    """
    Fetch unread emails from Gmail.
    
    Returns:
        dict: State updates with fetched emails
    """
    service = get_gmail_service()
    result = fetch_unread_emails(service, max_results=5)

    return {
        'emails': result,
        'current_index':0,
        'messages':['Fetched 5 emails']}


def select_email_node(state: EmailAgentState) -> dict:
    """
    Select the next email to process.
    
    Returns:
        dict: State updates with current email
    """
    # 1. Get emails list and current_index from state
    emails = state['emails']
    index = state['current_index']

    # 2. Check if index is valid (within list bounds)
    if index < len(emails):

    # 3. Get email at that index, Return state updates
      return {
          'current_email': emails[index],
          'messages': [f'Proccessing email {index+1}/{len(emails)}']
          }
    else:
      return {'current_email': None}


def analyze_email_node(state: EmailAgentState) -> dict:
    """
    Analyze current email using LLM.
    
    Returns:
        dict: State updates with analysis
    """
    # 1. Get current_email from state
    email = state['current_email']

    # 2. Call analyze_email() from llm_tools
    analysis = analyze_email(email)

    # 3. Return analysis
    return {
       'analysis': analysis,
        'messages':  [f"Analyzed: {analysis['category']}"]
        }


def generate_response_node(state: EmailAgentState) -> dict:
    """
    Generate draft response using LLM.
    
    Returns:
        dict: State updates with draft response
    """
    # 1. Get current_email and analysis from state
    email = state['current_email']
    analysis = state['analysis']

    # 2. Call generate_response()
    draft = generate_response(email, analysis)

    # 3. Return draft
    return {
       'draft_response': draft,
       'messages': [f"generated draft for {email['subject']}"]
    }


def create_draft_node(state: EmailAgentState) -> dict:
    """
    Create draft in Gmail.
    
    Returns:
        dict: State updates
    """
    # 1. Get current_email, draft_response from state
    email = state['current_email']
    draft_response = state['draft_response']
    service = get_gmail_service()

    # 2. Call create_draft() from gmail_tools
    draft = create_draft(
        service=service,
        to = email['sender'], 
        subject= f"Re: {email['subject']}",
        body= draft_response,
        thread_id= email['thread_id'])
    
    # Mark email as read since we processed it
    mark_as_read(service, email['id'])

    # 3. Increment current_index for next email
    # 4. Return updates
    return {
    "current_index": state['current_index'] + 1,
    "messages": [f"Draft created for: {email['subject']}"]
    }


def should_continue(state: EmailAgentState) -> str:
    """Decide if we should process more emails."""
    # Check if select_email_node found an email
    if state.get('current_email') is None:
        return "end"
    return "continue"


def should_respond(state: EmailAgentState) -> str:
    """Decide if we should respond to this email."""
    analysis = state.get('analysis', {})
    if analysis.get('should_respond', False):
        return "respond"
    else:
        # Skip this email, move to next
        return "skip"


def skip_email_node(state: EmailAgentState) -> dict:
    """Skip current email and move to next."""
    
    email = state['current_email']
    # Mark as read so we don't process it again
    mark_as_read(get_gmail_service(), email['id'])

    return {
        "current_index": state['current_index'] + 1,
        "messages": [f"Skipped: {state['current_email']['subject']}"]
    }

def create_email_agent():
    """
    Build and compile the LangGraph email agent.
    
    Returns:
        Compiled graph ready to run
    """
    # Initialize the graph
    workflow = StateGraph(EmailAgentState)
    
    # Add all nodes
    workflow.add_node("fetch_emails", fetch_email_node)
    workflow.add_node("select_email", select_email_node)
    workflow.add_node("analyze_email", analyze_email_node)
    workflow.add_node("generate_response", generate_response_node)
    workflow.add_node("create_draft", create_draft_node)
    workflow.add_node("skip_email", skip_email_node)  # Add the skip node
    
    # 1. Start → fetch
    workflow.add_edge(START, "fetch_emails")
    
    # 2. fetch → select
    workflow.add_edge("fetch_emails", "select_email")
    
    # 3. select → check if we have an email
    workflow.add_conditional_edges(
        "select_email",
        should_continue,
        {
            "continue": "analyze_email",  
            "end": END                     
        }
    )
    
    # 4. analyze → check if should respond
    workflow.add_conditional_edges(
        "analyze_email",
        should_respond,
        {
            "respond": "generate_response",  
            "skip": "skip_email"             
        }
    )
    
    # 5. generate → create draft
    workflow.add_edge("generate_response", "create_draft")
    
    # 6. create draft → select next email (loop back)
    workflow.add_edge("create_draft", "select_email")
    
    # 7. skip → select next email (loop back)
    workflow.add_edge("skip_email", "select_email")
    
    return workflow.compile()
























