from . import filesystem_tools
import time
import os
import json
from openai import OpenAI

# WARNING: Do not hardcode API keys in production code.
# This is for demonstration purposes only.
# In a real application, use environment variables.
OPENROUTER_API_KEY = "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"

class ManusInspiredAgent:
    def __init__(self, dry_run=False):
        self.history = []
        self.dry_run = dry_run
        self.tool_registry = {
            "create_file": filesystem_tools.create_file,
            "read_file": filesystem_tools.read_file,
            "append_to_file": filesystem_tools.append_to_file,
            "list_files": filesystem_tools.list_files,
            # We will add browser tools here later
        }

        # Initialize the OpenRouter client
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set.")

        self.llm_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        self.model = "google/gemini-2.0-flash-exp:free"

        print(f"Agent initialized in {'dry run' if dry_run else 'live'} mode.")

    def run(self, objective: str):
        """
        Runs the agent to achieve the given objective.
        """
        print(f"\n--- Starting objective: {objective} ---")

        # 1. Create a todo.md file to track the plan
        plan = self.generate_initial_plan(objective)
        self.execute_action({
            "tool_name": "create_file",
            "parameters": {"path": "todo.md", "content": plan}
        })

        # Main agent loop
        loop_count = 0
        while loop_count < 3:  # Limit loops for this example
            loop_count += 1
            print(f"\n--- Loop {loop_count} ---")

            # 2. Read the todo.md file to stay focused
            current_plan = self.execute_action({
                "tool_name": "read_file",
                "parameters": {"path": "todo.md"}
            })

            # 3. Decide on the next action
            next_action = self.decide_next_action(objective, current_plan)
            if not next_action:
                print("LLM failed to provide a next action. Ending run.")
                break

            # 4. Execute the action
            observation = self.execute_action(next_action)

            # 5. Update the history and the todo.md file
            self.update_history(next_action, observation)
            self.update_plan("todo.md", next_action, observation)

            # 6. Check if the objective is complete
            if self.is_objective_complete(objective, self.history):
                print("\n--- Objective complete! ---")
                break

        print("\n--- Final todo.md content ---")
        print(self.execute_action({"tool_name": "read_file", "parameters": {"path": "todo.md"}}))

        return "Objective run finished."

    def generate_initial_plan(self, objective: str) -> str:
        print("Generating initial plan...")
        # In a real scenario, this would be an LLM call
        return f"# Plan for: {objective}\n\n- Step 1: Open a browser and search for the objective.\n- Step 2: Extract the relevant information.\n- Step 3: Save the information to a file."

    def decide_next_action(self, objective: str, current_plan: str) -> dict:
        print("Deciding next action (calling LLM)...")

        system_prompt = """
        You are an expert AI agent. Your goal is to achieve the user's objective by calling tools.
        Review the objective, the current plan, and your history of previous actions.
        Then, decide on the single best tool to call next to progress on the plan.
        You must respond with a call to one of the available tools.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Objective: {objective}\n\nCurrent Plan:\n{current_plan}\n\nHistory:\n{self.history}"}
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Creates a new file with the given content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path for the new file."},
                            "content": {"type": "string", "description": "The content to write to the file."}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "append_to_file",
                    "description": "Appends content to the end of a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to the file to append to."},
                            "content": {"type": "string", "description": "The content to append."}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads and returns the content of a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to the file to read."}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "browser_open_url",
                    "description": "Opens a URL in the browser. This should be the first step for any research task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL to open."}
                        },
                        "required": ["url"]
                    }
                }
            }
        ]

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if tool_calls:
                    tool_call = tool_calls[0]
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    return {
                        "tool_name": function_name,
                        "parameters": function_args
                    }
                else:
                    print("LLM did not return a tool call.")
                    return None

            except Exception as e:
                print(f"Error calling LLM (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    print("LLM call failed after multiple retries.")
                    return None


    def execute_action(self, action: dict) -> str:
        """
        Executes a given action by looking it up in the tool registry.
        """
        tool_name = action["tool_name"]
        params = action["parameters"]
        print(f"Executing action: {tool_name} with params: {params}")

        if self.dry_run:
            return f"[Dry Run] Executed {tool_name} with {params}. At this point, the real tool would be called."

        if tool_name in self.tool_registry:
            tool_function = self.tool_registry[tool_name]
            try:
                return tool_function(**params)
            except Exception as e:
                return f"Error executing tool {tool_name}: {e}"
        else:
            if tool_name.startswith("browser_"):
                return f"[Dry Run] Executed browser tool {tool_name} with {params}."
            return f"Error: Tool '{tool_name}' not found."


    def update_history(self, action: dict, observation: str):
        print("Updating history...")
        self.history.append((action, observation))

    def update_plan(self, plan_file: str, action: dict, observation: str):
        print(f"Updating plan file: {plan_file}")
        content = f"\n\n---\n\n**Action:** `{action}`\n\n**Observation:**\n```\n{observation}\n```"
        self.execute_action({
            "tool_name": "append_to_file",
            "parameters": {"path": plan_file, "content": content}
        })


    def is_objective_complete(self, objective: str, history: list) -> bool:
        return len(self.history) >= 3

if __name__ == '__main__':
    agent = ManusInspiredAgent(dry_run=False)
    result = agent.run("Research the price of the new Acme gadget")
    print(f"\nAgent finished with result: {result}")
