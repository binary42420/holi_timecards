/**
 * Fix user credentials in localStorage to ensure correct admin password
 */

import { logInfo, logDebug } from './utils';

export const fixAdminCredentials = () => {
    try {
        logInfo('fixUserCredentials', 'Fixing admin credentials in localStorage');
        
        // Set correct admin credentials
        const adminUser = {
            username: 'admin',
            password: 'Hdfatboy1!',
            isManager: true,
            isAdmin: true,
            userId: 1,
            email: 'admin@handsonlabor.com'
        };
        
        localStorage.setItem('holi_user', JSON.stringify(adminUser));
        
        logInfo('fixUserCredentials', 'Admin credentials fixed', {
            username: adminUser.username,
            isManager: adminUser.isManager,
            isAdmin: adminUser.isAdmin
        });
        
        return adminUser;
    } catch (error) {
        console.error('Failed to fix admin credentials:', error);
        return null;
    }
};

export const clearAllCredentials = () => {
    try {
        localStorage.removeItem('holi_user');
        sessionStorage.removeItem('holi_session');
        logInfo('fixUserCredentials', 'All credentials cleared');
    } catch (error) {
        console.error('Failed to clear credentials:', error);
    }
};

// Auto-fix credentials on import
if (typeof window !== 'undefined') {
    // Check if we're in a browser environment
    const savedUser = localStorage.getItem('holi_user');
    if (savedUser) {
        try {
            const userData = JSON.parse(savedUser);
            if (userData.username === 'admin' && userData.password !== 'Hdfatboy1!') {
                logDebug('fixUserCredentials', 'Detected incorrect admin password, fixing...');
                fixAdminCredentials();
            }
        } catch (error) {
            logDebug('fixUserCredentials', 'Error checking saved credentials, clearing...');
            clearAllCredentials();
        }
    }
}
