# Contributing to Agentic Meeting Assistant

First off, thank you for considering contributing to Agentic Meeting Assistant! 🎉

It's people like you that make this project such a great tool for the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When creating a bug report, include:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Sample input** that causes the bug
- **Environment details** (Python version, OS, etc.)
- **Error messages** or logs

**Bug Report Template:**
```markdown
**Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Use this transcript: '...'
2. Run command: '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 11]
- Python: [e.g., 3.10]
- Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information.
```

### Suggesting Features

Feature suggestions are welcome! Please:
- **Check existing issues** for similar suggestions
- **Describe the feature** clearly
- **Explain the use case** and benefits
- **Provide examples** if possible

**Feature Request Template:**
```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Mockups, examples, or references.
```

### Improving Documentation

Documentation improvements are always appreciated:
- Fix typos or unclear explanations
- Add examples or use cases
- Improve API documentation
- Translate documentation
- Create tutorials or guides

### Contributing Code

We love code contributions! Here's how:

1. **Find an issue** to work on or create one
2. **Comment** on the issue to claim it
3. **Fork** the repository
4. **Create a branch** for your feature
5. **Make your changes**
6. **Test thoroughly**
7. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key (for testing)

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/agentic-meeting-assistant.git
cd agentic-meeting-assistant

# 2. Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Run tests to verify setup
python test_sample.py
```

### Project Structure

```
meeting-agent/
├── meeting_agent.py              # Basic agent
├── meeting_agent_enhanced.py     # Enhanced agent
├── test_sample.py                # Test script
├── requirements.txt              # Dependencies
├── examples/                     # Sample files
├── docs/                         # Documentation
└── tests/                        # Test files
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Run existing tests** to ensure nothing breaks
4. **Follow coding standards** (see below)
5. **Update CHANGELOG.md** with your changes

### PR Guidelines

1. **Create a descriptive title**
   - Good: "Add deadline estimation for high-priority tasks"
   - Bad: "Update code"

2. **Provide detailed description**
   - What changes were made?
   - Why were they made?
   - How were they tested?

3. **Link related issues**
   - Use "Fixes #123" or "Closes #456"

4. **Keep PRs focused**
   - One feature or fix per PR
   - Avoid mixing unrelated changes

5. **Respond to feedback**
   - Be open to suggestions
   - Make requested changes promptly

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues
Fixes #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] CHANGELOG.md updated
```

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

**Formatting:**
```python
# Use 4 spaces for indentation
def my_function():
    return True

# Maximum line length: 100 characters
# Use descriptive variable names
user_input = "meeting transcript"

# Add blank lines between functions
def function_one():
    pass


def function_two():
    pass
```

**Naming Conventions:**
```python
# Classes: PascalCase
class MeetingAgent:
    pass

# Functions and variables: snake_case
def extract_action_items():
    task_owner = "John"

# Constants: UPPER_SNAKE_CASE
MAX_TOKENS = 2000
DEFAULT_PRIORITY = "Medium"

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

**Type Hints:**
```python
from typing import List, Dict, Optional

def process_meeting(
    transcript: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process meeting transcript."""
    pass
```

**Docstrings:**
```python
def extract_action_items(transcript: str) -> List[Dict[str, Any]]:
    """
    Extract action items from meeting transcript.
    
    Args:
        transcript: Raw meeting transcript text
    
    Returns:
        List of action items with task, owner, deadline, priority
    
    Raises:
        ValueError: If transcript is empty
    
    Example:
        >>> items = extract_action_items("John: Fix the bug")
        >>> print(items[0]['task'])
        'Fix the bug'
    """
    pass
```

### Code Quality

**Keep functions small and focused:**
```python
# Good: Single responsibility
def parse_deadline(text: str) -> Optional[str]:
    """Parse deadline from text."""
    pass

def estimate_deadline(priority: str) -> str:
    """Estimate deadline based on priority."""
    pass

# Avoid: Multiple responsibilities
def parse_and_estimate_deadline(text: str, priority: str):
    """Do too many things."""
    pass
```

**Use meaningful names:**
```python
# Good
def infer_task_owner(task: str, participants: List[str]) -> str:
    pass

# Bad
def process(t: str, p: List[str]) -> str:
    pass
```

**Add comments for complex logic:**
```python
def classify_priority(task: str) -> str:
    # Check for urgency keywords first
    if any(keyword in task.lower() for keyword in URGENT_KEYWORDS):
        return "High"
    
    # Then check deadline proximity
    if has_immediate_deadline(task):
        return "High"
    
    # Default to medium if no indicators
    return "Medium"
```

## 🧪 Testing Guidelines

### Writing Tests

```python
def test_owner_inference():
    """Test that owners are correctly inferred from context."""
    agent = AgenticMeetingAgent()
    
    transcript = "John mentioned fixing the bug. Mike handles backend."
    result = agent.process_meeting(transcript)
    
    # Assert expected behavior
    assert len(result['action_items']) > 0
    assert result['action_items'][0]['owner'] == 'John'
    assert 'owner_inferred' in result['action_items'][0]['flags']
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_enhanced_agent.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Test Coverage

Aim for:
- **80%+ code coverage** for new features
- **100% coverage** for critical functions
- **Edge cases** tested
- **Error conditions** tested

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include type hints
- Provide usage examples
- Document exceptions

### README Updates

When adding features, update:
- Feature list
- Usage examples
- API reference
- Configuration options

### Changelog

Add entries to CHANGELOG.md:
```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Improve inference accuracy
- [ ] Add more test cases
- [ ] Optimize performance
- [ ] Enhance error handling

### Medium Priority
- [ ] Add new features (see roadmap)
- [ ] Improve documentation
- [ ] Add examples
- [ ] Create tutorials

### Low Priority
- [ ] Code refactoring
- [ ] UI improvements
- [ ] Additional integrations

## 💬 Communication

### Getting Help

- **GitHub Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Email**: For private matters

### Asking Questions

Before asking:
1. Check existing documentation
2. Search closed issues
3. Review FAQ

When asking:
- Be specific and clear
- Provide context
- Include relevant code/logs
- Be patient and respectful

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🙏

Your efforts help make this project better for everyone.

For questions about contributing, open an issue or reach out to the maintainers.