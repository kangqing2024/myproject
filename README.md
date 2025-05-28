![Logo](images/bpmn_assistant_logo.png)
参考原链接：https://github.com/jtlicardo/bpmn-assistant
在原项目基础上，加了用户信息，历史对话记录保存
BPMN Assistant is an application that uses Large Language Models (LLMs) to assist with creating, editing, and
interpreting Business Process Model and Notation (BPMN) diagrams.

## Quickstart

docker pull python:3.12-slim
docker pull node:20
docker pull nginx:stable-alpine

1. Clone the repository

```
git clone https://github.com/kangqing2024/myproject.git
```

```
cd myproject
```

2. Set up your environment variables

<details>
<summary>Linux, macOS</summary>

```
cd src/bpmn_assistant
```

```
cp .env.example .env
```

</details>

<details>
<summary>Windows</summary>

```
cd src\bpmn_assistant
```

```
copy .env.example .env
```

</details>

3. Open the `.env` file and replace the placeholder values with your actual API keys.

4. Build and run the application

```
docker-compose up --build
```

5. Open your browser and go to `http://localhost:8080`

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- At least one of the following API keys:
    - [OpenAI API key](https://platform.openai.com/docs/quickstart)
    - [Anthropic API key](https://console.anthropic.com/)
    - [Google AI Studio (Gemini) API key](https://aistudio.google.com/app/apikey)
    - [Fireworks AI API key](https://docs.fireworks.ai/getting-started/quickstart)

Note: You can use any combination of the API keys above, but at least one is required to use the app.

## Supported models

### OpenAI

* GPT-4o mini
* GPT-4o
* o3-mini


### Anthropic

* Claude 3.5 Haiku
* Claude 3.7 Sonnet

### Google

* Gemini 2.0 Flash
* Gemini 2.0 Pro

### Fireworks AI

* Llama 3.3 70B Instruct
* Qwen 2.5 72B Instruct
* Deepseek V3
* Deepseek R1

## Screenshots

![Screenshot](images/screenshot_1.png)

![Screenshot](images/screenshot_2.png)

## Core features

1. Diagram creation - Generates BPMN diagrams based on text descriptions.
2. Diagram editing - Modifies BPMN diagrams based on user input.
3. Diagram interpretation - Provides text descriptions of BPMN diagrams.
4. Drag-and-drop functionality - Users can drag and drop BPMN files (containing only supported elements) into the
   editor, then ask the LLM to edit or explain the process.

## Supported elements

The application currently supports a subset of BPMN elements:

* Task
* User task
* Service task
* Exclusive gateway
* Parallel gateway
* Start event
* End event

## Limitations

* The AI assistant does not "see" manual edits made to the diagram. It always responds based on its last generated
  version. Keep this in mind when interacting with the assistant after making manual changes.
* Pools and lanes are not and will not be supported.

## Contact

If you have any questions or feedback, please open an issue on this GitHub repository.
