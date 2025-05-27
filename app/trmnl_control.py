"""
TRMNL Device Control Interface

This module provides a simple Python interface for controlling TRMNL devices.
Use the create_image() function to programmatically update your device display.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import threading
import time
import schedule
from .image_utils import ImageGenerator
from .database import Database


class TRMNLController:
    """
    Main controller class for managing TRMNL devices programmatically.
    """
    
    def __init__(self, db_path: str = "trmnl.db", images_dir: str = "static/images"):
        self.db = Database(db_path)
        self.image_gen = ImageGenerator(images_dir)
        self.scheduled_jobs = []
        self._scheduler_running = False
    
    def create_image(self, content: str = None, device_id: str = None, 
                    filename: str = None, **kwargs) -> str:
        """
        Create an image for display on TRMNL device(s).
        
        Args:
            content: Text content to display on the device
            device_id: Specific device MAC address (if None, creates for all devices)
            filename: Custom filename for the image
            **kwargs: Additional parameters (width, height, etc.)
            
        Returns:
            str: Filename of the created image
            
        Example:
            controller = TRMNLController()
            
            # Create a simple text display
            controller.create_image("Hello World!")
            
            # Create with custom content
            weather_info = '''
            Today's Weather
            
            Temperature: 72°F
            Conditions: Sunny
            Humidity: 45%
            Wind: 5 mph SW
            '''
            controller.create_image(weather_info)
        """
        if content is None:
            content = f"TRMNL Update\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # If device_id specified, add it to the filename
        if device_id and filename:
            filename = f"{device_id}-{filename}"
        elif device_id:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            filename = f"{device_id}-{timestamp}"
        
        filename, file_path = self.image_gen.create_image(
            content=content, 
            filename=filename,
            **kwargs
        )
        
        return filename
    
    def create_html_image(self, html_content: str, device_id: str = None, 
                         filename: str = None) -> str:
        """
        Create an image from HTML content.
        
        Args:
            html_content: HTML content to render
            device_id: Specific device MAC address
            filename: Custom filename for the image
            
        Returns:
            str: Filename of the created image
        """
        filename, file_path = self.image_gen.html_to_image(html_content, filename)
        return filename
    
    def create_big_text_image(self, text: str, subtitle: str = None, device_id: str = None,
                             filename: str = None) -> str:
        """
        Create an image with big text that fills the screen.
        
        Args:
            text: Main text to display in large font
            subtitle: Optional smaller text below main text  
            device_id: Specific device MAC address
            filename: Custom filename for the image
            
        Returns:
            str: Filename of the created image
            
        Example:
            controller = TRMNLController()
            
            # Simple big text
            controller.create_big_text_image("HELLO WORLD")
            
            # With subtitle
            controller.create_big_text_image("ALERT", "System Status: OK")
        """
        if device_id and filename:
            filename = f"{device_id}-{filename}"
        elif device_id:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            filename = f"{device_id}-big-text-{timestamp}"
        
        filename, file_path = self.image_gen.create_big_text_image(text, subtitle, filename)
        return filename
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of all connected/registered devices.
        
        Returns:
            List of device information dictionaries
        """
        # This would need to be implemented in the database class
        # For now, return empty list
        return []
    
    def schedule_update(self, update_function, interval_minutes: int = 30, 
                       device_id: str = None):
        """
        Schedule regular updates to device(s).
        
        Args:
            update_function: Function that returns content string or calls create_image
            interval_minutes: How often to update (default 30 minutes)
            device_id: Specific device to update (if None, updates all)
            
        Example:
            def weather_update():
                # Your code to fetch weather data
                weather_data = get_weather_from_api()
                return f"Weather: {weather_data['temp']}°F, {weather_data['condition']}"
            
            controller.schedule_update(weather_update, interval_minutes=60)
        """
        def job():
            try:
                result = update_function()
                if isinstance(result, str):
                    self.create_image(result, device_id=device_id)
                # If function returns None, assume it handled create_image internally
            except Exception as e:
                print(f"Error in scheduled update: {e}")
        
        schedule.every(interval_minutes).minutes.do(job)
        self.scheduled_jobs.append(job)
        
        if not self._scheduler_running:
            self.start_scheduler()
    
    def start_scheduler(self):
        """Start the background scheduler for automatic updates."""
        def run_scheduler():
            while self._scheduler_running:
                schedule.run_pending()
                time.sleep(1)
        
        self._scheduler_running = True
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the background scheduler."""
        self._scheduler_running = False
        schedule.clear()
        self.scheduled_jobs = []


# Global controller instance for easy access
_controller = None

def get_controller() -> TRMNLController:
    """Get the global TRMNL controller instance."""
    global _controller
    if _controller is None:
        _controller = TRMNLController()
    return _controller

def create_image(content: str = None, device_id: str = None, 
                filename: str = None, **kwargs) -> str:
    """
    Convenience function to create an image using the global controller.
    
    This is the main function you'll use to update your TRMNL device.
    
    Args:
        content: Text content to display
        device_id: Specific device MAC address (optional)
        filename: Custom filename (optional)
        **kwargs: Additional parameters
        
    Returns:
        str: Filename of the created image
        
    Example:
        # Simple usage
        create_image("Hello from Python!")
        
        # With custom content
        status = f'''
        System Status
        
        CPU: 45%
        Memory: 2.1GB / 8GB
        Disk: 250GB free
        Uptime: 5 days
        
        Last updated: {datetime.now().strftime('%H:%M:%S')}
        '''
        create_image(status)
    """
    controller = get_controller()
    return controller.create_image(content, device_id, filename, **kwargs)

def create_big_text_image(text: str, subtitle: str = None, device_id: str = None,
                         filename: str = None) -> str:
    """
    Convenience function to create big text images using the global controller.
    
    Args:
        text: Main text to display in large font
        subtitle: Optional smaller text below main text  
        device_id: Specific device MAC address (optional)
        filename: Custom filename (optional)
        
    Returns:
        str: Filename of the created image
        
    Example:
        # Simple big text
        create_big_text_image("HELLO WORLD")
        
        # With subtitle  
        create_big_text_image("SYSTEM ALERT", "All systems operational")
        
        # Custom message
        create_big_text_image("WELCOME", f"Today is {datetime.now().strftime('%A')}")
    """
    controller = get_controller()
    return controller.create_big_text_image(text, subtitle, device_id, filename)

def schedule_updates(update_function, interval_minutes: int = 30):
    """
    Convenience function to schedule regular updates.
    
    Args:
        update_function: Function that returns content string
        interval_minutes: Update interval in minutes
        
    Example:
        def get_system_status():
            return f"System time: {datetime.now()}"
        
        schedule_updates(get_system_status, 15)  # Update every 15 minutes
    """
    controller = get_controller()
    controller.schedule_update(update_function, interval_minutes)