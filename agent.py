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

class FallbackLLM(BaseChatModel):
    def __init__(self, primary: BaseChatModel, fallback: BaseChatModel):
        self.primary = primary
        self.fallback = fallback
        self.model = getattr(primary, 'model', 'fallback-wrapper')

    @property
    def provider(self) -> str:
        return f"{self.primary.provider}-with-fallback"

    @property
    def name(self) -> str:
        return self.primary.name

    def _get_usage(self, response: Any) -> Optional[ChatInvokeUsage]:
        return None

    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T] | None = None
    ) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
        try:
            # print(f"Trying primary model: {self.primary.name}...") 
            return await self.primary.ainvoke(messages, output_format)
        except Exception as e:
            print(f"\n⚠️ Primary model failed: {e}")
            print(f"🔄 Switching to fallback model: {self.fallback.name}...\n")
            return await self.fallback.ainvoke(messages, output_format)

async def main():
    # Configure Google Gemini (Primary) - Direct API
    # Switching to 1.5-Flash for better stability and rate limits
    google_llm = ChatGoogle(
        model='gemini-1.5-flash',
        api_key=os.getenv('GOOGLE_API_KEY')
    )
    
    # Use Gemini directly without fallback for now to avoid Groq errors
    llm = google_llm

    print("\n🌐 Initializing Browser...")
    browser = Browser()
    
    try:
        print("\n✅ Ready! The agent is waiting for your commands.")
        print("Type 'exit' or 'quit' to close the program.\n")
        
        while True:
            try:
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
