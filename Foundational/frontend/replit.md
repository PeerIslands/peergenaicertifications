# Overview

This is a PDF chat application that allows users to upload PDF documents and have conversations with an AI assistant about their content. The application extracts text from uploaded PDFs and uses OpenAI's GPT model to provide contextual responses based on the document content. Users can manage their uploaded files, start new chat sessions, and interact with their documents through a clean, responsive interface.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **React + TypeScript**: Modern React application with TypeScript for type safety
- **Vite**: Fast development and build tooling with hot module replacement
- **Wouter**: Lightweight client-side routing library
- **TanStack Query**: Server state management for API calls and caching
- **shadcn/ui**: Modern component library built on Radix UI primitives with Tailwind CSS styling
- **Tailwind CSS**: Utility-first CSS framework for styling with custom design tokens

## Backend Architecture
- **Express.js**: RESTful API server handling file uploads, chat interactions, and data management
- **TypeScript**: Type-safe server-side development
- **In-Memory Storage**: Simple storage implementation using JavaScript Maps for development/demo purposes
- **File Processing**: PDF text extraction using pdf-parse library
- **Multer**: Middleware for handling multipart/form-data file uploads

## Data Storage Solutions
- **Development Storage**: In-memory storage using JavaScript Maps
- **Production Ready**: Configured for PostgreSQL with Drizzle ORM
- **Schema Design**: Three main entities - users, uploaded files, and chat messages
- **Database Migrations**: Drizzle Kit for schema management and migrations

## Authentication and Authorization
- **Session-Based**: Express session management with connect-pg-simple for PostgreSQL session storage
- **User Management**: Basic user creation and authentication system
- **Security**: CORS configuration and request validation

## API Structure
- **RESTful Endpoints**: Standard HTTP methods for CRUD operations
- **File Management**: Upload, retrieve, and delete PDF files
- **Chat System**: Message persistence and conversation history
- **Error Handling**: Comprehensive error responses and logging

## UI/UX Design Patterns
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Component Composition**: Reusable UI components with consistent styling
- **Theme System**: Light/dark mode support with CSS custom properties
- **Accessibility**: ARIA labels and keyboard navigation support

# External Dependencies

## Core Framework Dependencies
- **React Ecosystem**: React 18 with hooks, React DOM, TypeScript support
- **Express.js**: Web application framework for Node.js
- **Vite**: Next-generation frontend build tool

## Database and ORM
- **Drizzle ORM**: Type-safe SQL toolkit and ORM for PostgreSQL
- **@neondatabase/serverless**: Serverless PostgreSQL driver for Neon database
- **connect-pg-simple**: PostgreSQL session store for Express sessions

## AI Integration
- **OpenAI API**: GPT models for natural language processing and document Q&A
- **PDF Processing**: pdf-parse library for extracting text content from PDF files

## UI Component Libraries
- **Radix UI**: Comprehensive set of accessible UI primitives
- **shadcn/ui**: Pre-built component library based on Radix UI
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Icon library for consistent iconography

## State Management and Data Fetching
- **TanStack Query**: Server state management, caching, and synchronization
- **React Hook Form**: Form state management with validation
- **Zod**: TypeScript-first schema declaration and validation

## Development Tools
- **TypeScript**: Static type checking and improved developer experience
- **ESBuild**: Fast JavaScript bundler for production builds
- **PostCSS**: CSS processing and autoprefixing
- **Replit Integration**: Development environment and deployment platform support