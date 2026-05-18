"""
Enhanced Meeting Action Item Agent with Agentic Intelligence
Includes smart inference, deadline estimation, priority classification, and ambiguity detection
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Run: pip install openai python-dotenv")
    exit(1)


class AgenticMeetingAgent:
    """Enhanced agent with intelligent reasoning capabilities"""
    
    # Urgency keywords for priority classification
    URGENCY_KEYWORDS = {
        'high': ['urgent', 'critical', 'asap', 'immediately', 'emergency', 'blocker', 'must', 'crucial'],
        'medium': ['important', 'should', 'need', 'required', 'necessary'],
        'low': ['nice to have', 'optional', 'when possible', 'eventually', 'consider']
    }
    
    # Time indicators for deadline estimation
    TIME_INDICATORS = {
        'today': 0,
        'tomorrow': 1,
        'this week': 5,
        'next week': 7,
        'this month': 20,
        'next month': 30,
        'this quarter': 60,
        'asap': 2,
        'urgent': 2,
        'soon': 5
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the enhanced agent"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4"
    
    def parse_input(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse and validate input with enhanced metadata extraction"""
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")
        
        cleaned_transcript = self._clean_text(transcript)
        
        parsed_metadata = metadata or {}
        if not parsed_metadata.get("date"):
            parsed_metadata["date"] = datetime.now().isoformat()
        
        if not parsed_metadata.get("participants"):
            parsed_metadata["participants"] = self._extract_participants(cleaned_transcript)
        
        # Extract urgency indicators
        urgency_context = self._extract_urgency_context(cleaned_transcript)
        
        return {
            "transcript": cleaned_transcript,
            "metadata": parsed_metadata,
            "word_count": len(cleaned_transcript.split()),
            "urgency_context": urgency_context
        }
    
    def extract_action_items(self, parsed_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract action items with enhanced agentic reasoning"""
        transcript = parsed_input["transcript"]
        participants = parsed_input["metadata"].get("participants", [])
        urgency_context = parsed_input.get("urgency_context", {})
        
        # Create enhanced prompt with agentic instructions
        prompt = self._create_enhanced_extraction_prompt(transcript, participants)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an intelligent meeting analyst with reasoning capabilities. 
                        Extract action items and use your intelligence to:
                        1. Infer missing owners based on context and roles
                        2. Estimate deadlines from time indicators
                        3. Classify priority based on urgency words
                        4. Flag ambiguous or unclear tasks
                        Always provide reasoning for your inferences."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            action_items = self._parse_llm_response(content)
            
            # Apply agentic enhancements
            enhanced_items = []
            for item in action_items:
                enhanced_item = self._apply_agentic_magic(item, parsed_input)
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return []
    
    def _apply_agentic_magic(self, item: Dict[str, Any], parsed_input: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent reasoning to enhance action items"""
        
        # 1. Smart owner inference
        if not item.get("owner") or item.get("owner") == "Unknown":
            inferred_owner, reasoning = self._infer_owner(
                item.get("task", ""),
                parsed_input["transcript"],
                parsed_input["metadata"].get("participants", [])
            )
            if inferred_owner:
                item["owner"] = inferred_owner
                item["flags"] = item.get("flags", []) + ["owner_inferred"]
                item["reasoning"] = item.get("reasoning", "") + f" Owner inferred: {reasoning}"
        
        # 2. Deadline estimation
        if not item.get("deadline"):
            estimated_deadline, reasoning = self._estimate_deadline(
                item.get("task", ""),
                item.get("priority", "Medium"),
                parsed_input["transcript"]
            )
            if estimated_deadline:
                item["deadline"] = estimated_deadline
                item["flags"] = item.get("flags", []) + ["deadline_estimated"]
                item["reasoning"] = item.get("reasoning", "") + f" Deadline estimated: {reasoning}"
        
        # 3. Priority classification based on urgency
        if not item.get("priority") or item.get("priority") == "Medium":
            classified_priority, reasoning = self._classify_priority_smart(
                item.get("task", ""),
                parsed_input["transcript"],
                parsed_input.get("urgency_context", {})
            )
            item["priority"] = classified_priority
            if reasoning:
                item["reasoning"] = item.get("reasoning", "") + f" Priority: {reasoning}"
        
        # 4. Flag ambiguous tasks
        ambiguity_flags = self._detect_ambiguity(item.get("task", ""))
        if ambiguity_flags:
            item["flags"] = item.get("flags", []) + ambiguity_flags
            item["ambiguity_notes"] = self._generate_ambiguity_notes(ambiguity_flags)
        
        # Ensure flags is a list
        if "flags" not in item:
            item["flags"] = []
        
        return item
    
    def _infer_owner(self, task: str, transcript: str, participants: List[str]) -> Tuple[Optional[str], str]:
        """Intelligently infer task owner from context"""
        
        # Look for task mentions near participant names
        task_lower = task.lower()
        
        # Check for explicit mentions
        for participant in participants:
            # Look for patterns like "John will...", "Sarah to...", "Mike should..."
            patterns = [
                rf"{participant}[:\s]+.*?{re.escape(task_lower[:20])}",
                rf"{re.escape(task_lower[:20])}.*?{participant}",
                rf"{participant}.*?(will|should|to|can)\s+\w+.*?{re.escape(task_lower[:15])}"
            ]
            
            for pattern in patterns:
                if re.search(pattern, transcript, re.IGNORECASE):
                    return participant, f"mentioned in context of task"
        
        # Infer from role-based keywords
        role_keywords = {
            'ui': ['design', 'mockup', 'interface', 'frontend', 'ui', 'ux'],
            'backend': ['api', 'database', 'server', 'backend', 'integration'],
            'qa': ['test', 'testing', 'qa', 'quality', 'verify'],
            'pm': ['plan', 'schedule', 'coordinate', 'organize', 'meeting']
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                # Find participant who might have this role
                for participant in participants:
                    if role in participant.lower() or any(kw in transcript.lower() for kw in keywords):
                        return participant, f"inferred from role-related keywords: {role}"
        
        # If only one participant, assign to them
        if len(participants) == 1:
            return participants[0], "only participant in meeting"
        
        return None, "insufficient context to infer owner"
    
    def _estimate_deadline(self, task: str, priority: str, transcript: str) -> Tuple[Optional[str], str]:
        """Estimate deadline based on priority and context"""
        
        task_lower = task.lower()
        transcript_lower = transcript.lower()
        
        # Look for time indicators in task or nearby context
        for indicator, days in self.TIME_INDICATORS.items():
            if indicator in task_lower or indicator in transcript_lower:
                deadline = datetime.now() + timedelta(days=days)
                return deadline.strftime("%Y-%m-%d"), f"based on '{indicator}' indicator"
        
        # Estimate based on priority
        priority_deadlines = {
            'High': 3,      # 3 days for high priority
            'Medium': 7,    # 1 week for medium priority
            'Low': 14       # 2 weeks for low priority
        }
        
        days = priority_deadlines.get(priority, 7)
        deadline = datetime.now() + timedelta(days=days)
        return deadline.strftime("%Y-%m-%d"), f"estimated based on {priority} priority ({days} days)"
    
    def _classify_priority_smart(self, task: str, transcript: str, urgency_context: Dict) -> Tuple[str, str]:
        """Intelligently classify priority based on urgency indicators"""
        
        task_lower = task.lower()
        transcript_lower = transcript.lower()
        
        # Check for urgency keywords
        for priority, keywords in self.URGENCY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in task_lower or keyword in transcript_lower:
                    return priority.capitalize(), f"detected urgency keyword: '{keyword}'"
        
        # Check for deadline proximity
        deadline_patterns = [
            (r'today|now|immediately', 'High', 'immediate deadline'),
            (r'tomorrow|asap', 'High', 'urgent deadline'),
            (r'this week|friday', 'High', 'this week deadline'),
            (r'next week', 'Medium', 'next week deadline'),
            (r'this month|soon', 'Medium', 'this month deadline'),
            (r'eventually|someday', 'Low', 'flexible deadline')
        ]
        
        for pattern, priority, reason in deadline_patterns:
            if re.search(pattern, task_lower) or re.search(pattern, transcript_lower):
                return priority, reason
        
        # Default to Medium
        return 'Medium', 'no specific urgency indicators found'
    
    def _detect_ambiguity(self, task: str) -> List[str]:
        """Detect ambiguous or unclear tasks"""
        flags = []
        
        task_lower = task.lower()
        
        # Check for vague verbs
        vague_verbs = ['handle', 'deal with', 'look at', 'check', 'review', 'consider', 'think about']
        if any(verb in task_lower for verb in vague_verbs):
            flags.append("vague_action")
        
        # Check for missing specifics
        if len(task.split()) < 4:
            flags.append("too_brief")
        
        # Check for questions
        if '?' in task:
            flags.append("contains_question")
        
        # Check for multiple actions
        if ' and ' in task_lower or ' or ' in task_lower:
            if task_lower.count(' and ') > 1 or task_lower.count(' or ') > 1:
                flags.append("multiple_actions")
        
        # Check for unclear scope
        unclear_words = ['something', 'stuff', 'things', 'maybe', 'possibly']
        if any(word in task_lower for word in unclear_words):
            flags.append("unclear_scope")
        
        return flags
    
    def _generate_ambiguity_notes(self, flags: List[str]) -> str:
        """Generate helpful notes about ambiguities"""
        notes = []
        
        flag_messages = {
            "vague_action": "Task uses vague action verb - consider being more specific",
            "too_brief": "Task description is very brief - may need more details",
            "contains_question": "Task is phrased as a question - clarify the action needed",
            "multiple_actions": "Task contains multiple actions - consider splitting",
            "unclear_scope": "Task scope is unclear - define boundaries and deliverables"
        }
        
        for flag in flags:
            if flag in flag_messages:
                notes.append(flag_messages[flag])
        
        return "; ".join(notes)
    
    def _extract_urgency_context(self, text: str) -> Dict[str, Any]:
        """Extract urgency indicators from text"""
        urgency_found = []
        
        for priority, keywords in self.URGENCY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text.lower():
                    urgency_found.append({
                        'keyword': keyword,
                        'priority': priority
                    })
        
        return {
            'indicators': urgency_found,
            'has_urgency': len(urgency_found) > 0
        }
    
    def summarize_meeting(self, parsed_input: Dict[str, Any]) -> str:
        """Generate meeting summary"""
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
                    {"role": "system", "content": "You are a concise meeting summarizer."},
                    {"role": "user", "content": prompt}
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
        """Format output with agentic insights"""
        
        insights = self._calculate_insights(action_items)
        
        # Add agentic insights
        agentic_insights = self._calculate_agentic_insights(action_items)
        insights.update(agentic_insights)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(action_items)
        
        output = {
            "meeting_metadata": {
                "date": metadata.get("date"),
                "participants": metadata.get("participants", []),
                "processed_at": datetime.now().isoformat()
            },
            "summary": summary,
            "action_items": action_items,
            "insights": insights,
            "suggestions": suggestions,
            "agentic_enhancements": {
                "owners_inferred": sum(1 for item in action_items if "owner_inferred" in item.get("flags", [])),
                "deadlines_estimated": sum(1 for item in action_items if "deadline_estimated" in item.get("flags", [])),
                "ambiguous_tasks": sum(1 for item in action_items if any(f.startswith("vague") or f.startswith("unclear") for f in item.get("flags", [])))
            }
        }
        
        return output
    
    def _calculate_agentic_insights(self, action_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate insights about agentic enhancements"""
        return {
            "inferred_owners": sum(1 for item in action_items if "owner_inferred" in item.get("flags", [])),
            "estimated_deadlines": sum(1 for item in action_items if "deadline_estimated" in item.get("flags", [])),
            "flagged_ambiguous": sum(1 for item in action_items if any(
                f in ["vague_action", "unclear_scope", "too_brief"] 
                for f in item.get("flags", [])
            ))
        }
    
    def _generate_suggestions(self, action_items: List[Dict[str, Any]]) -> List[str]:
        """Generate intelligent suggestions"""
        suggestions = []
        
        # Check for inferred information
        inferred_count = sum(1 for item in action_items if "owner_inferred" in item.get("flags", []))
        if inferred_count > 0:
            suggestions.append(f"⚠️ {inferred_count} task owner(s) were inferred - please verify assignments")
        
        estimated_count = sum(1 for item in action_items if "deadline_estimated" in item.get("flags", []))
        if estimated_count > 0:
            suggestions.append(f"📅 {estimated_count} deadline(s) were estimated - confirm with team")
        
        # Check for ambiguous tasks
        ambiguous = [item for item in action_items if any(
            f in ["vague_action", "unclear_scope", "too_brief"] 
            for f in item.get("flags", [])
        )]
        if ambiguous:
            suggestions.append(f"🚩 {len(ambiguous)} task(s) flagged as ambiguous - clarification recommended")
        
        # Check for high priority clustering
        high_priority = [item for item in action_items if item.get("priority") == "High"]
        if len(high_priority) > len(action_items) * 0.7:
            suggestions.append("⚡ Many high-priority tasks - consider prioritizing further")
        
        # Check for missing owners
        no_owner = [item for item in action_items if not item.get("owner")]
        if no_owner:
            suggestions.append(f"👤 {len(no_owner)} task(s) still need owner assignment")
        
        return suggestions
    
    def process_meeting(
        self,
        transcript: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete end-to-end processing with agentic intelligence"""
        print("🤖 Initializing Agentic Meeting Agent...")
        print("📝 Parsing input with intelligence...")
        parsed_input = self.parse_input(transcript, metadata)
        
        print("🧠 Extracting action items with smart reasoning...")
        action_items = self.extract_action_items(parsed_input)
        
        print("📊 Generating summary...")
        summary = self.summarize_meeting(parsed_input)
        
        print("✨ Applying agentic magic...")
        print("   • Inferring missing owners")
        print("   • Estimating deadlines")
        print("   • Classifying priorities")
        print("   • Detecting ambiguities")
        
        print("✅ Formatting output with insights...")
        output = self.format_output(action_items, summary, parsed_input["metadata"])
        
        return output
    
    # Helper methods (same as base agent)
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\"\'\/\n]', '', text)
        return text.strip()
    
    def _extract_participants(self, text: str) -> List[str]:
        participants = set()
        participant_match = re.search(r'(?:Participants?|Attendees?):\s*([^\n]+)', text, re.IGNORECASE)
        if participant_match:
            names = re.split(r'[,;]|\sand\s', participant_match.group(1))
            for name in names:
                name = name.strip()
                if name and len(name.split()) <= 3:
                    participants.add(name)
        speaker_matches = re.findall(r'^([A-Z][a-z]+):\s', text, re.MULTILINE)
        participants.update(speaker_matches)
        return sorted(list(participants))
    
    def _create_enhanced_extraction_prompt(self, transcript: str, participants: List[str]) -> str:
        participants_str = ", ".join(participants) if participants else "Unknown"
        
        return f"""Analyze this meeting transcript and extract ALL action items with intelligent reasoning.

Meeting Transcript:
{transcript}

Participants: {participants_str}

For each action item, provide:
1. task: Clear description
2. owner: Person responsible (infer if not explicit)
3. deadline: Due date (estimate if not mentioned)
4. priority: High/Medium/Low (classify based on urgency)
5. confidence: Your confidence score (0.0-1.0)
6. flags: Any issues (e.g., "owner_inferred", "deadline_estimated", "vague_action")
7. reasoning: Brief explanation of your inferences

Return ONLY valid JSON:
{{
  "action_items": [
    {{
      "task": "Complete project proposal",
      "owner": "John Doe",
      "deadline": "2026-05-25",
      "priority": "High",
      "confidence": 0.95,
      "flags": [],
      "reasoning": "Explicitly stated by John"
    }}
  ]
}}"""
    
    def _parse_llm_response(self, content: str) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content)
            return data.get("action_items", [])
        except json.JSONDecodeError:
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                return data.get("action_items", [])
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("action_items", [])
            return []
    
    def _calculate_insights(self, action_items: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    """Example usage with agentic magic"""
    
    # Sample with missing information to showcase agentic capabilities
    sample_transcript = """
    Team Meeting - May 18, 2026
    Participants: Alice, Bob, Charlie
    
    We need to fix the critical login bug ASAP.
    Someone should update the documentation.
    The UI needs a refresh - it's important but not urgent.
    We should consider adding analytics eventually.
    """
    
    print("🤖 Initializing Enhanced Agentic Meeting Agent...")
    agent = AgenticMeetingAgent()
    
    print("\n" + "="*70)
    result = agent.process_meeting(sample_transcript)
    
    print("\n" + "="*70)
    print("📋 RESULTS WITH AGENTIC MAGIC")
    print("="*70)
    print(json.dumps(result, indent=2))
    
    output_file = "agentic_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Output saved to: {output_file}")
    
    print("\n✨ AGENTIC ENHANCEMENTS APPLIED:")
    enhancements = result.get("agentic_enhancements", {})
    print(f"   • Owners inferred: {enhancements.get('owners_inferred', 0)}")
    print(f"   • Deadlines estimated: {enhancements.get('deadlines_estimated', 0)}")
    print(f"   • Ambiguous tasks flagged: {enhancements.get('ambiguous_tasks', 0)}")


if __name__ == "__main__":
    main()

# Made with Bob
