import React, { useState, useEffect } from 'react';
import { useSocket } from '../utils';
import './TrashBin.css';

const TrashBin = () => {
  const { socket } = useSocket();
  const [deletedItems, setDeletedItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [filterType, setFilterType] = useState('all'); // 'all', 'users', 'jobs', 'shifts', 'clients'
  const [sortBy, setSortBy] = useState('newest'); // 'newest', 'oldest'
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDeletedItems();
  }, [socket]);

  const fetchDeletedItems = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    setIsLoading(true);
    setError('');

    const request = {
      request_id: 701, // GET_DELETED_ITEMS
      data: {}
    };

    socket.send(JSON.stringify(request));

    const handleResponse = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 701) {
          socket.removeEventListener('message', handleResponse);
          setIsLoading(false);
          
          if (response.success) {
            setDeletedItems(response.data || []);
          } else {
            setError(response.error || 'Failed to fetch deleted items');
          }
        }
      } catch (err) {
        console.error('Error parsing response:', err);
      }
    };

    socket.addEventListener('message', handleResponse);

    setTimeout(() => {
      socket.removeEventListener('message', handleResponse);
      if (isLoading) {
        setIsLoading(false);
        setError('Request timed out');
      }
    }, 10000);
  };

  const handleRestore = (itemId, itemType) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    const request = {
      request_id: 702, // RESTORE_ITEM
      data: {
        item_id: itemId,
        item_type: itemType
      }
    };

    socket.send(JSON.stringify(request));

    const handleResponse = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 702) {
          socket.removeEventListener('message', handleResponse);
          
          if (response.success) {
            // Remove restored item from the list
            setDeletedItems(prev => prev.filter(item => 
              !(item.id === itemId && item.type === itemType)
            ));
            setSelectedItems(prev => prev.filter(id => id !== `${itemType}_${itemId}`));
          } else {
            setError(response.error || 'Failed to restore item');
          }
        }
      } catch (err) {
        console.error('Error parsing response:', err);
      }
    };

    socket.addEventListener('message', handleResponse);
  };

  const handleBulkRestore = () => {
    if (selectedItems.length === 0) return;

    const request = {
      request_id: 703, // BULK_RESTORE_ITEMS
      data: {
        items: selectedItems.map(id => {
          const [type, itemId] = id.split('_');
          return { item_id: parseInt(itemId), item_type: type };
        })
      }
    };

    socket.send(JSON.stringify(request));

    const handleResponse = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 703) {
          socket.removeEventListener('message', handleResponse);
          
          if (response.success) {
            // Remove restored items from the list
            const restoredIds = selectedItems;
            setDeletedItems(prev => prev.filter(item => 
              !restoredIds.includes(`${item.type}_${item.id}`)
            ));
            setSelectedItems([]);
          } else {
            setError(response.error || 'Failed to restore items');
          }
        }
      } catch (err) {
        console.error('Error parsing response:', err);
      }
    };

    socket.addEventListener('message', handleResponse);
  };

  const handlePermanentDelete = (itemId, itemType) => {
    if (!window.confirm('Are you sure you want to permanently delete this item? This action cannot be undone.')) {
      return;
    }

    const request = {
      request_id: 704, // PERMANENT_DELETE_ITEM
      data: {
        item_id: itemId,
        item_type: itemType
      }
    };

    socket.send(JSON.stringify(request));

    const handleResponse = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 704) {
          socket.removeEventListener('message', handleResponse);
          
          if (response.success) {
            setDeletedItems(prev => prev.filter(item => 
              !(item.id === itemId && item.type === itemType)
            ));
            setSelectedItems(prev => prev.filter(id => id !== `${itemType}_${itemId}`));
          } else {
            setError(response.error || 'Failed to permanently delete item');
          }
        }
      } catch (err) {
        console.error('Error parsing response:', err);
      }
    };

    socket.addEventListener('message', handleResponse);
  };

  const handleSelectItem = (itemId, itemType) => {
    const id = `${itemType}_${itemId}`;
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(selectedId => selectedId !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedItems.length === filteredItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredItems.map(item => `${item.type}_${item.id}`));
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getItemIcon = (type) => {
    switch (type) {
      case 'user': return '👤';
      case 'job': return '💼';
      case 'shift': return '⏰';
      case 'client': return '🏢';
      default: return '📄';
    }
  };

  const getItemTypeName = (type) => {
    switch (type) {
      case 'user': return 'User';
      case 'job': return 'Job';
      case 'shift': return 'Shift';
      case 'client': return 'Client';
      default: return 'Item';
    }
  };

  // Filter and sort items
  const filteredItems = deletedItems
    .filter(item => filterType === 'all' || item.type === filterType)
    .sort((a, b) => {
      const dateA = new Date(a.deleted_at);
      const dateB = new Date(b.deleted_at);
      return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
    });

  return (
    <div className="trash-bin-container">
      <div className="trash-bin-header">
        <div className="header-content">
          <h1>🗑️ Trash Bin</h1>
          <p>Manage deleted items - restore or permanently delete</p>
        </div>
        
        <div className="header-actions">
          <button onClick={fetchDeletedItems} className="refresh-button" disabled={isLoading}>
            {isLoading ? 'Loading...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
          <button onClick={() => setError('')} className="close-error">×</button>
        </div>
      )}

      <div className="trash-controls">
        <div className="filter-controls">
          <label>Filter by type:</label>
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="all">All Items</option>
            <option value="user">Users</option>
            <option value="job">Jobs</option>
            <option value="shift">Shifts</option>
            <option value="client">Clients</option>
          </select>

          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="newest">Newest Deleted</option>
            <option value="oldest">Oldest Deleted</option>
          </select>
        </div>

        {filteredItems.length > 0 && (
          <div className="bulk-actions">
            <button onClick={handleSelectAll} className="select-all-button">
              {selectedItems.length === filteredItems.length ? 'Deselect All' : 'Select All'}
            </button>
            
            {selectedItems.length > 0 && (
              <button onClick={handleBulkRestore} className="bulk-restore-button">
                Restore Selected ({selectedItems.length})
              </button>
            )}
          </div>
        )}
      </div>

      <div className="trash-content">
        {isLoading && <div className="loading-message">Loading deleted items...</div>}

        {!isLoading && filteredItems.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🗑️</div>
            <h3>Trash bin is empty</h3>
            <p>No deleted items found.</p>
          </div>
        )}

        {!isLoading && filteredItems.length > 0 && (
          <div className="deleted-items-list">
            {filteredItems.map((item) => (
              <div key={`${item.type}_${item.id}`} className="deleted-item">
                <div className="item-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(`${item.type}_${item.id}`)}
                    onChange={() => handleSelectItem(item.id, item.type)}
                  />
                </div>

                <div className="item-info">
                  <div className="item-header">
                    <span className="item-icon">{getItemIcon(item.type)}</span>
                    <span className="item-type">{getItemTypeName(item.type)}</span>
                    <span className="item-name">{item.name}</span>
                  </div>
                  
                  <div className="item-details">
                    <span className="deleted-date">
                      Deleted: {formatDate(item.deleted_at)}
                    </span>
                    {item.description && (
                      <span className="item-description">{item.description}</span>
                    )}
                  </div>
                </div>

                <div className="item-actions">
                  <button
                    onClick={() => handleRestore(item.id, item.type)}
                    className="restore-button"
                    title="Restore item"
                  >
                    ↩️ Restore
                  </button>
                  
                  <button
                    onClick={() => handlePermanentDelete(item.id, item.type)}
                    className="permanent-delete-button"
                    title="Permanently delete"
                  >
                    🗑️ Delete Forever
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrashBin;
