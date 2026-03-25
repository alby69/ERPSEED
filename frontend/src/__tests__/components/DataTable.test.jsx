import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DataTable from '../../components/DataTable';

describe('DataTable Component', () => {
  const columns = [
    { header: 'ID', accessor: 'id' },
    { header: 'Name', accessor: 'name' },
  ];

  const data = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' },
  ];

  it('renders table headers correctly', () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
  });

  it('renders data rows correctly', () => {
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });

  it('shows "No data found" when data is empty', () => {
    render(<DataTable columns={columns} data={[]} />);
    expect(screen.getByText('No data found.')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn();
    render(<DataTable columns={columns} data={data} onEdit={onEdit} />);

    const editButtons = screen.getAllByText('Edit');
    editButtons[0].click();

    expect(onEdit).toHaveBeenCalledWith(data[0]);
  });
});
