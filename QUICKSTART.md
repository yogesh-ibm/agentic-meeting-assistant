# 🚀 Quick Start Guide

Get up and running with the Meeting Action Item Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
cd meeting-agent
pip install openai python-dotenv pydantic
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Key

1. Get your OpenAI API key from https://platform.openai.com/api-keys

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 3: Run the Example

```bash
python meeting_agent.py
```

You should see:
```
🤖 Initializing Meeting Agent...
============================================================
📝 Parsing input...
🔍 Extracting action items...
📊 Generating summary...
✅ Formatting output...
============================================================
📋 RESULTS
============================================================
{
  "meeting_metadata": { ... },
  "summary": "...",
  "action_items": [ ... ],
  "insights": { ... }
}

💾 Output saved to: meeting_output.json
```

## Step 4: Try Your Own Transcript

Create a file `my_meeting.txt`:
```
Team Meeting - May 18, 2026
Participants: Alice, Bob

Alice: I'll complete the report by Friday.
Bob: I'll review it next week.
```

Process it:
```python
from meeting_agent import MeetingAgent

agent = MeetingAgent()

with open("my_meeting.txt", "r") as f:
    transcript = f.read()

result = agent.process_meeting(transcript)
print(result)
```

## Step 5: Explore Examples

Check out:
- `examples/sample_input.txt` - Sample meeting transcript
- `examples/sample_output.json` - Expected output format

## Common Issues

**"OpenAI API key not found"**
→ Make sure `.env` file exists and contains `OPENAI_API_KEY=...`

**"Import openai could not be resolved"**
→ Run `pip install openai python-dotenv`

**"Rate limit exceeded"**
→ Wait a moment and try again, or upgrade your OpenAI plan

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize prompts in `meeting_agent.py`
- Integrate into your own applications
- Try different meeting formats

## Need Help?

- Check [README.md](README.md) for full documentation
- Review code comments in `meeting_agent.py`
- Open an issue on GitHub

---

**Happy Meeting Processing! 🎉**