import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../ToggleSwitch';

const CertificationsSettings = ({ settings, onUpdate, onMarkUnsaved, isLoading }) => {
  const initialFormData = {
    // Certification Requirements
    require_crew_chief_certification: true,
    require_forklift_certification: true,
    require_truck_driver_license: true,
    require_safety_training: true,
    require_background_check: true,
    // Certification Validity
    crew_chief_cert_validity_months: 24,
    forklift_cert_validity_months: 36,
    safety_training_validity_months: 12,
    background_check_validity_months: 12,
    // Training Requirements
    mandatory_safety_orientation: true,
    safety_orientation_duration_hours: 4,
    require_annual_safety_refresher: true,
    require_equipment_specific_training: true,
    // Role Experience Requirements
    stagehand_min_experience_months: 0,
    crew_chief_min_experience_months: 12,
    forklift_operator_min_experience_months: 6,
    truck_driver_min_experience_months: 3,
    // Certification Tracking
    auto_notify_expiring_certs: true,
    cert_expiry_warning_days: 30,
    suspend_expired_cert_workers: true,
    require_cert_photo_upload: true,
    // Verification Settings
    require_manager_cert_verification: true,
    allow_self_reported_experience: false,
    require_reference_verification: true,
    background_check_provider: 'Sterling Talent Solutions',
    // Skill Assessments
    require_practical_skill_test: true,
    skill_test_validity_months: 12,
    allow_skill_test_retakes: true,
    max_skill_test_attempts: 3,
    // Documentation
    require_cert_documentation: true,
    accept_digital_certificates: true,
    require_original_documents: false,
    document_retention_years: 7,
    // approved_training_providers and custom_certifications are JSON fields, will need special handling if editable here
  };

  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    if (settings && settings.certifications_settings) {
      setFormData(prev => ({ ...initialFormData, ...settings.certifications_settings }));
    } else if (settings && Object.keys(settings).length > 0 && !settings.certifications_settings) {
      setFormData(initialFormData);
    }
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : (type === 'number' ? parseInt(value, 10) : value);
    setFormData(prev => ({ ...prev, [name]: val }));
    onMarkUnsaved();
  };

  const handleToggle = (name) => {
    setFormData(prev => ({ ...prev, [name]: !prev[name] }));
    onMarkUnsaved();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate('certifications', formData); // 'certifications' matches the key in requestIdMap
  };
  
  if (!settings) {
    return <div>Loading certification settings...</div>;
  }
  const currentData = (settings && settings.certifications_settings) ? { ...initialFormData, ...settings.certifications_settings } : formData;

  return (
    <form onSubmit={handleSubmit} className="settings-form-category">
      <h3 className="category-title">Certifications & Role Requirements</h3>

      <section className="settings-subsection">
        <h4 className="subcategory-title">General Certification Requirements</h4>
        <div className="form-grid">
          <ToggleSwitch label="Require Crew Chief Certification" checked={currentData.require_crew_chief_certification} onChange={() => handleToggle('require_crew_chief_certification')} />
          <ToggleSwitch label="Require Forklift Certification" checked={currentData.require_forklift_certification} onChange={() => handleToggle('require_forklift_certification')} />
          <ToggleSwitch label="Require Truck Driver License" checked={currentData.require_truck_driver_license} onChange={() => handleToggle('require_truck_driver_license')} />
          <ToggleSwitch label="Require Safety Training Completion" checked={currentData.require_safety_training} onChange={() => handleToggle('require_safety_training')} />
          <ToggleSwitch label="Require Background Check" checked={currentData.require_background_check} onChange={() => handleToggle('require_background_check')} />
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Certification Validity Periods</h4>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="crew_chief_cert_validity_months">Crew Chief Cert Validity (months)</label>
            <input type="number" id="crew_chief_cert_validity_months" name="crew_chief_cert_validity_months" value={currentData.crew_chief_cert_validity_months} onChange={handleChange} min="1" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="forklift_cert_validity_months">Forklift Cert Validity (months)</label>
            <input type="number" id="forklift_cert_validity_months" name="forklift_cert_validity_months" value={currentData.forklift_cert_validity_months} onChange={handleChange} min="1" className="form-input" />
          </div>
          <div className="form-group">
            <label htmlFor="safety_training_validity_months">Safety Training Validity (months)</label>
            <input type="number" id="safety_training_validity_months" name="safety_training_validity_months" value={currentData.safety_training_validity_months} onChange={handleChange} min="1" className="form-input" />
          </div>
           <div className="form-group">
            <label htmlFor="background_check_validity_months">Background Check Validity (months)</label>
            <input type="number" id="background_check_validity_months" name="background_check_validity_months" value={currentData.background_check_validity_months} onChange={handleChange} min="1" className="form-input" />
          </div>
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Training Requirements</h4>
        <div className="form-grid">
            <ToggleSwitch label="Mandatory Safety Orientation" checked={currentData.mandatory_safety_orientation} onChange={() => handleToggle('mandatory_safety_orientation')} />
            <div className="form-group">
                <label htmlFor="safety_orientation_duration_hours">Safety Orientation Duration (hours)</label>
                <input type="number" id="safety_orientation_duration_hours" name="safety_orientation_duration_hours" value={currentData.safety_orientation_duration_hours} onChange={handleChange} min="0" className="form-input" />
            </div>
            <ToggleSwitch label="Require Annual Safety Refresher" checked={currentData.require_annual_safety_refresher} onChange={() => handleToggle('require_annual_safety_refresher')} />
            <ToggleSwitch label="Require Equipment-Specific Training" checked={currentData.require_equipment_specific_training} onChange={() => handleToggle('require_equipment_specific_training')} />
        </div>
      </section>

      <section className="settings-subsection">
        <h4 className="subcategory-title">Role Experience Requirements</h4>
        <div className="form-grid">
            <div className="form-group">
                <label htmlFor="stagehand_min_experience_months">Stagehand Min. Experience (months)</label>
                <input type="number" id="stagehand_min_experience_months" name="stagehand_min_experience_months" value={currentData.stagehand_min_experience_months} onChange={handleChange} min="0" className="form-input" />
            </div>
            <div className="form-group">
                <label htmlFor="crew_chief_min_experience_months">Crew Chief Min. Experience (months)</label>
                <input type="number" id="crew_chief_min_experience_months" name="crew_chief_min_experience_months" value={currentData.crew_chief_min_experience_months} onChange={handleChange} min="0" className="form-input" />
            </div>
            <div className="form-group">
                <label htmlFor="forklift_operator_min_experience_months">Forklift Operator Min. Experience (months)</label>
                <input type="number" id="forklift_operator_min_experience_months" name="forklift_operator_min_experience_months" value={currentData.forklift_operator_min_experience_months} onChange={handleChange} min="0" className="form-input" />
            </div>
            <div className="form-group">
                <label htmlFor="truck_driver_min_experience_months">Truck Driver Min. Experience (months)</label>
                <input type="number" id="truck_driver_min_experience_months" name="truck_driver_min_experience_months" value={currentData.truck_driver_min_experience_months} onChange={handleChange} min="0" className="form-input" />
            </div>
        </div>
      </section>
      
      {/* Add more sections for Certification Tracking, Verification, Skill Assessments, Documentation */}

      <div className="settings-actions">
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Certification Settings'}
        </button>
      </div>
    </form>
  );
};

export default CertificationsSettings;
