# Testing Guide

Comprehensive testing guide for the Foundational application.

## Table of Contents
- [Testing Strategy](#testing-strategy)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [End-to-End Testing](#end-to-end-testing)
- [CI/CD Integration](#cicd-integration)
- [Test Coverage](#test-coverage)

## Testing Strategy

The project uses a comprehensive testing strategy:

1. **Unit Tests**: Test individual components and functions
2. **Integration Tests**: Test service interactions
3. **E2E Tests**: Test complete user workflows
4. **Load Tests**: Test performance under load (optional)

## Backend Testing

### Setup

Install test dependencies:

```bash
cd backend
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_services/test_chat_service.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_chat"
```

### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_main.py            # Main app tests
├── test_services/          # Service tests
│   ├── test_chat_service.py
│   ├── test_session_service.py
│   └── test_process_file_service.py
└── test_utils/             # Utility tests
    ├── test_document_loader.py
    └── test_splitter.py
```

### Writing Tests

Example test:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_endpoint(async_client: AsyncClient, mock_openai):
    response = await async_client.post(
        "/chat/test_session",
        json={"message": "Hello"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

### Fixtures

Common fixtures in `conftest.py`:
- `async_client`: HTTP test client
- `mock_openai`: Mock OpenAI API calls
- `mock_mongodb`: Mock database
- `sample_pdf_file`: Sample PDF for testing

### Mocking External Services

```python
from unittest.mock import Mock, patch

@patch('openai.resources.chat.completions.Completions.create')
def test_with_mock(mock_openai):
    mock_openai.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    )
    # Your test code here
```

## Frontend Testing

### Setup

Install test dependencies:

```bash
cd frontend
npm install
```

The following packages are needed (add to package.json):
```json
{
  "devDependencies": {
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1",
    "@vitest/ui": "^1.0.4",
    "vitest": "^1.0.4",
    "jsdom": "^23.0.1"
  }
}
```

### Running Tests

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- src/components/ui/button.test.tsx
```

### Test Structure

```
frontend/src/
├── tests/
│   ├── setup.ts           # Test setup and globals
│   └── test-utils.tsx     # Custom render with providers
├── components/
│   ├── ui/
│   │   └── button.test.tsx
│   ├── chat/
│   │   ├── message.test.tsx
│   │   └── message-input.test.tsx
│   └── sidebar/
│       └── file-upload.test.tsx
└── App.test.tsx
```

### Writing Unit Tests

Example component test:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/tests/test-utils';
import { Button } from './button';

describe('Button', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    screen.getByText('Click me').click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Testing with React Query

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
);

render(<YourComponent />, { wrapper });
```

## End-to-End Testing

### Setup Playwright

```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

### Running E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Run specific test
npx playwright test e2e/chat.spec.ts

# Run in headed mode
npx playwright test --headed

# Run in specific browser
npx playwright test --project=chromium
```

### Test Structure

```
frontend/e2e/
├── app.spec.ts           # General app tests
├── chat.spec.ts          # Chat functionality
└── file-upload.spec.ts   # File upload tests
```

### Writing E2E Tests

Example:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Chat Flow', () => {
  test('should send and receive messages', async ({ page }) => {
    await page.goto('/');
    
    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-data/sample.pdf');
    
    // Wait for upload
    await page.waitForSelector('text=Upload successful');
    
    // Send message
    const input = page.locator('input[placeholder*="message"]');
    await input.fill('What is this document about?');
    await page.click('button[type="submit"]');
    
    // Verify response
    await expect(page.locator('text=AI is thinking')).toBeVisible();
    await expect(page.locator('.message-assistant')).toBeVisible({
      timeout: 10000
    });
  });
});
```

### Debugging E2E Tests

```bash
# Open Playwright Inspector
PWDEBUG=1 npm run test:e2e

# Generate test code
npx playwright codegen http://localhost:3000

# View trace
npx playwright show-trace trace.zip
```

## CI/CD Integration

### GitHub Actions

The project includes comprehensive CI/CD workflows:

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Backend tests
   - Frontend tests
   - E2E tests
   - Docker builds

2. **Code Quality** (`.github/workflows/code-quality.yml`)
   - Linting
   - Type checking
   - Code formatting

3. **Deployment** (`.github/workflows/deploy.yml`)
   - Build and push images
   - Deploy to production

### Running Tests in CI

Tests automatically run on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

### Test Reports

- Coverage reports uploaded to Codecov
- Playwright reports available as artifacts
- Test results in PR comments

## Test Coverage

### Backend Coverage

Target: 80% overall coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Frontend Coverage

Target: 70% overall coverage

```bash
# Generate coverage report
npm run test:coverage

# View HTML report
open coverage/index.html
```

### Coverage Requirements

Minimum coverage thresholds:
- Statements: 70%
- Branches: 65%
- Functions: 70%
- Lines: 70%

## Performance Testing

### Load Testing (Optional)

Using Locust for backend:

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

Example locustfile:

```python
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def send_message(self):
        self.client.post("/chat/test_session", json={
            "message": "What is this about?"
        })
```

## Best Practices

### General

1. **Write descriptive test names**
   ```python
   def test_user_can_upload_pdf_and_receive_confirmation()
   ```

2. **Use AAA pattern** (Arrange, Act, Assert)
   ```python
   def test_example():
       # Arrange
       user = create_test_user()
       
       # Act
       result = user.do_something()
       
       # Assert
       assert result == expected_value
   ```

3. **Keep tests independent**
   - Don't rely on test execution order
   - Clean up after each test
   - Use fixtures for setup/teardown

4. **Mock external dependencies**
   - Don't make real API calls
   - Use mock data
   - Control test environment

### Backend Specific

1. **Test edge cases**
   - Empty inputs
   - Invalid data
   - Large files
   - Concurrent requests

2. **Test error handling**
   ```python
   def test_handles_invalid_file():
       with pytest.raises(ValueError):
           process_file(invalid_file)
   ```

3. **Use async tests correctly**
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await some_async_function()
       assert result is not None
   ```

### Frontend Specific

1. **Test user interactions**
   ```typescript
   await userEvent.click(button);
   await userEvent.type(input, 'test message');
   ```

2. **Test accessibility**
   ```typescript
   expect(screen.getByRole('button', { name: /submit/i }))
     .toBeInTheDocument();
   ```

3. **Wait for async updates**
   ```typescript
   await waitFor(() => {
     expect(screen.getByText('Success')).toBeInTheDocument();
   });
   ```

## Troubleshooting

### Common Issues

1. **Tests timing out**
   - Increase timeout in test configuration
   - Check for unresolved promises
   - Verify mock setup

2. **Flaky tests**
   - Add proper waits
   - Remove dependencies on timing
   - Use test isolation

3. **Coverage not accurate**
   - Check ignored files
   - Verify source maps
   - Run coverage with correct options

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Note**: Keep tests up to date with code changes and aim for high coverage while focusing on meaningful tests.

