import httpx
import asyncio

API_URL = "http://127.0.0.1:8000/api/v1/chat/text"

async def verify_chat_history():
    session_id = "test-session-verify-1"
    
    # 1. Turn 1
    print("Sending: My name is Abin")
    msg1 = {"message": "My name is Abin", "session_id": session_id}
    async with httpx.AsyncClient() as client:
        try:
            resp1 = await client.post(API_URL, json=msg1, timeout=30.0)
            print(f"Response 1: {resp1.json().get('response')}")
        except Exception as e:
            print(f"Error 1: {e}")

    # 2. Turn 2
    print("\nSending: What is my name?")
    msg2 = {"message": "What is my name?", "session_id": session_id}
    async with httpx.AsyncClient() as client:
        try:
            resp2 = await client.post(API_URL, json=msg2, timeout=30.0)
            response_text = resp2.json().get('response')
            print(f"Response 2: {response_text}")
            
            if "Abin" in response_text:
                print("\nSUCCESS: Chat history preserved.")
            else:
                print("\nFAILURE: Chat history NOT preserved.")
        except Exception as e:
            print(f"Error 2: {e}")

if __name__ == "__main__":
    asyncio.run(verify_chat_history())
