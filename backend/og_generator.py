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
        Generate an OpenGraph image for a specific station matching the Figma design.
        
        Args:
            station_name: Name of the station to display
            
        Returns:
            PNG image bytes
        """
        # Create image with black background
        img = Image.new('RGB', (self.OG_WIDTH, self.OG_HEIGHT), self.BLACK)
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        station_font = self._get_font(80, bold=True)  # Large station name
        subtitle_font = self._get_font(42, bold=True)  # Subtitle text
        
        # Define layout dimensions
        black_section_height = 480  # Top black section (increased to fit logo + text)
        
        # Draw light gray bottom section (smaller now)
        draw.rectangle([(0, black_section_height), (self.OG_WIDTH, self.OG_HEIGHT)], fill='#F5F5F5')
        
        # Define left margin for alignment
        left_margin = 60
        
        # Load and place the T logo PNG
        logo_size = 120
        logo_x = left_margin
        logo_y = 80  # Top margin
        
        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'resources', 'T logo.png')
            print(f"Looking for logo at: {logo_path}")  # Debug log
            print(f"Logo exists: {os.path.exists(logo_path)}")  # Debug log
            
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                print(f"Loaded logo: {logo_img.size}, mode: {logo_img.mode}")  # Debug log
                
                # Resize logo to fit the desired size while maintaining aspect ratio
                logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Convert to RGBA if not already (for transparency support)
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')
                
                # Paste the logo onto the main image
                img.paste(logo_img, (logo_x, logo_y), logo_img)
                print("Logo pasted successfully")  # Debug log
            else:
                print("Logo file not found!")  # Debug log
                
        except Exception as e:
            print(f"Error loading logo: {e}")  # Debug log
        
        # Draw station name below the logo, left-aligned
        max_station_width = self.OG_WIDTH - (left_margin * 2)  # Full width minus margins
        station_lines = self._wrap_text(station_name, station_font, max_station_width)
        
        # Position station name below logo with same left alignment
        station_x = left_margin  # Same x position as logo
        station_start_y = logo_y + logo_size + 40  # Below logo with spacing
        
        line_height = station_font.getbbox('Ay')[3] - station_font.getbbox('Ay')[1]
        
        for i, line in enumerate(station_lines):
            line_y = station_start_y + (i * line_height)
            draw.text((station_x, line_y), line, fill=self.WHITE, font=station_font)
        
        # Draw subtitle in the light section
        subtitle = "Real-time Departure Board"
        subtitle_x = left_margin  # Same left alignment
        subtitle_y = black_section_height + 40  # Top margin in light section
        
        draw.text((subtitle_x, subtitle_y), subtitle, fill='#333333', font=subtitle_font)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    def generate_default_image(self) -> bytes:
        """Generate a default OpenGraph image for the homepage."""
        return self.generate_station_image("University of Waterloo")