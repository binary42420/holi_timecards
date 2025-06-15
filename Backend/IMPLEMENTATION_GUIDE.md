# EasyShifts Extended Settings Implementation Guide

## 🎯 Overview

This guide provides step-by-step instructions for implementing the comprehensive Extended Settings system in EasyShifts, specifically designed for Hands on Labor's event staffing operations in San Diego.

## 📋 What's Been Implemented

### 🗄️ Database Layer
- **10 New Settings Tables**: Complete schema for all settings categories
- **Migration Scripts**: Automated database setup and default data creation
- **Relationship Management**: Proper foreign keys and constraints

### 🔧 Backend Services
- **Extended Settings Controller**: CRUD operations for all settings
- **Settings Service Layer**: Business logic and validation
- **Settings Templates**: Pre-configured templates for different scenarios
- **Comprehensive Validation**: Input validation for all settings fields

### 🌐 API Layer
- **25 API Endpoints**: Complete CRUD and utility operations
- **Request/Response Handling**: Standardized API patterns
- **Error Management**: Comprehensive error handling and validation
- **Authentication**: Manager-level access control

### 🧪 Testing & Documentation
- **Unit Tests**: Comprehensive test coverage
- **API Documentation**: Complete endpoint documentation
- **Setup Scripts**: Automated initialization tools
- **User Documentation**: Implementation and usage guides

## 🚀 Implementation Steps

### Step 1: Database Setup

1. **Run Database Migration**:
   ```bash
   cd Backend/db/migrations
   python add_extended_settings_tables.py migrate
   ```

2. **Create Default Settings**:
   ```bash
   python add_extended_settings_tables.py create-defaults --workplace-id 1
   ```

3. **Verify Database Setup**:
   ```bash
   cd Backend
   python setup_extended_settings.py verify
   ```

### Step 2: Apply Default Configuration

1. **Apply Hands on Labor Template**:
   ```bash
   python setup_extended_settings.py setup --template hands_on_labor_default
   ```

2. **Verify Configuration**:
   ```bash
   python setup_extended_settings.py verify
   ```

### Step 3: Test Backend Implementation

1. **Run Unit Tests**:
   ```bash
   python -m pytest tests/test_extended_settings.py -v
   ```

2. **Test API Endpoints**:
   ```bash
   # Start the server
   python Server.py
   
   # Test basic functionality
   python test_extended_settings_api.py
   ```

### Step 4: Frontend Integration

#### 4.1 Create Settings Interface Components

**Main Settings Page** (`src/components/Settings/ExtendedSettings.jsx`):
```jsx
import React, { useState, useEffect } from 'react';
import { Tabs, Tab, Box, Alert } from '@mui/material';
import CompanyProfileSettings from './CompanyProfileSettings';
import UserManagementSettings from './UserManagementSettings';
// ... other setting components

const ExtendedSettings = () => {
    const [activeTab, setActiveTab] = useState(0);
    const [settings, setSettings] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAllSettings();
    }, []);

    const loadAllSettings = async () => {
        try {
            const response = await sendRequest(1111, {});
            if (response.success) {
                setSettings(response.data);
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                <Tab label="Company Profile" />
                <Tab label="User Management" />
                <Tab label="Certifications" />
                <Tab label="Client Management" />
                <Tab label="Job Configuration" />
                <Tab label="Timesheet Settings" />
                <Tab label="Google Integration" />
                <Tab label="Reporting" />
                <Tab label="Mobile & Accessibility" />
                <Tab label="System Administration" />
            </Tabs>
            
            {/* Tab panels for each settings category */}
            <TabPanel value={activeTab} index={0}>
                <CompanyProfileSettings 
                    settings={settings.company_profile} 
                    onUpdate={handleSettingsUpdate}
                />
            </TabPanel>
            {/* ... other tab panels */}
        </Box>
    );
};
```

#### 4.2 Individual Settings Components

**Company Profile Settings** (`src/components/Settings/CompanyProfileSettings.jsx`):
```jsx
import React, { useState } from 'react';
import { TextField, Button, Grid, Card, CardContent } from '@mui/material';

const CompanyProfileSettings = ({ settings, onUpdate }) => {
    const [formData, setFormData] = useState(settings || {});
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        try {
            const response = await sendRequest(1100, formData);
            if (response.success) {
                onUpdate('company_profile', response.data);
                showSuccessMessage('Company profile updated successfully');
            }
        } catch (error) {
            showErrorMessage('Failed to update company profile');
        } finally {
            setSaving(false);
        }
    };

    return (
        <Card>
            <CardContent>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            label="Company Name"
                            value={formData.company_name || ''}
                            onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            label="Company Email"
                            type="email"
                            value={formData.company_email || ''}
                            onChange={(e) => setFormData({...formData, company_email: e.target.value})}
                        />
                    </Grid>
                    {/* ... other fields */}
                    <Grid item xs={12}>
                        <Button 
                            variant="contained" 
                            onClick={handleSave}
                            disabled={saving}
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );
};
```

