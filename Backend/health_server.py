"""
Simple HTTP health check server for Cloud Run
Runs alongside the WebSocket server
"""

from aiohttp import web
import aiohttp_cors
import asyncio
import json
from datetime import datetime


async def health_check(request):
    """Health check endpoint for Cloud Run"""
    return web.Response(
        text=json.dumps({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "holi-timesheets-backend"
        }),
        content_type='application/json'
    )


async def create_health_app():
    """Create the health check web application"""
    app = web.Application()
    
    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add health check route
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)  # Root path also returns health
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app


async def start_health_server(port=8080):
    """Start the health check server"""
    app = await create_health_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Health check server started on port {port}")
    return runner


if __name__ == "__main__":
    async def main():
        runner = await start_health_server()
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            await runner.cleanup()
    
    asyncio.run(main())
