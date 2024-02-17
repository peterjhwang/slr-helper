# SLR Helper

This system is designed to help with the creation of SLR fine-tuning training dataset and test dataset. 

## Features
Currently, the system only supports a PDF file format. 


## Installing
This project is tested in Python 3.10. To install the required packages, run the following command:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After that, you need to create a .env file in the root of the project with the following content:

```bash
OPENAI_API_KEY=your_api_key
```

## Running
To run the system, you need to execute the following command:

```bash
source venv/bin/activate # If you haven't activated the virtual environment
python app.py
```

After that, you can access the system through the following URL: http://127.0.0.1:7860/

## Built With
* Python - The programming language used
* Gradio - The web framework used
