import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Header } from '@/components/layout/header';

describe('Header', () => {
  it('renders search input and user dropdown', () => {
    render(<Header />);
    const searchInput = screen.getByPlaceholderText('Tìm kiếm...');
    expect(searchInput).toBeInTheDocument();

    const defaultName = screen.getByText('Khách');
    expect(defaultName).toBeInTheDocument();
  });
});