from agents.email_agent import create_email_agent

def main():
    """Run the email automation agent."""
    
    print("🤖 Starting Email Automation Bot...\n")
    
    # Create the agent
    agent = create_email_agent()
    
    # Initial state
    initial_state = {
        "emails": [],
        "current_index": 0,
        "current_email": None,
        "analysis": None,
        "draft_response": "",
        "user_approved": False,
        "messages": []
    }
    
    # Run the agent
    try:
        result = agent.invoke(initial_state)
        
        # Print results
        print("\n" + "="*50)
        print("📊 EXECUTION SUMMARY")
        print("="*50)
        
        for msg in result['messages']:
            print(f"  ✓ {msg}")
        
        print(f"\n📧 Processed {result['current_index']} emails")
        print("\n✅ Check your Gmail drafts folder!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()