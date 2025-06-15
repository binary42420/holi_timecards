import EmployeeShiftItem from "./EmployeeShiftItem";
import '../../css/EmployeeShifts.css';

function EmployeeShifts({employees = []}) {
    return (
        <div className="employee-requests">
            <h2>Employee requests</h2>

            <div className="shift-list">
                {employees.map(emp => (
                    <EmployeeShiftItem
                        key={emp.name} // Added key prop for list items
                        name={emp.name}
                        request={emp.request_content}
                    />
                ))}
            </div>
        </div>
    );
}

export default EmployeeShifts;
