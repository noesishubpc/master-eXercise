# Robotic Arm & AI Advisor Installation & Deployment Guide

This guide walks you through deploying the **Robotic Arm & AI Advisor** Streamlit app to a Hugging Face Space and configuring a Hugging Face dataset `XYZ` for storing LLM result JSON files.

---

## 1. Prerequisites

Make sure you have:

- A [Hugging Face account](https://huggingface.co/join)
- `git` installed on your machine
- `Python >= 3.11` installed
- A valid Hugging Face token (`HF_TOKEN`) with write permissions
- (Optional) An OpenAI API key (`OPENAI_API_KEY`) if using OpenAI models

---

## 2. Create a Hugging Face Space

1. Go to [Create a New Space](https://huggingface.co/new-space).
2. Fill in:
      - **SDK**: `Streamlit`
      - **Space Name**: e.g., `robotic-arm-selector`
      - **License**: Select one appropriate
      - **Visibility**: `Public` or `Private`
3. Click **Create Space**.

---

## 3. Create and Add Access Tokens

### A. Create Hugging Face Token (`HF_TOKEN`)

1. Visit [Hugging Face Tokens](https://huggingface.co/settings/tokens).
2. Click **New token**, name it `HF_TOKEN`, set permissions to **Write**.
3. Copy the generated token securely.

### B. Add Hugging Face Token to Space

1. In your Space, go to **Settings > Secrets**.
2. Add a new secret:
   - **Name**: `HF_TOKEN`
   - **Value**: your copied token

### C. (Optional) Add OpenAI Token

If using OpenAI models (`gpt-4o`, etc.), add:

- **Name**: `OPENAI_API_KEY`
- **Value**: your OpenAI API key

---

## 4. Prepare and Upload Your Files

You need these files in your Space repository:

### `RoboticArm.py`

Your main Streamlit app. Ensure it includes code for uploading LLM result JSON to a Hugging Face dataset (see Section 7). [See source content](https://github.com/noesishubpc/master-eXercise/blob/main/RoboticArm.py)

### `requirements.txt`

List dependencies:
```
streamlit
huggingface_hub>=0.31.4
sentence-transformers
openai
pydantic
requests
```

### `README.md`

Configure your Space:
```yaml
title: RoboticArm
sdk: streamlit
emoji: (see file to render)
colorFrom: pink
colorTo: indigo
sdk_version: 1.44.1
app_file: RoboticArm.py
pinned: false
python_version: '3.11'
```

---

## 5. Upload and Deploy

### Option A: Upload through Web UI

1. In your Space, go to **Files and versions**.
2. Click **Add file > Upload files**.
3. Upload `RoboticArm.py`, `README.md`, and `requirements.txt`.

### Option B: Upload via Git

```bash
# Clone your space
git clone https://huggingface.co/spaces/<your-username>/robotic-arm-selector
cd robotic-arm-selector

# Add your files
cp /path/to/RoboticArm.py .
cp /path/to/README.md .
cp /path/to/requirements.txt .

# Commit and push
git add .
git commit -m "Add initial app files"
git push
```

Once uploaded, the Space will build and deploy automatically. View and test your app via the Space URL.

---

## 6. Create and Configure the Hugging Face Dataset `XYZ`

To store LLM result JSON files from the app, create a HF dataset repository. Name of the dataset can be anything! As long as you replace XYZ with your name of the dataset.

### A. Create the dataset repository

You can do this locally or via the website.

1. **Via CLI (locally)**:
   ```bash
   huggingface-cli login
   huggingface-cli repo create XYZ --type dataset
   ```
   Replace `XYZ` with your chosen name. Choose `public` or `private` as needed.

2. **Via Web UI**:
      - Go to [New dataset](https://huggingface.co/new-dataset).
      - Name it `XYZ`, set visibility.

3. **Record the full repo ID**: e.g. `your-username/XYZ`. This will be used in code.

### B. Add HF token for dataset access

- In your local environment (if testing outside Spaces), set:
  ```bash
  export HF_TOKEN="<your_hf_token>"
  ```
- In the Space, you already added `HF_TOKEN` as a secret (Section 3).

---

## 7. Integrate Dataset Upload in `RoboticArm.py`

Modify your Streamlit app to upload LLM results (`response_llm_json.json`) to the `XYZ` dataset.

In order to divert to your dataset, locate the following code snippet and edit it appropriately to match your own Hugging Face dataset.

```python
api = HfApi()
with open("response_llm_json.json", "rb") as fobj:
   api.upload_file(
         path_or_fileobj=fobj,
         path_in_repo="response_llm_json.json",
         repo_id="your-username/XYZ",
         repo_type="dataset",
         commit_message="Upload generated file",
         token=os.getenv("HF_TOKEN")
   )
```

**Replace** `repo_id` with your dataset ID/ dataset name.

---

## 8. Testing the Upload Flow

1. Deploy or run the app in your Space.
2. In the UI, enter a valid prompt to trigger LLM call and JSON creation.
3. Observe the Streamlit UI for success message.
4. Visit your Hugging Face dataset page: https://huggingface.co/datasets/your-username/XYZ to see uploaded JSON files.

---

## 9. Appendix: Example Workflow Summary

1. **Create Space** and add secrets (`HF_TOKEN`, optionally `OPENAI_API_KEY`).
2. **Create HF dataset** named `XYZ`, note `your-username/XYZ`.
3. **Prepare files** (`RoboticArm.py`, `requirements.txt`, `README.md`) with upload logic.
4. **Upload files** to Space via UI or Git, then deploy.
5. **Test** the app: trigger LLM, observe upload success in UI.
6. **Verify** dataset contents on HF Hub.

