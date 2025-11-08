# How to Run Test Cases

## Step 1: Install Required Dependencies

Before running the tests, you need to install the React testing libraries:

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

## Step 2: Run Tests

### Run All Tests (Client + Server)
```bash
npm test
```

This will run all test files in both `server/` and `client/` directories once.

### Run Tests in Watch Mode
```bash
npm run test:watch
```

This will run tests in watch mode, automatically re-running tests when files change. Press `q` to quit.

### Run Tests with Coverage Report
```bash
npm test -- --coverage
```

This will generate a coverage report showing which parts of your code are tested.

### Run Only Client-Side Tests
```bash
npm test -- client
```

This filters to only run tests in the `client/` directory.

### Run Only Server-Side Tests
```bash
npm test -- server
```

This filters to only run tests in the `server/` directory.

### Run a Specific Test File
```bash
npm test -- client/src/lib/__tests__/utils.test.ts
```

### Run Tests Matching a Pattern
```bash
npm test -- --grep "api"
```

This runs only tests whose names match "api".

## Step 3: View Coverage Report

After running with `--coverage`, you can view the HTML coverage report:

```bash
open coverage/index.html
```

Or on Linux:
```bash
xdg-open coverage/index.html
```

## Available Test Scripts

- `npm test` - Run all tests once
- `npm run test:watch` - Run tests in watch mode

## Test File Locations

- **Client tests**: `client/src/**/*.test.{ts,tsx}`
- **Server tests**: `server/**/*.test.ts`
- **Test setup**: `client/src/__tests__/setup.ts`

## Troubleshooting

### If tests fail with "Cannot find module '@testing-library/react'"
Install the missing dependencies:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### If tests fail with "jsdom is not defined"
Make sure `jsdom` is installed:
```bash
npm install --save-dev jsdom
```

### If you see path alias errors
The vitest.config.ts should already be configured with the correct aliases. Make sure you're running tests from the project root directory.

## Test Structure

- **Library Tests**: `client/src/lib/__tests__/`
- **Hook Tests**: `client/src/hooks/__tests__/`
- **Component Tests**: `client/src/components/__tests__/`
- **Page Tests**: `client/src/pages/__tests__/`

