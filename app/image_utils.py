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
        Create an image with MASSIVE text that fills the entire screen.
        
        Args:
            text: Main text to display in huge font
            subtitle: Optional smaller text below main text
            filename: Custom filename (if None, generates timestamp-based name)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Tuple of (filename, file_path)
        """
        # Always use manual drawing to ensure massive text
        return self._create_massive_text_manually(text, subtitle, filename, width, height)
    
    def _create_massive_text_manually(self, text: str, subtitle: str = None, filename: str = None,
                                     width: int = 800, height: int = 480) -> Tuple[str, str]:
        """Create massive text by drawing it manually when font scaling fails."""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d-T%H-%M-%SZ")
            filename = f"big-text-manual-{timestamp}"
            
        # Create PIL image
        image = Image.new('1', (width, height), 1)  # 1-bit image, white background
        draw = ImageDraw.Draw(image)
        
        # Calculate character size to fit screen - make it MASSIVE
        char_count = len(text.replace(' ', ''))  # Don't count spaces
        spaces_count = text.count(' ')
        if char_count == 0:
            char_count = 1
            
        # Use most of the screen for the text
        available_width = width - 20
        available_height = height - 100 if subtitle else height - 20
        
        # Make each character take up most of the available space
        char_width = available_width // (char_count + spaces_count // 2)  # Spaces take less room
        char_height = available_height * 2 // 3  # Use 2/3 of available height
        
        # Center everything
        total_width = char_count * char_width + (spaces_count * char_width // 3)
        start_x = (width - total_width) // 2
        start_y = (available_height - char_height) // 2 + 10
        
        current_x = start_x
        
        for char in text:
            if char == ' ':
                current_x += char_width // 3  # Small space for actual spaces
                continue
                
            # Draw MASSIVE filled rectangles for each character
            rect_width = char_width - 8  # Small spacing between characters
            rect_height = char_height
            
            # Fill the entire character area with black
            draw.rectangle([current_x, start_y, current_x + rect_width, start_y + rect_height], 
                         fill=0)  # Solid black rectangles
            
            # Add white details inside to make letters more recognizable
            inner_margin = rect_width // 8
            inner_x = current_x + inner_margin
            inner_y = start_y + inner_margin
            inner_width = rect_width - 2 * inner_margin
            inner_height = rect_height - 2 * inner_margin
            
            # Add character-specific white cutouts to make it look like letters
            if char.upper() == 'H':
                # H: vertical bars with horizontal connection
                bar_width = inner_width // 4
                draw.rectangle([inner_x + bar_width, inner_y, inner_x + inner_width - bar_width, inner_y + inner_height], fill=1)
                draw.rectangle([inner_x, inner_y + inner_height//3, inner_x + inner_width, inner_y + 2*inner_height//3], fill=0)
            elif char.upper() == 'E':
                # E: remove right side except for horizontal bars
                draw.rectangle([inner_x + inner_width//2, inner_y, inner_x + inner_width, inner_y + inner_height], fill=1)
                draw.rectangle([inner_x, inner_y + inner_height//3, inner_x + inner_width, inner_y + 2*inner_height//3], fill=0)
            elif char.upper() == 'L':
                # L: remove top right
                draw.rectangle([inner_x + inner_width//3, inner_y, inner_x + inner_width, inner_y + 2*inner_height//3], fill=1)
            elif char.upper() == 'O':
                # O: hollow center
                draw.ellipse([inner_x + inner_width//4, inner_y + inner_height//4, 
                            inner_x + 3*inner_width//4, inner_y + 3*inner_height//4], fill=1)
            elif char.upper() == 'W':
                # W: two V shapes
                draw.polygon([inner_x + inner_width//4, inner_y, inner_x + inner_width//2, inner_y + inner_height//2,
                            inner_x + 3*inner_width//4, inner_y], fill=1)
            elif char.upper() == 'R':
                # R: like P but with diagonal
                draw.rectangle([inner_x + inner_width//2, inner_y, inner_x + inner_width, inner_y + inner_height//2], fill=1)
                draw.rectangle([inner_x + inner_width//3, inner_y + inner_height//4, inner_x + inner_width, inner_y + 3*inner_height//4], fill=1)
            elif char.upper() == 'D':
                # D: rounded right side
                draw.rectangle([inner_x + 2*inner_width//3, inner_y, inner_x + inner_width, inner_y + inner_height], fill=1)
                draw.ellipse([inner_x + inner_width//3, inner_y, inner_x + inner_width, inner_y + inner_height], fill=1, outline=0)
            
            current_x += char_width
        
        # Draw subtitle if provided
        if subtitle:
            sub_y = start_y + char_height + 30
            # Use default font for subtitle but try to make it larger
            try:
                from PIL import ImageFont
                sub_font = ImageFont.load_default()
            except:
                sub_font = None
                
            sub_bbox = draw.textbbox((0, 0), subtitle, font=sub_font) if sub_font else (0, 0, len(subtitle) * 8, 16)
            sub_width = sub_bbox[2] - sub_bbox[0]
            sub_x = (width - sub_width) // 2
            
            draw.text((sub_x, sub_y), subtitle, fill=0, font=sub_font)
        
        # Save as PNG
        png_path = self.output_dir / f"{filename}.png"
        self._convert_to_monochrome_png(image, png_path)
        
        return filename, str(png_path)
    
    def _find_max_font_size_that_fits(self, draw: ImageDraw.Draw, text: str, max_width: int, max_height: int) -> int:
        """Find the maximum font size that fits within the given dimensions."""
        # Start with a very large font size and work down
        for font_size in range(200, 10, -5):  # Try sizes from 200 down to 10
            try:
                from PIL import ImageFont
                test_font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=test_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Scale the estimated size based on desired font size
                estimated_width = text_width * (font_size / 11)  # 11 is approx default font size
                estimated_height = text_height * (font_size / 11)
                
                if estimated_width <= max_width and estimated_height <= max_height:
                    return font_size
            except:
                continue
                
        return 80  # Fallback to a large size
    
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