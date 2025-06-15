import React, { useState, useEffect } from "react"; // Added useEffect
import Select from "react-select";
import { useSocket } from "../utils";

export default function SettingsForm() {
    const { socket } = useSocket();
    const [shifts, setShifts] = useState(null); // Stores selected option object
    const [days, setDays] = useState([]);   // Stores array of selected option objects
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false); // Optional loading state

    const shiftOptions = [
        { value: 1, label: '1' },
        { value: 2, label: '2' },
        { value: 3, label: '3' }
    ];

    const dayOptions = [
        { value: 'sunday', label: 'Sunday' },
        { value: 'monday', label: 'Monday' },
        { value: 'tuesday', label: 'Tuesday' },
        { value: 'wednesday', label: 'Wednesday' },
        { value: 'thursday', label: 'Thursday' },
        { value: 'friday', label: 'Friday' },
        { value: 'saturday', label: 'Saturday' }
    ];

    // Effect to listen for responses to request ID 991
    useEffect(() => {
        if (!socket) return;

        const handleMessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 991) {
                    setIsLoading(false);
                    if (response.success) {
                        setSuccessMessage(response.message || 'Preferences saved successfully!');
                        setErrorMessage('');
                    } else {
                        setErrorMessage(response.error || 'Failed to save preferences.');
                        setSuccessMessage('');
                    }
                }
            } catch (e) {
                setIsLoading(false);
                setErrorMessage('Error processing server response.');
                console.error('WebSocket message error in SettingsForm:', e);
            }
        };

        socket.addEventListener('message', handleMessage);
        return () => {
            socket.removeEventListener('message', handleMessage);
        };
    }, [socket]);

    function handleSubmit(e) {
        e.preventDefault();
        if (!shifts) {
            setErrorMessage("Please select the number of shifts per day.");
            return;
        }

        if (socket && socket.readyState === WebSocket.OPEN) {
            setIsLoading(true);
            setSuccessMessage('');
            setErrorMessage('');

            const selectedDays = days ? days.map(day => day.value) : []; // Ensure days is an array

            const request = {
                request_id: 991, // SAVE_PREFERENCES
                data: {
                    number_of_shifts_per_day: shifts.value,
                    closed_days: selectedDays,
                },
            };

            socket.send(JSON.stringify(request));
            console.log("Sent preferences to server: ", request);
        } else {
            setErrorMessage("Socket not connected. Cannot save preferences.");
            console.error("Socket not connected");
        }
        // alert('Saved!'); // Replaced with message state
    }

    return (
        <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '400px', margin: '0 auto' }}>
            {successMessage && <p style={{ color: 'green', textAlign: 'center' }}>{successMessage}</p>}
            {errorMessage && <p style={{ color: 'red', textAlign: 'center' }}>Error: {errorMessage}</p>}

            <div style={{ textAlign: 'left', marginBottom: '5px' }}>
                <label htmlFor="shiftsPerDay">Shifts per day</label>
            </div>
            <Select
                inputId="shiftsPerDay"
                options={shiftOptions}
                value={shifts}
                onChange={setShifts}
                placeholder="Pick shift count"
                isClearable
            />

            <div style={{ textAlign: 'left', marginBottom: '5px', marginTop: '15px' }}>
                <label htmlFor="closedDays">Closed days</label>
            </div>
            <Select
                inputId="closedDays"
                options={dayOptions}
                value={days}
                onChange={setDays}
                placeholder="Pick closed days"
                isMulti
                closeMenuOnSelect={false}
            />

            <button type="submit" disabled={isLoading} style={{ marginTop: '20px', padding: '10px 15px' }}>
                {isLoading ? 'Saving...' : 'Save Preferences'}
            </button>
        </form>
    );
}
