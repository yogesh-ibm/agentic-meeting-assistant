"""
Meeting Action Item Agent
A simple, modular agent that extracts action items from meeting transcripts using LLM.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import OpenAI, provide helpful error if not available
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Run: pip install openai python-dotenv")
    exit(1)


class MeetingAgent:
    """Main agent class for processing meeting transcripts"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Meeting Agent
        
        Args:
            api_key: OpenAI API key (if not provided, reads from OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Read from env or default to gpt-3.5-turbo
    
    def parse_input(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse and validate input transcript
        
        Args:
            transcript: Raw meeting transcript text
            metadata: Optional metadata (date, participants, etc.)
        
        Returns:
            Parsed input dictionary
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")
        
        # Clean the transcript
        cleaned_transcript = self._clean_text(transcript)
        
        # Extract or use provided metadata
        parsed_metadata = metadata or {}
        if not parsed_metadata.get("date"):
            parsed_metadata["date"] = datetime.now().isoformat()
        
        if not parsed_metadata.get("participants"):
            parsed_metadata["participants"] = self._extract_participants(cleaned_transcript)
        
        return {
            "transcript": cleaned_transcript,
            "metadata": parsed_metadata,
            "word_count": len(cleaned_transcript.split())
        }
    
    def extract_action_items(self, parsed_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract action items from parsed transcript using LLM
        
        Args:
            parsed_input: Parsed input from parse_input()
        
        Returns:
            List of action items with task, owner, deadline, priority
        """
        transcript = parsed_input["transcript"]
        participants = parsed_input["metadata"].get("participants", [])
        
        # Create prompt for LLM
        prompt = self._create_extraction_prompt(transcript, participants)
        
        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert meeting analyst. Extract action items accurately and return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse LLM response
            content = response.choices[0].message.content
            action_items = self._parse_llm_response(content)
            
            return action_items
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return []
    
    def summarize_meeting(self, parsed_input: Dict[str, Any]) -> str:
        """
        Generate a concise meeting summary
        
        Args:
            parsed_input: Parsed input from parse_input()
        
        Returns:
            Meeting summary text
        """
        transcript = parsed_input["transcript"]
        
        prompt = f"""Summarize this meeting in 2-3 sentences. Focus on:
- Main topics discussed
- Key decisions made
- Overall meeting purpose

Meeting Transcript:
{transcript}

Provide only the summary, no additional text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise meeting summarizer."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Unable to generate summary."
    
    def format_output(
        self,
        action_items: List[Dict[str, Any]],
        summary: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format final output as structured JSON
        
        Args:
            action_items: List of extracted action items
            summary: Meeting summary
            metadata: Meeting metadata
        
        Returns:
            Structured output dictionary
        """
        # Calculate insights
        insights = self._calculate_insights(action_items)
        
        output = {
            "meeting_metadata": {
                "date": metadata.get("date"),
                "participants": metadata.get("participants", []),
                "processed_at": datetime.now().isoformat()
            },
            "summary": summary,
            "action_items": action_items,
            "insights": insights
        }
        
        return output
    
    def process_meeting(
        self,
        transcript: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end processing of a meeting transcript
        
        Args:
            transcript: Raw meeting transcript
            metadata: Optional metadata
        
        Returns:
            Complete structured output
        """
        print("📝 Parsing input...")
        parsed_input = self.parse_input(transcript, metadata)
        
        print("🔍 Extracting action items...")
        action_items = self.extract_action_items(parsed_input)
        
        print("📊 Generating summary...")
        summary = self.summarize_meeting(parsed_input)
        
        print("✅ Formatting output...")
        output = self.format_output(action_items, summary, parsed_input["metadata"])
        
        return output
    
    # Helper methods
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\"\'\/\n]', '', text)
        return text.strip()
    
    def _extract_participants(self, text: str) -> List[str]:
        """Extract participant names from text"""
        participants = set()
        
        # Look for "Participants:" or "Attendees:" lines
        participant_match = re.search(r'(?:Participants?|Attendees?):\s*([^\n]+)', text, re.IGNORECASE)
        if participant_match:
            names = re.split(r'[,;]|\sand\s', participant_match.group(1))
            for name in names:
                name = name.strip()
                if name and len(name.split()) <= 3:
                    participants.add(name)
        
        # Look for speaker labels (Name: text)
        speaker_matches = re.findall(r'^([A-Z][a-z]+):\s', text, re.MULTILINE)
        participants.update(speaker_matches)
        
        return sorted(list(participants))
    
    def _create_extraction_prompt(self, transcript: str, participants: List[str]) -> str:
        """Create prompt for action item extraction"""
        participants_str = ", ".join(participants) if participants else "Unknown"
        
        return f"""Analyze this meeting transcript and extract ALL action items.

Meeting Transcript:
{transcript}

Participants: {participants_str}

For each action item, provide:
1. task: Clear description of what needs to be done
2. owner: Person responsible (if mentioned or can be inferred)
3. deadline: Due date in YYYY-MM-DD format (if mentioned or can be inferred)
4. priority: "High", "Medium", or "Low" based on urgency
5. confidence: Your confidence score (0.0-1.0)

Return ONLY a JSON array in this exact format:
{{
  "action_items": [
    {{
      "task": "Complete project proposal",
      "owner": "John Doe",
      "deadline": "2026-05-25",
      "priority": "High",
      "confidence": 0.95
    }}
  ]
}}

If no action items found, return: {{"action_items": []}}"""
    
    def _parse_llm_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract action items"""
        try:
            # Try to parse as JSON directly
            data = json.loads(content)
            return data.get("action_items", [])
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                return data.get("action_items", [])
            
            # Try to extract any JSON object
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("action_items", [])
            
            print("Warning: Could not parse LLM response as JSON")
            return []
    
    def _calculate_insights(self, action_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate insights from action items"""
        total = len(action_items)
        
        priority_counts = {"High": 0, "Medium": 0, "Low": 0}
        tasks_without_owners = 0
        tasks_without_deadlines = 0
        total_confidence = 0.0
        
        for item in action_items:
            priority = item.get("priority", "Medium")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            if not item.get("owner"):
                tasks_without_owners += 1
            
            if not item.get("deadline"):
                tasks_without_deadlines += 1
            
            total_confidence += item.get("confidence", 0.0)
        
        avg_confidence = total_confidence / total if total > 0 else 0.0
        
        return {
            "total_tasks": total,
            "high_priority": priority_counts.get("High", 0),
            "medium_priority": priority_counts.get("Medium", 0),
            "low_priority": priority_counts.get("Low", 0),
            "tasks_without_owners": tasks_without_owners,
            "tasks_without_deadlines": tasks_without_deadlines,
            "average_confidence": round(avg_confidence, 2)
        }


def main():
    """Example usage"""
    
    # Sample meeting transcript
    sample_transcript = """
    Team Standup - May 18, 2026
    Participants: Alice, Bob, Charlie
    
    Alice: I'll finish the user authentication module by Friday, May 22nd.
    Bob: I need to review Alice's code and deploy to staging by next Tuesday.
    Charlie: I'll update the documentation this week. It's important we have this ready.
    
    Next meeting: Monday 10 AM
    """
    
    # Initialize agent
    print("🤖 Initializing Meeting Agent...")
    agent = MeetingAgent()
    
    # Process meeting
    print("\n" + "="*60)
    result = agent.process_meeting(sample_transcript)
    
    # Display results
    print("\n" + "="*60)
    print("📋 RESULTS")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    # Save to file
    output_file = "meeting_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Output saved to: {output_file}")


if __name__ == "__main__":
    main()

# Made with Bob
