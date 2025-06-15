import React, { useState, useEffect } from 'react';

const CompanyProfileSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const [formData, setFormData] = useState({
    company_name: '',
    company_tagline: '',
    company_description: '',
    company_website: '',
    company_email: '',
    company_phone: '',
    company_address: '',
    company_logo_url: '',
    company_primary_color: '#2563eb',
    company_secondary_color: '#1e40af',
    // ... other fields from CompanyProfile model
  });

  useEffect(() => {
    if (settings && settings.company_profile) {
      setFormData(prev => ({ ...prev, ...settings.company_profile }));
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Pass only the company_profile part of the data
    onUpdate('company-profile', formData); 
  };

  if (!settings || !settings.company_profile) {
    return <div>Loading company profile settings...</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Company Information & Branding</h3>
      
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="company_name">Company Name</label>
          <input type="text" id="company_name" name="company_name" value={formData.company_name || ''} onChange={handleChange} className="form-input" />
        </div>
        <div className="form-group">
          <label htmlFor="company_tagline">Tagline</label>
          <input type="text" id="company_tagline" name="company_tagline" value={formData.company_tagline || ''} onChange={handleChange} className="form-input" />
        </div>
        <div className="form-group full-width">
          <label htmlFor="company_description">Description</label>
          <textarea id="company_description" name="company_description" value={formData.company_description || ''} onChange={handleChange} className="form-input" rows="3"></textarea>
        </div>
        <div className="form-group">
          <label htmlFor="company_website">Website</label>
          <input type="url" id="company_website" name="company_website" value={formData.company_website || ''} onChange={handleChange} className="form-input" />
        </div>
        <div className="form-group">
          <label htmlFor="company_email">Email</label>
          <input type="email" id="company_email" name="company_email" value={formData.company_email || ''} onChange={handleChange} className="form-input" />
        </div>
        <div className="form-group">
          <label htmlFor="company_phone">Phone</label>
          <input type="tel" id="company_phone" name="company_phone" value={formData.company_phone || ''} onChange={handleChange} className="form-input" />
        </div>
        <div className="form-group full-width">
          <label htmlFor="company_address">Address</label>
          <textarea id="company_address" name="company_address" value={formData.company_address || ''} onChange={handleChange} className="form-input" rows="2"></textarea>
        </div>
      </div>

      <h4 className="subcategory-title">Branding</h4>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="company_logo_url">Logo URL</label>
          <input type="url" id="company_logo_url" name="company_logo_url" value={formData.company_logo_url || ''} onChange={handleChange} className="form-input" />
        </div>
        <div className="form-group">
          <label htmlFor="company_primary_color">Primary Color</label>
          <input type="color" id="company_primary_color" name="company_primary_color" value={formData.company_primary_color || '#2563eb'} onChange={handleChange} className="form-input-color" />
        </div>
        <div className="form-group">
          <label htmlFor="company_secondary_color">Secondary Color</label>
          <input type="color" id="company_secondary_color" name="company_secondary_color" value={formData.company_secondary_color || '#1e40af'} onChange={handleChange} className="form-input-color" />
        </div>
      </div>
      
      {/* Add other fields from CompanyProfile model here */}

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Company Profile'}
        </button>
      </div>
    </form>
  );
};

export default CompanyProfileSettings;
