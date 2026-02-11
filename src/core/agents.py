import os
import random
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .models import Lead, Message, Hypothesis

# Mock data for fallback/simulation
MOCK_TRIGGERS = [
    "Recently raised Series B funding",
    "Hiring for Head of Sales",
    "expanding into APAC region",
    "Released new API documentation",
    "Featured in TechCrunch top startups"
]

class BaseAgent:
    def __init__(self, model_name="gpt-4o", temperature=0.7):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY"):
             self.llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=temperature)
        elif self.api_key:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        else:
            self.llm = None  # Fallback mode
            print("Warning: No API Key found. Using simulation mode.")

class Researcher(BaseAgent):
    def research_lead(self, lead: Lead) -> Lead:
        """
        Research a lead to find triggers.
        In a real scenario, this would use web search tools.
        Here we simulate or use LLM knowledge if available.
        """
        if self.llm:
            # Real LLM-based "research" (hallucinated triggers based on company name for now if no web access)
            prompt = ChatPromptTemplate.from_template(
                "You are an expert lead researcher. For the company {company} and title {title}, "
                "generate 3 plausible 'trigger events' that would make them a good prospect for B2B SaaS. "
                "Return them as a comma-separated list."
            )
            chain = prompt | self.llm | StrOutputParser()
            try:
                result = chain.invoke({"company": lead.company, "title": lead.title})
                lead.triggers = [t.strip() for t in result.split(',')]
            except Exception as e:
                print(f"Error researching {lead.company}: {e}")
                lead.triggers = random.sample(MOCK_TRIGGERS, 2)
        else:
            # Simulation mode
            lead.triggers = random.sample(MOCK_TRIGGERS, 2)
        
        # Also generate a mini persona profile
        lead.persona_profile = {
            "pain_points": ["Manual data entry", "Low conversion rates", "Lack of visibility"],
            "goals": ["Increase pipeline", "Automate outreach", "Improve ROI"],
            "kpis": ["Meeting booked rate", "CAC", "LTV"]
        }
        return lead

class Strategist(BaseAgent):
    def generate_message(self, lead: Lead, hypothesis: Hypothesis, variant: str) -> Message:
        """
        Generate a message based on the hypothesis and lead triggers.
        """
        if self.llm:
            prompt = ChatPromptTemplate.from_template(
                "You are a world-class Growth Strategist. Write a cold email to {name}, {title} at {company}. \n"
                "Context: They recently experienced these triggers: {triggers}. \n"
                "Hypothesis to test: {hypothesis_desc} \n"
                "Goal: Book a meeting. \n"
                "Style: {variant} (e.g., specific tone or structure). \n"
                "Keep it under 150 words. Return JSON with 'subject', 'body', and 'reasoning'."
            )
            # Simple simulation for JSON return for now
            # In production, use JsonOutputParser
            chain = prompt | self.llm | StrOutputParser()
            try:
                raw_result = chain.invoke({
                    "name": lead.name,
                    "title": lead.title,
                    "company": lead.company,
                    "triggers": ", ".join(lead.triggers),
                    "hypothesis_desc": hypothesis.description,
                    "variant": hypothesis.experiment_variant
                })
                # Basic parsing (LLM might not always return perfect JSON without strict mode)
                # For robustness in this demo, we'll just treat the whole text as body if parsing fails
                import json
                try:
                    data = json.loads(raw_result)
                    content = data.get("body", raw_result)
                    subject = data.get("subject", "Quick question")
                    reasoning = data.get("reasoning", "Aligned with hypothesis")
                except:
                    # Fallback if not valid JSON
                    content = raw_result
                    subject = f"Question for {lead.name}"
                    reasoning = "Generated based on prompt"

            except Exception as e:
                print(f"Error generating message: {e}")
                content = f"Hi {lead.name}, spotted your news about {lead.triggers[0]}. adhering to {hypothesis.name}."
                subject = "Connect?"
                reasoning = "Fallback generation"
        else:
            # Simulation mode
            content = (f"Hi {lead.name}, \n\n"
                      f"Saw that {lead.company} is {lead.triggers[0] if lead.triggers else 'growing'}. "
                      f"Our solution fits your need for {hypothesis.name}. \n\n"
                      "Constructed via Simulation logic.")
            subject = f"Idea for {lead.company}"
            reasoning = "Simulated output based on fixed templates."

        return Message(
            content=content,
            subject_line=subject,
            variant_type=variant,
            reasoning=reasoning,
            lead_id=lead.name # Using name as ID for simplicity
        )
