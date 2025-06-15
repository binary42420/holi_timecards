#!/usr/bin/env node

/**
 * Google OAuth Configuration Checker for EasyShifts
 * Run this script to verify your Google OAuth setup
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 EasyShifts Google OAuth Configuration Checker');
console.log('=' * 50);

// Check if we're in the right directory
const currentDir = process.cwd();
const isInRoot = fs.existsSync(path.join(currentDir, 'app')) && fs.existsSync(path.join(currentDir, 'Backend'));
const isInApp = fs.existsSync(path.join(currentDir, 'src')) && fs.existsSync(path.join(currentDir, 'package.json'));

if (!isInRoot && !isInApp) {
    console.log('❌ Please run this script from the EasyShifts root directory or app directory');
    process.exit(1);
}

const appDir = isInRoot ? path.join(currentDir, 'app') : currentDir;
const backendDir = isInRoot ? path.join(currentDir, 'Backend') : path.join(currentDir, '..', 'Backend');

console.log('📁 Checking directories...');
console.log(`   App directory: ${appDir}`);
console.log(`   Backend directory: ${backendDir}`);

// Check frontend .env file
console.log('\n📄 Checking frontend .env file...');
const frontendEnvPath = path.join(appDir, '.env');

if (fs.existsSync(frontendEnvPath)) {
    console.log('✅ Frontend .env file found');
    
    const frontendEnvContent = fs.readFileSync(frontendEnvPath, 'utf8');
    const frontendClientIdMatch = frontendEnvContent.match(/REACT_APP_GOOGLE_CLIENT_ID=(.+)/);
    
    if (frontendClientIdMatch) {
        const clientId = frontendClientIdMatch[1].trim();
        console.log(`✅ Frontend Google Client ID found: ${clientId.substring(0, 20)}...`);
        
        if (clientId.includes('.apps.googleusercontent.com')) {
            console.log('✅ Client ID format looks correct');
        } else {
            console.log('⚠️  Client ID format might be incorrect (should end with .apps.googleusercontent.com)');
        }
    } else {
        console.log('❌ REACT_APP_GOOGLE_CLIENT_ID not found in frontend .env');
    }
} else {
    console.log('❌ Frontend .env file not found');
    console.log('   Create app/.env with: REACT_APP_GOOGLE_CLIENT_ID=your_client_id_here');
}

// Check backend .env file
console.log('\n📄 Checking backend .env file...');
const backendEnvPath = path.join(backendDir, '.env');

if (fs.existsSync(backendEnvPath)) {
    console.log('✅ Backend .env file found');
    
    const backendEnvContent = fs.readFileSync(backendEnvPath, 'utf8');
    const backendClientIdMatch = backendEnvContent.match(/GOOGLE_CLIENT_ID=(.+)/);
    
    if (backendClientIdMatch) {
        const clientId = backendClientIdMatch[1].trim();
        console.log(`✅ Backend Google Client ID found: ${clientId.substring(0, 20)}...`);
    } else {
        console.log('❌ GOOGLE_CLIENT_ID not found in backend .env');
    }
} else {
    console.log('❌ Backend .env file not found');
    console.log('   Create Backend/.env with: GOOGLE_CLIENT_ID=your_client_id_here');
}

// Check if Client IDs match
if (fs.existsSync(frontendEnvPath) && fs.existsSync(backendEnvPath)) {
    const frontendContent = fs.readFileSync(frontendEnvPath, 'utf8');
    const backendContent = fs.readFileSync(backendEnvPath, 'utf8');
    
    const frontendId = frontendContent.match(/REACT_APP_GOOGLE_CLIENT_ID=(.+)/)?.[1]?.trim();
    const backendId = backendContent.match(/GOOGLE_CLIENT_ID=(.+)/)?.[1]?.trim();
    
    if (frontendId && backendId && frontendId === backendId) {
        console.log('✅ Frontend and backend Client IDs match');
    } else if (frontendId && backendId) {
        console.log('⚠️  Frontend and backend Client IDs do not match');
        console.log(`   Frontend: ${frontendId.substring(0, 20)}...`);
        console.log(`   Backend:  ${backendId.substring(0, 20)}...`);
    }
}

// Check package.json dependencies
console.log('\n📦 Checking dependencies...');
const packageJsonPath = path.join(appDir, 'package.json');

if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    if (dependencies['@react-oauth/google']) {
        console.log('✅ @react-oauth/google dependency found');
    } else {
        console.log('❌ @react-oauth/google dependency missing');
        console.log('   Run: npm install @react-oauth/google');
    }
} else {
    console.log('❌ package.json not found in app directory');
}

// Check backend requirements
console.log('\n🐍 Checking backend dependencies...');
const requirementsPath = path.join(backendDir, 'requirements.txt');

if (fs.existsSync(requirementsPath)) {
    const requirements = fs.readFileSync(requirementsPath, 'utf8');
    
    const googleDeps = ['google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'python-dotenv'];
    const missingDeps = googleDeps.filter(dep => !requirements.includes(dep));
    
    if (missingDeps.length === 0) {
        console.log('✅ All required Google OAuth dependencies found in requirements.txt');
    } else {
        console.log('⚠️  Some Google OAuth dependencies might be missing:');
        missingDeps.forEach(dep => console.log(`   - ${dep}`));
    }
} else {
    console.log('❌ requirements.txt not found in Backend directory');
}

// Summary and next steps
console.log('\n📋 Summary and Next Steps:');
console.log('=' * 50);

console.log('\n🔧 To fix Google OAuth issues:');
console.log('1. Go to Google Cloud Console: https://console.cloud.google.com/');
console.log('2. Navigate to APIs & Services → Credentials');
console.log('3. Edit your OAuth 2.0 Client ID');
console.log('4. Add these Authorized JavaScript origins:');
console.log('   - http://localhost:3000');
console.log('   - http://127.0.0.1:3000');
console.log('   - https://localhost:3000');
console.log('5. Add these Authorized redirect URIs:');
console.log('   - http://localhost:3000');
console.log('   - http://localhost:3000/signup');
console.log('   - http://localhost:3000/login');
console.log('6. Save changes and restart your development servers');

console.log('\n🚀 To test:');
console.log('1. Start backend: cd Backend && python Server.py');
console.log('2. Start frontend: cd app && npm start');
console.log('3. Navigate to http://localhost:3000/signup');
console.log('4. Click "Sign up with Google"');

console.log('\n📚 For detailed troubleshooting, see:');
console.log('   - GOOGLE_OAUTH_TROUBLESHOOTING.md');
console.log('   - http://localhost:3000/google-oauth-setup');

console.log('\n✨ Happy coding!');
