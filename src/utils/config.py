"""
Configuration Manager for Voice Mode

Handles loading, saving, and managing application settings.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from copy import deepcopy


class ConfigManager:
    """Manages application configuration with user overrides"""

    def __init__(self):
        # Paths
        self.app_support_dir = Path.home() / "Library" / "Application Support" / "VoiceMode"
        self.user_config_path = self.app_support_dir / "settings.yaml"
        self.history_path = self.app_support_dir / "history.json"

        # Default config path (in repository)
        self.default_config_path = Path(__file__).parent.parent.parent / "config" / "default_settings.yaml"
        self.prompts_config_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"

        # Ensure directories exist
        self.app_support_dir.mkdir(parents=True, exist_ok=True)

        # Load configurations
        self.default_config = self._load_yaml(self.default_config_path)
        self.user_config = self._load_user_config()
        self.prompts = self._load_yaml(self.prompts_config_path)

        # Merged config (defaults + user overrides)
        self.config = self._merge_configs(self.default_config, self.user_config)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file"""
        if not path.exists():
            return {}

        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def _load_user_config(self) -> Dict[str, Any]:
        """Load user configuration, create from defaults if doesn't exist"""
        if not self.user_config_path.exists():
            # First run - create user config from defaults
            return {}

        return self._load_yaml(self.user_config_path)

    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config into default config"""
        result = deepcopy(default)

        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key_path: Dot-separated path (e.g., "hotkey.type")
            default: Default value if key doesn't exist

        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any, save: bool = True) -> None:
        """
        Set configuration value using dot notation

        Args:
            key_path: Dot-separated path (e.g., "hotkey.type")
            value: Value to set
            save: Whether to save to disk immediately
        """
        keys = key_path.split('.')
        config = self.config
        user_config = self.user_config

        # Update both configs
        for i, key in enumerate(keys[:-1]):
            if key not in config:
                config[key] = {}
            config = config[key]

            if key not in user_config:
                user_config[key] = {}
            user_config = user_config[key]

        # Set the final value
        config[keys[-1]] = value
        user_config[keys[-1]] = value

        if save:
            self.save()

    def save(self) -> bool:
        """Save user configuration to disk"""
        try:
            with open(self.user_config_path, 'w') as f:
                yaml.dump(self.user_config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.user_config = {}
        self.config = deepcopy(self.default_config)
        self.save()

    def get_prompt(self, prompt_name: str) -> Optional[Dict[str, str]]:
        """
        Get a Claude prompt template by name

        Args:
            prompt_name: Name of the prompt (e.g., "formal", "casual")

        Returns:
            Prompt dictionary with 'system' and 'user_template' keys
        """
        if 'prompts' in self.prompts and prompt_name in self.prompts['prompts']:
            return self.prompts['prompts'][prompt_name]
        return None

    def get_all_prompts(self) -> Dict[str, Dict[str, str]]:
        """Get all available Claude prompts"""
        return self.prompts.get('prompts', {})

    def format_prompt(self, prompt_name: str, transcription: str, context: Optional[Dict[str, str]] = None) -> tuple[str, str]:
        """
        Format a prompt with transcription and context

        Args:
            prompt_name: Name of the prompt template
            transcription: The transcribed text
            context: Optional context dictionary

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        prompt = self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")

        system = prompt.get('system', '')
        user_template = prompt.get('user_template', '')

        # Format context section
        context_section = ""
        if context and self.get('claude.include_context', True):
            context_template = self.prompts.get('context_template', '')
            context_section = context_template.format(
                active_app=context.get('active_app', 'Unknown'),
                window_title=context.get('window_title', 'Unknown'),
                screen_text=context.get('screen_text', 'None'),
                browser_tabs=', '.join(context.get('browser_tabs', []))
            )

        # Format user prompt
        user_prompt = user_template.format(
            transcription=transcription,
            context_section=context_section,
            custom_instructions=context.get('custom_instructions', '') if context else ''
        )

        return system, user_prompt

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting"""
        self.set(key, value)


# Global config instance
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance (singleton)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
