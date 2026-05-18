# 🤖 Meeting Action Item Agent

A simple, modular Python agent that extracts action items from meeting transcripts using LLM (OpenAI GPT).

## ✨ Features

- **Action Item Extraction** - Automatically identifies tasks from meeting transcripts
- **Owner Detection** - Determines who is responsible for each task
- **Deadline Parsing** - Extracts or infers deadlines from natural language
- **Priority Classification** - Assigns High/Medium/Low priority to tasks
- **Meeting Summarization** - Generates concise meeting summaries
- **Confidence Scoring** - Provides confidence levels for extractions
- **Clean Modular Design** - Easy to understand and extend

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

```bash
# Clone or download this directory
cd meeting-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Usage

#### Basic Usage

```python
from meeting_agent import MeetingAgent

# Initialize agent
agent = MeetingAgent()

# Process a meeting transcript
transcript = """
Team Standup - May 18, 2026
Participants: Alice, Bob, Charlie

Alice: I'll finish the authentication module by Friday.
Bob: I need to review the code and deploy to staging.
Charlie: I'll update the documentation this week.
"""

# Get results
result = agent.process_meeting(transcript)
print(result)
```

#### Run the Example

```bash
python meeting_agent.py
```

This will process the built-in sample transcript and save output to `meeting_output.json`.

#### Process Custom Transcript

```python
from meeting_agent import MeetingAgent

agent = MeetingAgent()

# Read transcript from file
with open("examples/sample_input.txt", "r") as f:
    transcript = f.read()

# Process with metadata
result = agent.process_meeting(
    transcript,
    metadata={
        "date": "2026-05-18",
        "participants": ["Sarah", "Mike", "Lisa", "Tom"]
    }
)

# Save results
import json
with open("output.json", "w") as f:
    json.dump(result, f, indent=2)
