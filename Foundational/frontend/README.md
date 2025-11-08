# Frontend Application

A modern React application built with TypeScript, Vite, and Tailwind CSS. This frontend provides a chat interface with file upload capabilities and integrates with a backend API.

## 🚀 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **Radix UI** - Accessible component primitives
- **React Query** - Data fetching and caching
- **Wouter** - Lightweight routing
- **Framer Motion** - Animations
- **Lucide React** - Icons

## 📋 Prerequisites

Before running this application, make sure you have:

- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **Backend API** running on `http://localhost:8000` (see backend README for setup)

## 🛠️ Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd peergenaicertifications/Foundational/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## 🏃‍♂️ Running the Application

### Development Mode

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

The dev server includes:
- Hot module replacement (HMR)
- TypeScript compilation
- Tailwind CSS processing
- API proxy to backend (`/api/*` routes are proxied to `http://localhost:8000`)

### Production Preview

To preview the production build locally:

```bash
npm run build
npm run start
```

This will:
1. Build the application for production
2. Start a preview server to test the production build

## 🏗️ Building for Production

### Build Command

```bash
npm run build
```

This command will:
- Compile TypeScript to JavaScript
- Bundle and optimize assets
- Process CSS with Tailwind
- Generate production-ready files in the `dist/public` directory

### Build Output

The build process creates optimized files in:
```
dist/
└── public/
    ├── index.html
    ├── assets/
    │   ├── index-[hash].js
    │   └── index-[hash].css
    └── ...
```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── chat/           # Chat-related components
│   ├── sidebar/        # Sidebar components
│   └── ui/             # Base UI components (Radix UI)
├── hooks/              # Custom React hooks
├── lib/                # Utility libraries and configurations
├── pages/              # Page components
├── App.tsx             # Main application component
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## 🔧 Configuration

### Environment Variables

The application uses the following configuration:

- **API Base URL**: `http://localhost:8000` (configured in `vite.config.ts`)
- **Development Port**: `3000`
- **Build Output**: `dist/public`

### Vite Configuration

Key configuration in `vite.config.ts`:
- React plugin for JSX support
- Path aliases (`@/` for `src/`, `@shared/` for shared types)
- API proxy for backend communication
- Build output directory

### TypeScript Configuration

TypeScript is configured in `tsconfig.json` with:
- Strict type checking
- Path mapping for imports
- ES modules support
- React JSX support

## 🎨 Styling

The application uses:
- **Tailwind CSS** for utility-first styling
- **CSS Variables** for theming
- **Radix UI** components with custom styling
- **Framer Motion** for animations

## 📱 Features

- **Chat Interface**: Real-time chat with AI
- **File Upload**: Support for document uploads
- **Session Management**: Chat session persistence
- **Responsive Design**: Mobile-friendly interface
- **Dark/Light Theme**: Theme switching capability
- **Type Safety**: Full TypeScript support

## 🚨 Troubleshooting

### Common Issues

1. **Port 3000 already in use**:
   ```bash
   # Kill process using port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **Backend connection issues**:
   - Ensure backend is running on `http://localhost:8000`
   - Check API proxy configuration in `vite.config.ts`

3. **Build failures**:
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npx tsc --noEmit`

4. **Styling issues**:
   - Ensure Tailwind CSS is properly configured
   - Check if CSS files are imported correctly

### Development Tips

- Use browser dev tools for debugging
- Check the Network tab for API calls
- Use React DevTools extension for component debugging
- Monitor console for TypeScript errors

## 📦 Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Preview production build |

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for all new files
3. Add proper type definitions
4. Test your changes thoroughly
5. Update documentation as needed

## 📄 License

This project is licensed under the MIT License.
