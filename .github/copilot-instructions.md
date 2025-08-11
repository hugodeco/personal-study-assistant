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
* **NEVER include obvious answer hints in multiple choice options** - avoid parenthetical explanations like "Verde (vidro)", "Azul (papel)", "cantei (ação que terminou)", etc. that make the correct answer obvious and compromise educational assessment quality.
* **AVOID obvious visual hints in question icons** - don't use 🚲 when asking about bicycles, 🌞 when asking about solar energy, 🚌 when asking about public transport, etc. Use neutral icons instead.

## Pedagogical Quality Standards
* Multiple choice questions should test genuine knowledge, not reading comprehension of hints
* Remove obvious clues from answer options that reveal the correct choice
* Avoid visual hints in emojis that give away the answer
* Examples of what to AVOID:
  - "Verde (vidro)" → Use "Verde" instead
  - "cantei (ação que terminou)" → Use "cantei" instead  
  - "parecer (conecta sujeito)" → Use "parecer" instead
  - "🚲 Which transport is most sustainable?" → Use "🚶‍♀️" or "⚡" instead
  - "🌞 Which energy source is cleanest?" → Use "⚡" instead
  - "cantei (ação que terminou)" → Use "cantei" instead  
  - "parecer (conecta sujeito)" → Use "parecer" instead
* Maintain appropriate difficulty level without compromising educational integrity
* Ensure all options are plausible to require actual subject knowledge
* By default, do not create evaluation questions

## Form Generation - IMPORTANT
* **ALWAYS use the `form.py` script from the project root to create Google Forms**
* **NEVER use `global/generator.py` directly** - it has path resolution issues
* Command syntax: `python form.py [quiz_name]` (without .json extension)
* Examples:
  - `python form.py pronomes` (creates form from forms/pronomes.json)
  - `python form.py verbos_e_logica_reforco` (creates reinforcement quiz)
* The script automatically handles file paths, authentication, and form creation
* **ASYNCHRONOUS PROCESSING:** Forms are generated asynchronously by Google's API
  - Execute the command once and wait for completion
  - Do NOT run the same command multiple times
  - Google processes the form in the background
  - Check `ultimo_formulario_criado.txt` for completion status
* Results are saved in `ultimo_formulario_criado.txt` with links and details
* If form generation fails, check the terminal output for specific error messages