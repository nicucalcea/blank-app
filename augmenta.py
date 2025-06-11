import streamlit as st
import yaml
import os
import json
from copy import deepcopy

# Function to load settings from YAML file
def load_settings():
    yaml_path = "augmenta.yaml"
    default_settings = {
        "input_csv": "data/input.csv",
        "output_csv": "data/output.csv",
        "model": {
            "provider": "openai",
            "name": "gpt-4o-mini"
        },
        "search": {
            "engine": "google",
            "results": 10
        },
        "prompt": {
            "system": "You are an expert researcher.",
            "user": "# Instructions\n\nResearch the following entity..."
        },
        "structure": {
            "industry": {
                "type": "str",
                "description": "What industry is this organisation or person associated with?",
                "options": ["Agriculture, Forestry and Fishing", "Manufacturing", "Other"]
            },
            "explanation": {
                "type": "str",
                "description": "A brief explanation"
            }
        },
        "examples": [],
        "logfire": False
    }
    
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, 'r') as file:
                loaded_settings = yaml.safe_load(file)
                if loaded_settings:
                    return loaded_settings
                return default_settings
        except Exception as e:
            st.warning(f"Error loading settings: {e}")
            return default_settings
    else:
        # Create default settings file if it doesn't exist
        try:
            with open(yaml_path, 'w') as file:
                yaml.dump(default_settings, file, sort_keys=False)
            return default_settings
        except Exception as e:
            st.warning(f"Error creating default settings file: {e}")
            return default_settings

# Enhanced function to save settings to YAML file with debug information
def save_settings(settings):
    yaml_path = "augmenta.yaml"
    try:
        # Print debug info
        st.write(f"Attempting to save to {os.path.abspath(yaml_path)}")
        
        # Make sure settings is not None
        if settings is None:
            st.error("Cannot save None settings")
            return False
        
        # Write to file
        with open(yaml_path, 'w') as file:
            yaml.dump(settings, file, sort_keys=False)
            
        # Verify file was written
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as file:
                content = file.read()
                if content:
                    st.success(f"Settings saved successfully! File size: {len(content)} bytes")
                    return True
                else:
                    st.error("File was created but is empty")
                    return False
        else:
            st.error("File was not created")
            return False
    except Exception as e:
        st.error(f"Error saving settings: {str(e)}")
        return False

# Load saved settings at startup
if 'settings_loaded' not in st.session_state:
    st.session_state.settings = load_settings()
    st.session_state.settings_loaded = True

# Utility function to update and immediately save settings
def update_and_save(key, value):
    keys = key.split('.')
    current = st.session_state.settings
    
    # Navigate to the right depth
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Update the value
    current[keys[-1]] = value
    
    # Save immediately
    save_result = save_settings(st.session_state.settings)
    return save_result

st.title('Augmenta')

# Debug information
with st.expander("Debug Information"):
    st.write("Current Working Directory:", os.getcwd())
    st.write("YAML File Path:", os.path.abspath("augmenta.yaml"))
    st.write("File exists:", os.path.exists("augmenta.yaml"))
    st.write("Current Settings:", st.session_state.settings)
    
    if st.button("Force Reload Settings"):
        st.session_state.settings = load_settings()
        st.experimental_rerun()

