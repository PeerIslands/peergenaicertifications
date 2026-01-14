# PeerGenAI Certifications - Chat PDF Application

A full-stack chat application that allows users to upload PDF documents and interact with them using AI-powered chat. Built with React, Express.js, MongoDB, and Ollama for local AI processing.

## Features

- 📄 **PDF Upload & Processing**: Upload PDF documents and extract text content
- 🤖 **AI-Powered Chat**: Chat with your PDF documents using Ollama's local AI models
- 💾 **Document Storage**: MongoDB-based storage for PDF documents and chat history
- 🎨 **Modern UI**: Beautiful React interface with Tailwind CSS and Radix UI components
- 🔍 **Context-Aware Responses**: AI responses are contextualized based on PDF content

## Prerequisites

Before running this application, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **npm** or **yarn**
- **MongoDB** (local instance or MongoDB Atlas)
- **Ollama** (for local AI processing)

### Installing Ollama

1. **macOS**: 
   ```bash
   brew install ollama
   ```

2. **Linux**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Windows**: Download from [ollama.ai](https://ollama.ai/download)

4. **Pull the required model**:
   ```bash
   ollama pull llama3:latest
   ```

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd peergenaicertifications
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database
   DATABASE_URL=mongodb://localhost:27017/chatpdf
   # Or use MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/chatpdf
   
   # Ollama Configuration
   OLLAMA_HOST=http://localhost:11434
   
   # Server Configuration
   PORT=5000
   NODE_ENV=development
   ```

4. **Start MongoDB** (if using local instance):
   ```bash
   # macOS with Homebrew
   brew services start mongodb-community
   
   # Or start manually
   mongod
   ```

5. **Start Ollama**:
   ```bash
   ollama serve
   ```

## Running the Application

### Development Mode

1. **Start the development server**:
   ```bash
   npm run dev
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

The application will automatically:
- Start the Express.js backend server
- Serve the React frontend with hot reloading
- Connect to MongoDB
- Connect to Ollama for AI processing

### Production Mode

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Start the production server**:
   ```bash
   npm start
   ```

## Usage

1. **Upload a PDF**: Click the upload button and select a PDF file (max 10MB)
2. **Wait for Processing**: The PDF will be processed and text will be extracted
3. **Start Chatting**: Ask questions about the PDF content in the chat interface
4. **View Sources**: AI responses will include source references from the PDF

## Project Structure

```
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utility functions
├── server/                # Express.js backend
│   ├── index.ts          # Server entry point
│   ├── routes.ts         # API routes
│   ├── db.ts             # Database connection
│   └── storage.ts        # Data storage functions
├── shared/               # Shared schemas and types
└── uploads/              # PDF upload directory
```

## API Endpoints

- `POST /api/upload` - Upload PDF file
- `GET /api/documents` - Get all documents
- `GET /api/documents/:id` - Get specific document
- `POST /api/chat` - Send chat message
- `GET /api/chat/:documentId` - Get chat history for document

## Troubleshooting

### Common Issues

1. **Ollama not responding**:
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is installed: `ollama list`
   - Pull the model: `ollama pull llama3:latest`

2. **MongoDB connection issues**:
   - Verify MongoDB is running
   - Check DATABASE_URL in your `.env` file
   - Ensure network access if using MongoDB Atlas

3. **Port conflicts**:
   - Change PORT in `.env` file if 5000 is occupied
   - Ensure Ollama is running on port 11434

4. **PDF upload issues**:
   - Check file size (max 10MB)
   - Ensure file is a valid PDF
   - Check uploads directory permissions

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run check` - TypeScript type checking

### Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Radix UI
- **Backend**: Express.js, TypeScript, Node.js
- **Database**: MongoDB
- **AI**: Ollama with Llama3 model
- **Build Tools**: Vite, ESBuild

---

## Original Instructions

**Branch Creation**

•	Participants can create branches with their full name. For example, if your name is John Doe, you can create branch name as /johndoe

•	Participants submit their code inside this branch. 

•	Participants should raise PR to indicate their submission. Only one PR will be allowed per person for submission.

•	PRs will be reviewed but not approved and merged into main branch.

**Code Submission**

•	Ensure code follows proper standards based on the technology used.

•	Include unit test cases and test results where applicable.

•	Code should follow proper structure for folders such as common, frontend, backend etc and files such as readme, build and deployment scripts.

•	Readme should include instructions on how to build and run the code locally including any dependencies.

