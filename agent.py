from browser_use import Agent, Browser, Controller
from browser_use.llm.groq.chat import ChatGroq
from browser_use.llm.google.chat import ChatGoogle
from browser_use.llm.base import BaseChatModel, ChatInvokeCompletion
from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeUsage
import os
import asyncio
from dotenv import load_dotenv
from typing import TypeVar, Any, Optional

load_dotenv()

T = TypeVar('T')

import sys

async def main():
    # Configure Google Gemini (Primary) - Direct API
    # Reverting to gemini-2.0-flash-exp as 1.5-pro failed to navigate (tool use issue)
    google_llm = ChatGoogle(
        model='gemini-2.0-flash-exp',
        api_key=os.getenv('GOOGLE_API_KEY')
    )
    
    # Simplify: Use single LLM to avoid credit errors
    llm = google_llm

    print("\n🌐 Initializing Local Browser...")
    # Standard local browser
    browser = Browser()
    
    # Check for command line arguments
    initial_task = None
    if len(sys.argv) > 1:
        initial_task = " ".join(sys.argv[1:])

    try:
        print("\n✅ Ready! The agent is waiting for your commands.")
        print("Type 'exit' or 'quit' to close the program.\n")
        
        while True:
            try:
                if initial_task:
                    task = initial_task
                    initial_task = None # Execute once then fall back to interactive
                    print(f"🤖 Processing command from arguments: {task}")
                else:
                    task = input("🤖 What task should I perform? > ")
                if not task.strip():
                    continue
                    
                if task.lower() in ['exit', 'quit', 'salir', 'cerrar']:
                    print("Goodbye!")
                    break

                print(f"\n🚀 Starting task: {task}\n")
                
                # Create a new agent for each task to reset context/history if needed
                # Or we could keep it to maintain history, but usually per-task is cleaner
                agent = Agent(
                    task=task,
                    llm=llm,
                    browser=browser,
                )

                await agent.run()
                print("\n✅ Task completed!\n")
                
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                continue
            except Exception as e:
                print(f"\n❌ An error occurred during the task: {e}\n")
                
    finally:
        print("Closing browser...")
        await browser.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
