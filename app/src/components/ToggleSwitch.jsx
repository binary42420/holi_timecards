import React from 'react';
import '../css/ToggleSwitch.css';

const ToggleSwitch = ({ checked, onChange, disabled = false, size = 'medium' }) => {
  return (
    <label className={`toggle-switch ${size} ${disabled ? 'disabled' : ''}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="toggle-input"
      />
      <span className="toggle-slider">
        <span className="toggle-knob"></span>
      </span>
    </label>
  );
};

export default ToggleSwitch;
