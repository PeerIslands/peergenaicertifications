# PeerGenAI Certifications
Repository for submitting the code deliverables as part of hands-on exercises in Peer GenAI Certifications

**Overview**

In this git, participants will submit their code deliverables built as part of hands-on exercises in Peer GenAI Certifications. Users can create branches with their names from main, push their code and raise PRs. PRs will be reviewed but not approved. See below for details.

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

# DocuRAG – PDF Search & Analysis Application

## Overview

DocuRAG is a web application that lets users **upload, analyze, and search PDF documents** using AI-powered insights. It uses **Retrieval-Augmented Generation (RAG)** technology to enhance document processing and search.

* **Frontend:** React 18 + TypeScript
* **Backend:** Node.js + Express
* **Database:** MongoDB
* **File Storage:** Local filesystem
* **Authentication:** Google OAuth
* **AI Integration:** OpenAI GPT models

## User Preferences

* **Communication Style:** Simple, everyday language.

## System Architecture

### Frontend

* **Framework:** React 18 + TypeScript + Vite
* **UI Library:** shadcn/ui (built on Radix UI)
* **Styling:** Tailwind CSS, custom design system inspired by Fluent/Material Design
* **State Management:**

  * Server state: TanStack Query
  * Local state: React hooks
* **Routing:** Wouter (lightweight client-side routing)
* **Theme:** Custom theme provider supporting light/dark mode

### Backend

* **Runtime:** Node.js with Express.js
* **Language:** TypeScript (ES modules)
* **API:** RESTful endpoints for PDF management & search
* **File Processing:** pdfjs-dist for PDF text extraction
* **Development:** Hot reloading via Vite middleware

## Data Storage

* **Database:** MongoDB

  * Stores user data, PDF metadata, and extracted PDF content for search
  * Supports vector search for advanced AI-based retrieval
* **File Storage:** Local filesystem

## Authentication & Authorization

* **Method:** Google OAuth
* **User Model:** Email-based with optional avatar
* **Session Management:** Express sessions using SESSION\_SECRET

## AI & Search Integration

* **AI Provider:** OpenAI (GPT-4o-mini, optionally GPT-5)
* **Text Processing:** Server-side PDF text extraction, cleanup, and validation
* **Search:** Database-driven PDF search with vector search enabled
* **RAG:** Foundation in place for future retrieval-augmented generation

## RAG 
<img width="790" height="413" alt="image" src="https://github.com/user-attachments/assets/fe0f9d59-ae82-4d4f-a002-48cebb451e33" />
<img width="838" height="668" alt="image" src="https://github.com/user-attachments/assets/4348a136-458a-4265-a1ae-24f7aadc787e" />


