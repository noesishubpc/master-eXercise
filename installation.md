# Robotic Arm & AI Advisor Installation & Deployment Guide

This guide walks you through deploying the **Robotic Arm & AI Advisor** Streamlit app to a Hugging Face Space.

---

## 1. Prerequisites

Make sure you have:

- A [Hugging Face account](https://huggingface.co/join)
- `git` installed on your machine
- `Python >= 3.11` installed

---

## 2. Create a Hugging Face Space

1. Go to [Create a New Space](https://huggingface.co/new-space).
2. Fill in the following:
   - **SDK**: `Streamlit`
   - **Space Name**: e.g., `robotic-arm-selector`
   - **License**: Select one appropriate for your work
   - **Visibility**: Choose `Public` or `Private`
3. Click **Create Space**.

---

## 3. Create and Add Access Tokens

### A. Create Hugging Face Token (`HF_TOKEN`)

1. Visit [Hugging Face Tokens](https://huggingface.co/settings/tokens).
2. Click **New token**, name it `HF_TOKEN`, set permissions to **Write**.
3. Copy the generated token securely.

### B. Add Hugging Face Token to Space

1. Go to your Space → **Settings > Secrets**.
2. Add a new secret:
   - **Name**: `HF_TOKEN`
   - **Value**: your copied token

### C. (Optional) Add OpenAI Token

If you're using OpenAI models like `gpt-4o`, also add:

- **Name**: `OPENAI_API_KEY`
- **Value**: your OpenAI API key from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

---

## 4. Prepare and Upload Your Files

You need these 3 files in your Space repository:

### `RoboticArm.py`

Your main Streamlit app. [See source content](#RoboticArm.py)

---

### `requirements.txt`

Dependencies to install:

```
streamlit
huggingface_hub==0.31.4
sentence-transformers
openai
pydantic
```

---

### `README.md`

Configuration file for your Hugging Face Space:

```
title: RoboticArm
sdk: streamlit
emoji: 🌖
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

---

## 6. Final Steps

Once uploaded, your Space will automatically build and deploy.

You can:

- View your app live from the Space page.
- Share the URL with others.
- Embed it in other websites or documentation.

---

## Troubleshooting Tips

- **App stuck on “Building…”**: Check the `requirements.txt` and Space logs.
- **`HF_TOKEN` or OpenAI issues**: Double-check secret names and values.
- **Incompatible Python version**: Ensure `python_version: '3.11'` is set in your `README.md`.

---

## Reference

- [Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Streamlit SDK Docs](https://huggingface.co/docs/hub/spaces-sdks-streamlit)

---