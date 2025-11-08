import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environmentMatchGlobs: [
      ['server/**/*.test.ts', 'node'],
      ['client/**/*.test.{ts,tsx}', 'jsdom'],
      ['client/**/*.spec.{ts,tsx}', 'jsdom'],
    ],
    setupFiles: ['./client/src/__tests__/setup.ts'],
    include: ['server/**/*.test.ts', 'client/**/*.test.{ts,tsx}', 'client/**/*.spec.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'server/**/*.ts',
        'client/src/**/*.{ts,tsx}',
      ],
      exclude: [
        'server/**/*.test.ts',
        'server/**/*.d.ts',
        'client/src/**/*.test.{ts,tsx}',
        'client/src/**/*.spec.{ts,tsx}',
        'client/src/__tests__/**',
        'client/src/**/*.d.ts',
        'client/src/components/ui/**',
        'client/src/components/examples/**',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, 'client', 'src'),
      '@shared': path.resolve(import.meta.dirname, 'shared'),
      '@assets': path.resolve(import.meta.dirname, 'attached_assets'),
    },
  },
});

