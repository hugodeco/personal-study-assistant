<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Google Forms API Integration Project

This project integrates with Google Forms API to create and manage forms programmatically.

## Development Guidelines

- Use Python 3.8+ with type hints
- Follow PEP 8 coding standards
- Use Google API Client Library for Python
- Implement proper error handling and logging
- Use OAuth2 for authentication
- Structure code with clear separation of concerns
- Add comprehensive docstrings for all functions
- Use environment variables for sensitive configuration

## Forms
* On creating a new form, ensure the JSON structure is valid and follows the defined schema `global/schema.json`.
* Each form should be defined in a separate JSON file within the `forms/` directory.
* If not specified, ask about the level of difficulty for the quiz.
* After generating a new form, review all created questions and answers to ensure there are no duplicate answers.
* Avoid naming sections in a way that suggests the answer to the question, e.g. Section: "Personal Pronouns" for the question "What type of pronoun is used in the sentence: ______ ?".