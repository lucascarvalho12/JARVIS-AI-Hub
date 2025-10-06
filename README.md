# JARVIS AI Hub - Advanced Self-Developing AI Assistant

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive, self-developing AI assistant system that can autonomously create, edit, and improve its own code while providing intelligent assistance across multiple platforms including smartphones, cars, and smart homes.

## 🚀 **Revolutionary Features**

### **🧠 Self-Development Capabilities**
- **Autonomous Code Generation**: Creates new functions and applications based on user requirements
- **Self-Modification**: Analyzes and improves its own codebase automatically
- **Intelligent Research**: Continuously gathers information to enhance capabilities
- **Adaptive Learning**: Learns from interactions and performance data
- **Safe Deployment**: Multiple deployment strategies with validation and rollback

### **🔧 Core AI Hub Features**
- **Multi-Platform Integration**: Seamlessly connects smartphones, cars, and smart homes
- **Dynamic Skill System**: JSON schema-based extensible skill framework
- **Circuit Breaker Pattern**: Resilient system architecture with failure isolation
- **OpenAI GPT Integration**: Advanced language model fallback for complex queries
- **Real-time Monitoring**: Comprehensive metrics and performance tracking
- **Professional Web Interface**: Modern React dashboard with multiple themes

## 🏗️ **System Architecture**

### **Backend Components**
```
JARVIS AI Hub Backend
├── AI Core Engine (orchestrator.py)
├── Self-Development Module
│   ├── Code Generation Engine
│   ├── Code Analyzer & Evaluation Unit
│   ├── Knowledge & Learning Repository
│   ├── Performance Analyzer
│   ├── Research Agent
│   ├── Validation Framework
│   └── Deployment Manager
├── Device Integration Layer
│   ├── Smartphone Integration
│   ├── Car Integration
│   └── Home Automation
├── Skills Framework
│   ├── Device Control Skills
│   ├── Information Request Skills
│   └── Custom Skills (Extensible)
└── API Gateway & Security
```

### **Frontend Components**
```
JARVIS AI Hub Dashboard
├── Chat Interface (AI Assistant)
├── Skills Management
├── System Metrics & Monitoring
├── Device Control Panels
├── Error Logging & Analysis
├── Settings & Configuration
└── Multi-Theme Support
```

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.11 or higher
- Node.js 18 or higher
- Git

### **Quick Start**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/lucascarvalho12/JARVIS-AI-Hub.git
   cd JARVIS-AI-Hub
   ```

2. **Backend Setup**
   ```bash
   # Install Python dependencies
   pip3 install --break-system-packages -r requirements.txt
   
   # Configure environment variables
   cp .env.example .env
   # Edit .env and add your OpenAI API key:
   # OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Frontend Setup**
   ```bash
   cd ai-hub-dashboard
   
   # Install Node.js dependencies
   pnpm install
   ```

4. **Start the System**
   
   **Terminal 1 - Backend:**
   ```bash
   cd JARVIS-AI-Hub
   python3 src/main.py
   ```
   
   **Terminal 2 - Frontend:**
   ```bash
   cd JARVIS-AI-Hub/ai-hub-dashboard
   pnpm run dev --host
   ```

5. **Access Your JARVIS AI Hub**
   - **Frontend Dashboard**: http://localhost:5173
   - **Backend API**: http://localhost:5000

## 🎯 **Self-Development Capabilities**

### **Autonomous Code Generation**
The AI can create new code based on natural language descriptions:

```python
# Example: Request new functionality
POST /api/self-development/initiate
{
    "goal": "Create a new skill for weather forecasting",
    "priority": "medium"
}
```

### **Code Analysis & Improvement**
Automatically analyzes existing code and suggests improvements:

```python
# Example: Analyze performance
POST /api/self-development/initiate
{
    "goal": "Improve performance of device control module",
    "priority": "high"
}
```

### **Research & Learning**
Conducts autonomous research to enhance capabilities:

```python
# Example: Research new technologies
POST /api/self-development/initiate
{
    "goal": "Research latest IoT protocols for smart home integration",
    "priority": "medium"
}
```

### **Safe Deployment Strategies**

The system supports multiple deployment strategies:

- **Safe Deployment**: Immediate replacement with validation
- **Gradual Deployment**: Phased rollout with testing
- **Canary Deployment**: Limited release with monitoring
- **Blue-Green Deployment**: Environment switching with rollback

## 📡 **API Endpoints**

### **Core AI Endpoints**
- `POST /api/chat` - Enhanced chat with skill routing
- `GET /api/skills` - List all available skills
- `POST /api/skills/reload` - Reload skills dynamically
- `GET /api/health` - System health check
- `GET /api/metrics` - Prometheus monitoring metrics

