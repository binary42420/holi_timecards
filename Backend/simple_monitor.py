#!/usr/bin/env python3
"""
Simple Connection Pool Monitoring for EasyShifts Backend
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

def load_environment():
    """Load environment variables"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def monitor_database_connections():
    """Monitor database connection pool"""
    print("🗄️  Database Connection Pool Status")
    print("-" * 40)
    
    try:
        from main import get_db_session, engine
        
        # Get connection pool info
        pool = engine.pool
        
        pool_size = pool.size()
        checked_out = pool.checkedout()
        overflow = pool.overflow()
        checked_in = pool.checkedin()
        
        print(f"   Pool Size: {pool_size}")
        print(f"   Checked Out: {checked_out}")
        print(f"   Overflow: {overflow}")
        print(f"   Checked In: {checked_in}")
        
        # Calculate utilization
        total_connections = pool_size + overflow
        utilization = (checked_out / total_connections * 100) if total_connections > 0 else 0
        
        print(f"   Utilization: {utilization:.1f}%")
        
        # Status indicator
        if utilization > 80:
            print("   Status: ⚠️  HIGH USAGE")
        elif utilization > 60:
            print("   Status: 🟡 MODERATE USAGE")
        else:
            print("   Status: ✅ NORMAL")
        
        return {
            'pool_size': pool_size,
            'checked_out': checked_out,
            'overflow': overflow,
            'checked_in': checked_in,
            'utilization': utilization,
            'status': 'high' if utilization > 80 else 'moderate' if utilization > 60 else 'normal'
        }
        
    except Exception as e:
        print(f"   ❌ Error monitoring database: {e}")
        return {'error': str(e)}

def monitor_redis_connections():
    """Monitor Redis connection pool"""
    print("\n🔴 Redis Connection Pool Status")
    print("-" * 40)
    
    try:
        from config.redis_config import redis_config
        
        # Get Redis client
        redis_client = redis_config.get_sync_connection()
        
        # Test connection
        ping_result = redis_client.ping()
        print(f"   Connection: {'✅ ACTIVE' if ping_result else '❌ FAILED'}")
        
        # Get Redis info
        info = redis_client.info()
        
        connected_clients = info.get('connected_clients', 'N/A')
        used_memory = info.get('used_memory_human', 'N/A')
        total_commands = info.get('total_commands_processed', 'N/A')
        
        print(f"   Connected Clients: {connected_clients}")
        print(f"   Used Memory: {used_memory}")
        print(f"   Total Commands: {total_commands}")
        
        # Calculate hit ratio
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total_requests = hits + misses
        hit_ratio = (hits / total_requests * 100) if total_requests > 0 else 100
        
        print(f"   Hit Ratio: {hit_ratio:.1f}%")
        
        # Status indicator
        if hit_ratio > 90:
            print("   Status: ✅ EXCELLENT")
        elif hit_ratio > 70:
            print("   Status: 🟡 GOOD")
        else:
            print("   Status: ⚠️  NEEDS OPTIMIZATION")
        
        return {
            'ping': ping_result,
            'connected_clients': connected_clients,
            'used_memory': used_memory,
            'total_commands': total_commands,
            'hit_ratio': hit_ratio,
            'status': 'excellent' if hit_ratio > 90 else 'good' if hit_ratio > 70 else 'needs_optimization'
        }
        
    except Exception as e:
        print(f"   ❌ Error monitoring Redis: {e}")
        return {'error': str(e)}

