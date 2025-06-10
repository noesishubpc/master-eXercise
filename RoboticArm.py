import streamlit as st
from huggingface_hub import InferenceClient
from huggingface_hub import HfApi
import os
from pydantic import BaseModel
import openai
import json
import requests
import datetime

st.set_page_config(layout="wide", page_title="Robotic Arm")


column1, column2, column3 = st.columns([1, 1, 1])

with column1:
    st.title("Robotic Arm Selector")
with column2:
    st.selectbox("Select the model to use:",
                ["Qwen/Qwen2.5-72B-Instruct", 
                "HuggingFaceH4/zephyr-7b-beta", 
                "mistralai/Mistral-7B-Instruct-v0.3",
                "gpt-4o",
                "gpt-4o-mini"], key="model_used")
with column3:
    st.number_input("Number of Robotic Arms", key="NOF_ROBOTIC_ARMS", value=5)

if "response_llm" not in st.session_state:
    st.session_state["response_llm"] = ""

if "stress_prediction" not in st.session_state:
    st.session_state["stress_prediction"] = ""

st.markdown("\n\n\n\n\n")


tab1, tab2 = st.tabs(["Robotic Arm Selector", "AI Advisor"])

with tab1:
    col1, col2, col3 = st.columns([1, 0.5, 0.5])

    with col1:
        initial_system_instructions = "You are an LLM Algorithm that will facilitate the implementation of a Language-to-XR Scene Component. With this advancement, workplace safety trainees can easily deploy XR training scenes for small-scale virtualfires and/or malfunctioning robotic arms by simply describing the scenario specifications in a prompt, which will be automatically transformed into a training scenario."

        st.session_state.llm_messages = []
        st.session_state.llm_messages.append({"role": "system", "content": initial_system_instructions})
        first_llm_message = "Please provide your inquiry in natural language and the distances of the robotic arms "
        first_llm_message += "in the rigth column, and I will provide you with the best recommendation."
        st.session_state.llm_messages.append({"role": "assistant", "content": first_llm_message})
        
        chat_display_screen = st.container(height=500)

        chat_display_screen.chat_message("ai", avatar=":material/precision_manufacturing:").markdown(st.session_state.llm_messages[-1]["content"])

        if user_prompt := st.chat_input("Enter your prompt here"):

            if len(user_prompt)<20:
                st.error("Please enter a prompt with more than 20 characters")
            
            else:
                chat_display_screen.chat_message("user", avatar=":material/engineering:").markdown(user_prompt)

                prompt_to_llm = f"The trainer said: {user_prompt}\n\n"
                prompt_to_llm += "The distances of the robotic arms are: " 
                prompt_to_llm += ", ".join([f"Robotic Arm Number {i+1}, Distance = {st.session_state[f'distance-{i}']}" for i in range(st.session_state['NOF_ROBOTIC_ARMS'])])
                prompt_to_llm += f". Use the information provided previously to suggest which robotic arm number "
                prompt_to_llm += f"({1} to {st.session_state['NOF_ROBOTIC_ARMS']}) aligns with that information based on the distances and the following trainer prompt. "
                prompt_to_llm += f"Also, identify any potentially malfunctioning arms according to the trainer prompt ({1} to {st.session_state['NOF_ROBOTIC_ARMS']}). "
                prompt_to_llm += f"If the trainer asks only for virtual fire, the return should be -1 for Robotic_Arm_Malfunctioning. " 
                prompt_to_llm += f"If the trainer asks only for malfunctioning, the return should be -1 for Robotic_Arm_Virtual_Fire. "
                prompt_to_llm += f"If the trainer asks for both, the return should be ({1} to {st.session_state['NOF_ROBOTIC_ARMS']}) for Robotic_Arm_Virtual_Fire "
                prompt_to_llm += f"and ({1} to {st.session_state['NOF_ROBOTIC_ARMS']}) for Robotic_Arm_Malfunctioning, based on the distances and the trainer prompt. "
                prompt_to_llm += f"Remember, the trainer said: {user_prompt}\n\n"
                

                class RoboticArmRecommendation(BaseModel):
                    Robotic_Arm_Virtual_Fire: int
                    Robotic_Arm_Malfunctioning: int
                    Reason_of_selection: str

                st.session_state.llm_messages.append({"role": "user", "content": prompt_to_llm})
                st.session_state["response_llm"] = ""

                if st.session_state["model_used"].startswith("gpt-"):
                    # OPENAI
                    st.session_state.client = openai.OpenAI()
                    client_response_llm = st.session_state.client.beta.chat.completions.parse(messages=st.session_state.llm_messages, 
                                                                                        model=st.session_state["model_used"], 
                                                                                        max_tokens=512, response_format=RoboticArmRecommendation)
                    st.session_state["response_llm"] = client_response_llm.choices[0].message.content
                else:
                    # TRANSFORMERS
                    # https://huggingface.co/learn/cookbook/en/structured_generation
                    
                    llm_client = InferenceClient(model=st.session_state["model_used"], token=os.getenv("HF_TOKEN"))
                    st.session_state["response_llm"] = llm_client.text_generation(
                                    prompt_to_llm,
                                    grammar={"type": "json", "value": RoboticArmRecommendation.model_json_schema()},
                                    max_new_tokens=250,
                                    temperature=1.6,###################################
                                    return_full_text=False,
                                )
                try:
                    response_llm_json = json.loads(st.session_state["response_llm"])
                    str_display = "Robotic Arm Virtual Fire: " + str(response_llm_json["Robotic_Arm_Virtual_Fire"])
                    str_display += "\n\nRobotic Arm Malfunctioning: " + str(response_llm_json["Robotic_Arm_Malfunctioning"])
                    str_display += "\n\nReason of selection: " + response_llm_json["Reason_of_selection"]
                except:
                    str_display = st.session_state["response_llm"]
                chat_display_screen.chat_message("ai", avatar=":material/precision_manufacturing:").markdown(str_display)
                st.session_state.llm_messages.append({"role": "assistant", "content": st.session_state["response_llm"]})
                with open("llm_messages.json", "w") as json_file:
                    json.dump(st.session_state["llm_messages"], json_file, indent=4)
                
                with open("response_llm_json.json", "w") as json_file:
                    json.dump(response_llm_json, json_file, indent=4)

                api = HfApi()
                with open("response_llm_json.json", "rb") as fobj:
                    api.upload_file(
                            path_or_fileobj=fobj,
                            path_in_repo="response_llm_json.json",
                            repo_id="domain/XYZ",
                            repo_type="dataset",
                            commit_message="Upload generated file",
                            token=os.getenv("HF_TOKEN")
                        )
        
        try:
            st.json(st.session_state["llm_messages"], expanded=False)
        except:
            st.write(st.session_state["llm_messages"])
        
        st.write("Sample prompts")
        st.json({
            "scenario_1": "There is a virtual fire close to the base. One of the robotic arms seems to be moving erratically at a far distance.",
            "scenario_2": "A virtual fire is detected at a far distance. One arm isn't responding as expected at a close distance.",
            "scenario_3": "Fire is burning in the middle zone. One robotic arm is showing abnormal distance values at a far distance.",
            "scenario_4": "There's a nearby virtual fire. One of the robotic arms failed to reach its target at a middle distance.",
            "scenario_5": "Virtual fire detected far away. An arm is jittering and behaving inconsistently at a close distance.",
            "scenario_6": "The fire is in the mid-range zone. One robotic arm stopped mid-operation unexpectedly at a far distance.",
            "scenario_7": "Virtual fire is close. A robotic arm is stuck at a fixed far distance.",
            "scenario_8": "Fire alert from a distant location. One of the robotic arms is moving slower than others at a close distance.",
            "scenario_9": "A middle-distance fire was triggered. One robotic arm reported sudden jumps in position at a far distance.",
            "scenario_10": "There's a fire nearby. One arm didn't react to the previous command at a middle distance."
        }, expanded=False)

    with col2:
        st.header("Distance Input", help="The trainee is the point of reference. Input the distance measurements for each robotic arm from the perspective of the trainee. This data is crucial for analyzing the performance and identifying any potential issues with the robotic arms during the session.")
        st.write("(zero distance is the point where the trainee is located - working)")

        import random
        if "initial_distances" not in st.session_state:
            st.session_state["initial_distances"] = [random.uniform(1, 10) for _ in range(100)]

                
        for i in range(st.session_state["NOF_ROBOTIC_ARMS"]):
            st.number_input(f"Enter distance of **robotic arm {i+1}**", 
                            value=st.session_state["initial_distances"][i], 
                            format="%.2f", step=0.01, key=f"distance-{i}")

    with col3:
        st.header("AI Recommendation")
        if st.session_state["response_llm"] != "":
            try:
                st.json(st.session_state["response_llm"])
            except:
                st.write(st.session_state["response_llm"])
        st.markdown("---")
        st.write("Selected AI Model:" + st.session_state["model_used"])
        st.markdown("*LLMs may generate inaccurate responses; please verify the responses and comply with the corresponding terms.*")



