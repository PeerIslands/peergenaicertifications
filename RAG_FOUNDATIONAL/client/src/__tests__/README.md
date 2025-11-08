# Client-Side Test Suite

This directory contains comprehensive test cases for all client-side files.

## Setup

Before running tests, ensure the following dependencies are installed:

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

## Test Structure

- **Library Tests** (`lib/__tests__/`): Tests for utility functions, API client, and helper functions
- **Hook Tests** (`hooks/__tests__/`): Tests for custom React hooks
- **Component Tests** (`components/__tests__/`): Tests for reusable components
- **Page Tests** (`pages/__tests__/`): Tests for page components

## Running Tests

From the project root:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm test -- --coverage
```

## Test Coverage

The test suite covers:
- ✅ All library utilities (api, authUtils, utils, logger)
- ✅ All custom hooks (useAuth, useToast, useIsMobile)
- ✅ All main components (PdfCard, UploadZone, AppSidebar)
- ✅ All pages (Chat, Dashboard, Landing, Upload, NotFound)
- ✅ App component and routing logic

