import React, { useState } from 'react';
import { useSocket } from '../utils';
import { useAuth } from '../contexts/AuthContext';

const TestGoogleSignup = () => {
    const [result, setResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { socket } = useSocket();
    const { login } = useAuth();

    const testManagerSignup = () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setResult('❌ WebSocket not connected');
            return;
        }

        setIsLoading(true);
        setResult('🔄 Testing manager signup...');

        const mockRequest = {
            request_id: 70, // GOOGLE_SIGNUP_MANAGER
            data: {
                username: 'test_manager_' + Date.now(),
                name: 'Test Manager',
                email: 'test@example.com',
                googleData: {
                    sub: 'mock_google_id_' + Date.now(),
                    email: 'test@example.com',
                    name: 'Test Manager',
                    picture: 'https://via.placeholder.com/96',
                    email_verified: true
                }
            }
        };

        const handleResponse = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 70) {
                    socket.removeEventListener('message', handleResponse);
                    setIsLoading(false);

                    if (response.success) {
                        setResult(`✅ Manager signup successful!\nUsername: ${response.data.username}\nIs Manager: ${response.data.is_manager}`);
                        // Auto-login the test user
                        login(response.data.username, null, response.data.is_manager, true);
                    } else {
                        setResult(`❌ Manager signup failed: ${response.error}`);
                    }
                }
            } catch (error) {
                setResult(`❌ Error parsing response: ${error.message}`);
                setIsLoading(false);
            }
        };

        socket.addEventListener('message', handleResponse);
        socket.send(JSON.stringify(mockRequest));

        console.log('Sent test request:', mockRequest);
    };

    const testEmployeeSignup = () => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setResult('❌ WebSocket not connected');
            return;
        }

        setIsLoading(true);
        setResult('🔄 Testing employee signup...');

        const mockRequest = {
            request_id: 69, // GOOGLE_SIGNUP_EMPLOYEE
            data: {
                username: 'test_employee_' + Date.now(),
                name: 'Test Employee',
                email: 'employee@example.com',
                businessName: 'Test Business',
                googleData: {
                    sub: 'mock_google_id_emp_' + Date.now(),
                    email: 'employee@example.com',
                    name: 'Test Employee',
                    picture: 'https://via.placeholder.com/96',
                    email_verified: true
                },
                certifications: {
                    canCrewChief: true,
                    canForklift: false,
                    canTruck: true
                }
            }
        };

        const handleResponse = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.request_id === 69) {
                    socket.removeEventListener('message', handleResponse);
                    setIsLoading(false);

                    if (response.success) {
                        setResult(`✅ Employee signup successful!\nUsername: ${response.data.username}\nIs Manager: ${response.data.is_manager}`);
                        login(response.data.username, null, response.data.is_manager, true);
                    } else {
                        setResult(`❌ Employee signup failed: ${response.error}`);
                    }
                }
            } catch (error) {
                setResult(`❌ Error parsing response: ${error.message}`);
                setIsLoading(false);
            }
        };

        socket.addEventListener('message', handleResponse);
        socket.send(JSON.stringify(mockRequest));

        console.log('Sent test employee request:', mockRequest);
    };

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
            <h2>🧪 Test Google Signup Backend</h2>
            <p>This tests the Google signup functionality without requiring Google OAuth setup.</p>
            
            <div style={{ marginBottom: '20px' }}>
                <button 
                    onClick={testManagerSignup}
                    disabled={isLoading}
                    style={{
                        padding: '10px 20px',
                        marginRight: '10px',
                        backgroundColor: '#4285f4',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isLoading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {isLoading ? 'Testing...' : 'Test Manager Signup'}
                </button>
                
                <button 
                    onClick={testEmployeeSignup}
                    disabled={isLoading}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#34a853',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isLoading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {isLoading ? 'Testing...' : 'Test Employee Signup'}
                </button>
            </div>

            <div style={{
                padding: '15px',
                backgroundColor: '#f5f5f5',
                borderRadius: '5px',
                minHeight: '100px',
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace'
            }}>
                {result || 'Click a button to test the signup functionality...'}
            </div>

            <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
                <strong>WebSocket Status:</strong> {socket?.readyState === WebSocket.OPEN ? '✅ Connected' : '❌ Disconnected'}
            </div>
        </div>
    );
};

export default TestGoogleSignup;
