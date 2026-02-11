from src.core.models import Lead, Hypothesis, Message
from src.core.agents import Researcher, Strategist
from src.core.simulator import FunnelSimulator

def test_flow():
    print("Testing Backend Flow...")
    
    # 1. Setup Lead
    lead = Lead(name="Test User", title="VP Sales", company="TestCorp")
    print(f"Lead created: {lead.name}")

    # 2. Research
    researcher = Researcher() # Will use simulation if no key
    lead = researcher.research_lead(lead)
    print(f"Researched: {lead.triggers}")
    
    # 3. Strategy
    hypothesis = Hypothesis(
        name="ROI Focus", 
        description="Focus on saving money.", 
        experiment_variant="A"
    )
    strategist = Strategist()
    msg = strategist.generate_message(lead, hypothesis, "Professional")
    print(f"Message Generated: {msg.subject_line} - {msg.content[:50]}...")
    
    # 4. Simulate
    simulator = FunnelSimulator()
    result = simulator.simulate_outcome(lead, msg, hypothesis)
    print(f"Simulation Result: Meeting Booked? {result.meeting_booked}")

if __name__ == "__main__":
    test_flow()
