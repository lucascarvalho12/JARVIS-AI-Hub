# JARVIS AI Hub

A personalized AI hub system designed to connect your phone, car, and house into an integrated network for a JARVIS-like AI assistant/companion.

## Table of Contents

- [Project Overview](#project-overview)
- [System Components](#system-components)
- [Deployment Instructions](#deployment-instructions)
  - [Backend API (Flask)](#backend-api-flask)
  - [Web Dashboard (React)](#web-dashboard-react)
- [Usage](#usage)
- [Features](#features)
- [Future Enhancements (Requires Upgrade)](#future-enhancements-requires-upgrade)

## Project Overview

The JARVIS AI Hub aims to create a seamless, intelligent ecosystem that learns, adapts, and anticipates your needs across your personal devices and home environment. It acts as a centralized command center, orchestrating various aspects of your digital life through a robust backend and an intuitive web-based dashboard.

## System Components

### 1. Backend API System (`ai_hub_backend/`)

-   **Framework:** Flask
-   **Purpose:** Handles device communication, AI processing, data management, and integration logic.
-   **Key Modules:**
    -   User profiles, device registry, conversation history, task execution.
    -   Integration modules for smartphones, cars, and smart home devices.
    -   AI learning system for pattern recognition and adaptive responses.

### 2. Web Dashboard Interface (`ai-hub-dashboard/`)

-   **Framework:** React
-   **Purpose:** Provides a modern, intuitive web interface for monitoring and controlling all connected devices, interacting with the AI assistant, and visualizing system status.
-   **Key Features:**
    -   JARVIS-inspired design with a dark theme.
    -   Real-time device control (lights, thermostat, security, etc.).
    -   Multi-tab interface for Home, Car, and Phone management.
    -   AI chat interface with voice command support.
    -   System monitoring (device status, energy tracking).

## Deployment Instructions

To get your JARVIS AI Hub up and running, follow these steps:

### Backend API (Flask)

1.  **Navigate to the backend directory:**
    ```bash
    cd JARVIS-AI-Hub/ai_hub_backend
    ```

2.  **Activate the Python virtual environment:**
    ```bash
    source venv/bin/activate
    ```
    *If `venv` does not exist, you might need to create it and install dependencies. First, ensure `pip` is installed, then run:*
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Start the Flask development server:**
    ```bash
    python src/main.py
    ```
    *The backend will typically run on `http://127.0.0.1:5000` or `http://localhost:5000`. Keep this terminal open.*

### Web Dashboard (React)

1.  **Open a new terminal and navigate to the frontend directory:**
    ```bash
    cd JARVIS-AI-Hub/ai-hub-dashboard
    ```

2.  **Install Node.js dependencies (if not already done):**
    ```bash
    pnpm install
    ```
    *If `pnpm` is not installed, you can install it via `npm install -g pnpm`.*

3.  **Start the React development server:**
    ```bash
    pnpm run dev --host
    ```
    *The frontend will typically run on `http://127.0.0.1:5173` or `http://localhost:5173`. Keep this terminal open.*

## Usage

Once both the backend and frontend servers are running:

1.  **Open your web browser** and navigate to the address provided by the React development server (e.g., `http://localhost:5173/`).
2.  You will see the **JARVIS AI Hub Dashboard** interface.
3.  You can interact with the AI assistant via the chat interface and observe the simulated device controls.
4.  To register actual devices and leverage the AI learning capabilities, you would interact with the backend API directly (e.g., using `curl` or a custom client application).

## Features

-   **Device Integration**: Seamless control and monitoring of smartphones, cars, and smart home devices.
-   **Voice Commands**: Natural language processing for intuitive interaction.
-   **AI Learning System**: Analyzes user patterns, predicts intentions, and adapts responses for a personalized experience.
-   **Automation**: Supports smart routines and proactive suggestions based on learned behavior.
-   **Security**: Designed with encrypted communications and local data processing for privacy.
-   **Scalability**: Modular architecture allows for easy expansion and integration of new devices and services.
-   **Real-time Monitoring**: Live status updates for all connected devices and system health.
-   **Mobile-Friendly**: Responsive web interface accessible from any device.

## Future Enhancements (Requires Upgrade)

To unlock advanced capabilities such as the AI autonomously creating and programming its own applications and functions based on user input, an upgrade to the Wide Research feature is required. This feature provides advanced capabilities for code generation, autonomous development, and integration with external programming environments.


