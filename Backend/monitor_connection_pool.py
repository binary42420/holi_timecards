#!/usr/bin/env python3
"""
Connection Pool Monitoring for EasyShifts Backend
Monitors database and Redis connection usage
"""

import os
import time
import json
import psutil
from datetime import datetime, timedelta
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
        
        print(f"   Pool Size: {pool.size()}")
        print(f"   Checked Out: {pool.checkedout()}")
        print(f"   Overflow: {pool.overflow()}")
        print(f"   Checked In: {pool.checkedin()}")
        
        # Calculate utilization
        total_connections = pool.size() + pool.overflow()
        used_connections = pool.checkedout()
        utilization = (used_connections / total_connections * 100) if total_connections > 0 else 0
        
        print(f"   Utilization: {utilization:.1f}%")
        
        # Status indicator
        if utilization > 80:
            print("   Status: ⚠️  HIGH USAGE")
        elif utilization > 60:
            print("   Status: 🟡 MODERATE USAGE")
        else:
            print("   Status: ✅ NORMAL")
        
        return {
            'pool_size': pool.size(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'checked_in': pool.checkedin(),
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
        
        # Get Redis info
        info = redis_client.info()
        
        print(f"   Connected Clients: {info.get('connected_clients', 'N/A')}")
        print(f"   Used Memory: {info.get('used_memory_human', 'N/A')}")
        print(f"   Max Memory: {info.get('maxmemory_human', 'N/A') or 'Unlimited'}")
        print(f"   Total Commands: {info.get('total_commands_processed', 'N/A')}")
        print(f"   Keyspace Hits: {info.get('keyspace_hits', 'N/A')}")
        print(f"   Keyspace Misses: {info.get('keyspace_misses', 'N/A')}")
        
        # Calculate hit ratio
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total_requests = hits + misses
        hit_ratio = (hits / total_requests * 100) if total_requests > 0 else 0
        
        print(f"   Hit Ratio: {hit_ratio:.1f}%")
        
        # Status indicator
        if hit_ratio > 90:
            print("   Status: ✅ EXCELLENT")
        elif hit_ratio > 70:
            print("   Status: 🟡 GOOD")
        else:
            print("   Status: ⚠️  NEEDS OPTIMIZATION")
        
        return {
            'connected_clients': info.get('connected_clients'),
            'used_memory': info.get('used_memory'),
            'used_memory_human': info.get('used_memory_human'),
            'total_commands': info.get('total_commands_processed'),
            'hit_ratio': hit_ratio,
            'status': 'excellent' if hit_ratio > 90 else 'good' if hit_ratio > 70 else 'needs_optimization'
        }
        
    except Exception as e:
        print(f"   ❌ Error monitoring Redis: {e}")
        return {'error': str(e)}

def monitor_system_resources():
    """Monitor system resources"""
    print("\n💻 System Resources")
    print("-" * 40)
    
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   CPU Usage: {cpu_percent}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        print(f"   Memory Usage: {memory.percent}%")
        print(f"   Available Memory: {memory.available / (1024**3):.1f} GB")
        
        # Disk usage
        disk = psutil.disk_usage('/')
        print(f"   Disk Usage: {disk.percent}%")
        print(f"   Free Disk: {disk.free / (1024**3):.1f} GB")
        
        # Network connections
        connections = psutil.net_connections()
        established = len([c for c in connections if c.status == 'ESTABLISHED'])
        print(f"   Network Connections: {established}")
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3),
            'network_connections': established
        }
        
    except Exception as e:
        print(f"   ❌ Error monitoring system: {e}")
        return {'error': str(e)}

def test_application_health():
    """Test application health endpoints"""
    print("\n🏥 Application Health")
    print("-" * 40)
    
    try:
        # Test login functionality
        from handlers.login import handle_login
        
        login_data = {'username': 'admin', 'password': 'Hdfatboy1!'}
        response, user_session = handle_login(login_data, '127.0.0.1')
        
        login_success = response.get('user_exists', False)
        print(f"   Login Test: {'✅ PASS' if login_success else '❌ FAIL'}")
        
        # Test database query
        from main import get_db_session
        from db.controllers.users_controller import UsersController
        
        with get_db_session() as session:
            users_controller = UsersController(session)
            users = users_controller.get_all_entities()
            user_count = len(users)
        
        print(f"   Database Query: ✅ PASS ({user_count} users)")
        
        # Test Redis session
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
        
        return {
            'login_test': login_success,
            'database_test': True,
            'user_count': user_count,
            'redis_test': redis_success,
            'overall_health': login_success and redis_success
        }
        
    except Exception as e:
        print(f"   ❌ Error testing health: {e}")
        return {'error': str(e)}

def save_monitoring_data(data):
    """Save monitoring data to file"""
    monitoring_file = Path('monitoring_data.json')
    
    # Load existing data
    if monitoring_file.exists():
        with open(monitoring_file, 'r') as f:
            try:
                existing_data = json.load(f)
            except:
                existing_data = []
    else:
        existing_data = []
    
    # Add new data point
    data['timestamp'] = datetime.now().isoformat()
    existing_data.append(data)
    
    # Keep only last 100 data points
    if len(existing_data) > 100:
        existing_data = existing_data[-100:]
    
    # Save data
    with open(monitoring_file, 'w') as f:
        json.dump(existing_data, f, indent=2)

def generate_monitoring_report():
    """Generate a monitoring report"""
    print("📊 EasyShifts Connection Pool & Performance Monitor")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Collect all monitoring data
    db_data = monitor_database_connections()
    redis_data = monitor_redis_connections()
    system_data = monitor_system_resources()
    health_data = test_application_health()
    
    # Combine data
    monitoring_data = {
        'database': db_data,
        'redis': redis_data,
        'system': system_data,
        'health': health_data
    }
    
    # Save data
    save_monitoring_data(monitoring_data)
    
    # Overall status
    print("\n🎯 Overall Status")
    print("-" * 40)
    
    issues = []
    
    if db_data.get('utilization', 0) > 80:
        issues.append("High database connection usage")
    
    if redis_data.get('hit_ratio', 100) < 70:
        issues.append("Low Redis cache hit ratio")
    
    if system_data.get('cpu_percent', 0) > 80:
        issues.append("High CPU usage")
    
    if system_data.get('memory_percent', 0) > 80:
        issues.append("High memory usage")
    
    if not health_data.get('overall_health', False):
        issues.append("Application health check failed")
    
    if issues:
        print("   ⚠️  Issues Found:")
        for issue in issues:
            print(f"      • {issue}")
    else:
        print("   ✅ All systems operating normally")
    
    return monitoring_data

def continuous_monitoring(interval=60):
    """Run continuous monitoring"""
    print("🔄 Starting Continuous Monitoring")
    print(f"   Interval: {interval} seconds")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            generate_monitoring_report()
            print(f"\n⏳ Next check in {interval} seconds...")
            print("=" * 60)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")

def main():
    """Main monitoring function"""
    import sys
    
    # Load environment
    load_environment()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "continuous":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            continuous_monitoring(interval)
        elif sys.argv[1] == "report":
            generate_monitoring_report()
        else:
            print("Usage: python monitor_connection_pool.py [continuous [interval]|report]")
    else:
        generate_monitoring_report()

if __name__ == "__main__":
    main()
