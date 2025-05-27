#!/usr/bin/env python3
"""
Example usage of the TRMNL controller for programmatic device control.

This demonstrates how to use the create_image() function and schedule
automatic updates to your TRMNL device.
"""

import time
from datetime import datetime
from app.trmnl_control import create_image, schedule_updates, get_controller


def main():
    """Main example demonstrating TRMNL control."""
    
    print("TRMNL Controller Example")
    print("=" * 40)
    
    # Example 1: Simple text display
    print("1. Creating simple text display...")
    create_image("Hello from Python!\n\nThis is your TRMNL device\nrunning a custom server.")
    
    # Example 2: System status display
    print("2. Creating system status display...")
    status_content = f"""
System Dashboard

Date: {datetime.now().strftime('%Y-%m-%d')}
Time: {datetime.now().strftime('%H:%M:%S')}

Server Status: Online
Database: Connected
Images: Generated

Last Update: {datetime.now().strftime('%H:%M:%S')}

Ready for device connection!
"""
    create_image(status_content)
    
    # Example 3: Custom filename
    print("3. Creating image with custom filename...")
    create_image(
        "Custom filename example\n\nThis image has a specific name.",
        filename="my-custom-display"
    )
    
    # Example 4: Scheduled updates (commented out for demo)
    print("4. Setting up scheduled updates...")
    
    def time_update():
        """Function to generate time-based content."""
        return f"""
Current Time Display

{datetime.now().strftime('%A')}
{datetime.now().strftime('%B %d, %Y')}
{datetime.now().strftime('%I:%M:%S %p')}

Auto-refreshed every 5 minutes
Server: Custom FastAPI TRMNL
"""
    
    # Schedule updates every 5 minutes
    # schedule_updates(time_update, interval_minutes=5)
    
    print("\nExample completed!")
    print("Check the static/images/ directory for generated images.")
    print("\nTo run the server:")
    print("  python -m uvicorn app.main:app --reload")
    print("\nTo schedule automatic updates:")
    print("  Uncomment the schedule_updates line and run this script in background")


def demo_weather_display():
    """Example of a weather-like display."""
    weather_content = f"""
Weather Dashboard

Today: Monday, January 15
Temperature: 72°F
Condition: Sunny
Humidity: 45%
Wind: 5 mph SW

Tomorrow: Partly Cloudy
High: 68°F, Low: 52°F

Last updated: {datetime.now().strftime('%I:%M %p')}
"""
    create_image(weather_content, filename="weather-demo")
    print("Weather demo display created!")


def demo_todo_list():
    """Example of a todo list display."""
    todo_content = """
Today's Tasks

✓ Review server logs
✓ Update documentation
▢ Deploy new features
▢ Test device connection
▢ Schedule maintenance

Daily standup: 10:00 AM
Sprint review: 3:00 PM

Progress: 2/5 tasks complete
"""
    create_image(todo_content, filename="todo-demo")
    print("Todo list demo display created!")


def demo_server_monitoring():
    """Example of server monitoring display."""
    monitoring_content = f"""
Server Monitoring

Status: OPERATIONAL
Uptime: 99.9%

CPU Usage: 45%
Memory: 2.1GB / 8GB (26%)
Disk: 250GB / 500GB (50%)

Active Connections: 12
Requests/min: 145
Error Rate: 0.01%

Last Check: {datetime.now().strftime('%H:%M:%S')}
Next Check: {(datetime.now()).strftime('%H:%M:%S')}
"""
    create_image(monitoring_content, filename="monitoring-demo")
    print("Server monitoring demo display created!")


if __name__ == "__main__":
    # Run main example
    main()
    
    print("\nAdditional Examples:")
    print("=" * 40)
    
    # Run additional demos
    demo_weather_display()
    demo_todo_list()
    demo_server_monitoring()
    
    print("\nAll examples completed!")
    print(f"Generated images at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")