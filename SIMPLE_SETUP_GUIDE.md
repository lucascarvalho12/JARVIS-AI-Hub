# JARVIS AI Hub: Easy Setup Guide for Young Builders! 🚀

Hey there, future AI genius! 👋 Are you ready to build your very own JARVIS AI Hub, just like Tony Stark? It might sound super complicated, but don't worry! This guide will help you get your AI up and running with easy steps. Think of it like building with LEGOs, but for computers!

## What is JARVIS AI Hub? 🤔

Imagine having a super-smart computer friend that can talk to your phone, your car, and even your house! That's what JARVIS AI Hub is. It's like a brain for all your gadgets, helping them work together. And the coolest part? This JARVIS can even learn to make itself better and smarter all by itself! It's like it can teach itself new tricks!

## What You'll Need (Your Tools! 🛠️)

Before we start building, you'll need a few things on your computer. Don't worry if you don't have them, we'll show you how to get them!

1.  **A Computer**: Any computer (like a laptop or desktop) will work.
2.  **Internet Access**: To download the special tools we need.
3.  **Python**: This is a special language your computer understands. It's like the language JARVIS speaks. We need version 3.11 or newer. (Don't worry, we'll check this!)
4.  **Node.js**: This helps us build the cool screen (dashboard) for JARVIS. We need version 18 or newer.
5.  **Git**: This is like a magic notebook that remembers all the changes we make to our JARVIS code. It helps us get the JARVIS code from the internet.
6.  **An OpenAI Key**: This is like a secret password that lets your JARVIS talk to a super-smart AI brain on the internet. It helps JARVIS understand and answer your questions. You'll need to ask an adult to help you get this, as it usually costs a little bit of money.

Let's check if you have Python and Node.js already!

### Checking for Python 🐍

Open your computer's 


terminal (it's like a special window where you type commands). On Windows, you can search for "Command Prompt" or "PowerShell". On Mac or Linux, search for "Terminal".

Type this command and press Enter:

```bash
python3 --version
```

If you see something like `Python 3.11.0` or `Python 3.12.1`, great! You have Python. If it says `Python 3.10.x` or older, or if it says "command not found", you might need to ask an adult to help you install a newer version of Python. You can usually download it from the official Python website.

### Checking for Node.js 🌐

In the same terminal window, type this command and press Enter:

```bash
node --version
```

If you see something like `v18.12.0` or `v20.0.0`, awesome! You have Node.js. If it says an older version or "command not found", ask an adult to help you install a newer version from the official Node.js website.

### Checking for Git 📚

Again, in the terminal, type this command and press Enter:

```bash
git --version
```

If you see a version number like `git version 2.34.1`, you're good! If not, ask an adult to help you install Git. It's usually a quick install.

## Step 1: Get the JARVIS Code! 📥

First, we need to get all the special files that make up JARVIS from the internet. It's like downloading a game!

1.  **Open your terminal** (the same window where you typed commands before).

2.  **Type this command** and press Enter. This tells your computer to copy all the JARVIS files into a new folder called `JARVIS-AI-Hub`:

    ```bash
    git clone https://github.com/lucascarvalho12/JARVIS-AI-Hub.git
    ```

3.  **Go into the new folder**. Type this and press Enter:

    ```bash
    cd JARVIS-AI-Hub
    ```

    Now you are inside the JARVIS project folder!

## Step 2: Set Up the Brain (Backend)! 🧠

This part is about getting the 


brain of JARVIS ready. The brain is called the "backend" because it works behind the scenes.

1.  **Install special Python tools**: JARVIS needs some extra tools to work. Type this command and press Enter:

    ```bash
    pip3 install --break-system-packages -r requirements.txt
    ```

    This might take a little while, like downloading updates for a game. Just wait until it finishes.

2.  **Give JARVIS its secret key**: Remember that OpenAI Key? We need to tell JARVIS what it is. First, we make a copy of a special file:

    ```bash
    cp .env.example .env
    ```

    Now, you need to **edit the `.env` file**. You can open it with a simple text editor (like Notepad on Windows, TextEdit on Mac, or any code editor). Look for a line that says `OPENAI_API_KEY=your_openai_api_key_here`.

    **Replace `your_openai_api_key_here` with your actual OpenAI Key.** Make sure there are no spaces around the `=` sign. It should look something like this:

    ```
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

    **Save the file** after you make the change.

## Step 3: Set Up the Screen (Frontend)! 🖥️

This part is about getting the cool screen, or "dashboard," for JARVIS ready. This is what you will see and interact with.

1.  **Go into the dashboard folder**: Type this and press Enter:

    ```bash
    cd ai-hub-dashboard
    ```

2.  **Install special Node.js tools**: Just like the brain, the screen needs its own special tools. Type this command and press Enter:

    ```bash
    pnpm install
    ```

    This will also take some time. Be patient!

## Step 4: Start Your JARVIS! 🎉

Now for the exciting part! We will start both the brain and the screen of your JARVIS. You will need **two terminal windows** open at the same time for this.

### **Terminal Window 1 (for the Brain - Backend):**

1.  Make sure you are in the main `JARVIS-AI-Hub` folder. If you are still in `ai-hub-dashboard`, type `cd ..` and press Enter.

2.  Type this command and press Enter to start the brain:

    ```bash
    python3 src/main.py
    ```

    You will see some messages, but don't close this window! It needs to stay open for JARVIS to work.

### **Terminal Window 2 (for the Screen - Frontend):**

1.  Make sure you are in the `ai-hub-dashboard` folder. If you are in the main `JARVIS-AI-Hub` folder, type `cd ai-hub-dashboard` and press Enter.

2.  Type this command and press Enter to start the screen:

    ```bash
    pnpm run dev --host
    ```

    You will see some messages, and it will tell you a special web address, like `http://localhost:5173`. This is where you can see your JARVIS!

## Step 5: Talk to Your JARVIS! 🗣️

1.  **Open your internet browser** (like Chrome, Firefox, or Edge).

2.  **Type the special web address** (like `http://localhost:5173`) into the address bar and press Enter.

3.  **Ta-da!** You should now see your very own JARVIS AI Hub dashboard! You can click on the "Chat" tab and type messages to your JARVIS. Try typing "Turn on the lights" and see what it says!

## What Can Your JARVIS Do? ✨

Your JARVIS is super smart! It can:

-   **Talk to you**: Just like a smart assistant!
-   **Control things**: Like turning on lights (it will pretend for now, but it knows how!)
-   **Learn and Grow**: It can even try to make itself better and add new features all by itself! This is a very advanced part, so it will take time to learn.

## Having Trouble? 🆘

If something doesn't work, don't worry! Computers can be tricky. Ask an adult for help, or you can look at the main `README.md` file in the `JARVIS-AI-Hub` folder for more detailed instructions.

**Congratulations! You've built your own JARVIS AI Hub!** Keep exploring and learning! 🤖💡