with st.expander("Basic Configuration", expanded=True):
    st.subheader('Files')
    
    col1, col2 = st.columns(2)
    
    with col1:
        input_csv = st.text_input("Input CSV path", st.session_state.settings.get("input_csv", ""))
        uploaded_file = st.file_uploader("Or upload a file", type=["csv"])
    
    with col2:
        output_csv = st.text_input("Output CSV path", st.session_state.settings.get("output_csv", ""))
    
    if st.button("Save File Paths"):
        st.session_state.settings["input_csv"] = input_csv
        st.session_state.settings["output_csv"] = output_csv
        save_settings(st.session_state.settings)
    
    st.subheader('Model Configuration')
    
    col1, col2 = st.columns(2)
    
    model_settings = st.session_state.settings.get("model", {})
    
    with col1:
        model_provider = st.selectbox(
            "Select Model Provider",
            ["openai", "google", "azure", "anthropic"],
            index=["openai", "google", "azure", "anthropic"].index(model_settings.get("provider", "openai"))
        )
    
    with col2:
        model_name = st.text_input("Model Name", model_settings.get("name", ""))
    
    if st.button("Save Model Settings"):
        if "model" not in st.session_state.settings:
            st.session_state.settings["model"] = {}
        st.session_state.settings["model"]["provider"] = model_provider
        st.session_state.settings["model"]["name"] = model_name
        save_settings(st.session_state.settings)
    
    st.subheader('Search Configuration')
    
    col1, col2 = st.columns(2)
    
    search_settings = st.session_state.settings.get("search", {})
    
    with col1:
        search_engine = st.selectbox(
            "Select Search Engine",
            ["google", "bing", "duckduckgo", "brave"],
            index=["google", "bing", "duckduckgo", "brave"].index(search_settings.get("engine", "google"))
        )
    
    with col2:
        search_results = st.number_input("Number of search results", 
                                          min_value=1, 
                                          max_value=100, 
                                          value=int(search_settings.get("results", 10)))
    
    if st.button("Save Search Settings"):
        if "search" not in st.session_state.settings:
            st.session_state.settings["search"] = {}
        st.session_state.settings["search"]["engine"] = search_engine
        st.session_state.settings["search"]["results"] = int(search_results)
        save_settings(st.session_state.settings)
    
    st.subheader('Prompt Configuration')
    
    prompt_settings = st.session_state.settings.get("prompt", {})
    
    # Fix for handling prompt as string or dict
    if isinstance(prompt_settings, str):
        # If prompt is a string, convert it to dict format
        system_prompt = ""
        user_prompt = prompt_settings
    else:
        system_prompt = prompt_settings.get("system", "")
        user_prompt = prompt_settings.get("user", "")
    
    system_prompt = st.text_area(
        "System Prompt",
        system_prompt
    )
    
    user_prompt = st.text_area(
        "User Prompt",
        user_prompt,
        height=300
    )
    
    logfire = st.checkbox("Enable LogFire", st.session_state.settings.get("logfire", False))
    
    if st.button("Save Prompt Settings"):
        if "prompt" not in st.session_state.settings or isinstance(st.session_state.settings["prompt"], str):
            st.session_state.settings["prompt"] = {}
        st.session_state.settings["prompt"]["system"] = system_prompt
        st.session_state.settings["prompt"]["user"] = user_prompt
        st.session_state.settings["logfire"] = logfire
        save_settings(st.session_state.settings)

