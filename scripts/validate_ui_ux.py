#!/usr/bin/env python3
"""
UI/UX Validation Script
Check if frontend code complies with design system specifications
"""

import re
import sys
from pathlib import Path
from typing import List


class UIUXValidator:
    def __init__(self, frontend_dir: Path):
        self.frontend_dir = frontend_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> bool:
        """Run all validations"""
        print("Starting UI/UX validation...\n")
        
        self.validate_css_variables()
        self.validate_html_accessibility()
        self.validate_responsive_design()
        self.validate_icon_usage()
        self.validate_animation_performance()
        self.validate_component_states()
        
        self.print_results()
        return len(self.errors) == 0
    
    def validate_css_variables(self):
        """Validate CSS variable usage"""
        print("Checking CSS variable usage...")
        css_files = list(self.frontend_dir.rglob("*.css"))
        
        if not css_files:
            self.errors.append("No CSS files found")
            return
        
        for css_file in css_files:
            content = css_file.read_text()
            
            # Check for hardcoded colors
            hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
            for color in hex_colors:
                if color not in ['#FFFFFF', '#000000']:  # Allow pure black and white
                    # Exclude colors in comments and CSS variable definitions
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if color in line:
                            # Skip if it's a comment
                            if '/*' in line or '//' in line:
                                continue
                            # Skip if it's a CSS variable definition
                            if '--' in line and ':' in line:
                                continue
                            # Otherwise, it's a hardcoded color
                            self.warnings.append(
                                f"{css_file}:{i}: Found hardcoded color {color}, consider using CSS variables"
                            )
                            break
            
            # Check CSS variable definitions
            required_vars = ['--primary:', '--text-primary:', '--bg-primary:', '--border-color:']
            for var in required_vars:
                if var not in content:
                    self.errors.append(f"{css_file}: Missing {var} variable definition")
    
    def validate_html_accessibility(self):
        """Validate HTML accessibility"""
        print("Checking HTML accessibility...")
        html_files = list(self.frontend_dir.rglob("*.html"))
        
        if not html_files:
            self.errors.append("No HTML files found")
            return
        
        for html_file in html_files:
            content = html_file.read_text()
            
            # Check img alt attributes
            img_pattern = r'<img(?![^>]*\balt=)[^>]*>'
            imgs_without_alt = re.findall(img_pattern, content)
            if imgs_without_alt:
                self.errors.append(
                    f"{html_file}: Found {len(imgs_without_alt)} img tags missing alt attribute"
                )
            
            # Check button accessibility
            button_pattern = r'<button(?![^>]*(aria-label|aria-labelledby|>.*[a-zA-Z]+.*<))[^>]*>'
            buttons_without_label = re.findall(button_pattern, content)
            if buttons_without_label:
                self.warnings.append(
                    f"{html_file}: Found {len(buttons_without_label)} buttons that may lack accessibility labels"
                )
            
            # Check form labels
            input_pattern = r'<input(?![^>]*\bid=)[^>]*>'
            inputs_without_id = re.findall(input_pattern, content)
            if inputs_without_id:
                self.errors.append(
                    f"{html_file}: Found {len(inputs_without_id)} input tags missing id attribute (for label association)"
                )
            
            # Check semantic tags
            if '<div class="header">' in content or '<div class="footer">' in content:
                self.warnings.append(
                    f"{html_file}: Consider using semantic tags (header, footer, nav, main, etc.)"
                )
    
    def validate_responsive_design(self):
        """Validate responsive design"""
        print("Checking responsive design...")
        css_files = list(self.frontend_dir.rglob("*.css"))
        
        if not css_files:
            return
        
        for css_file in css_files:
            content = css_file.read_text()
            
            # Check media queries
            breakpoints = ['375px', '768px', '1024px', '1440px']
            found_breakpoints = set()
            
            media_queries = re.findall(r'@media[^{]*{', content)
            for mq in media_queries:
                for bp in breakpoints:
                    if bp in mq:
                        found_breakpoints.add(bp)
            
            for bp in breakpoints:
                if bp not in content:
                    self.warnings.append(f"{css_file}: No media query found for {bp} breakpoint")
            
            # Check touch targets
            if 'min-height' not in content and 'min-width' not in content:
                self.warnings.append(
                    f"{css_file}: Consider setting minimum size for buttons (44x44px)"
                )
            
            # Check Grid and Flexbox usage
            if 'display: grid' not in content and 'display: flex' not in content:
                self.warnings.append(
                    f"{css_file}: Consider using CSS Grid or Flexbox for flexible layouts"
                )
    
    def validate_icon_usage(self):
        """Validate icon usage"""
        print("Checking icon usage...")
        html_files = list(self.frontend_dir.rglob("*.html"))
        
        if not html_files:
            return
        
        for html_file in html_files:
            content = html_file.read_text()
            
            # Check emoji usage
            emoji_pattern = r'[\U0001F300-\U0001F9FF]'
            emojis = re.findall(emoji_pattern, content)
            if emojis:
                self.errors.append(
                    f"{html_file}: Found emoji usage ({len(emojis)} instances), consider using SVG icons"
                )
            
            # Check SVG icon usage
            if emojis and '<svg' not in content:
                self.warnings.append(
                    f"{html_file}: Found emojis but no SVG icons, consider replacing with SVG"
                )
    
    def validate_animation_performance(self):
        """Validate animation performance"""
        print("Checking animation performance...")
        css_files = list(self.frontend_dir.rglob("*.css"))
        
        if not css_files:
            return
        
        for css_file in css_files:
            content = css_file.read_text()
            
            # Check animation duration
            transition_pattern = r'transition:\s*([^;]+)'
            transitions = re.findall(transition_pattern, content)
            for trans in transitions:
                duration_match = re.search(r'(\d+)ms', trans)
                if duration_match:
                    duration = int(duration_match.group(1))
                    if duration > 300:
                        self.warnings.append(
                            f"{css_file}: Animation duration {duration}ms exceeds recommended value (300ms)"
                        )
                
                # Check if performance-optimized properties are used
                if 'transform' not in trans and 'opacity' not in trans:
                    self.warnings.append(
                        f"{css_file}: Consider using transform or opacity for better animation performance"
                    )
            
            # Check prefers-reduced-motion
            if '@media (prefers-reduced-motion: reduce)' not in content:
                self.errors.append(
                    f"{css_file}: Missing prefers-reduced-motion support"
                )
    
    def validate_component_states(self):
        """Validate component states"""
        print("Checking component states...")
        css_files = list(self.frontend_dir.rglob("*.css"))
        
        if not css_files:
            return
        
        for css_file in css_files:
            content = css_file.read_text()
            
            # Check button states
            if '.btn' in content:
                required_states = [':hover', ':focus', ':disabled']
                for state in required_states:
                    if state not in content:
                        self.warnings.append(
                            f"{css_file}: Buttons missing {state} state"
                        )
            
            # Check cursor-pointer
            if '.btn' in content and 'cursor: pointer' not in content:
                self.warnings.append(
                    f"{css_file}: Buttons missing cursor: pointer"
                )
            
            # Check form validation states
            if 'input' in content or '.input' in content:
                if ':focus' not in content:
                    self.warnings.append(
                        f"{css_file}: Input fields missing :focus state"
                    )
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*60)
        print("Validation Results")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All checks passed!")
        
        print("="*60)
        
        if self.errors:
            print(f"\nValidation failed: {len(self.errors)} errors found")
        elif self.warnings:
            print(f"\nValidation passed with {len(self.warnings)} warnings")
        else:
            print("\nValidation successful!")


def main():
    project_root = Path(__file__).parent.parent
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print(f"Error: Frontend directory not found: {frontend_dir}")
        sys.exit(1)
    
    validator = UIUXValidator(frontend_dir)
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
