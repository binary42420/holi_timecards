#!/usr/bin/env python3
"""
Redis Health Check and Monitoring for EasyShifts
Provides comprehensive monitoring of Redis performance, sessions, and cache health
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.production')

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.redis_config import redis_config, session_manager, cache_manager
from cache.redis_cache import cache_metrics, smart_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisHealthMonitor:
    """Comprehensive Redis health monitoring"""
    
    def __init__(self):
        self.redis_client = None
        self.health_status = {
            'overall': 'unknown',
            'connection': 'unknown',
            'memory': 'unknown',
            'performance': 'unknown',
            'sessions': 'unknown',
            'cache': 'unknown'
        }
    
    def check_connection(self) -> Dict:
        """Check Redis connection health"""
        try:
            self.redis_client = redis_config.get_sync_connection()
            
            # Test basic connectivity
            start_time = time.time()
            ping_result = self.redis_client.ping()
            ping_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            if ping_result:
                status = 'healthy' if ping_time < 100 else 'slow'
                self.health_status['connection'] = status
                
                return {
                    'status': status,
                    'ping_time_ms': round(ping_time, 2),
                    'connected': True,
                    'message': f"Connection successful (ping: {ping_time:.2f}ms)"
                }
            else:
                self.health_status['connection'] = 'unhealthy'
                return {
                    'status': 'unhealthy',
                    'connected': False,
                    'message': "Ping failed"
                }
                
        except Exception as e:
            self.health_status['connection'] = 'unhealthy'
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e),
                'message': f"Connection failed: {e}"
            }
    
    def check_memory_usage(self) -> Dict:
        """Check Redis memory usage"""
        try:
            if not self.redis_client:
                return {'status': 'unknown', 'message': 'No Redis connection'}
            
            info = self.redis_client.info('memory')
            
            used_memory = info.get('used_memory', 0)
            used_memory_human = info.get('used_memory_human', 'Unknown')
            max_memory = info.get('maxmemory', 0)
            
            # Calculate memory usage percentage
            if max_memory > 0:
                memory_usage_percent = (used_memory / max_memory) * 100
            else:
                memory_usage_percent = 0
            
            # Determine status based on usage
            if memory_usage_percent < 70:
                status = 'healthy'
            elif memory_usage_percent < 85:
                status = 'warning'
            else:
                status = 'critical'
            
            self.health_status['memory'] = status
            
            return {
                'status': status,
                'used_memory': used_memory,
                'used_memory_human': used_memory_human,
                'max_memory': max_memory,
                'usage_percent': round(memory_usage_percent, 2),
                'message': f"Memory usage: {used_memory_human} ({memory_usage_percent:.1f}%)"
            }
            
        except Exception as e:
            self.health_status['memory'] = 'unknown'
            return {
                'status': 'unknown',
                'error': str(e),
                'message': f"Memory check failed: {e}"
            }
    
    def check_performance_metrics(self) -> Dict:
        """Check Redis performance metrics"""
        try:
            if not self.redis_client:
                return {'status': 'unknown', 'message': 'No Redis connection'}
            
            info = self.redis_client.info('stats')
            
            total_commands = info.get('total_commands_processed', 0)
            total_connections = info.get('total_connections_received', 0)
            connected_clients = info.get('connected_clients', 0)
            ops_per_sec = info.get('instantaneous_ops_per_sec', 0)
            
            # Check for performance issues
            if ops_per_sec > 1000:
                status = 'high_load'
            elif connected_clients > 50:
                status = 'warning'
            else:
                status = 'healthy'
            
            self.health_status['performance'] = status
            
            return {
                'status': status,
                'total_commands': total_commands,
                'total_connections': total_connections,
                'connected_clients': connected_clients,
                'ops_per_sec': ops_per_sec,
                'message': f"Performance: {ops_per_sec} ops/sec, {connected_clients} clients"
            }
            
        except Exception as e:
            self.health_status['performance'] = 'unknown'
            return {
                'status': 'unknown',
                'error': str(e),
                'message': f"Performance check failed: {e}"
            }
    
    def check_session_health(self) -> Dict:
        """Check session management health"""
        try:
            if not self.redis_client:
                return {'status': 'unknown', 'message': 'No Redis connection'}
            
            # Count active sessions
            session_pattern = f"{redis_config.session_prefix}*"
            session_keys = list(self.redis_client.scan_iter(match=session_pattern))
            active_sessions = len(session_keys)
            
            # Check for expired sessions
            expired_sessions = 0
            valid_sessions = 0
            
            for key in session_keys[:10]:  # Sample first 10 sessions
                try:
                    session_data = self.redis_client.get(key)
                    if session_data:
                        data = json.loads(session_data)
                        created_at = datetime.fromisoformat(data.get('created_at', ''))
                        if datetime.utcnow() - created_at > timedelta(seconds=redis_config.session_timeout):
                            expired_sessions += 1
                        else:
                            valid_sessions += 1
                except Exception:
                    expired_sessions += 1
            
            # Determine status
            if active_sessions == 0:
                status = 'no_sessions'
            elif expired_sessions > valid_sessions:
                status = 'cleanup_needed'
            else:
                status = 'healthy'
            
            self.health_status['sessions'] = status
            
            return {
                'status': status,
                'active_sessions': active_sessions,
                'sampled_valid': valid_sessions,
                'sampled_expired': expired_sessions,
                'message': f"Sessions: {active_sessions} active"
            }
            
        except Exception as e:
            self.health_status['sessions'] = 'unknown'
            return {
                'status': 'unknown',
                'error': str(e),
                'message': f"Session check failed: {e}"
            }
    
    def check_cache_health(self) -> Dict:
        """Check cache performance and health"""
        try:
            if not self.redis_client:
                return {'status': 'unknown', 'message': 'No Redis connection'}
            
            # Count cache entries
            cache_pattern = f"{redis_config.cache_prefix}*"
            cache_keys = list(self.redis_client.scan_iter(match=cache_pattern))
            cache_entries = len(cache_keys)
            
            # Get cache metrics
            metrics = cache_metrics.get_metrics()
            
            total_hits = sum(cache_type.get('hits', 0) for cache_type in metrics.values())
            total_misses = sum(cache_type.get('misses', 0) for cache_type in metrics.values())
            
            if total_hits + total_misses > 0:
                hit_ratio = total_hits / (total_hits + total_misses)
            else:
                hit_ratio = 0
            
            # Determine status based on hit ratio
            if hit_ratio > 0.8:
                status = 'excellent'
            elif hit_ratio > 0.6:
                status = 'good'
            elif hit_ratio > 0.4:
                status = 'fair'
            else:
                status = 'poor'
            
            self.health_status['cache'] = status
            
            return {
                'status': status,
                'cache_entries': cache_entries,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_ratio': round(hit_ratio, 3),
                'message': f"Cache: {cache_entries} entries, {hit_ratio:.1%} hit ratio"
            }
            
        except Exception as e:
            self.health_status['cache'] = 'unknown'
            return {
                'status': 'unknown',
                'error': str(e),
                'message': f"Cache check failed: {e}"
            }
    
    def run_comprehensive_check(self) -> Dict:
        """Run all health checks and return comprehensive report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'unknown',
            'checks': {}
        }
        
        # Run all checks
        checks = {
            'connection': self.check_connection,
            'memory': self.check_memory_usage,
            'performance': self.check_performance_metrics,
            'sessions': self.check_session_health,
            'cache': self.check_cache_health
        }
        
        for check_name, check_func in checks.items():
            try:
                report['checks'][check_name] = check_func()
            except Exception as e:
                report['checks'][check_name] = {
                    'status': 'error',
                    'error': str(e),
                    'message': f"Check failed: {e}"
                }
        
        # Determine overall status
        statuses = [check.get('status', 'unknown') for check in report['checks'].values()]
        
        if 'unhealthy' in statuses or 'critical' in statuses or 'error' in statuses:
            overall_status = 'unhealthy'
        elif 'warning' in statuses or 'slow' in statuses:
            overall_status = 'warning'
        elif all(status in ['healthy', 'excellent', 'good', 'no_sessions'] for status in statuses):
            overall_status = 'healthy'
        else:
            overall_status = 'unknown'
        
        report['overall_status'] = overall_status
        self.health_status['overall'] = overall_status
        
        return report
    
    def print_health_report(self, report: Dict):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("REDIS HEALTH CHECK REPORT")
        print("="*60)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {report['overall_status'].upper()}")
        print("-"*60)
        
        for check_name, check_result in report['checks'].items():
            status = check_result.get('status', 'unknown').upper()
            message = check_result.get('message', 'No message')
            
            # Add status emoji
            status_emoji = {
                'HEALTHY': '✅',
                'EXCELLENT': '🌟',
                'GOOD': '✅',
                'WARNING': '⚠️',
                'SLOW': '⚠️',
                'POOR': '⚠️',
                'CRITICAL': '❌',
                'UNHEALTHY': '❌',
                'ERROR': '❌',
                'UNKNOWN': '❓',
                'NO_SESSIONS': 'ℹ️',
                'CLEANUP_NEEDED': '🧹',
                'HIGH_LOAD': '🔥',
                'FAIR': '⚠️'
            }
            
            emoji = status_emoji.get(status, '❓')
            print(f"{check_name.title()}: {emoji} {status}")
            print(f"  {message}")
            
            if 'error' in check_result:
                print(f"  Error: {check_result['error']}")
            
            print()
        
        print("="*60)

def main():
    """Main health check function"""
    print("EasyShifts Redis Health Check")
    print("=" * 30)
    
    monitor = RedisHealthMonitor()
    report = monitor.run_comprehensive_check()
    monitor.print_health_report(report)
    
    # Return appropriate exit code
    overall_status = report['overall_status']
    if overall_status == 'healthy':
        return 0
    elif overall_status == 'warning':
        return 1
    else:
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
