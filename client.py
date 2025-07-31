from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import traceback
import json
from google import genai
from ast import literal_eval
from concurrent.futures import TimeoutError
import sys
import config
from prompt import prefix_prompt, main_prompt

import logging
logging.basicConfig(
    filename="logs.log",
    format='%(asctime)s - %(process)d - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON schema for agent llm response
class Response(BaseModel):
  function_name: str
  params: list[str]
  final_ans: str
  reasoning_type: str

client = genai.Client(api_key=config.GEMINI_API_KEY)

max_iterations = 25
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    # model="gemini-1.5-flash",
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': Response,
                    },
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main(query):
    reset_state() 
    print("Starting main execution...")
    try:
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()
                
                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools")

                # Create system prompt with available tools
                print("Creating system prompt...")
                print(f"Number of tools: {len(tools)}")
                
                try:                    
                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            
                            if 'properties' in params:
                                param_details = []
                                for param_name, param_info in params['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            print(f"Added description for tool: {tool_desc}")
                        except Exception as e:
                            print(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                    
                    tools_description = "\n".join(tools_description)
                    print("Successfully created tools description")
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"
                print("Created system prompt...")
                
                support_prompt = f"{prefix_prompt}: {tools_description}"
                system_prompt = main_prompt

                # query = """I am looking for stable matching Gale Shapley algorithm. In which lecture was it taught?"""
                print("Starting iteration loop...")
                
                global iteration, last_response
                while iteration < max_iterations:
                    print(f"\n------------------------------------- Iteration {iteration + 1} -----------------------------------------------------")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    prompt = f"{support_prompt} {system_prompt}\n\nQuery: {current_query}"
                    print(f"Prompt being passed to LLM: {prompt}")
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()                        
                        response_text = literal_eval(json.loads(json.dumps(response_text))) # validation part
                        if not Response(**response_text):
                            iteration_response.append(
                                f"In the {iteration + 1} llm generated reponse which is not as per valid schema. LLM response: {response_text}. Valid expected schema: {Response}"
                            )
                            continue
                        else:
                            print(f"Successfull LLM Response: {response_text}") 
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        iteration_response.append(
                                f"In the {iteration + 1} llm generated reponse which throwed exception as: {str(e)}. LLM response: {response_text}. Valid expected schema: {Response}"
                            )
                        continue
                    
                    func_name = response_text.get("function_name", None)
                    if func_name != 'None':
                        params = response_text.get("params", [])
                        print(f"DEBUG: Raw parameters: {params}")
                        
                        try:
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                print(f"DEBUG: Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")

                            print(f"DEBUG: Found tool: {tool.name}")
                            print(f"DEBUG: Tool schema: {tool.inputSchema}")

                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            print(f"DEBUG: Schema properties: {schema_properties}")

                            for param_name, param_info in schema_properties.items():
                                if not params:  # Check if we have enough parameters
                                    raise ValueError(f"Not enough parameters provided for {func_name}")
                                    
                                value = params.pop(0)  # Get and remove the first parameter
                                param_type = param_info.get('type', 'string')
                                
                                print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
                                
                                # Convert the value to the correct type based on the schema
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    # Handle array input
                                    if isinstance(value, str):
                                        value = value.strip('[]').split(',')
                                    arguments[param_name] = [int(x.strip()) for x in value]
                                else:
                                    arguments[param_name] = str(value)

                            print(f"DEBUG: Final arguments: {arguments}")
                            print(f"DEBUG: Calling tool {func_name}")
                            
                            result = await session.call_tool(func_name, arguments=arguments)
                            print(f"DEBUG: Raw result: {result}")
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                print(f"DEBUG: Result has content attribute")
                                # Handle multiple content items
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                print(f"DEBUG: Result has no content attribute")
                                iteration_result = str(result)
                                
                            print(f"DEBUG: Final iteration result: {iteration_result}")
                            
                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)
                            
                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                f"and the function returned {result_str}."
                            )
                            last_response = iteration_result

                            if func_name == "view_pdf":
                                print("=================================================================================================")
                                print(f"Search Successfull. Result found in PDF: {arguments["pdf_file_path"]}, at page number: {arguments["page_number"]}")
                                print("=============================== AGENT EXECUTION COMPLETE ========================================")
                                break
                        except Exception as e:
                            print(f"DEBUG: Error details: {str(e)}")
                            print(f"DEBUG: Error type: {type(e)}")
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break                        
                    else:
                        print(f"Uncertain response from llm, needs reprocessing or next tools need to be called.")
                        iteration_response.append(
                                f"In the {iteration + 1} iteration you returned response: {response_text}. Please re-assess and respond again or guide with next steps."
                            )
                        last_response = iteration_result
                    iteration += 1

    except Exception as e:
        print(f"Error in main execution: {e}")
        traceback.print_exc()
    finally:
        reset_state()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py \"<your query here>\"")
        sys.exit(1)

    query_input = sys.argv[1]
    asyncio.run(main(query_input))