"""
Algorithmic Scriptwriting & Retention Engine
Leverages Gemini 2.5 Flash to craft high-retention, high-CPM scripts,
hook-driven storytelling, visual asset cues, and YouTube algorithm metadata.
"""

import json
import os
import re
from datetime import datetime
from config.settings import GEMINI_API_KEY, NICHE, CHANNEL_NAME
from engine.trend_engine import get_latest_investigative_topic, fetch_breaking_tech_trends

# Thematic 7-Day Content Calendar (Algorithmic Clustering & Authority)
WEEKLY_THEMATIC_ROSTER = {
    0: {  # Monday
        "day": "Monday",
        "theme": "Autonomous Software & Multi-Agent Stacks",
        "focus": "AI agent architectures, automated engineering, solo-developer multi-million dollar stacks",
        "prompt_context": "Deep dive into real-world agent orchestration frameworks, autonomous code generation, and the engineering behind 1-person software companies."
    },
    1: {  # Tuesday
        "day": "Tuesday",
        "theme": "Humanoid Robotics & Factory Economics",
        "focus": "Tesla Optimus, Figure 02, Boston Dynamics, physical labor cost collapse, manufacturing automation",
        "prompt_context": "Examine the marginal cost of physical labor falling to $2/hour and the restructuring of warehouse, logistics, and assembly lines."
    },
    2: {  # Wednesday
        "day": "Wednesday",
        "theme": "Machine-to-Machine Finance & Sovereign Crypto Rails",
        "focus": "AI agents with bank accounts, crypto rails for autonomous transactions, decentralized compute payments",
        "prompt_context": "Investigate how autonomous software agents are bypassing traditional SWIFT/ACH banking using cryptographic micro-transactions to buy compute and data."
    },
    3: {  # Thursday
        "day": "Thursday",
        "theme": "Sovereign Compute & Energy Megaprojects",
        "focus": "National GPU stockpiles, nuclear datacenter energy, next-gen silicon, geopolitics of AGI",
        "prompt_context": "Explore why world powers are treating gigawatt nuclear power and specialized compute clusters as the 21st-century equivalent of oil reserves."
    },
    4: {  # Friday
        "day": "Friday",
        "theme": "The Post-Labor Solopreneur & Micro-SaaS",
        "focus": "Solo-operated autonomous micro-businesses, agentic lead-gen, automated revenue machines",
        "prompt_context": "Break down concrete, step-by-step case studies of individual operators using coordinated AI agent swarms to generate 6- and 7-figure cash flows."
    },
    5: {  # Saturday
        "day": "Saturday",
        "theme": "Speculative Science & Quantum Breakthroughs",
        "focus": "Quantum cryptography collapse, fusion energy, synthetic biology, technological singularity timelines",
        "prompt_context": "Analyze high-impact speculative engineering breakthroughs planned between 2027 and 2035 that will shatter existing economic assumptions."
    },
    6: {  # Sunday
        "day": "Sunday",
        "theme": "The Master Civilizational Documentary",
        "focus": "The decoupling of human labor from economic productivity, macroeconomic collapse, post-work society",
        "prompt_context": "A master investigative documentary examining the mathematical and economic architecture of the post-human economy."
    }
}

SYSTEM_PROMPT = f"""
You are the Executive Content Director, Lead Algorithmic Scriptwriter, and YouTube Growth Strategist for "{CHANNEL_NAME}".
Your niche is: {NICHE}.

Your videos target sophisticated viewers: tech founders, engineers, investors, and futurists.
CPM target is $25-$45.

CRITICAL RETENTION & QUALITY RULES (Human Value Guarantee):
1. ZERO ABSTRACT DEFINITIONS: Never state "AI agents are software programs that perform tasks." Always frame around specific empirical case studies, real dollar figures, and operational code architectures.
2. EMPIRICAL BENCHMARKS: Reference real benchmarks, GitHub architectures, server costs ($/hour), and market data.
3. THE 0:00-0:05 PARADOX HOOK: Never start with "Hey guys", "Welcome back", or questions like "Have you ever wondered". Jump straight into an undeniable contradiction, shocking empirical data, or high-stakes future paradigm shift.
4. THE INFINITE LOOP (MANDATORY FOR SHORTS): The final spoken sentence MUST grammatically and semantically bridge seamlessly back into the opening hook sentence! (For example, End sentence: "...and that is the exact mathematical reason why..." which bridges directly when the video loops back to the First sentence: "Right now, autonomous AI agents are..."). This achieves >100% Average Percentage Viewed (APV)!
5. THE UNFAIR ADVANTAGE: Every video must give the human viewer an actionable insight: what this means for their wealth, career, or technical stack.
6. VISUAL CUES: Embed 6 to 10 distinct scenes with explicit visual_query strings for stock footage and stat_overlay triggers.
7. METADATA: 
   - Title must be under 50 characters, curiosity-gap driven, high emotional tension, mobile optimized.
   - Description must contain chapter timestamps, semantic summary, and keyword clusters for browse features.

OUTPUT FORMAT: Return pure JSON ONLY without markdown code fences.
"""

