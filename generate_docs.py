#!/usr/bin/env python3
"""
Documentation Generation Script for HTTP Service

This script provides a convenient way to generate, build, and manage
documentation for the HTTP Service project.
"""

import os
import sys
import subprocess
import argparse
import webbrowser
from pathlib import Path


class DocumentationGenerator:
    """Handles documentation generation and management."""
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.build_dir = self.docs_dir / "_build"
        self.html_dir = self.build_dir / "html"
        
    def check_dependencies(self) -> bool:
        """Check if required documentation dependencies are installed."""
        try:
            import sphinx
            import sphinx_rtd_theme
            import myst_parser
            import sphinx_autodoc_typehints
            print("✅ All documentation dependencies are installed")
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            print("Install with: pip install -r requirements-docs.txt")
            return False
    
    def build_html(self, clean: bool = False, serve: bool = False) -> bool:
        """Build HTML documentation."""
        if not self.check_dependencies():
            return False
            
        if clean:
            self.clean()
            
        print("🔨 Building HTML documentation...")
        
        try:
            # Change to docs directory and build
            os.chdir(self.docs_dir)
            result = subprocess.run([
                "sphinx-build", "-b", "html", ".", "_build/html"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ HTML documentation built successfully!")
                print(f"📁 Output: {self.html_dir.absolute()}")
                
                if serve:
                    self.serve_docs()
                    
                return True
            else:
                print("❌ Failed to build documentation:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error building documentation: {e}")
            return False
        finally:
            # Return to original directory
            os.chdir("..")
    
    def build_pdf(self, clean: bool = False) -> bool:
        """Build PDF documentation."""
        if not self.check_dependencies():
            return False
            
        if clean:
            self.clean()
            
        print("🔨 Building PDF documentation...")
        
        try:
            os.chdir(self.docs_dir)
            
            # Build LaTeX
            result = subprocess.run([
                "sphinx-build", "-b", "latex", ".", "_build/latex"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Failed to build LaTeX:")
                print(result.stderr)
                return False
            
            # Build PDF from LaTeX
            os.chdir("_build/latex")
            result = subprocess.run(["make"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PDF documentation built successfully!")
                print("📁 Output: docs/_build/latex/")
                return True
            else:
                print("❌ Failed to build PDF:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error building PDF: {e}")
            return False
        finally:
            os.chdir("../..")
    
    def build_epub(self, clean: bool = False) -> bool:
        """Build EPUB documentation."""
        if not self.check_dependencies():
            return False
            
        if clean:
            self.clean()
            
        print("🔨 Building EPUB documentation...")
        
        try:
            os.chdir(self.docs_dir)
            result = subprocess.run([
                "sphinx-build", "-b", "epub", ".", "_build/epub"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ EPUB documentation built successfully!")
                print("📁 Output: docs/_build/epub/")
                return True
            else:
                print("❌ Failed to build EPUB:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error building EPUB: {e}")
            return False
        finally:
            os.chdir("..")
    
    def check_links(self) -> bool:
        """Check for broken links in documentation."""
        if not self.check_dependencies():
            return False
            
        print("🔍 Checking documentation links...")
        
        try:
            os.chdir(self.docs_dir)
            result = subprocess.run([
                "sphinx-build", "-b", "linkcheck", ".", "_build/linkcheck"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Link check completed successfully!")
                return True
            else:
                print("⚠️  Link check found issues:")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"❌ Error checking links: {e}")
            return False
        finally:
            os.chdir("..")
    
    def check_spelling(self) -> bool:
        """Check spelling in documentation."""
        try:
            import sphinxcontrib.spelling
        except ImportError:
            print("❌ sphinxcontrib-spelling not installed")
            print("Install with: pip install sphinxcontrib-spelling")
            return False
            
        print("🔍 Checking documentation spelling...")
        
        try:
            os.chdir(self.docs_dir)
            result = subprocess.run([
                "sphinx-build", "-b", "spelling", ".", "_build/spelling"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Spelling check completed successfully!")
                return True
            else:
                print("⚠️  Spelling check found issues:")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"❌ Error checking spelling: {e}")
            return False
        finally:
            os.chdir("..")
    
    def clean(self) -> None:
        """Clean build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        if self.build_dir.exists():
            import shutil
            shutil.rmtree(self.build_dir)
            print("✅ Build artifacts cleaned")
        else:
            print("ℹ️  No build artifacts to clean")
    
    def serve_docs(self, port: int = 8000) -> None:
        """Serve documentation locally."""
        if not self.html_dir.exists():
            print("❌ Documentation not built. Run build first.")
            return
            
        print(f"🌐 Serving documentation at http://localhost:{port}")
        print("Press Ctrl+C to stop server")
        
        try:
            os.chdir(self.html_dir)
            subprocess.run(["python", "-m", "http.server", str(port)])
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except Exception as e:
            print(f"❌ Error serving documentation: {e}")
        finally:
            os.chdir("../..")
    
    def open_docs(self) -> None:
        """Open documentation in default browser."""
        index_file = self.html_dir / "index.html"
        
        if not index_file.exists():
            print("❌ Documentation not built. Run build first.")
            return
            
        print("🌐 Opening documentation in browser...")
        webbrowser.open(f"file://{index_file.absolute()}")
    
    def show_status(self) -> None:
        """Show documentation build status."""
        print("📊 Documentation Status:")
        print(f"📁 Docs directory: {self.docs_dir.absolute()}")
        print(f"📁 Build directory: {self.build_dir.absolute()}")
        
        if self.build_dir.exists():
            print("✅ Build directory exists")
            
            if self.html_dir.exists():
                print("✅ HTML documentation built")
                
                # Count files
                html_files = list(self.html_dir.rglob("*.html"))
                print(f"📄 HTML files: {len(html_files)}")
                
                # Check for index
                if (self.html_dir / "index.html").exists():
                    print("✅ Index page exists")
                else:
                    print("❌ Index page missing")
            else:
                print("❌ HTML documentation not built")
        else:
            print("❌ Build directory does not exist")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate and manage HTTP Service documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_docs.py build          # Build HTML documentation
  python generate_docs.py build --serve  # Build and serve locally
  python generate_docs.py build --clean  # Clean and rebuild
  python generate_docs.py pdf            # Build PDF documentation
  python generate_docs.py epub           # Build EPUB documentation
  python generate_docs.py check-links    # Check for broken links
  python generate_docs.py check-spelling # Check spelling
  python generate_docs.py clean          # Clean build artifacts
  python generate_docs.py status         # Show build status
  python generate_docs.py open           # Open in browser
        """
    )
    
    parser.add_argument(
        "command",
        choices=[
            "build", "pdf", "epub", "check-links", "check-spelling",
            "clean", "status", "open", "serve"
        ],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve documentation locally after building"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for serving documentation (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = DocumentationGenerator()
    
    # Execute command
    if args.command == "build":
        success = generator.build_html(clean=args.clean, serve=args.serve)
        sys.exit(0 if success else 1)
        
    elif args.command == "pdf":
        success = generator.build_pdf(clean=args.clean)
        sys.exit(0 if success else 1)
        
    elif args.command == "epub":
        success = generator.build_epub(clean=args.clean)
        sys.exit(0 if success else 1)
        
    elif args.command == "check-links":
        success = generator.check_links()
        sys.exit(0 if success else 1)
        
    elif args.command == "check-spelling":
        success = generator.check_spelling()
        sys.exit(0 if success else 1)
        
    elif args.command == "clean":
        generator.clean()
        
    elif args.command == "status":
        generator.show_status()
        
    elif args.command == "open":
        generator.open_docs()
        
    elif args.command == "serve":
        generator.serve_docs(port=args.port)


if __name__ == "__main__":
    main()
