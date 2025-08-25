#!/usr/bin/env python3
"""
Slide Generator CLI Tool

A command-line interface for the Slide Generator API.
"""

import argparse
import requests
import json
import sys
import os
from typing import Optional


class SlideGeneratorCLI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Status: {data['status']}")
                print(f"📋 Version: {data['version']}")
                return True
            else:
                print(f"❌ API Health Check Failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")
            return False
    
    def get_layouts(self):
        """Get available slide layouts"""
        try:
            response = requests.get(f"{self.api_url}/layouts")
            if response.status_code == 200:
                layouts = response.json()
                print("📋 Available Layouts:")
                for layout in layouts:
                    print(f"  • {layout}")
            else:
                print(f"❌ Failed to get layouts: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")
    
    def get_themes(self):
        """Get available themes"""
        try:
            response = requests.get(f"{self.api_url}/themes")
            if response.status_code == 200:
                themes = response.json()
                print("🎨 Available Themes:")
                for theme in themes:
                    print(f"  • {theme}")
            else:
                print(f"❌ Failed to get themes: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")
    
    def generate_presentation(self, topic: str, num_slides: int, theme: str = "modern", 
                            output_file: Optional[str] = None):
        """Generate a presentation"""
        try:
            data = {
                "topic": topic,
                "num_slides": num_slides,
                "theme": theme
            }
            
            print(f"🎯 Generating presentation: '{topic}' ({num_slides} slides, {theme} theme)")
            
            response = requests.post(f"{self.api_url}/generate", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Presentation generated successfully!")
                print(f"📄 Filename: {result['filename']}")
                print(f"⏱️  Processing time: {result['processing_time']}s")
                
                # Download the file if output_file is specified
                if output_file:
                    self.download_presentation(result['filename'], output_file)
                else:
                    print(f"📥 Download URL: {self.base_url}{result['download_url']}")
                
                return result
            else:
                print(f"❌ Failed to generate presentation: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"Error: {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")
            return None
    
    def download_presentation(self, filename: str, output_file: str):
        """Download a presentation file"""
        try:
            print(f"📥 Downloading {filename}...")
            response = requests.get(f"{self.api_url}/download/{filename}")
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded to: {output_file}")
            else:
                print(f"❌ Failed to download: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")
    
    def list_samples(self):
        """List available sample presentations"""
        try:
            response = requests.get(f"{self.api_url}/samples")
            if response.status_code == 200:
                samples = response.json()
                if samples:
                    print("📚 Available Sample Presentations:")
                    for sample in samples:
                        print(f"  • {sample}")
                else:
                    print("📚 No sample presentations available")
            else:
                print(f"❌ Failed to get samples: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {self.api_url}")


def main():
    parser = argparse.ArgumentParser(description="Slide Generator CLI Tool")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="API base URL (default: http://localhost:8000)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Get layouts command
    subparsers.add_parser("layouts", help="Get available layouts")
    
    # Get themes command
    subparsers.add_parser("themes", help="Get available themes")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a presentation")
    generate_parser.add_argument("topic", help="Presentation topic")
    generate_parser.add_argument("--slides", "-s", type=int, default=5, 
                               help="Number of slides (default: 5)")
    generate_parser.add_argument("--theme", "-t", default="modern", 
                               help="Presentation theme (default: modern)")
    generate_parser.add_argument("--output", "-o", help="Output file path")
    
    # List samples command
    subparsers.add_parser("samples", help="List sample presentations")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SlideGeneratorCLI(args.url)
    
    if args.command == "health":
        cli.health_check()
    elif args.command == "layouts":
        cli.get_layouts()
    elif args.command == "themes":
        cli.get_themes()
    elif args.command == "generate":
        cli.generate_presentation(args.topic, args.slides, args.theme, args.output)
    elif args.command == "samples":
        cli.list_samples()


if __name__ == "__main__":
    main() 