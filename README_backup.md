# JARVIS AI Hub - Enhanced Edition

A sophisticated, extensible AI assistant system inspired by Tony Stark's JARVIS. This enhanced version features dynamic skill routing, circuit breaker resilience, OpenAI GPT fallback, and comprehensive monitoring capabilities.

## 🚀 Features

### Core AI Capabilities
- **Dynamic Skill System**: Extensible skill-based architecture with JSON schema definitions
- **Intelligent Routing**: Automatic request routing to appropriate skills based on natural language processing
- **GPT Fallback**: Seamless fallback to OpenAI GPT-4 for unmatched requests
- **Circuit Breaker**: Resilient system design that isolates failing components
- **Prometheus Metrics**: Comprehensive monitoring and performance tracking

### Smart Home Integration
- **Device Control**: Control lights, thermostats, locks, and security systems
- **Natural Language Processing**: Understands commands like "turn on the living room lights"
- **Multi-Device Support**: Manage multiple devices across different locations
- **Status Monitoring**: Real-time device status and system health

### Information Services
- **Time & Date**: Current time and date information
- **Weather**: Weather information and forecasts (simulated)
- **System Status**: AI system health and performance metrics
- **General Q&A**: Powered by OpenAI GPT for comprehensive knowledge

### Web Interface
- **Modern React Dashboard**: Futuristic JARVIS-inspired interface
- **Real-time Chat**: Interactive conversation with the AI
- **Device Management**: Visual controls for smart home devices
- **System Monitoring**: Live metrics and status displays

## 🏗️ Architecture

```
JARVIS AI Hub
├── Backend (Flask)
│   ├── Orchestrator Engine
│   │   ├── Schema Loader
│   │   ├── Skill Router
│   │   ├── Circuit Breaker
│   │   └── GPT Fallback
│   ├── Skills System
│   │   ├── Device Control
│   │   ├── Information Request
│   │   └── [Extensible...]
│   ├── API Endpoints
│   │   ├── /api/chat
│   │   ├── /api/skills
│   │   ├── /api/metrics
│   │   └── /api/health
│   └── Database (SQLite)
└── Frontend (React)
    ├── Chat Interface
    ├── Device Dashboard
    ├── System Monitoring
    └── Settings Panel
```

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key** (for GPT fallback functionality)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/lucascarvalho12/JARVIS-AI-Hub.git
cd JARVIS-AI-Hub
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip3 install --break-system-packages -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file and add your OpenAI API key
nano .env
```

Add your OpenAI API key to the `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Frontend Setup

```bash
cd ai-hub-dashboard

# Install Node.js dependencies
pnpm install

# Build for production (optional)
pnpm run build
```

### 4. Run the System

#### Start Backend
```bash
# From the root directory
python3 src/main.py
```
The backend will run on `http://localhost:5000`

#### Start Frontend (Development)
```bash
# In a new terminal, from ai-hub-dashboard directory
cd ai-hub-dashboard
pnpm run dev --host
```
The frontend will run on `http://localhost:5173`

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_integration.py
```

This will test:
- Schema loading and skill matching
- Individual skill execution
- Orchestrator functionality
- Flask application setup
- API endpoints (if server is running)

## 📡 API Endpoints

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "turn on the living room lights",
  "user_id": "user123"
}
```

### Skills Management
```http
GET /api/skills                    # List all available skills
POST /api/skills/reload            # Reload skills from disk
```

### System Monitoring
```http
GET /api/health                    # Health check
GET /api/system/status             # Detailed system status
GET /api/metrics                   # Prometheus metrics
POST /api/system/circuit-breaker/reset  # Reset circuit breaker
```

## 🎯 Skills System

### Creating New Skills

1. **Create Schema** (`src/schemas/skill_name/v1.json`):
```json
{
  "name": "my_skill",
  "version": "1.0",
  "description": "Description of what this skill does",
  "action": "my_action",
  "keywords": ["keyword1", "keyword2"],
  "parameters": {
    "param1": {
      "type": "string",
      "description": "Parameter description"
    }
  }
}
```

2. **Create Skill Module** (`src/skills/my_skill.py`):
```python
def execute(input_data: dict) -> dict:
    """
    Execute the skill
    
    Args:
        input_data: Input data containing user request
        
    Returns:
        dict: Response from skill execution
    """
    return {
        "response": "Skill executed successfully!",
        "success": True
    }
```

3. **Reload Skills**:
```bash
curl -X POST http://localhost:5000/api/skills/reload
```

### Available Skills

#### Device Control (`device_control`)
- Controls smart home devices
- Supports: lights, thermostats, locks, security systems
- Commands: "turn on/off", "set temperature", "lock/unlock"

#### Information Request (`information_request`)
- Handles information queries
- Supports: time, date, weather, system status
- Commands: "what time is it", "system status", "weather"

## 📊 Monitoring

### Prometheus Metrics

The system exposes the following metrics at `/api/metrics`:

- `skill_calls_total`: Total skill executions by skill name
- `skill_failures_total`: Total skill failures by skill name  
- `gpt_calls_total`: Total GPT fallback calls
- `request_duration_seconds`: Request processing duration by type

### Circuit Breaker

The circuit breaker protects against failing skills:
- **Closed**: Normal operation
- **Open**: Skill disabled after repeated failures
- **Half-Open**: Testing if skill has recovered

Configuration:
- Failure threshold: 3 failures
- Reset timeout: 30 seconds

## 🔧 Configuration

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here

# Flask Configuration  
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key

# Circuit Breaker
CIRCUIT_BREAKER_FAIL_MAX=3
CIRCUIT_BREAKER_RESET_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

### Database

The system uses SQLite by default. The database file is created automatically at `src/database/app.db`.

## 🚀 Deployment

### Production Backend

```bash
# Install production WSGI server
pip3 install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### Production Frontend

```bash
cd ai-hub-dashboard
pnpm run build

# Serve static files with nginx or similar
```

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   - Ensure `OPENAI_API_KEY` is set in `.env` file
   - GPT fallback will be disabled without valid API key

2. **Dependencies Missing**
   - Run: `pip3 install --break-system-packages -r requirements.txt`
   - For frontend: `pnpm install` in `ai-hub-dashboard/`

3. **Port Conflicts**
   - Backend default: 5000
   - Frontend default: 5173
   - Change ports in respective configuration files

4. **Circuit Breaker Triggered**
   - Reset via: `POST /api/system/circuit-breaker/reset`
   - Check skill logs for underlying issues

### Logs

- Backend logs: Console output when running `python3 src/main.py`
- Skill execution: Logged with INFO level
- Errors: Logged with ERROR level

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your skill or enhancement
4. Run tests: `python3 test_integration.py`
5. Submit a pull request

### Adding Skills

Follow the skills system documentation above. All skills should:
- Have proper error handling
- Return consistent response format
- Include logging
- Have corresponding JSON schema

## 📄 License

This project is open source. Please refer to the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Tony Stark's JARVIS from the Marvel Cinematic Universe
- Built with Flask, React, and modern AI technologies
- Enhanced with orchestrator pattern for scalability and resilience

---

**Experience the future of AI assistance with JARVIS!** 🤖✨

For support and questions, please open an issue on GitHub.