### **Device Integration Endpoints**
- `POST /api/register` - Register new device
- `GET /api/ai/devices` - List connected devices
- `POST /api/control/device` - Control device
- `GET /api/status/device/{id}` - Get device status

### **Self-Development Endpoints**
- `POST /api/self-development/initiate` - Start self-development process
- `GET /api/self-development/status/{id}` - Check development status
- `POST /api/self-development/validate` - Validate generated code
- `POST /api/self-development/deploy` - Deploy code changes
- `GET /api/self-development/history` - View development history

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///jarvis_hub.db

# Security
SECRET_KEY=your_secret_key_here

# Self-Development Settings
ENABLE_SELF_DEVELOPMENT=true
VALIDATION_LEVEL=comprehensive
DEFAULT_DEPLOYMENT_STRATEGY=safe
```

## 🧪 **Testing**

### **Run Integration Tests**
```bash
python3 test_integration.py
```

### **Test Self-Development Features**
```bash
# Test code generation
curl -X POST http://localhost:5000/api/self-development/initiate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Create a simple calculator function", "priority": "low"}'

# Test validation framework
curl -X POST http://localhost:5000/api/self-development/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b): return a + b", "language": "python"}'
```

## 📊 **Monitoring & Metrics**

The system provides comprehensive monitoring through:

- **Prometheus Metrics**: Available at `/api/metrics`
- **Health Checks**: Available at `/api/health`
- **Performance Analytics**: Built-in performance tracking
- **Error Logging**: Comprehensive error tracking and analysis
- **Self-Development History**: Track all autonomous improvements

## 🔒 **Security Features**

- **Code Validation**: Comprehensive safety checks for generated code
- **Sandboxed Execution**: Safe execution environment for testing
- **Access Control**: API authentication and authorization
- **Audit Logging**: Complete audit trail of all activities
- **Rollback Capabilities**: Safe rollback for failed deployments

## 🎨 **Frontend Features**

### **Dashboard Themes**
- Corporate Theme (Default)
- Executive Theme
- Minimal Theme

### **Key Interface Components**
- **AI Chat Interface**: Natural language interaction
- **Device Control Panels**: Real-time device management
- **System Monitoring**: Live metrics and performance data
- **Skills Management**: View and manage AI capabilities
- **Error Analysis**: Comprehensive error tracking
- **Settings Panel**: System configuration and preferences

## 🚀 **Advanced Usage**

### **Creating Custom Skills**

1. **Define Schema** (`src/schemas/my_skill/v1.json`):
```json
{
  "skill_name": "my_skill",
  "version": "1.0",
  "description": "My custom skill",
  "parameters": {
    "input": {"type": "string", "required": true}
  }
}
```

2. **Implement Skill** (`src/skills/my_skill.py`):
```python
def execute_skill(parameters):
    input_data = parameters.get('input', '')
    # Your skill logic here
    return {"success": True, "result": f"Processed: {input_data}"}
```

3. **Reload Skills**:
```bash
curl -X POST http://localhost:5000/api/skills/reload
```

### **Autonomous Improvement Workflow**

1. **Initiate Self-Development**:
```python
development_result = ai_hub.initiate_self_development(
    "Optimize database query performance",
    priority="high"
)
```

2. **Monitor Progress**:
```python
status = ai_hub.get_development_status(development_result['development_id'])
```

3. **Review and Deploy**:
```python
if status['validation_passed']:
    deployment_result = ai_hub.deploy_improvements(
        development_result['development_id'],
        strategy="gradual"
    )
```

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: [Wiki](https://github.com/lucascarvalho12/JARVIS-AI-Hub/wiki)
- **Issues**: [GitHub Issues](https://github.com/lucascarvalho12/JARVIS-AI-Hub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lucascarvalho12/JARVIS-AI-Hub/discussions)

## 🎯 **Roadmap**

### **Current Version (v2.0)**
- ✅ Self-development capabilities
- ✅ Advanced validation framework
- ✅ Multiple deployment strategies
- ✅ Comprehensive monitoring
- ✅ Professional web interface

### **Upcoming Features (v2.1)**
- 🔄 Enhanced machine learning integration
- 🔄 Voice command processing
- 🔄 Mobile application
- 🔄 Cloud deployment options
- 🔄 Advanced security features

### **Future Vision (v3.0)**
- 🔮 Fully autonomous AI companion
- 🔮 Cross-platform synchronization
- 🔮 Advanced predictive capabilities
- 🔮 Enterprise-grade scalability
- 🔮 AI-to-AI communication protocols

## 🌟 **Acknowledgments**

- OpenAI for GPT integration
- Flask and React communities
- Contributors and testers
- Open source community

---

**JARVIS AI Hub** - *Your Intelligent, Self-Developing AI Companion* 🤖✨

*"The future of AI assistance is here - autonomous, intelligent, and constantly improving."*