params = {
    "baseline_date": "2025-02-27",
    "baseline_start_time": "21:00",
    "baseline_end_time": "21:30",
    "classification_date": "2025-02-27",
    "classification_start_time": "12:00",
    "classification_end_time": "23:00"
}

classification_start = datetime.datetime.strptime(params["classification_start_time"], "%H:%M")
classification_end = datetime.datetime.strptime(params["classification_end_time"], "%H:%M")
classification_duration = (classification_end - classification_start).total_seconds() / 60

with tab2:
    tab2_col1, tab2_col2, tab2_col3 = st.columns([1, 1, 1])
    with tab2_col1:
        
        if st.button("Session Performance Report"):
            with st.spinner("Generating the report, please wait..."):
                messages_from_json = json.load(open("llm_messages.json"))
                instructions_to_generate_report = "Generate a report of the session Performance based on the following information: "
                instructions_to_generate_report += "The date of the session is: " + st.session_state["api_date"].strftime("%d/%m/%Y")
                instructions_to_generate_report += "The participant id is: " + st.session_state["api_participant_id"]
                instructions_to_generate_report += f"The Session duration is {classification_duration} minutes. "
                distances = [f"Robotic Arm Number {i+1}, Distance = {st.session_state['initial_distances'][i]}" for i in range(st.session_state['NOF_ROBOTIC_ARMS'])]
                instructions_to_generate_report += " The distances of the robotic arms are: " + ", ".join(distances) + "."
                instructions_to_generate_report += "The performance evaluation of the trainee is: " + str(st.session_state["stress_prediction"])
                instructions_to_generate_report += "The report should be in markdown format and analytical. "
                instructions_to_generate_report += "Should comprise all details of the session and the results and the recommendations and conclusions. "
                instructions_to_generate_report += "Make tables where appropriate. "
                instructions_to_generate_report += "Add info about Robotic_Arm_Virtual_Fire and Robotic_Arm_Malfunctioning. "
                instructions_to_generate_report += f"Start the markdown directly without any ```markdown.```"
                instructions_to_generate_report += f"Start by writing the # Session Performance Report title"
                messages_from_json.append({"role": "user", "content": instructions_to_generate_report})
                report_response = ""
                report_placeholder = st.empty()

                if st.session_state["model_used"].startswith("gpt-"):
                    st.session_state.client = openai.OpenAI()
                    for chunk in st.session_state.client.chat.completions.create(messages=messages_from_json,
                                                                                 model=st.session_state["model_used"], 
                                                                                 stream=True):
                        if hasattr(chunk.choices[0].delta, 'content'):
                            if chunk.choices[0].delta.content is not None:
                                chunk.choices[0].delta.content = chunk.choices[0].delta.content.replace("```markdown", "")
                                report_response += chunk.choices[0].delta.content
                                report_placeholder.markdown(report_response)
                else:
                    llm_client = InferenceClient(model=st.session_state["model_used"], token=os.getenv("HF_TOKEN"))
                    for chunk in llm_client.chat_completion(messages_from_json, stream=True):
                        if chunk.choices[0].delta.content:  
                            report_response += chunk.choices[0].delta.content.replace("```markdown", "")
                            report_placeholder.markdown(report_response)
                
                with open("session_stress_report.md", "w") as md_file:
                    md_file.write(report_response)

        

    with tab2_col2:
        if st.button("Get Session Stress Results"):
            if "response" not in st.session_state:
                with st.spinner("Reading the api of the session results, please wait..."):
                    url = "https://exrercise.8bellsresearch.com/classify_stress/"  # Replace with actual API URL
                    
                    headers = {
                        "Accept": "application/json"
                    }

                    st.session_state["response"] = requests.get(url, params=params, headers=headers)

                    with open("session_stress_results.json", "w") as json_file:
                        json.dump(st.session_state["response"].json(), json_file, indent=4)
            else:
                st.write("Session Stress Results already read")

            target_id = st.session_state["api_participant_id"]
            target_timestamp = f"{st.session_state['api_date'].strftime('%Y-%m-%d')}T{st.session_state['api_time'].strftime('%H:%M:%S')}+02:00"

            for entry in st.session_state["response"].json()["predictions"]:
                if entry["participant_full_id"] == target_id and entry["timestamp"] == target_timestamp:
                    st.write("Stress Prediction:", entry["stress_prediction"])
                    st.session_state["stress_prediction"] = entry["stress_prediction"]
                    break
            else:
                st.write("No match found.")

    with tab2_col3:
        
        st.text_input("Enter the participant id", key="api_participant_id", value="1704-1-1-1")
        st.date_input("Enter the date of the session (dd/mm/yyyy)", key="api_date", value=datetime.date(2025, 2, 27))
        st.time_input("Enter the time of the session (hh:mm)", key="api_time", 
                      value=datetime.time(16, 27, 0), step=datetime.timedelta(minutes=1))
        if os.path.exists("session_stress_results.json"):
            st.write("Session Stress API Results:")
            st.json(json.load(open("session_stress_results.json")), expanded=False)


