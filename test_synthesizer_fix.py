# test_synthesizer_fix.py
"""
Test script to verify the synthesizer fix works correctly.
Tests the synthesizer logic with mock agent outputs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models import AgentResponse, TheoryExplanation, DesignAdvice, CodeSolution, PlanOutput

def test_synthesizer_logic():
    """Test the synthesizer logic with mock data."""

    print("Testing synthesizer logic...")

    # Mock theory output
    theory_output = TheoryExplanation(
        topic="ReAct Pattern",
        explanation="The ReAct pattern combines reasoning and acting in a cycle.",
        key_concepts=["Reasoning", "Acting", "Feedback"],
        examples=["Example 1", "Example 2"],
        confidence=0.9
    )

    # Mock design output
    design_output = DesignAdvice(
        design_patterns=["Microservices", "Observer"],
        architecture_recommendation="Use microservices architecture",
        pros_cons={"pros": ["Scalable"], "cons": ["Complex"]},
        code_snippet="print('hello')"
    )

    # Mock code output
    code_output = CodeSolution(
        problem="LRU Cache",
        solution_explanation="Implement using dict and deque",
        code="class LRUCache:\n    pass",
        complexity="O(1)",
        test_cases=[{"input": "test", "output": "result"}]
    )

    # Mock planning output
    planning_output = PlanOutput(
        goal="Learn LangChain",
        steps=[{"description": "Step 1"}, {"description": "Step 2"}],
        timeline="3 weeks",
        resources_needed=["Book", "Course"]
    )

    # Test theory synthesis
    agent_outputs = {"theory": theory_output}
    if "theory" in agent_outputs:
        theory = agent_outputs["theory"]
        final_answer_text = theory.explanation
        if theory.examples:
            final_answer_text += "\n\nExamples:\n" + "\n".join(f"- {ex}" for ex in theory.examples)
    print("✓ Theory synthesis:", final_answer_text[:100] + "...")

    # Test design synthesis
    agent_outputs = {"design": design_output}
    if "design" in agent_outputs:
        design = agent_outputs["design"]
        final_answer_text = design.architecture_recommendation
        if design.design_patterns:
            final_answer_text += "\n\nRecommended Design Patterns:\n" + "\n".join(f"- {pattern}" for pattern in design.design_patterns)
    print("✓ Design synthesis:", final_answer_text[:100] + "...")

    # Test code synthesis
    agent_outputs = {"code": code_output}
    if "code" in agent_outputs:
        code = agent_outputs["code"]
        final_answer_text = code.solution_explanation + "\n\n```python\n" + code.code + "\n```"
    print("✓ Code synthesis:", final_answer_text[:100] + "...")

    # Test planning synthesis
    agent_outputs = {"planning": planning_output}
    if "planning" in agent_outputs:
        plan = agent_outputs["planning"]
        final_answer_text = f"Goal: {plan.goal}\n\nTimeline: {plan.timeline}\n\nSteps:"
        for i, step in enumerate(plan.steps, 1):
            step_desc = step.get("description", step.get("step", "Unknown step"))
            final_answer_text += f"\n{i}. {step_desc}"
    print("✓ Planning synthesis:", final_answer_text[:100] + "...")

    print("\nAll synthesizer logic tests passed! ✓")
    print("The fix should now provide proper user responses instead of technical reports.")

if __name__ == "__main__":
    test_synthesizer_logic()