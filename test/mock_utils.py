"""
Mock utilities for EDMC-StreamSource plugin testing.

This module provides mock implementations of EDMC modules and classes
for testing the plugin without requiring the full EDMC environment.
"""

import sys
from pathlib import Path


class MockConfig:
    """Mock implementation of EDMC config module."""
    
    def __init__(self, outdir=None):
        self.outdir = outdir
    
    def get_str(self, key):
        """Mock get_str method."""
        if key == 'outdir':
            return self.outdir
        return None


class MockLocale:
    """Mock implementation of EDMC Locale class."""
    
    @staticmethod
    def string_from_number(num, precision):
        """Mock string_from_number method."""
        return f"{num:.{precision}f}"


def setup_mock_environment(outdir=None):
    """
    Setup mock EDMC environment for testing.
    
    Args:
        outdir: Output directory for mock config
        
    Returns:
        tuple: (config, edmc_data, l10n) mock modules
    """
    # Create mock modules
    config = MockConfig(outdir)
    
    # Create edmc_data mock
    edmc_data = type('MockModule', (), {})()
    edmc_data.coriolis_ship_map = {
        'sidewinder': 'Sidewinder',
        'eagle': 'Eagle Mk II',
        'hauler': 'Hauler',
        'adder': 'Adder',
        'viper': 'Viper Mk III',
        'cobramkiii': 'Cobra Mk III',
        'type6': 'Type-6 Transporter',
        'dolphin': 'Dolphin',
        'type7': 'Type-7 Transporter',
        'asp': 'Asp Explorer',
        'vulture': 'Vulture',
        'empire_trader': 'Imperial Clipper',
        'federation_dropship': 'Federal Dropship',
        'python': 'Python',
        'belugaliner': 'Beluga Liner',
        'ferdelance': 'Fer-de-Lance',
        'anaconda': 'Anaconda',
        'federation_corvette': 'Federal Corvette',
        'cutter': 'Imperial Cutter',
        'krait_mkii': 'Krait Mk II',
        'krait_light': 'Krait Phantom'
    }
    
    # Create l10n mock
    l10n = type('MockModule', (), {})()
    l10n.Locale = MockLocale
    
    # Replace imports with mocks in sys.modules
    sys.modules['config'] = type('MockModule', (), {'config': config})()
    sys.modules['edmc_data'] = edmc_data
    sys.modules['l10n'] = l10n
    
    return config, edmc_data, l10n


def add_project_to_path():
    """Add project root to Python path for imports."""
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def create_test_journal_entry(event_type, **kwargs):
    """
    Create a test journal entry with common fields.
    
    Args:
        event_type: Type of journal event
        **kwargs: Additional fields for the entry
        
    Returns:
        dict: Mock journal entry
    """
    base_entry = {
        'timestamp': '2025-10-21T12:00:00Z',
        'event': event_type
    }
    base_entry.update(kwargs)
    return base_entry


def create_test_state(**kwargs):
    """
    Create a test game state with common fields.
    
    Args:
        **kwargs: State fields
        
    Returns:
        dict: Mock game state
    """
    base_state = {
        'ShipType': 'sidewinder',
        'ShipName': 'Test Ship'
    }
    base_state.update(kwargs)
    return base_state