```

## 📋 API Reference

### MeetingAgent Class

#### `__init__(api_key: Optional[str] = None)`

Initialize the agent with an OpenAI API key.

**Parameters:**
- `api_key` (optional): OpenAI API key. If not provided, reads from `OPENAI_API_KEY` environment variable.

#### `parse_input(transcript: str, metadata: Optional[Dict] = None) -> Dict`

Parse and validate input transcript.

**Parameters:**
- `transcript`: Raw meeting transcript text
- `metadata` (optional): Dictionary with date, participants, etc.

**Returns:** Parsed input dictionary with cleaned transcript and metadata

#### `extract_action_items(parsed_input: Dict) -> List[Dict]`

Extract action items from parsed transcript using LLM.

**Parameters:**
- `parsed_input`: Output from `parse_input()`

**Returns:** List of action items, each containing:
- `task`: Description of the task
- `owner`: Person responsible
- `deadline`: Due date (YYYY-MM-DD format)
- `priority`: "High", "Medium", or "Low"
- `confidence`: Confidence score (0.0-1.0)

#### `summarize_meeting(parsed_input: Dict) -> str`

Generate a concise meeting summary.

**Parameters:**
- `parsed_input`: Output from `parse_input()`

**Returns:** Meeting summary text (2-3 sentences)

#### `format_output(action_items: List, summary: str, metadata: Dict) -> Dict`

Format final output as structured JSON.

**Parameters:**
- `action_items`: List of extracted action items
- `summary`: Meeting summary
- `metadata`: Meeting metadata

**Returns:** Complete structured output with insights

#### `process_meeting(transcript: str, metadata: Optional[Dict] = None) -> Dict`

Complete end-to-end processing (convenience method).

**Parameters:**
- `transcript`: Raw meeting transcript
- `metadata` (optional): Meeting metadata

**Returns:** Complete structured output

## 📊 Output Format

```json
{
  "meeting_metadata": {
    "date": "2026-05-18T00:00:00",
    "participants": ["Alice", "Bob", "Charlie"],
    "processed_at": "2026-05-18T09:30:00.000000"
  },
  "summary": "Team standup covering authentication module completion, code review, and documentation updates.",
  "action_items": [
    {
      "task": "Finish authentication module",
      "owner": "Alice",
      "deadline": "2026-05-22",
      "priority": "High",
      "confidence": 0.95
    }
  ],
  "insights": {
    "total_tasks": 3,
    "high_priority": 2,
    "medium_priority": 1,
    "low_priority": 0,
    "tasks_without_owners": 0,
    "tasks_without_deadlines": 0,
    "average_confidence": 0.93
  }
}
```

## 📁 Project Structure

```
meeting-agent/
├── meeting_agent.py      # Main agent implementation
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variable template
├── README.md            # This file
└── examples/
    ├── sample_input.txt    # Sample meeting transcript
    └── sample_output.json  # Expected output format
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your-api-key-here
```

### Model Selection

By default, the agent uses `gpt-4`. To use a different model, modify the `model` attribute:

```python
agent = MeetingAgent()
agent.model = "gpt-3.5-turbo"  # Faster and cheaper
```

## 💡 Examples

### Example 1: Simple Meeting

**Input:**
```
Team Standup - May 18, 2026
Alice: I'll finish the report by Friday.
Bob: I'll review it next week.
```

**Output:**
```json
{
  "action_items": [
    {
      "task": "Finish the report",
      "owner": "Alice",
      "deadline": "2026-05-22",
      "priority": "Medium",
      "confidence": 0.95
    },
    {
      "task": "Review the report",
      "owner": "Bob",
      "deadline": "2026-05-27",
      "priority": "Medium",
      "confidence": 0.90
    }
  ]
}
```

### Example 2: Complex Meeting

See `examples/sample_input.txt` and `examples/sample_output.json` for a complete example with multiple participants and tasks.

## 🎯 How It Works

1. **Input Parsing**
   - Validates transcript
   - Cleans text
   - Extracts participants and metadata

2. **Action Item Extraction**
   - Sends transcript to LLM with structured prompt
   - Parses LLM response
   - Extracts tasks, owners, deadlines, priorities

3. **Meeting Summarization**
   - Generates concise summary using LLM
   - Focuses on key topics and decisions

4. **Output Formatting**
   - Structures data as JSON
   - Calculates insights and statistics
   - Adds metadata

## 🔍 Key Functions Explained

### `parse_input()`
- Validates input is not empty
- Cleans text (removes extra whitespace, special characters)
- Extracts participant names from text
- Adds metadata (date, participants)

### `extract_action_items()`
- Creates structured prompt for LLM
- Calls OpenAI API
- Parses JSON response
- Returns list of action items

### `summarize_meeting()`
- Creates summarization prompt
- Calls OpenAI API
- Returns concise summary text

### `format_output()`
- Combines all extracted data
- Calculates insights (task counts, priorities, etc.)
- Returns structured JSON output

## 🚨 Error Handling

The agent includes error handling for:
- Missing API key
- Empty transcripts
- LLM API failures
- JSON parsing errors

Errors are logged to console and graceful fallbacks are provided.

## 🔐 Security

- API keys are loaded from environment variables
- No sensitive data is logged
- Transcripts are not stored permanently

## 📈 Performance

- Average processing time: 3-5 seconds per meeting
- Depends on transcript length and LLM model
- Use `gpt-3.5-turbo` for faster processing

## 🛠️ Customization

### Custom Prompts

Modify the `_create_extraction_prompt()` method to customize how action items are extracted:

```python
def _create_extraction_prompt(self, transcript: str, participants: List[str]) -> str:
    # Your custom prompt here
    return f"Custom prompt: {transcript}"
```

### Additional Fields

Add custom fields to action items by modifying the prompt and parsing logic.

### Different LLM Providers

Replace OpenAI client with other providers (Anthropic, Cohere, etc.) by modifying the `extract_action_items()` and `summarize_meeting()` methods.

## 🐛 Troubleshooting

**Issue: "OpenAI API key not found"**
- Solution: Set `OPENAI_API_KEY` in `.env` file

**Issue: "Import openai could not be resolved"**
- Solution: Run `pip install openai python-dotenv`

**Issue: Low confidence scores**
- Solution: Provide more detailed transcripts with explicit task assignments

**Issue: Missing action items**
- Solution: Use clear action verbs (complete, review, update, etc.)

## 📚 Learn More

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Python dotenv](https://pypi.org/project/python-dotenv/)
- [JSON in Python](https://docs.python.org/3/library/json.html)

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- Built with OpenAI GPT models
- Inspired by modern meeting assistant tools

---

**Questions?** Open an issue or reach out for support!

**Happy Meeting Processing! 🎉**