import yaml
from typing import Dict, List, Optional
from aintellivr.utils.directories import directories


class RoutingConfiguration:
    def __init__(self, config: Dict):
        self.departments = config.get("departments", {})
        self.prerequisites = config.get("prerequisites", {})
        self.routing_rules = config.get("routing_rules", [])
        self.global_rules = config.get("global_rules", {})

    def get_department(self, dept_id: str) -> Optional[Dict]:
        """Get department configuration by ID."""
        return self.departments.get(dept_id)

    def get_prerequisite(self, prereq_id: str) -> Optional[Dict]:
        """Get prerequisite configuration by ID."""
        return self.prerequisites.get(prereq_id)

    def get_routing_rule_by_intent(self, intent: str) -> Optional[Dict]:
        """Find routing rule matching the given intent."""
        for rule in self.routing_rules:
            if rule.get("intent") == intent:
                return rule
        return None

    def get_emergency_keywords(self) -> List[str]:
        """Get list of emergency keywords."""
        return self.global_rules.get("emergency_keywords", [])

    def get_prerequisites_for_intent(self, intent: str) -> Dict[str, List[str]]:
        """Get required and optional prerequisites for an intent."""
        rule = self.get_routing_rule_by_intent(intent)
        if not rule:
            return {"required": [], "optional": []}

        return {
            "required": rule.get("required_prerequisites", []),
            "optional": rule.get("optional_prerequisites", []),
        }

    def __repr__(self):
        return (
            f"RoutingConfiguration(departments={self.departments},"
            f" prerequisites={self.prerequisites}, "
            f"routing_rules={self.routing_rules}, "
            f"global_rules={self.global_rules})"
        )

    def __str__(self):
        return (
            f"RoutingConfiguration(departments={self.departments}, "
            f"prerequisites={self.prerequisites}, "
            f"routing_rules={self.routing_rules}, "
            f"global_rules={self.global_rules})"
        )


def load_routing_config() -> RoutingConfiguration:
    """
    Load and parse the routing configuration YAML file.

    Returns:
        RoutingConfiguration object containing the parsed configuration

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        yaml.YAMLError: If the YAML is invalid
    """
    try:
        path = directories.config_dir / "routing_rules.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r") as file:
            config = yaml.safe_load(file)

        # Basic validation of required sections
        required_sections = [
            "departments",
            "prerequisites",
            "routing_rules",
            "global_rules",
        ]
        missing_sections = [
            section for section in required_sections if section not in config
        ]

        if missing_sections:
            raise ValueError(
                f"Missing required sections in config: {', '.join(missing_sections)}"
            )

        return RoutingConfiguration(config)

    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML configuration: {str(e)}")


ROUTING_CONFIG = load_routing_config()
