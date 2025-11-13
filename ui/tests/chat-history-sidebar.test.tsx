import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatHistorySidebar from '@/components/chat/chat-history-sidebar';
import { api } from '@/lib/api';

// Mock API helper
vi.mock('@/lib/api', () => {
  return {
    api: {
      historiesList: vi.fn(async () => ({ data: { items: [
        { conversation_id: 'abc123', user_id: 'default', preview: 'Hello world', created_at: '2025-01-01', updated_at: '2025-01-02' },
      ], page: 1, limit: 50, total: 1 } })),
      historiesDelete: vi.fn(async () => ({ status: 200 })),
      historiesCreate: vi.fn(async () => ({ status: 200 })),
    },
  };
});

describe('ChatHistorySidebar', () => {
  beforeEach(() => {
    // Reset localStorage
    localStorage.clear();
  });

  it('loads and displays conversation list', async () => {
    render(<ChatHistorySidebar userId="default" selectedId={null} onSelectConversation={() => {}} onNewConversation={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('abc123')).toBeInTheDocument();
      expect(screen.getByText('Hello world')).toBeInTheDocument();
    });
  });

  it('starts a new chat', async () => {
    const onNew = vi.fn();
    render(<ChatHistorySidebar userId="default" selectedId={null} onSelectConversation={() => {}} onNewConversation={onNew} />);
    const newBtns = screen.getAllByTestId('new-chat-btn');
    expect(newBtns.length).toBeGreaterThan(0);
    newBtns.forEach((btn) => fireEvent.click(btn));
    await waitFor(() => {
      expect(api.historiesCreate).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(onNew).toHaveBeenCalled();
    });
  });
});