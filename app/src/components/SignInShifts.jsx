import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useSocket } from '../utils';

const SignInShifts = () => {
    const { socket } = useSocket();
    const [shiftsString, setShiftsString] = useState('');
    const [requestSubmitted, setRequestSubmitted] = useState(false);
    const [isInRequestWindow, setIsInRequestWindow] = useState(false);
    const [requestWindowStart, setRequestWindowStart] = useState(null);
    const [requestWindowEnd, setRequestWindowEnd] = useState(null);
    const [loadingWindowInfo, setLoadingWindowInfo] = useState(true);
    const [error, setError] = useState('');

    const fetchWindowInfo = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            setLoadingWindowInfo(true);
            setError('');
            // Request 1: Check if currently in window
            const inWindowRequest = { request_id: 41 };
            socket.send(JSON.stringify(inWindowRequest));

            // Request 2: Get window times
            const windowTimesRequest = { request_id: 42 };
            socket.send(JSON.stringify(windowTimesRequest));
        } else {
            setError("WebSocket is not connected. Cannot fetch request window information.");
            setLoadingWindowInfo(false);
        }
    }, [socket]);

    useEffect(() => {
        if (socket) {
            fetchWindowInfo();

            const handleMessage = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    if (response.request_id === 41) { // Is In Request Window response
                        if (response.success) {
                            setIsInRequestWindow(response.data.is_in_window);
                        } else {
                            setError(response.error || "Failed to check request window status.");
                        }
                        // setLoadingWindowInfo(false); // Wait for both responses or handle separately
                    } else if (response.request_id === 42) { // Get Request Window Times response
                        if (response.success && response.data) {
                            setRequestWindowStart(response.data.requests_window_start ? new Date(response.data.requests_window_start) : null);
                            setRequestWindowEnd(response.data.requests_window_end ? new Date(response.data.requests_window_end) : null);
                        } else {
                            setError(response.error || "Failed to fetch request window times.");
                        }
                        setLoadingWindowInfo(false); // Consider loading complete after this response
                    } else if (response.request_id === 40) { // Submit shifts response
                        if (response.success) {
                            setRequestSubmitted(true);
                            setShiftsString(''); // Clear textarea after successful submission
                            setSuccessMessage(response.message || "Shift request submitted successfully!");
                            setError('');
                        } else {
                            setRequestSubmitted(false);
                            setError(response.error || "Failed to submit shift request.");
                            setSuccessMessage('');
                        }
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message in SignInShifts:', e);
                    setError("Error processing server response.");
                    setLoadingWindowInfo(false);
                }
            };

            socket.addEventListener('message', handleMessage);
            return () => {
                socket.removeEventListener('message', handleMessage);
            };
        }
    }, [socket, fetchWindowInfo]);

    const [successMessage, setSuccessMessage] = useState(''); // For submission success

    const onSubmit = () => {
        if (!isInRequestWindow) {
            setError("Shift requests are currently not being accepted.");
            return;
        }
        if (!shiftsString.trim()) {
            setError("Please enter your availability.");
            return;
        }
        if (socket && socket.readyState === WebSocket.OPEN) {
            setError('');
            setSuccessMessage('');
            const request = {
                request_id: 40, // SUBMIT_EMPLOYEE_SHIFT_REQUEST
                data: { shiftsString },
            };
            socket.send(JSON.stringify(request));
            console.log('Request for shifts has been submitted');
            // setRequestSubmitted(true); // Moved to handleMessage for confirmation
        } else {
            setError("WebSocket is not connected. Cannot submit request.");
        }
    };

    const formatDateTime = (date) => {
        if (!date) return 'N/A';
        return date.toLocaleString();
    };

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '20px auto', textAlign: 'center', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h1>Submit Your Availability</h1>

            {loadingWindowInfo ? (
                <p>Loading request window information...</p>
            ) : (
                <div style={{ margin: '10px 0', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
                    <p><strong>Request Window:</strong></p>
                    <p>Opens: {formatDateTime(requestWindowStart)}</p>
                    <p>Closes: {formatDateTime(requestWindowEnd)}</p>
                    {!isInRequestWindow && requestWindowEnd && new Date() > requestWindowEnd && (
                        <p style={{ color: 'orange', fontWeight: 'bold' }}>The request window has passed.</p>
                    )}
                     {!isInRequestWindow && requestWindowStart && new Date() < requestWindowStart && (
                        <p style={{ color: 'blue', fontWeight: 'bold' }}>The request window has not opened yet.</p>
                    )}
                </div>
            )}

            {error && <p style={{ color: 'red', marginTop: '10px' }}>Error: {error}</p>}
            {successMessage && <p style={{ color: 'green', marginTop: '10px' }}>{successMessage}</p>}

            <textarea
                cols={65}
                rows={5}
                required
                value={shiftsString} // Controlled component
                onChange={(e) => { setShiftsString(e.target.value); setRequestSubmitted(false); setSuccessMessage(''); setError(''); }}
                placeholder="Enter your shift availability here..."
                style={{ width: '95%', padding: '10px', marginTop: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
                disabled={loadingWindowInfo || !isInRequestWindow}
            />
            <br />
            <button 
                onClick={onSubmit} 
                style={{ marginTop: '15px', padding: '10px 20px', fontSize: '16px' }}
                disabled={loadingWindowInfo || !isInRequestWindow || !shiftsString.trim()}
            >
                Submit Availability
            </button>
            
            {requestSubmitted && !error && <p style={{color: 'green', marginTop: '10px'}}>Your request has been submitted successfully!</p>}
            
            <div style={{ marginTop: '20px' }}>
                <Link to="/employeeProfile">Back to Profile</Link>
            </div>
        </div>
    );
};

export default SignInShifts;
