import os
import json
import tempfile
import sys
from unittest import mock
import pytest

# Add src to sys.path to import the plugin script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import plugin

def test_merge_settings():
    target = {"theme": "Light", "pluginSearchPaths": []}
    source = {"theme": "Dark", "hotkey": "Alt+Space"}
    
    changed = plugin.merge_settings(target, source)
    assert changed is True
    assert target["theme"] == "Dark"
    assert target["hotkey"] == "Alt+Space"
    assert target["pluginSearchPaths"] == []
    
    # Test identical data yields no changes
    changed2 = plugin.merge_settings(target, {"theme": "Dark"})
    assert changed2 is False

@mock.patch("os.getenv")
def test_get_settings_path(mock_getenv):
    mock_getenv.return_value = "C:\\Users\\Test\\AppData\\Roaming"
    expected = "C:\\Users\\Test\\AppData\\Roaming\\FlowLauncher\\Settings.json"
    assert plugin.get_settings_path() == expected

@mock.patch("os.getenv")
@mock.patch("os.path.isdir")
def test_check_installed_true(mock_isdir, mock_getenv):
    mock_getenv.return_value = "C:\\Users\\Test\\AppData\\Roaming"
    mock_isdir.return_value = True
    
    response = plugin.check_installed({}, "req-1")
    assert response["success"] is True
    assert response["data"]["installed"] is True

def test_apply_config_dry_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        with mock.patch("plugin.get_settings_path") as mock_get_path:
            settings_file = os.path.join(tmpdir, "Settings.json")
            mock_get_path.return_value = settings_file
            
            args = {"theme": "Dark", "builtinPlugins": {"Calculator": {"enabled": True}}}
            context = {"dryRun": True}
            
            # Application with a dry-run
            response = plugin.apply_config(args, context, "req-2")
            
            assert response["success"] is True
            assert response["changed"] is True
            
            # Settings.json should NOT be created
            assert not os.path.exists(settings_file)

def test_apply_config_real_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        with mock.patch("plugin.get_settings_path") as mock_get_path:
            settings_file = os.path.join(tmpdir, "Settings.json")
            mock_get_path.return_value = settings_file
            
            args = {"theme": "Dark", "hotkey": "Alt+Space"}
            context = {"dryRun": False}
            
            # Application with dryRun = false
            response = plugin.apply_config(args, context, "req-3")
            
            assert response["success"] is True
            assert response["changed"] is True
            
            # Verify directories and Settings.json was physically created/written
            assert os.path.exists(settings_file)
            with open(settings_file, "r") as f:
                data = json.load(f)
                assert data["theme"] == "Dark"
                assert data["hotkey"] == "Alt+Space"