import '@testing-library/jest-dom/vitest';

// Mock next/navigation for components using router
vi.mock('next/navigation', async () => {
  return {
    useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }),
  } as any;
}); 