import React, { useState, useEffect, useRef } from 'react';
import { useSocket } from '../utils';
import './AdvancedSearch.css';

const AdvancedSearch = ({ onResultSelect, placeholder = "Search...", searchTypes = ['all'] }) => {
  const { socket } = useSocket();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [filters, setFilters] = useState({
    type: 'all',
    dateRange: 'all',
    status: 'all'
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const searchRef = useRef(null);
  const resultsRef = useRef(null);
  const debounceRef = useRef(null);

  const searchTypeOptions = [
    { value: 'all', label: 'All', icon: '🔍' },
    { value: 'employees', label: 'Employees', icon: '👥' },
    { value: 'jobs', label: 'Jobs', icon: '💼' },
    { value: 'shifts', label: 'Shifts', icon: '📅' },
    { value: 'clients', label: 'Clients', icon: '🏢' },
    { value: 'timesheets', label: 'Timesheets', icon: '⏰' },
    { value: 'invoices', label: 'Invoices', icon: '💰' }
  ];

  const dateRangeOptions = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'quarter', label: 'This Quarter' },
    { value: 'year', label: 'This Year' }
  ];

  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'pending', label: 'Pending' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' }
  ];

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.request_id === 1000) { // ADVANCED_SEARCH
          setIsSearching(false);
          if (response.success) {
            setResults(response.data || []);
            setShowResults(true);
            setSelectedIndex(-1);
          } else {
            setResults([]);
            setShowResults(false);
          }
        }
      } catch (e) {
        console.error('Error parsing search response:', e);
        setIsSearching(false);
        setResults([]);
        setShowResults(false);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const performSearch = (searchQuery, searchFilters) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    if (!searchQuery.trim()) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setIsSearching(true);
    const request = {
      request_id: 1000, // ADVANCED_SEARCH
      data: {
        query: searchQuery.trim(),
        filters: searchFilters,
        limit: 20
      }
    };
    socket.send(JSON.stringify(request));
  };

  const handleInputChange = (e) => {
    const newQuery = e.target.value;
    setQuery(newQuery);

    // Debounce search
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      performSearch(newQuery, filters);
    }, 300);
  };

  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...filters, [filterType]: value };
    setFilters(newFilters);
    
    if (query.trim()) {
      performSearch(query, newFilters);
    }
  };

  const handleKeyDown = (e) => {
    if (!showResults || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < results.length) {
          handleResultSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowResults(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleResultSelect = (result) => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    setSelectedIndex(-1);
    
    if (onResultSelect) {
      onResultSelect(result);
    }
  };

  const getResultIcon = (type) => {
    const typeConfig = searchTypeOptions.find(opt => opt.value === type);
    return typeConfig ? typeConfig.icon : '📄';
  };

  const highlightMatch = (text, query) => {
    if (!query.trim()) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="search-highlight">{part}</mark>
      ) : part
    );
  };

  const formatResultSubtext = (result) => {
    switch (result.type) {
      case 'employees':
        return `${result.role || 'Employee'} • ${result.email || ''}`;
      case 'jobs':
        return `${result.client_name || ''} • ${result.status || ''}`;
      case 'shifts':
        return `${result.job_name || ''} • ${new Date(result.date).toLocaleDateString()}`;
      case 'clients':
        return `${result.contact_email || ''} • ${result.phone || ''}`;
      case 'timesheets':
        return `${result.employee_name || ''} • ${result.date || ''}`;
      case 'invoices':
        return `${result.client_name || ''} • $${result.amount || 0}`;
      default:
        return result.description || '';
    }
  };

  return (
    <div className="advanced-search" ref={searchRef}>
      <div className="search-input-container">
        <div className="search-input-wrapper">
          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => query && setShowResults(true)}
            placeholder={placeholder}
            className="search-input"
          />
          <div className="search-icons">
            {isSearching && <div className="search-spinner">⏳</div>}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className={`advanced-toggle ${showAdvanced ? 'active' : ''}`}
              title="Advanced Search Options"
            >
              ⚙️
            </button>
          </div>
        </div>

        {showAdvanced && (
          <div className="advanced-filters">
            <div className="filter-group">
              <label>Type:</label>
              <select
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
              >
                {searchTypeOptions
                  .filter(option => searchTypes.includes('all') || searchTypes.includes(option.value))
                  .map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
              </select>
            </div>
            <div className="filter-group">
              <label>Date:</label>
              <select
                value={filters.dateRange}
                onChange={(e) => handleFilterChange('dateRange', e.target.value)}
              >
                {dateRangeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label>Status:</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {showResults && (
        <div className="search-results" ref={resultsRef}>
          {results.length === 0 ? (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <div className="no-results-text">
                {isSearching ? 'Searching...' : 'No results found'}
              </div>
            </div>
          ) : (
            <div className="results-list">
              {results.map((result, index) => (
                <div
                  key={`${result.type}-${result.id}`}
                  className={`result-item ${index === selectedIndex ? 'selected' : ''}`}
                  onClick={() => handleResultSelect(result)}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <div className="result-icon">
                    {getResultIcon(result.type)}
                  </div>
                  <div className="result-content">
                    <div className="result-title">
                      {highlightMatch(result.title || result.name, query)}
                    </div>
                    <div className="result-subtext">
                      {formatResultSubtext(result)}
                    </div>
                  </div>
                  <div className="result-type">
                    {result.type}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdvancedSearch;
