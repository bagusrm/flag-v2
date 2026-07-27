#!/usr/bin/env python3
"""CAPTURE THE FLAG - CTF Framework
All-in-one CLI framework for CTF challenges.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import FlagApp

def main():
    try:
        app = FlagApp()
        app.initialize()
        app.run()
    except KeyboardInterrupt:
        print('\nExiting...')
        sys.exit(0)
    except Exception as e:
        print(f'Fatal error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