#### 4.3 Settings Templates Interface

**Templates Selection** (`src/components/Settings/TemplatesManager.jsx`):
```jsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Button, Grid, Typography } from '@mui/material';

const TemplatesManager = ({ onApplyTemplate }) => {
    const [templates, setTemplates] = useState([]);
    const [applying, setApplying] = useState(null);

    useEffect(() => {
        loadTemplates();
    }, []);

    const loadTemplates = async () => {
        const response = await sendRequest(1121, {});
        if (response.success) {
            setTemplates(response.data.templates);
        }
    };

    const applyTemplate = async (templateId) => {
        setApplying(templateId);
        try {
            const response = await sendRequest(1122, { template_id: templateId });
            if (response.success) {
                onApplyTemplate(response.data);
                showSuccessMessage('Template applied successfully');
            }
        } catch (error) {
            showErrorMessage('Failed to apply template');
        } finally {
            setApplying(null);
        }
    };

    return (
        <Grid container spacing={3}>
            {templates.map((template) => (
                <Grid item xs={12} md={6} key={template.id}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">{template.name}</Typography>
                            <Typography variant="body2" color="textSecondary">
                                {template.description}
                            </Typography>
                            <Typography variant="caption" display="block">
                                Recommended for: {template.recommended_for}
                            </Typography>
                            <Button
                                variant="contained"
                                onClick={() => applyTemplate(template.id)}
                                disabled={applying === template.id}
                                sx={{ mt: 2 }}
                            >
                                {applying === template.id ? 'Applying...' : 'Apply Template'}
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};
```

### Step 5: Google Integration Setup

1. **Configure Google OAuth**:
   - Create Google Cloud Project
   - Enable Calendar, Gmail, Drive, Maps APIs
   - Create OAuth 2.0 credentials
   - Add redirect URIs

2. **Update Environment Variables**:
   ```bash
   # Add to .env file
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   GOOGLE_REDIRECT_URI=https://easyshifts.app/auth/google/callback
   ```

3. **Test Google Integration**:
   ```javascript
   // Test connection
   const testResponse = await sendRequest(1113, {
       google_client_id: 'your_client_id',
       google_client_secret: 'your_client_secret'
   });
   ```

### Step 6: Production Deployment

1. **Environment Setup**:
   ```bash
   # Production environment variables
   DATABASE_URL=your_production_db_url
   GOOGLE_CLIENT_ID=your_production_client_id
   GOOGLE_CLIENT_SECRET=your_production_client_secret
   ```

2. **Deploy Database Changes**:
   ```bash
   # Run migrations on production
   python add_extended_settings_tables.py migrate --database-url $DATABASE_URL
   python setup_extended_settings.py setup --template hands_on_labor_default
   ```

3. **Verify Deployment**:
   ```bash
   python setup_extended_settings.py verify
   ```

## 🔧 Configuration for Hands on Labor

### Recommended Initial Settings

1. **Company Profile**:
   - Company Name: "Hands on Labor"
   - Default Hourly Rate: $28.50
   - Operating Hours: 6:00 AM - 10:00 PM
   - Time Zone: America/Los_Angeles

2. **User Management**:
   - Crew Chief Premium: $5.00/hour
   - Forklift Operator Premium: $3.00/hour
   - Truck Driver Premium: $4.00/hour

3. **Certifications**:
   - Crew Chief Certification: Required (24 months validity)
   - Forklift Certification: Required (36 months validity)
   - Safety Training: Required (12 months validity)

4. **Job Configuration**:
   - Require Crew Chief per shift
   - Maximum 8 workers per crew chief
   - Minimum 24 hours notice for new jobs

## 🛡️ Security Considerations

1. **Access Control**: All settings require manager-level access
2. **Data Validation**: Comprehensive input validation on all fields
3. **Audit Logging**: All changes are logged for compliance
4. **Backup Strategy**: Automated daily backups with 30-day retention

## 📊 Monitoring & Maintenance

1. **Health Checks**: Use endpoint 1115 for system monitoring
2. **Settings Summary**: Use endpoint 1117 for configuration analysis
3. **Backup Management**: Use endpoints 1116 and 1119 for backup operations
4. **Template Updates**: Regularly review and update settings templates

## 🔄 Ongoing Management

1. **Regular Reviews**: Monthly settings review and optimization
2. **Template Updates**: Quarterly template refinements
3. **Integration Monitoring**: Weekly Google integration health checks
4. **Compliance Audits**: Annual compliance and security reviews

## 📞 Support & Troubleshooting

1. **Logs**: Check application logs for detailed error information
2. **Validation**: Use endpoint 1124 to validate settings before applying
3. **Backup/Restore**: Use export/import functionality for configuration management
4. **Health Monitoring**: Regular system health checks using endpoint 1115

This implementation provides a robust, scalable foundation for managing all aspects of Hands on Labor's operations through EasyShifts, with comprehensive configuration options and enterprise-grade features.
