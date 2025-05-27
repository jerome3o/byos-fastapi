import os
import subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple
import hashlib
import tempfile


class ImageGenerator:
    def __init__(self, output_dir: str = "static/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_image(self, content: str = None, filename: str = None, 
                    width: int = 800, height: int = 480) -> Tuple[str, str]:
        """
        Create an image for the TRMNL device.
        
        Args:
            content: Text content to display (if None, creates a default image)
            filename: Custom filename (if None, generates timestamp-based name)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Tuple of (filename, file_path)
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d-T%H-%M-%SZ")
            content_hash = hashlib.md5((content or "default").encode()).hexdigest()[:8]
            filename = f"generated-{timestamp}-{content_hash}"
        
        # Create PIL image
        image = Image.new('1', (width, height), 1)  # 1-bit image, white background
        draw = ImageDraw.Draw(image)
        
        if content:
            self._draw_text_content(draw, content, width, height)
        else:
            self._draw_default_content(draw, width, height)
        
        # Save as PNG
        png_path = self.output_dir / f"{filename}.png"
        self._convert_to_monochrome_png(image, png_path)
        
        return filename, str(png_path)
    
    def _draw_text_content(self, draw: ImageDraw.Draw, content: str, width: int, height: int):
        """Draw text content on the image."""
        try:
            # Try to use a system font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Split content into lines and draw
        lines = content.split('\n')
        y_offset = 50
        line_height = 30
        
        for line in lines[:15]:  # Limit to 15 lines to fit on screen
            if y_offset + line_height > height - 50:
                break
            draw.text((50, y_offset), line[:60], fill=0, font=font)  # Black text, limit line length
            y_offset += line_height
    
    def _draw_default_content(self, draw: ImageDraw.Draw, width: int, height: int):
        """Draw default content when no content is provided."""
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw border
        draw.rectangle([10, 10, width-10, height-10], outline=0, width=3)
        
        # Draw title
        title = "TRMNL Custom Server"
        draw.text((50, 50), title, fill=0, font=font)
        
        # Draw timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        draw.text((50, 100), f"Generated: {timestamp}", fill=0, font=font)
        
        # Draw status
        draw.text((50, 150), "Status: Server Running", fill=0, font=font)
        draw.text((50, 200), "Ready for device connection", fill=0, font=font)
    
    def _convert_to_monochrome_png(self, image: Image.Image, output_path: Path):
        """Convert PIL image to proper monochrome PNG using ImageMagick if available."""
        # First save as temporary PNG
        temp_path = output_path.with_suffix('.tmp.png')
        image.save(temp_path)
        
        try:
            # Try to use ImageMagick for better monochrome conversion
            subprocess.run([
                'magick', str(temp_path),
                '-monochrome', '-colors', '2', '-depth', '1', '-strip',
                f'png:{output_path}'
            ], check=True, capture_output=True)
            temp_path.unlink()  # Remove temp file
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to PIL if ImageMagick not available
            temp_path.rename(output_path)
    
    def html_to_image(self, html_content: str, filename: str = None) -> Tuple[str, str]:
        """
        Convert HTML content to image (basic implementation).
        For production use, consider using a proper HTML-to-image service.
        """
        # This is a simplified implementation
        # For real HTML rendering, you'd want to use something like playwright or selenium
        text_content = self._extract_text_from_html(html_content)
        return self.create_image(content=text_content, filename=filename)
    
    def _extract_text_from_html(self, html: str) -> str:
        """Basic HTML text extraction."""
        import re
        # Remove HTML tags
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html).strip()
    
    def create_big_text_image(self, text: str, subtitle: str = None, filename: str = None, 
                             width: int = 800, height: int = 480) -> Tuple[str, str]:
        """
        Create an image with very large text that fills the screen.
        
        Args:
            text: Main text to display in large font
            subtitle: Optional smaller text below main text
            filename: Custom filename (if None, generates timestamp-based name)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Tuple of (filename, file_path)
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d-T%H-%M-%SZ")
            filename = f"big-text-{timestamp}"
        
        # Create PIL image
        image = Image.new('1', (width, height), 1)  # 1-bit image, white background
        draw = ImageDraw.Draw(image)
        
        # Try to get the largest possible font size that fits
        main_font_size = self._find_max_font_size(draw, text, width - 40, height // 2)
        
        try:
            # Try to use a better font if available
            from PIL import ImageFont
            main_font = ImageFont.load_default()
        except:
            main_font = None
        
        # Get text dimensions
        if main_font:
            bbox = draw.textbbox((0, 0), text, font=main_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # Fallback estimation
            text_width = len(text) * 6
            text_height = 11
        
        # Center the main text
        main_x = (width - text_width) // 2
        main_y = (height - text_height) // 2
        
        # If we have a subtitle, move main text up a bit
        if subtitle:
            main_y = main_y - 30
        
        # Draw main text
        draw.text((main_x, main_y), text, fill=0, font=main_font)
        
        # Draw subtitle if provided
        if subtitle:
            if main_font:
                sub_bbox = draw.textbbox((0, 0), subtitle, font=main_font)
                sub_width = sub_bbox[2] - sub_bbox[0]
            else:
                sub_width = len(subtitle) * 6
            
            sub_x = (width - sub_width) // 2
            sub_y = main_y + text_height + 20
            draw.text((sub_x, sub_y), subtitle, fill=0, font=main_font)
        
        # Draw a border for effect
        draw.rectangle([5, 5, width-5, height-5], outline=0, width=2)
        
        # Save as PNG
        png_path = self.output_dir / f"{filename}.png"
        self._convert_to_monochrome_png(image, png_path)
        
        return filename, str(png_path)
    
    def _find_max_font_size(self, draw: ImageDraw.Draw, text: str, max_width: int, max_height: int) -> int:
        """Find the maximum font size that fits within the given dimensions."""
        # This is a simplified version - PIL's default font doesn't support sizing
        # In a real implementation, you'd use a TTF font with variable sizing
        return 24  # Default size
    
    def create_hello_world_image(self, filename: str = None) -> Tuple[str, str]:
        """Create a dramatic HELLO WORLD image with big text."""
        timestamp = datetime.utcnow().strftime('%H:%M:%S')
        subtitle = f"YOUR TRMNL IS HACKED! 🚀 | Time: {timestamp}"
        
        return self.create_big_text_image(
            text="HELLO WORLD",
            subtitle=subtitle,
            filename=filename or f"hello-world-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        )

    def create_welcome_image(self, device_id: str) -> Tuple[str, str]:
        """Create a welcome image for device setup."""
        content = f"""Welcome to TRMNL!

Device: {device_id}
Server: Custom FastAPI
Status: Successfully Connected

Your device is now configured
and ready to display content.

Refresh rate: 30 minutes
Image format: PNG (1-bit)
Resolution: 800x480

Server time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"""
        
        filename = f"welcome-{device_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        return self.create_image(content=content, filename=filename)