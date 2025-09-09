# AnyForge UI Test

A modern web-based interface for the Any-Forge AI agent framework, featuring a React frontend with TypeScript and a FastAPI backend.

## Features

- **Modern UI**: React + TypeScript with shadcn/ui components
- **Real-time Streaming**: WebSocket support for live agent responses
- **Progressive Disclosure**: Intuitive step-by-step agent configuration
- **OAuth Integration**: Composio authentication for third-party tools
- **AI-Powered Assistance**: Automatic tool selection and instruction generation
- **Multi-turn Chat**: Interactive conversation with agent persistence

## Architecture

```
any-forge/
├── backend_enhanced.py    # FastAPI REST backend
├── backend_websocket.py   # WebSocket server for streaming
├── frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/   # UI components
│   │   └── hooks/        # Custom React hooks
│   └── package.json
└── src/                   # Core any-forge logic
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/alexmeckes/anyforge-uitest.git
cd anyforge-uitest
```

### 2. Set up Python environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set up frontend

```bash
cd frontend
npm install
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key
COMPOSIO_API_KEY=your_composio_api_key
```

## Running the Application

### Start the backend servers

```bash
# Terminal 1: REST API
python backend_enhanced.py

# Terminal 2: WebSocket server
python backend_websocket.py
```

### Start the frontend

```bash
# Terminal 3
cd frontend
npm run dev
```

The application will be available at http://localhost:5173

## Usage

1. **Create an Agent**: Click "Create New Agent" to start the progressive disclosure flow
2. **Configure Integration**: Select and authenticate with Composio integrations
3. **Define Task**: Describe what your agent should do
4. **Select Tools**: Choose tools manually or let AI recommend them
5. **Set Instructions**: Add custom instructions or use AI-generated ones
6. **Run Agent**: Chat with your configured agent in real-time

## Development

### Backend Development

The backend uses FastAPI with async support:

```bash
# Run with auto-reload
uvicorn backend_enhanced:app --reload --port 8002
```

### Frontend Development

The frontend uses Vite for fast development:

```bash
cd frontend
npm run dev  # Development server with HMR
npm run build  # Production build
```

## Project Structure

- `backend_enhanced.py`: Main FastAPI backend with all REST endpoints
- `backend_websocket.py`: WebSocket server for real-time agent streaming
- `frontend/`: React application
  - `src/components/`: UI components (agent-builder, chat, etc.)
  - `src/hooks/`: Custom hooks (WebSocket management)
  - `src/lib/`: Utilities and helpers

## API Endpoints

### REST API (port 8002)

- `GET /api/agents`: List all agents
- `POST /api/agents`: Create new agent
- `GET /api/integrations`: List available integrations
- `POST /api/tools/search`: Search for tools
- `POST /api/generate/instructions`: Generate agent instructions
- `POST /api/agents/{id}/run`: Execute agent

### WebSocket (port 8003)

- `ws://localhost:8003/ws/agent/{session_id}`: Real-time agent streaming

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT

## Acknowledgments

Built on top of the [Any-Forge](https://github.com/amadad/any-forge) framework.
