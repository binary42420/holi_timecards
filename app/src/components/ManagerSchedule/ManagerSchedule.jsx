import React, { useEffect, useState, useCallback } from 'react';
import EmployeeShifts from './EmployeeShifts';
import ScheduleBoard from "./ScheduleBoard";
import '../../css/ManagerSchedule.css';

function ManagerSchedule({ socket }) {
    const [loading, setLoading] = useState(true);
    const [employeesRequests, setEmployeesRequests] = useState([]);
    const [allWorkers, setAllWorkers] = useState([]);
    const [preferences, setPreferences] = useState({
        number_of_shifts_per_day: 2,
        closed_days: []
    });
    const [startDate, setStartDate] = useState(null);
    const [assignedShifts, setAssignedShifts] = useState([]); 
    
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isPublished, setIsPublished] = useState(false);
    const [boardContent, setBoardContent] = useState({});

    const sendGetEmployeesRequestsData = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ request_id: 91 }));
        }
    }, [socket]);

    const sendGetAllWorkers = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ request_id: 93 }));
        }
    }, [socket]);

    const sendGetPreferences = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ request_id: 95 }));
        }
    }, [socket]);

    const sendGetStartDate = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ request_id: 97 }));
        }
    }, [socket]);

    const sendGetAssignedShifts = useCallback((currentStartDate) => {
        if (socket && socket.readyState === WebSocket.OPEN && currentStartDate) {
            socket.send(JSON.stringify({
                request_id: 98,
                data: { start_date: currentStartDate.toISOString() } 
            }));
        }
    }, [socket]);

    const sendGetBoardStatus = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ request_id: 86 })); 
        }
    }, [socket]);
    
    const fetchData = useCallback(async () => {
        setLoading(true);
        setErrorMessage('');
        setSuccessMessage('');
        sendGetEmployeesRequestsData();
        sendGetAllWorkers();
        sendGetPreferences();
        sendGetStartDate(); 
        sendGetBoardStatus();
    }, [socket, sendGetEmployeesRequestsData, sendGetAllWorkers, sendGetPreferences, sendGetStartDate, sendGetBoardStatus]);


    useEffect(() => {
        if (socket && startDate) {
            sendGetAssignedShifts(startDate);
        }
    }, [socket, startDate, sendGetAssignedShifts]);


    useEffect(() => {
        if (!socket) return;

        const handleMessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                console.log("ManagerSchedule received:", response);

                if (response.success === false && response.error) {
                    setErrorMessage(response.error);
                } else {
                    setErrorMessage(''); 
                }

                switch (response.request_id) {
                    case 91: 
                        if (response.success) setEmployeesRequests(response.data || []);
                        else setErrorMessage(response.error || 'Failed to get employee requests.');
                        break;
                    case 93: 
                        if (response.success) setAllWorkers(response.data || []);
                        else setErrorMessage(response.error || 'Failed to get workers.');
                        break;
                    case 95: 
                        if (response.success) setPreferences(response.data || { number_of_shifts_per_day: 2, closed_days: [] });
                        else setErrorMessage(response.error || 'Failed to get preferences.');
                        break;
                    case 97: 
                        if (response.success && response.data) setStartDate(new Date(response.data));
                        else setErrorMessage(response.error || 'Failed to get start date.');
                        break;
                    case 98: 
                        if (response.success) {
                            setAssignedShifts(response.data || []);
                        } else {
                             setErrorMessage(response.error || 'Failed to get assigned shifts.');
                        }
                        break;
                    case 86: 
                        if (response.success && typeof response.data?.is_published === 'boolean') {
                            setIsPublished(response.data.is_published);
                            if (response.data.content) {
                                setBoardContent(response.data.content);
                            }
                        } else {
                            setErrorMessage(response.error || 'Failed to get board status.');
                        }
                        break;
                    case 81: 
                    case 82: 
                    case 83: 
                    case 84: 
                    case 85: 
                        if (response.success) {
                            setSuccessMessage(response.message || response.data?.message || 'Operation successful.');
                            if (response.data && typeof response.data.is_published === 'boolean') {
                                setIsPublished(response.data.is_published);
                            }
                            fetchData(); 
                        } else {
                            setErrorMessage(response.error || 'Board operation failed.');
                        }
                        break;
                    default:
                        break;
                }

                // Check if we have all required data to stop loading
                if (preferences && startDate && allWorkers.length >= 0 && assignedShifts.length >= 0) {
                    setLoading(false);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message in ManagerSchedule:', error);
                setErrorMessage('Error processing server response.');
                setLoading(false);
            }
        };

        socket.addEventListener('message', handleMessage);
        if (socket.readyState === WebSocket.OPEN) {
            fetchData();
        }

        return () => {
            socket.removeEventListener('message', handleMessage);
        };
    }, [socket, fetchData]); 

    const handleBoardAction = (requestId, actionData = null) => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setErrorMessage('WebSocket is not connected.');
            return;
        }
        setLoading(true);
        setErrorMessage('');
        setSuccessMessage('');
        const request = { request_id: requestId };
        if (actionData) {
            request.data = actionData;
        }
        socket.send(JSON.stringify(request));
    };
    
    const handleCreateNewBoard = () => handleBoardAction(81);
    
    const handleSaveBoard = () => {
        if (!startDate) {
            setErrorMessage("Start date is not available to save the board.");
            return;
        }

        const newBoardContent = {};
        const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const shiftPartsOrder = ['morning', 'noon', 'evening']; 

        daysOfWeek.forEach(day => {
            newBoardContent[day] = {};
            shiftPartsOrder.forEach(part => {
                newBoardContent[day][part] = []; 
            });
        });

        (assignedShifts || []).forEach(workerEntry => {
            const workerName = workerEntry.name;
            (workerEntry.shifts || []).forEach(shift => {
                try {
                    const shiftDateObj = new Date(shift.shiftDate);
                    const dayName = shiftDateObj.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
                    const shiftPart = shift.shiftPart; 

                    if (newBoardContent[dayName] && newBoardContent[dayName][shiftPart]) {
                        if (!newBoardContent[dayName][shiftPart].includes(workerName)) {
                             newBoardContent[dayName][shiftPart].push(workerName);
                        }
                    }
                } catch (e) {
                    console.error("Error processing shift for saving board content:", shift, e);
                }
            });
        });
        
        handleBoardAction(82, {
            week_start_date: startDate.toISOString().split('T')[0], 
            content: newBoardContent, 
        });
    };

    const handleResetBoard = () => handleBoardAction(83);
    const handlePublishBoard = () => handleBoardAction(84);
    const handleUnpublishBoard = () => handleBoardAction(85);

    return (
        <div className="manager-schedule">
            {successMessage && <p style={{ color: 'green', border: '1px solid green', padding: '10px' }}>{successMessage}</p>}
            {errorMessage && <p style={{ color: 'red', border: '1px solid red', padding: '10px' }}>Error: {errorMessage}</p>}

            {loading ? (
                <div>Loading schedule data...</div>
            ) : (
                <div className="board-and-requests">
                    <EmployeeShifts employees={employeesRequests} className="EmployeeShifts" />
                    {preferences && startDate ? (
                        <ScheduleBoard
                            partsCount={preferences.number_of_shifts_per_day}
                            closedDays={preferences.closed_days}
                            startDate={startDate}
                            allWorkers={allWorkers} 
                            assignedShifts={assignedShifts} 
                            className="ScheduleBoard"
                        />
                    ) : (
                        <div>Loading preferences or start date...</div>
                    )}
                </div>
            )}

            <div className="buttons">
                <button onClick={handleCreateNewBoard} disabled={loading}>Create New Board</button>
                <button onClick={handleSaveBoard} disabled={loading || isPublished}>Save Current Board</button>
                <button onClick={handleResetBoard} disabled={loading || isPublished}>Reset Current Board</button>
                {isPublished ? (
                    <button onClick={handleUnpublishBoard} disabled={loading}>Unpublish Board</button>
                ) : (
                    <button onClick={handlePublishBoard} disabled={loading}>Publish Board</button>
                )}
            </div>
        </div>
    );
}

export default ManagerSchedule;