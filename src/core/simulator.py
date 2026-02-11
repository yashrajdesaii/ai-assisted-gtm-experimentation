import random
from .models import Lead, Message, ExperimentResult, Hypothesis

class FunnelSimulator:
    def simulate_outcome(self, lead: Lead, message: Message, hypothesis: Hypothesis) -> ExperimentResult:
        """
        Simulate the outcome of sending a message to a lead.
        Uses a weighted probability model based on 'hooks' and 'persona fit'.
        """
        
        # Base conversion rates (industry averagesish)
        p_open = 0.40
        p_reply = 0.05
        p_meeting = 0.015

        # Intelligence Layer: Adjust probabilities based on simulated 'quality'
        # 1. Relevance Boost: If message mentions a specific trigger
        start_trigger_bonus = 0.0
        if lead.triggers:
            for trigger in lead.triggers:
                if trigger.lower() in message.content.lower():
                    start_trigger_bonus += 0.15 # Huge boost for personalization
        
        # 2. Persona/Hypothesis Fit
        # Example logic: 'VP of Sales' loves 'ROI' (Variant A), 'Founder' loves 'Vision' (Variant B)
        # This is hardcoded for the "simulation" effect requested in PRD
        variant_bonus = 0.0
        title = lead.title.lower()
        if "sales" in title and "roi" in hypothesis.description.lower():
             variant_bonus += 0.10
        elif "founder" in title and "social proof" in hypothesis.description.lower():
             variant_bonus += 0.10
        elif "engineer" in title and "technical" in hypothesis.description.lower():
             variant_bonus += 0.15

        # Apply modifiers
        final_p_open = min(0.9, p_open + (start_trigger_bonus * 0.5))
        final_p_reply = min(0.4, p_reply + start_trigger_bonus + variant_bonus)
        final_p_meeting = min(0.2, p_meeting + (variant_bonus * 0.5))

        # Monte Carlo Simulation
        is_sent = True
        is_opened = random.random() < final_p_open
        is_replied = False
        is_meeting = False

        if is_opened:
            is_replied = random.random() < final_p_reply
        
        if is_replied:
            is_meeting = random.random() < final_p_meeting
            
        return ExperimentResult(
            lead_id=lead.name,
            variant_chosen=message.variant_type,
            sent=is_sent,
            opened=is_opened,
            replied=is_replied,
            meeting_booked=is_meeting
        )