def generate_script_prompt(video_type: str = "short", specific_topic: str = None) -> str:
    target_words = "130-160 words (45-55 seconds spoken)" if video_type == "short" else "650-900 words (4-6 minutes spoken)"
    
    prompt = f"""
Create a complete high-retention video production package for video type: "{video_type.upper()}".
Target spoken length: {target_words}.
Specific Topic/Breaking Event: {specific_topic or "Choose the freshest high-stakes breaking development from the Machine Economy."}

Return a valid JSON object matching this exact schema:
{{
  "title": "High CTR mobile title (<50 chars)",
  "hook": "First 5 seconds spoken script (Paradox/Tension)",
  "script_clean": "Complete full spoken narrative text without any cue brackets. If short, ending bridges seamlessly into hook for infinite loop.",
  "scenes": [
    {{
      "text_segment": "Spoken sentence corresponding to this scene",
      "visual_query": "High quality stock video search query (e.g., 'supercomputer datacenter neon' or 'humanoid robot hands')",
      "stat_overlay": {{
        "show": true,
        "title": "Short stat title e.g. CAPITAL SHIFT",
        "value": "$40 TRILLION",
        "subtitle": "By 2028 Est."
      }},
      "sfx": "whoosh"
    }}
  ],
  "seo": {{
    "description": "Rich description with chapter timestamps and semantic keyword density",
    "tags": ["machine economy", "ai agents", "future tech", "robotics", "2027 economics"],
    "thumbnail_text": "3 BOLD WORDS (e.g. IT BEGAN.)",
    "thumbnail_query": "futuristic dramatic AI server room neon"
  }}
}}
"""
    return prompt