def test_application_health():
    """Test application health"""
    print("\n🏥 Application Health Tests")
    print("-" * 40)
    
    health_results = {}
    
    try:
        # Test login functionality
        print("   Testing login functionality...")
        from handlers.login import handle_login
        
        login_data = {'username': 'admin', 'password': 'Hdfatboy1!'}
        response, user_session = handle_login(login_data, '127.0.0.1')
        
        login_success = response.get('user_exists', False)
        print(f"   Login Test: {'✅ PASS' if login_success else '❌ FAIL'}")
        health_results['login_test'] = login_success
        
    except Exception as e:
        print(f"   Login Test: ❌ ERROR - {e}")
        health_results['login_test'] = False
    
    try:
        # Test database query
        print("   Testing database query...")
        from main import get_db_session
        from db.controllers.users_controller import UsersController
        
        with get_db_session() as session:
            users_controller = UsersController(session)
            users = users_controller.get_all_entities()
            user_count = len(users)
        
        print(f"   Database Query: ✅ PASS ({user_count} users)")
        health_results['database_test'] = True
        health_results['user_count'] = user_count
        
    except Exception as e:
        print(f"   Database Query: ❌ ERROR - {e}")
        health_results['database_test'] = False
    
    try:
        # Test Redis session
        print("   Testing Redis session...")
        from config.redis_config import session_manager
        
        test_session_id = f"health_check_{int(time.time())}"
        test_data = {'test': True, 'timestamp': datetime.now().isoformat()}
        
        session_created = session_manager.create_session(test_session_id, test_data)
        if session_created:
            session_retrieved = session_manager.get_session(test_session_id)
            session_deleted = session_manager.delete_session(test_session_id)
            redis_success = session_retrieved is not None
        else:
            redis_success = False
        
        print(f"   Redis Session: {'✅ PASS' if redis_success else '❌ FAIL'}")
        health_results['redis_test'] = redis_success
        
    except Exception as e:
        print(f"   Redis Session: ❌ ERROR - {e}")
        health_results['redis_test'] = False
    
    # Overall health
    overall_health = all([
        health_results.get('login_test', False),
        health_results.get('database_test', False),
        health_results.get('redis_test', False)
    ])
    
    print(f"   Overall Health: {'✅ HEALTHY' if overall_health else '❌ ISSUES DETECTED'}")
    health_results['overall_health'] = overall_health
    
    return health_results

def test_database_session_fixes():
    """Test that database session fixes are working"""
    print("\n🔧 Database Session Fix Validation")
    print("-" * 40)
    
    try:
        # Test shifts controller (the one you highlighted)
        print("   Testing shifts controller...")
        from db.controllers.shifts_controller import convert_shift_for_client
        print("   ✅ Shifts controller imports successfully")
        
        # Test that we can create multiple sessions without issues
        print("   Testing multiple database sessions...")
        from main import get_db_session
        from db.controllers.users_controller import UsersController
        
        session_count = 0
        for i in range(5):
            with get_db_session() as session:
                users_controller = UsersController(session)
                users = users_controller.get_all_entities()
                session_count += 1
        
        print(f"   ✅ Successfully created {session_count} database sessions")
        
        # Test concurrent session usage
        print("   Testing session context management...")
        with get_db_session() as session1:
            with get_db_session() as session2:
                controller1 = UsersController(session1)
                controller2 = UsersController(session2)
                users1 = controller1.get_all_entities()
                users2 = controller2.get_all_entities()
        
        print("   ✅ Concurrent sessions working correctly")
        
        return {
            'shifts_controller_import': True,
            'multiple_sessions': True,
            'concurrent_sessions': True,
            'session_count_tested': session_count
        }
        
    except Exception as e:
        print(f"   ❌ Database session test failed: {e}")
        return {'error': str(e)}

def generate_monitoring_report():
    """Generate a comprehensive monitoring report"""
    print("📊 EasyShifts Connection Pool & Performance Monitor")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Collect all monitoring data
    db_data = monitor_database_connections()
    redis_data = monitor_redis_connections()
    health_data = test_application_health()
    session_data = test_database_session_fixes()
    
    # Overall status
    print("\n🎯 Overall Status Summary")
    print("-" * 40)
    
    issues = []
    successes = []
    
    # Check database
    if db_data.get('utilization', 0) > 80:
        issues.append("High database connection usage")
    else:
        successes.append("Database connection pool healthy")
    
    # Check Redis
    if not redis_data.get('ping', False):
        issues.append("Redis connection failed")
    elif redis_data.get('hit_ratio', 100) < 70:
        issues.append("Low Redis cache hit ratio")
    else:
        successes.append("Redis connection healthy")
    
    # Check application health
    if not health_data.get('overall_health', False):
        issues.append("Application health check failed")
    else:
        successes.append("Application health checks passed")
    
    # Check database session fixes
    if session_data.get('error'):
        issues.append("Database session fixes not working")
    else:
        successes.append("Database session fixes working correctly")
    
    # Display results
    if successes:
        print("   ✅ Successes:")
        for success in successes:
            print(f"      • {success}")
    
    if issues:
        print("   ⚠️  Issues Found:")
        for issue in issues:
            print(f"      • {issue}")
    else:
        print("   🎉 All systems operating normally!")
    
    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'database': db_data,
        'redis': redis_data,
        'health': health_data,
        'session_fixes': session_data,
        'issues': issues,
        'successes': successes
    }
    
    return summary

def main():
    """Main monitoring function"""
    # Load environment
    load_environment()
    
    # Generate report
    summary = generate_monitoring_report()
    
    # Save to file
    with open('monitoring_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Report saved to: monitoring_summary.json")

if __name__ == "__main__":
    main()
