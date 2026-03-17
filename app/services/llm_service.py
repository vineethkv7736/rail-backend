import google.generativeai as genai
from app.core.config import settings
import json

from app.core.tools import railway_tools
from app.core.prompts import SYSTEM_PERSONA

class LLMService:
    def __init__(self):
        self.sessions = {} # In-memory session storage
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                'gemini-flash-latest',
                tools=railway_tools,
                system_instruction=SYSTEM_PERSONA
            )
        else:
            self.model = None
            print("WARNING: Gemini API Key not found.")

    async def generate_response(self, prompt: str, system_instruction: str = None, session_id: str = None) -> dict:
        if not self.model:
            return {"text": "Error: LLM not configured.", "language_code": "en-IN"}
        
        debug_data = {"tools_used": [], "raw_api_response": {}}

        try:
            # 1. Get or Create Chat Session
            chat = None
            if session_id:
                if session_id in self.sessions:
                    print(f"Resuming session: {session_id}")
                    chat = self.sessions[session_id]
                else:
                    print(f"Creating new session: {session_id}")
                    chat = self.model.start_chat(history=[])
                    self.sessions[session_id] = chat
            else:
                # Stateless mode
                chat = self.model.start_chat()
            
            # Helper to execute tools locally
            def execute_tool(tool_name, tool_args):
                print(f"Executing Tool: {tool_name} with {tool_args}")
                for tool in railway_tools:
                    if tool.__name__ == tool_name:
                        return tool(**tool_args)
                return {"error": "Tool not found"}

            # First turn: Ask model what to do
            # We explicitly tell it about tools in system prompt or let it decide
            # Actually, `enable_automatic_function_calling=False` but `tools` configured 
            # lets us see the FunctionCall part.
            
            # Re-init model with tools but disable auto-execution
            self.model._tools = railway_tools 
            
            # Prepend current IST time so model can filter trains by departure time
            from datetime import datetime, timezone, timedelta
            ist = timezone(timedelta(hours=5, minutes=30))
            now_ist = datetime.now(ist).strftime("%A, %d %B %Y, %I:%M %p IST")
            time_aware_prompt = f"[Current Date & Time: {now_ist}]\n\n{prompt}"
            
            response = await chat.send_message_async(time_aware_prompt)
            
            # Loop max 10 times for chained tool calls
            for _ in range(10):
                try:
                    part = response.candidates[0].content.parts[0]
                except (IndexError, AttributeError):
                    text = response.text
                    break

                if part.function_call:
                    fc = part.function_call
                    tool_name = fc.name
                    tool_args = {k: v for k, v in fc.args.items()}
                    
                    # Capture debug info
                    debug_data["tools_used"].append({"name": tool_name, "args": tool_args})
                    
                    # Execute tool
                    tool_result = execute_tool(tool_name, tool_args)
                    debug_data["raw_api_response"] = tool_result # Keep last or accumulate? Keep last for now.
                    
                    # Send result back to model
                    from google.generativeai.protos import Content, Part, FunctionResponse
                    
                    tool_response = Part(
                        function_response=FunctionResponse(
                            name=tool_name,
                            response={"result": tool_result}
                        )
                    )
                    
                    # Send tool output and get NEXT response (which could be text OR another tool call)
                    response = await chat.send_message_async(Content(parts=[tool_response]))
                else:
                    text = response.text
                    break
            else:
                # If loop finishes without break, we gracefully fail
                text = "I'm having trouble validating the station details with the server. Could you please provide the specific **Station Code** (e.g., 'TVC' for Trivandrum)?"

            # Parse JSON from final text if needed
            result_json = {}
            try:
                clean_text = text.strip()
                if clean_text.startswith("```json"): clean_text = clean_text[7:-3]
                result_json = json.loads(clean_text)
            except:
                result_json = {"text": text, "language_code": "en-IN", "intent": "GENERAL"}

            # Attach debug info
            result_json["debug_info"] = debug_data
            return result_json

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"LLM Generation Error: {e}")
            return {"text": "I am having trouble connecting right now. Please try again.", "language_code": "en-IN", "intent": "ERROR"}

llm_service = LLMService()
