"""
OpenGraph Image Generator

Generates dynamic OpenGraph images for station pages that match the Figma design.
Creates images with station names overlaid on a departure board template.
"""

import io
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional


class OGImageGenerator:
    def __init__(self):
        # OpenGraph image dimensions (1200x630 is the standard)
        self.OG_WIDTH = 1200
        self.OG_HEIGHT = 630
        
        # Design colors from your CSS variables
        self.BLACK = '#000000'
        self.WHITE = '#ffffff'
        self.DARK_GREY = '#1e1c1c'
        self.LIGHT_GREY = '#dbdbdb'
        self.LIGHT_GREEN = '#9fd30a'
        
        # Font sizes
        self.TITLE_FONT_SIZE = 72
        self.SUBTITLE_FONT_SIZE = 36
        self.SMALL_FONT_SIZE = 24
        
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get Overpass font with the specified size. Falls back to default if not available."""
        try:
            # Use Overpass font from backend resources
            font_path = os.path.join(os.path.dirname(__file__), 'resources', 'overpass-bold.otf')
            
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
                    
            # Fallback to default font
            return ImageFont.load_default()
            
        except Exception:
            return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, just add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def generate_station_image(self, station_name: str) -> bytes:
        """
        Generate an OpenGraph image for a specific station.
        
        Args:
            station_name: Name of the station to display
            
        Returns:
            PNG image bytes
        """
        # Create image with black background
        img = Image.new('RGB', (self.OG_WIDTH, self.OG_HEIGHT), self.BLACK)
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        title_font = self._get_font(self.TITLE_FONT_SIZE, bold=True)
        subtitle_font = self._get_font(self.SUBTITLE_FONT_SIZE)
        small_font = self._get_font(self.SMALL_FONT_SIZE)
        
        # Draw main title "Live Departures"
        main_title = "Live Departures"
        title_bbox = draw.textbbox((0, 0), main_title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.OG_WIDTH - title_width) // 2
        title_y = 80
        
        draw.text((title_x, title_y), main_title, fill=self.WHITE, font=title_font)
        
        # Draw station name (wrapped if necessary)
        max_station_width = self.OG_WIDTH - 100  # 50px margin on each side
        station_lines = self._wrap_text(station_name, subtitle_font, max_station_width)
        
        # Calculate total height of station name text
        line_height = subtitle_font.getbbox('Ay')[3] - subtitle_font.getbbox('Ay')[1] + 10
        total_station_height = len(station_lines) * line_height
        
        # Position station name in the center area
        station_start_y = title_y + title_font.getbbox('A')[3] + 60
        
        for i, line in enumerate(station_lines):
            line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (self.OG_WIDTH - line_width) // 2
            line_y = station_start_y + (i * line_height)
            
            draw.text((line_x, line_y), line, fill=self.LIGHT_GREEN, font=subtitle_font)
        
        # Draw subtitle
        subtitle = "Real-time transit departures"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.OG_WIDTH - subtitle_width) // 2
        subtitle_y = station_start_y + total_station_height + 40
        
        draw.text((subtitle_x, subtitle_y), subtitle, fill=self.LIGHT_GREY, font=small_font)
        
        # Draw decorative elements to match departure board aesthetic
        # Top border line
        draw.rectangle([(50, 50), (self.OG_WIDTH - 50, 52)], fill=self.LIGHT_GREEN)
        
        # Bottom border line  
        draw.rectangle([(50, self.OG_HEIGHT - 52), (self.OG_WIDTH - 50, self.OG_HEIGHT - 50)], fill=self.LIGHT_GREEN)
        
        # Side accent lines
        draw.rectangle([(48, 50), (50, self.OG_HEIGHT - 50)], fill=self.LIGHT_GREY)
        draw.rectangle([(self.OG_WIDTH - 50, 50), (self.OG_WIDTH - 48, self.OG_HEIGHT - 50)], fill=self.LIGHT_GREY)
        
        # Add small dots to mimic departure board look
        dot_size = 4
        for i in range(0, self.OG_WIDTH, 40):
            if i > 100 and i < self.OG_WIDTH - 100:  # Don't overlap with borders
                draw.ellipse([(i, 25), (i + dot_size, 25 + dot_size)], fill=self.DARK_GREY)
                draw.ellipse([(i, self.OG_HEIGHT - 25 - dot_size), (i + dot_size, self.OG_HEIGHT - 25)], fill=self.DARK_GREY)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    def generate_default_image(self) -> bytes:
        """Generate a default OpenGraph image for the homepage."""
        return self.generate_station_image("University of Waterloo")