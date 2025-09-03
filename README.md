# Manus-Inspired AI Agent

This project is a powerful, state-of-the-art AI agent for browser automation, inspired by the "Context Engineering" principles outlined by the Manus AI team. It uses a combination of a browser control server, a file system toolset, and a Large Language Model (LLM) to achieve complex objectives.

## Core Concepts

This agent is built on the following principles:

*   **Context Engineering:** We leverage the in-context learning abilities of frontier models rather than training custom models.
*   **File System as Memory:** The agent uses the local file system as a persistent, external memory to store plans, observations, and results.
*   **LLM-Powered Decision Making:** The agent uses an LLM to reason about its objective, plan its actions, and choose the correct tool for each step.
*   **Modularity:** The agent is designed to be modular, with separate components for browser control, file system operations, and agent logic.

## Project Structure

*   `manus_inspired_agent/`: The main Python package for the agent.
    *   `agent.py`: The core agent logic, including the main agent loop and the LLM integration.
    *   `filesystem_tools.py`: A collection of tools for interacting with the file system.
*   `node_modules/`: Contains the browser control server (`@rpx_/mcpx`).
*   `.gitignore`: Configured to ignore `node_modules` and other temporary files.

## Setup and Installation

To use this agent, you will need to set up the browser control server, the browser extension, and the agent itself.

### 1. Install the Browser Control Server

The browser control server is the `@rpx_/mcpx` npm package. It is already included in the `node_modules` directory. If you need to reinstall it, you can run the following command in the root of the project:

```bash
npm install @rpx_/mcpx
```

### 2. Install the Browser Extension

The `@rpx_/mcpx` server requires a companion browser extension to be installed in your Chrome browser.

**Instructions:**

1.  **Download the Extension:**
    *   Go to the GitHub repository for the extension: [https://github.com/Rudra78996/mcpX/tree/main/extension](https://github.com/Rudra78996/mcpX/tree/main/extension)
    *   Click the "Code" button and then "Download ZIP".
    *   Unzip the downloaded file on your computer.
2.  **Open Chrome Extensions:**
    *   Open a new tab in your Chrome browser and navigate to `chrome://extensions`.
3.  **Enable Developer Mode:**
    *   In the top-right corner of the Extensions page, turn on the "Developer mode" toggle switch.
4.  **Load the Extension:**
    *   Click the "Load unpacked" button that appears on the top-left.
    *   In the file dialog that opens, navigate to the folder you unzipped in step 1, and select the `extension` folder inside it.

The **mcpX Browser Extension** should now be installed and visible in your extensions list.

## How to Use

This agent is designed to be used with a compatible MCP client, such as the **Roo Code** VS Code extension.

### Configuring Roo Code

To configure Roo Code to use this agent, you will need to tell it how to start the `@rpx_/mcpx` server. You can do this by creating or modifying your Roo Code configuration file (usually found in the settings of the extension in VS Code).

You will need to add a server configuration that looks like this:

```json
{
  "mcpServers": {
    "manus_inspired_agent_browser": {
      "command": "npx",
      "args": ["@rpx_/mcpx@latest"],
      "env": {}
    }
  }
}
```

This tells Roo Code that it can start a server named `manus_inspired_agent_browser` by running the command `npx @rpx_/mcpx@latest`.

### Running the Agent

Once Roo Code is configured, you can start interacting with the agent. The core logic is in `manus_inspired_agent/agent.py`. You can run this script to have the agent attempt to achieve an objective.

The agent is designed to be controlled by another layer of code (like Roo Code), which would be responsible for:
1.  Providing the agent with an objective.
2.  Calling the agent's `run` method.
3.  Handling the results.

The current `agent.py` script has a `if __name__ == '__main__':` block that runs a simple example objective. You can modify this to test the agent with different objectives.
