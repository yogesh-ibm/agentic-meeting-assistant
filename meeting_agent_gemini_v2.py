"""
Meeting Action Item Agent - Gemini Version (Updated)
A simple, modular agent that extracts action items from meeting transcripts using Google Gemini.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Google GenAI (new package)
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Google GenAI library not installed. Run: pip install google-genai")
    exit(1)


class MeetingAgentGemini:
    """Main agent class for processing meeting transcripts using Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Meeting Agent with Gemini
        
        Args:
            api_key: Google API key (if not provided, reads from GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"  # Using the latest available model
    
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
        Extract action items from parsed transcript using Gemini
        
        Args:
            parsed_input: Parsed input from parse_input()
        
        Returns:
            List of action items with task, owner, deadline, priority
        """
        transcript = parsed_input["transcript"]
        participants = parsed_input["metadata"].get("participants", [])
        
        # Create prompt for Gemini
        prompt = self._create_extraction_prompt(transcript, participants)
        
        # Call Gemini
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Parse Gemini response
            content = response.text
            action_items = self._parse_llm_response(content)
            
            return action_items
            
        except Exception as e:
            print(f"Error calling Gemini: {e}")
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
            
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
            metadata: Optional meeting metadata
        
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
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-:.,!?]', '', text)
        return text.strip()
    
    def _extract_participants(self, transcript: str) -> List[str]:
        """Extract participant names from transcript"""
        # Look for patterns like "Name:" or "Name said"
        pattern = r'([A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?:'
        matches = re.findall(pattern, transcript)
        # Remove duplicates and return
        return list(set(matches))
    
    def _create_extraction_prompt(self, transcript: str, participants: List[str]) -> str:
        """Create prompt for action item extraction"""
        participants_str = ", ".join(participants) if participants else "Unknown"
        
        prompt = f"""Extract action items from this meeting transcript.

Meeting Participants: {participants_str}

For each action item, provide:
1. task: Clear description of what needs to be done
2. owner: Person responsible (from participants list, or "Unassigned")
3. deadline: Due date in YYYY-MM-DD format (infer from context, or use "TBD")
4. priority: "High", "Medium", or "Low"
5. confidence: Your confidence in this extraction (0.0 to 1.0)

Return ONLY a valid JSON array of action items. No additional text.

Example format:
[
  {{
    "task": "Complete the report",
    "owner": "Alice",
    "deadline": "2026-05-25",
    "priority": "High",
    "confidence": 0.95
  }}
]

Meeting Transcript:
{transcript}

JSON array of action items:"""
        
        return prompt
    
    def _parse_llm_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured action items"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                action_items = json.loads(json_str)
                return action_items
            else:
                print("No JSON found in response")
                return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
    
    def _calculate_insights(self, action_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate insights from action items"""
        total_tasks = len(action_items)
        
        priority_counts = {
            "high_priority": sum(1 for item in action_items if item.get("priority", "").lower() == "high"),
            "medium_priority": sum(1 for item in action_items if item.get("priority", "").lower() == "medium"),
            "low_priority": sum(1 for item in action_items if item.get("priority", "").lower() == "low")
        }
        
        tasks_without_owners = sum(1 for item in action_items if not item.get("owner") or item.get("owner") == "Unassigned")
        tasks_without_deadlines = sum(1 for item in action_items if not item.get("deadline") or item.get("deadline") == "TBD")
        
        confidences = [item.get("confidence", 0.0) for item in action_items]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "total_tasks": total_tasks,
            **priority_counts,
            "tasks_without_owners": tasks_without_owners,
            "tasks_without_deadlines": tasks_without_deadlines,
            "average_confidence": round(avg_confidence, 2)
        }


def main():
    """Example usage"""
    print("🤖 Initializing Meeting Agent (Gemini v2)...")
    print("=" * 60)
    
    # Initialize agent
    agent = MeetingAgentGemini()
    
    # Sample transcript
    sample_transcript = """
    Team Standup - May 20, 2026
    Participants: Alice, Bob
    
    Alice: I'll finish the authentication module by Friday.
    Bob: I need to review the code and deploy to staging by next week.
    Alice: Also, I'll update the documentation this week.
    """
    
    # Process meeting
    result = agent.process_meeting(sample_transcript)
    
    # Display results
    print("=" * 60)
    print("📋 RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    # Save to file
    output_file = "meeting_output_gemini.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Output saved to: {output_file}")


if __name__ == "__main__":
    main()

# Made with Bob