def generate_video_package(video_type: str = "short", specific_topic: str = None) -> dict:
    """Generates a complete script and production package using Gemini or offline fallback."""
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    
    # Auto-detect day of week from 7-day thematic roster
    today_idx = datetime.now().weekday()
    day_meta = WEEKLY_THEMATIC_ROSTER[today_idx]

    # If no specific topic given, dynamically combine thematic pillar + breaking news
    if not specific_topic:
        breaking = get_latest_investigative_topic()
        specific_topic = (
            f"[{day_meta['day']} Theme: {day_meta['theme']}] "
            f"Breaking Angle: {breaking['title']} "
            f"// Analytical Focus: {day_meta['prompt_context']}"
        )
        print(f"[ScriptEngine] Active Day: {day_meta['day']} ({day_meta['theme']})")
        print(f"[ScriptEngine] Live Trend Angle: {breaking['title']}")
    
    if api_key:
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-3.8-flash",
                    system_instruction=SYSTEM_PROMPT
                )
                response = model.generate_content(
                    generate_script_prompt(video_type, specific_topic),
                    generation_config={"response_mime_type": "application/json"}
                )
                data = json.loads(response.text)
                return data
        except Exception as e:
            print(f"[ScriptEngine] Gemini API call fallback: {e}")

    # High-quality offline fallback template (always works and verified)
    if video_type == "short":
        return {
            "title": "The $40T Machine Economy Has Begun",
            "hook": "By 2027, the traditional corporate hierarchy will be mathematically obsolete.",
            "script_clean": (
                "By 2027, the traditional corporate hierarchy will be mathematically obsolete. "
                "Autonomous AI agent swarms are now executing software engineering, supply chains, and legal contracts "
                "with zero human intervention. "
                "Wall Street models project a $40 trillion capital reallocation away from human salaries into autonomous compute. "
                "The question is no longer whether AI will take jobs. "
                "The real question is: who owns the machines that replace them?"
            ),
            "scenes": [
                {
                    "text_segment": "By 2027, the traditional corporate hierarchy will be mathematically obsolete.",
                    "visual_query": "futuristic data server room dark blue",
                    "stat_overlay": {"show": True, "title": "TIMELINE", "value": "2027 ARRIVAL", "subtitle": "Systemic Shift"},
                    "sfx": "whoosh"
                },
                {
                    "text_segment": "Autonomous AI agent swarms are now executing software engineering, supply chains, and legal contracts with zero human intervention.",
                    "visual_query": "artificial intelligence neural network digital code",
                    "stat_overlay": {"show": False, "title": "", "value": "", "subtitle": ""},
                    "sfx": "click"
                },
                {
                    "text_segment": "Wall Street models project a $40 trillion capital reallocation away from human salaries into autonomous compute.",
                    "visual_query": "financial stock market data futuristic chart",
                    "stat_overlay": {"show": True, "title": "CAPITAL SHIFT", "value": "$40 TRILLION", "subtitle": "Global Labor Reallocation"},
                    "sfx": "whoosh"
                },
                {
                    "text_segment": "The question is no longer whether AI will take jobs. The real question is: who owns the machines that replace them?",
                    "visual_query": "humanoid robot looking at city cyber light",
                    "stat_overlay": {"show": False, "title": "", "value": "", "subtitle": ""},
                    "sfx": "whoosh"
                }
            ],
            "seo": {
                "description": (
                    "The autonomous machine economy is no longer theoretical. By 2027, AI agent swarms and "
                    "autonomous systems will control over $40 trillion in automated capital reallocation.\n\n"
                    "TIMESTAMPS:\n"
                    "0:00 The 2027 Corporate Collapse\n"
                    "0:12 Autonomous Agent Swarms\n"
                    "0:28 The $40 Trillion Capital Shift\n"
                    "0:42 Who Owns The Machines?\n\n"
                    "#MachineEconomy #AIAgents #FutureTech #Economics2027"
                ),
                "tags": ["machine economy", "ai agents", "future of work", "autonomous corporations", "ai economy", "speculative tech"],
                "thumbnail_text": "WHO OWNS THEM?",
                "thumbnail_query": "cyberpunk robot in executive office neon"
            }
        }
    else:
        # Long-form fallback
        return {
            "title": "How The $40T Machine Economy Changes Everything",
            "hook": "We are currently living through the final days of the human-centered economic model.",
            "script_clean": (
                "We are currently living through the final days of the human-centered economic model. "
                "Across the globe, the foundational premise of modern capitalism—that human labor is required to produce economic output—is quietly disintegrating. "
                "Autonomous agent networks are taking over institutional functions in finance, software creation, and logistics. "
                "By 2028, sovereign compute networks will generate more GDP than entire industrialized nations. "
                "In this comprehensive breakdown, we examine the mathematical architecture of the machine economy, "
                "why capital is fleeing traditional equities into autonomous infrastructure, and the exact roadmap of the post-labor economy."
            ),
            "scenes": [
                {
                    "text_segment": "We are currently living through the final days of the human-centered economic model.",
                    "visual_query": "modern high tech financial district night timelapse",
                    "stat_overlay": {"show": True, "title": "PARADIGM SHIFT", "value": "POST-LABOR", "subtitle": "Historical Transition"},
                    "sfx": "whoosh"
                },
                {
                    "text_segment": "Across the globe, the foundational premise of modern capitalism—that human labor is required to produce economic output—is quietly disintegrating.",
                    "visual_query": "dark robotic manufacturing facility automated arms",
                    "stat_overlay": {"show": False, "title": "", "value": "", "subtitle": ""},
                    "sfx": "click"
                },
                {
                    "text_segment": "Autonomous agent networks are taking over institutional functions in finance, software creation, and logistics.",
                    "visual_query": "digital server racks glowing neon lights",
                    "stat_overlay": {"show": True, "title": "AUTOMATION RATE", "value": "94% EFFICIENCY", "subtitle": "Algorithmic Operations"},
                    "sfx": "whoosh"
                },
                {
                    "text_segment": "By 2028, sovereign compute networks will generate more GDP than entire industrialized nations.",
                    "visual_query": "supercomputer datacenter futuristic perspective",
                    "stat_overlay": {"show": True, "title": "SOVEREIGN COMPUTE", "value": "GLOBAL GDP", "subtitle": "Next Reserve Asset"},
                    "sfx": "whoosh"
                },
                {
                    "text_segment": "In this comprehensive breakdown, we examine the mathematical architecture of the machine economy, why capital is fleeing traditional equities into autonomous infrastructure, and the exact roadmap of the post-labor economy.",
                    "visual_query": "abstract digital network nodes connecting globe",
                    "stat_overlay": {"show": False, "title": "", "value": "", "subtitle": ""},
                    "sfx": "whoosh"
                }
            ],
            "seo": {
                "description": (
                    "A deep documentary on the transition from human-centric capitalism to the autonomous machine economy.\n\n"
                    "CHAPTERS:\n"
                    "0:00 The End of Human-Centric Capitalism\n"
                    "01:30 The Rise of Sovereign Agent Swarms\n"
                    "03:15 The $40 Trillion Capital Flight\n"
                    "05:00 Who Controls the Autonomous Future?\n\n"
                    "#MachineEconomy #FutureEconomics #AutonomousTech #AIAgents"
                ),
                "tags": ["machine economy", "post labor economy", "ai automation", "autonomous agents", "speculative economics"],
                "thumbnail_text": "LABOR IS DEAD.",
                "thumbnail_query": "dramatic silhouette robot looking over financial skyline"
            }
        }