with st.expander("Output Structure"):
    st.header('Output Structure')
    
    structure = saved_settings.get("structure", {})
    
    # Display existing fields
    st.subheader("Current Fields")
    
    for field_name, field_config in structure.items():
        with st.expander(f"{field_name}: {field_config.get('type', 'str')}"):
            st.text_input(f"Field Type", field_config.get("type", "str"), key=f"type_{field_name}", disabled=True)
            field_desc = st.text_area(f"Description", field_config.get("description", ""), key=f"desc_{field_name}")
            field_config["description"] = field_desc
            
            if "options" in field_config:
                options_str = "\n".join(field_config["options"])
                new_options = st.text_area(f"Options (one per line)", options_str, key=f"options_{field_name}")
                field_config["options"] = [opt for opt in new_options.split("\n") if opt.strip()]
    
    # Add new field UI
    st.subheader("Add New Field")
    col1, col2 = st.columns(2)
    
    with col1:
        new_field_name = st.text_input("Field Name")
    
    with col2:
        new_field_type = st.selectbox("Field Type", ["str", "int", "float", "bool", "list"])
    
    new_field_desc = st.text_area("Field Description")
    
    has_options = st.checkbox("Add Options")
    new_field_options = []
    
    if has_options:
        new_options_str = st.text_area("Options (one per line)")
        new_field_options = [opt for opt in new_options_str.split("\n") if opt.strip()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Add Field") and new_field_name:
            if "structure" not in saved_settings:
                saved_settings["structure"] = {}
                
            saved_settings["structure"][new_field_name] = {
                "type": new_field_type,
                "description": new_field_desc
            }
            
            if new_field_options:
                saved_settings["structure"][new_field_name]["options"] = new_field_options
                
            if save_settings(saved_settings):
                st.success(f"Field '{new_field_name}' added successfully!")
                st.experimental_rerun()
    
    with col2:
        # Save structure changes
        if st.button("Save Structure Changes"):
            if save_settings(saved_settings):
                st.success("Structure updated successfully!")

with st.expander("Examples"):
    st.header('Examples')
    
    examples = saved_settings.get("examples", [])
    
    for i, example in enumerate(examples):
        with st.expander(f"Example {i+1}: {example.get('input', 'Unnamed')}"):
            input_val = st.text_input("Input", example.get("input", ""), key=f"ex_input_{i}")
            output = example.get("output", {})
            example["input"] = input_val
            
            st.subheader("Output")
            
            for field_name, field_value in output.items():
                if isinstance(field_value, str):
                    new_value = st.text_area(f"{field_name}", field_value, key=f"ex_{i}_{field_name}")
                    output[field_name] = new_value
                elif isinstance(field_value, (int, float)):
                    new_value = st.number_input(f"{field_name}", value=float(field_value), key=f"ex_{i}_{field_name}")
                    output[field_name] = new_value
            
            if st.button(f"Delete Example #{i+1}", key=f"del_example_{i}"):
                examples.pop(i)
                if save_settings(saved_settings):
                    st.success(f"Example #{i+1} deleted!")
                    st.experimental_rerun()
    
    # Save examples changes
    if examples and st.button("Save Example Changes"):
        if save_settings(saved_settings):
            st.success("Example changes saved successfully!")
    
    # Add new example
    st.subheader("Add New Example")
    
    new_input = st.text_input("Input")
    
    if "structure" in saved_settings:
        structure = saved_settings["structure"]
        new_output = {}
        
        for field_name, field_config in structure.items():
            field_type = field_config.get("type", "str")
            
            if field_type == "str":
                if "options" in field_config:
                    new_output[field_name] = st.selectbox(
                        field_name, 
                        field_config["options"],
                        key=f"new_example_{field_name}"
                    )
                else:
                    new_output[field_name] = st.text_area(
                        field_name,
                        "",
                        key=f"new_example_{field_name}"
                    )
            elif field_type in ["int", "float"]:
                new_output[field_name] = st.number_input(
                    field_name,
                    key=f"new_example_{field_name}"
                )
            elif field_type == "bool":
                new_output[field_name] = st.checkbox(
                    field_name,
                    key=f"new_example_{field_name}"
                )
        
        if st.button("Add Example") and new_input:
            if "examples" not in saved_settings:
                saved_settings["examples"] = []
                
            saved_settings["examples"].append({
                "input": new_input,
                "output": new_output
            })
            
            if save_settings(saved_settings):
                st.success("Example added successfully!")
                st.experimental_rerun()
    else:
        st.info("Define structure fields first before adding examples.")

with st.expander("Advanced Configuration"):
    st.header('Advanced Configuration')
    
    # Raw YAML editor
    raw_yaml = st.text_area("Edit Raw YAML", yaml.dump(saved_settings), height=500)
    
    if st.button("Save Raw YAML"):
        try:
            parsed_yaml = yaml.safe_load(raw_yaml)
            if save_settings(parsed_yaml):
                st.success("YAML configuration saved successfully!")
        except Exception as e:
            st.error(f"Error parsing YAML: {e}")
    
    # Export/Import
    st.subheader("Export/Import Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.download_button(
            "Download Configuration", 
            yaml.dump(saved_settings), 
            file_name="augmenta_config.yaml"
        ):
            st.info("Configuration downloaded")
    
    with col2:
        uploaded_config = st.file_uploader("Upload Configuration", type=["yaml", "yml"])
        
        if uploaded_config is not None and st.button("Import Configuration"):
            try:
                imported_settings = yaml.safe_load(uploaded_config)
                if save_settings(imported_settings):
                    st.success("Configuration imported successfully!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Error importing configuration: {e}")

# Global Save Button
st.header("Save All Changes")
if st.button("Save All Configuration", type="primary"):
    # Update all settings
    st.session_state.settings["input_csv"] = input_csv
    st.session_state.settings["output_csv"] = output_csv
    
    if "model" not in st.session_state.settings:
        st.session_state.settings["model"] = {}
    st.session_state.settings["model"]["provider"] = model_provider
    st.session_state.settings["model"]["name"] = model_name
    
    if "search" not in st.session_state.settings:
        st.session_state.settings["search"] = {}
    st.session_state.settings["search"]["engine"] = search_engine
    st.session_state.settings["search"]["results"] = int(search_results)
    
    if "prompt" not in st.session_state.settings or isinstance(st.session_state.settings["prompt"], str):
        st.session_state.settings["prompt"] = {}
    st.session_state.settings["prompt"]["system"] = system_prompt
    st.session_state.settings["prompt"]["user"] = user_prompt
    
    st.session_state.settings["logfire"] = logfire
    
    # Save to file
    if save_settings(st.session_state.settings):
        st.balloons()
        st.success("All settings saved successfully!")

# Run button for the entire configuration
st.header("Run Augmenta")
if st.button("Run", type="primary"):
    # Make sure to save before running
    update_result = save_settings(st.session_state.settings)
    if update_result:
        st.info("Starting process with current configuration...")
    else:
        st.error("Failed to save settings before running")
    # This would be where your process execution code goes