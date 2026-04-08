from .models import IntelliNotifyObservation

# This dictionary defines the tasks for the OpenEnv grader
TASKS = {
    "security_scan_01": {
        "description": "Scan the network for unauthorized devices.",
        "required_actions": ["scan_network"],
        "difficulty": "easy"
    },
    "malware_analysis_02": {
        "description": "Analyze the suspicious process running on 'Workstation-4'.",
        "required_actions": ["check_logs", "quarantine_device"],
        "difficulty": "medium"
    },
    "phishing_mitigation_03": {
        "description": "Identify and block the source of the recent phishing emails.",
        "required_actions": ["check_logs", "block_ip"],
        "difficulty": "hard"
    }
}
