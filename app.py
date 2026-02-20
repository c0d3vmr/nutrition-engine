"""
EatWell - Personalized Nutrition App
A beautiful, interactive prototype for personalized nutrition planning with health equity focus.
"""

import streamlit as st
from typing import Optional
import os

# OpenAI import (optional - for AI chatbot)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import app modules
from user_context import (
    UserContext, Financials, Logistics, MedicalHistory, LabResults,
    create_sample_user
)
from bio_analyzer import analyze_lab_data, NutrientPriorityList
from resource_locator import resource_locator, ResourceMap, StoreType
from shopping_planner import (
    generate_shopping_list, ShoppingList, ShoppingPriority,
    get_item_explanation
)

# Page config
st.set_page_config(
    page_title="EatWell - Personalized Nutrition",
    page_icon="🥕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished look
st.markdown("""
<style>
    /* Color Palette:
       Light Orange: #ffd09b
       Orange: #ec813b
       Light Green: #d1d69d
       Dark Green: #4f7e52
    */
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #4f7e52;
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        color: #666;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffd09b 0%, #d1d69d 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .priority-critical { 
        background-color: #ffebee; 
        border-left: 4px solid #c62828;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .priority-high { 
        background-color: #ffd09b; 
        border-left: 4px solid #ec813b;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .priority-moderate { 
        background-color: #ffefd6; 
        border-left: 4px solid #ec813b;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .priority-optional { 
        background-color: #d1d69d; 
        border-left: 4px solid #4f7e52;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .store-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(79,126,82,0.15);
        margin: 0.5rem 0;
        border: 1px solid #d1d69d;
    }
    .nutrient-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        background-color: #d1d69d;
        color: #4f7e52;
    }
    .explanation-box {
        background: linear-gradient(135deg, #ffffff 0%, #d1d69d40 100%);
        border: 1px solid #d1d69d;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .free-badge {
        background-color: #4f7e52;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .snap-badge {
        background-color: #ec813b;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .edu-card {
        background: linear-gradient(135deg, #ffd09b40 0%, #d1d69d60 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #4f7e52;
    }
    .edu-card h4 {
        color: #4f7e52;
        margin-bottom: 0.5rem;
    }
    .simple-explain {
        background: linear-gradient(135deg, #ffd09b40 0%, #ffd09b80 100%);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid #ffd09b;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .simple-explain strong {
        color: #4f7e52;
    }
    .glossary-term {
        background: #d1d69d;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4f7e52;
    }
    /* Streamlit overrides for cohesive theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #4f7e52;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        min-width: 140px;
        flex-grow: 1;
        border: 1px solid #d1d69d;
        border-bottom: none;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #d1d69d40;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f7e52 !important;
        color: white !important;
        border-color: #4f7e52 !important;
    }
    /* Wider content area for main tabs */
    .stMainBlockContainer {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* Make tab content panels wider */
    .stTabs [data-baseweb="tab-panel"] {
        width: 100%;
        padding: 1rem 0;
    }
    section[data-testid="stSidebar"] + section .stTabs {
        width: 100%;
    }
    .stButton>button {
        background-color: #ec813b;
        color: white;
        border: none;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #4f7e52;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        color: #4f7e52;
    }
    div[data-testid="stMetricDelta"] {
        color: #ec813b;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HEALTH LITERACY CONTENT - Plain language explanations
# =============================================================================

HEALTH_GLOSSARY = {
    "MTHFR": {
        "simple": "A gene that helps your body use vitamins, especially folate (a B vitamin)",
        "detail": """MTHFR is like a factory worker in your body that converts folate into a usable form. Some people have gene variants that make this worker slower:

**Common MTHFR Mutations:**
• **C677T** - The most studied variant. Having one copy (heterozygous) reduces enzyme activity by ~35%. Having two copies (homozygous) reduces it by ~70%. This is the variant most associated with higher homocysteine levels.
• **A1298C** - Less impactful alone, but combined with C677T can significantly affect folate processing.
• **Compound heterozygous** (one C677T + one A1298C) - Similar effect to having two C677T copies.

**What this means for you:** If you have these variants, your body has a harder time converting regular folate into methylfolate (the active form). The solution? Eat more folate-rich foods or consider methylfolate supplements.

**How to check your MTHFR status:**
• **23andMe or AncestryDNA** - These consumer tests include MTHFR data in raw files (use free tools like Genetic Genie or Promethease to interpret)
• **Doctor-ordered test** - Ask your doctor for MTHFR genetic testing, especially if you have family history of heart disease, blood clots, or pregnancy complications
• **Specialized labs** - Labs like LabCorp, Quest, or specialty genetic testing companies offer MTHFR panels
• **Cost** - Consumer DNA tests: $99-199; Medical tests: $100-400 (often covered by insurance with medical necessity)""",
        "why_matters": "If you have an MTHFR variant, you may need MORE folate-rich foods than average. About 40% of people have at least one copy of C677T, so this is very common!",
        "food_connection": "spinach, lentils, asparagus, broccoli, avocado, fortified cereals"
    },
    "Methylation": {
        "simple": "A process your body uses to turn genes on/off and detoxify",
        "detail": "Think of methylation like light switches in your house. Your body is constantly flipping these switches to control which genes are active. Good methylation = smooth operation. Poor methylation = some lights stuck on or off, which can affect mood, energy, and health.",
        "why_matters": "Supporting methylation with the right nutrients helps your body run smoothly.",
        "food_connection": "eggs, leafy greens, beets"
    },
    "Vitamin B12": {
        "simple": "A vitamin needed for energy, brain function, and making red blood cells",
        "detail": "B12 is like fuel for your brain and blood cells. Without enough, you might feel tired, foggy, or weak. Your body can't make B12—you must get it from food (meat, eggs, fortified foods) or supplements.",
        "why_matters": "Low B12 is common and causes fatigue and brain fog. Many people don't get enough.",
        "food_connection": "eggs, sardines, fortified cereals, nutritional yeast"
    },
    "Vitamin D": {
        "simple": "The 'sunshine vitamin' that helps bones, immune system, and mood",
        "detail": "Your skin makes Vitamin D when you're in sunlight, but many people don't get enough sun (especially in winter or if you have darker skin). Low Vitamin D is linked to weak bones, getting sick often, and feeling down.",
        "why_matters": "Most people are low in Vitamin D without knowing it. It affects almost every part of your body.",
        "food_connection": "fortified milk, salmon, egg yolks, mushrooms"
    },
    "Iron": {
        "simple": "A mineral that carries oxygen in your blood",
        "detail": "Iron is like a delivery truck that carries oxygen to every cell in your body. Without enough iron, cells don't get the oxygen they need, making you feel exhausted, cold, or short of breath.",
        "why_matters": "Iron deficiency is the #1 nutritional deficiency worldwide, especially in women.",
        "food_connection": "spinach, lentils, beef, fortified cereals"
    },
    "CRP": {
        "simple": "A blood test that measures inflammation (swelling) in your body",
        "detail": "CRP (C-Reactive Protein) is like a smoke alarm for inflammation. When it's high, something in your body is irritated or fighting—even if you can't feel it. Chronic inflammation is linked to heart disease, diabetes, and many other conditions.",
        "why_matters": "High CRP means your body is stressed. Anti-inflammatory foods can help calm it down.",
        "food_connection": "berries, fatty fish, turmeric, leafy greens, olive oil"
    },
    "Homocysteine": {
        "simple": "An amino acid that can damage blood vessels when too high",
        "detail": "Homocysteine is a natural byproduct in your blood, but high levels scratch and damage your blood vessel walls—like sandpaper on a pipe. B vitamins (especially folate and B12) help keep it low.",
        "why_matters": "High homocysteine increases heart disease risk. B vitamins from food can lower it.",
        "food_connection": "leafy greens, eggs, fortified cereals"
    },
    "Fasting Glucose": {
        "simple": "Blood sugar level after not eating for 8+ hours",
        "detail": "This test shows how well your body manages sugar. High fasting glucose means your body is having trouble moving sugar from blood into cells—an early warning sign for diabetes.",
        "why_matters": "Catching high glucose early lets you make food changes before diabetes develops.",
        "food_connection": "fiber-rich foods: oats, beans, vegetables"
    },
    "Omega-3 Fatty Acids": {
        "simple": "Healthy fats that reduce inflammation and support brain health",
        "detail": "Omega-3s are like oil for a squeaky machine—they help everything run smoothly, especially your brain, heart, and joints. Most Americans don't get enough because we don't eat much fish.",
        "why_matters": "Omega-3s fight inflammation and support mental health. Very important for brain function.",
        "food_connection": "salmon, sardines, walnuts, flaxseed, chia seeds"
    },
    "SNAP": {
        "simple": "Government food assistance program (food stamps)",
        "detail": "SNAP (Supplemental Nutrition Assistance Program) provides money on an EBT card to buy groceries. It's accepted at most grocery stores and many farmers markets. There's no shame in using it—it's there to help.",
        "why_matters": "SNAP can significantly expand your food budget and access to healthy options.",
        "food_connection": "Most foods except hot prepared foods and alcohol"
    },
    "WIC": {
        "simple": "Nutrition program for pregnant women, new mothers, and young children",
        "detail": "WIC (Women, Infants, and Children) provides specific healthy foods plus nutrition education. It covers things like milk, eggs, whole grains, fruits, and vegetables.",
        "why_matters": "WIC ensures mothers and children get key nutrients during critical growth periods.",
        "food_connection": "milk, eggs, whole grain bread, fruits, vegetables, infant formula"
    },
    "Fiber": {
        "simple": "The part of plant foods your body can't digest—but it keeps you healthy!",
        "detail": "Fiber is like a broom for your insides. It sweeps through your digestive system, keeping things moving, feeding good gut bacteria, and helping control blood sugar. There are two types: soluble fiber (dissolves in water, lowers cholesterol) and insoluble fiber (adds bulk, prevents constipation).",
        "why_matters": "Most people only get half the fiber they need. Low fiber is linked to constipation, high cholesterol, and blood sugar problems.",
        "food_connection": "oats, beans, lentils, apples, berries, broccoli, whole grains"
    },
    "Protein": {
        "simple": "Building blocks your body needs to make muscles, skin, hormones, and more",
        "detail": "Protein is made of amino acids—like Lego pieces that your body rearranges to build and repair tissues. You need protein every day because your body can't store it. Complete proteins (from animal foods) have all the building blocks; plant proteins often need to be combined.",
        "why_matters": "Not getting enough protein can cause muscle loss, weakness, slow healing, and hair loss.",
        "food_connection": "eggs, chicken, fish, beans, lentils, tofu, Greek yogurt, nuts"
    },
    "Carbohydrates": {
        "simple": "Your body's main source of quick energy",
        "detail": "Carbs break down into glucose (sugar) that powers your brain and muscles. Not all carbs are equal: complex carbs (whole grains, vegetables) release energy slowly, while simple carbs (sugar, white bread) spike blood sugar fast. Choose complex carbs most of the time.",
        "why_matters": "Choosing the right carbs helps maintain steady energy and healthy blood sugar levels.",
        "food_connection": "whole grains (oats, brown rice), vegetables, fruits, beans, sweet potatoes"
    },
    "Calcium": {
        "simple": "A mineral that builds strong bones and teeth",
        "detail": "Calcium is the main building material for your skeleton. Your body also uses it for muscle movement, nerve signals, and heart rhythm. If you don't eat enough calcium, your body takes it from your bones, making them weaker over time.",
        "why_matters": "Low calcium over time leads to weak, brittle bones (osteoporosis), especially in women.",
        "food_connection": "dairy (milk, yogurt, cheese), fortified plant milks, leafy greens, canned fish with bones"
    },
    "Magnesium": {
        "simple": "A mineral that helps muscles relax, supports sleep, and calms the nervous system",
        "detail": "Magnesium is involved in over 300 body processes! It helps muscles relax after they contract, supports deep sleep, and keeps your heart rhythm steady. Many people are low in magnesium without knowing it.",
        "why_matters": "Low magnesium is linked to muscle cramps, anxiety, poor sleep, and heart palpitations.",
        "food_connection": "pumpkin seeds, almonds, spinach, black beans, dark chocolate, avocado"
    },
    "Zinc": {
        "simple": "A mineral that supports your immune system and wound healing",
        "detail": "Zinc is like a security guard for your immune system. It helps fight off viruses and bacteria, heals wounds, and even affects your sense of taste and smell. Your body can't store much zinc, so you need it regularly from food.",
        "why_matters": "Low zinc makes you more likely to get sick and slows down healing.",
        "food_connection": "oysters, beef, pumpkin seeds, chickpeas, cashews, fortified cereals"
    },
    "Folate": {
        "simple": "A B vitamin essential for cell growth and making DNA",
        "detail": "Folate (also called B9) helps your body make new cells and is especially critical during pregnancy for the baby's brain and spine development. 'Folic acid' is the synthetic form in supplements; 'folate' is the natural form in food.",
        "why_matters": "Getting enough folate is crucial for preventing birth defects and supporting overall cell health.",
        "food_connection": "leafy greens, lentils, asparagus, broccoli, fortified cereals, avocado"
    },
    "Potassium": {
        "simple": "A mineral that helps control blood pressure and muscle function",
        "detail": "Potassium works opposite to sodium—it helps lower blood pressure by relaxing blood vessel walls. It also helps muscles contract properly, including your heart. Most Americans get too little potassium and too much sodium.",
        "why_matters": "Low potassium can cause muscle weakness, cramps, and high blood pressure.",
        "food_connection": "bananas, potatoes, sweet potatoes, beans, spinach, yogurt"
    },
    "Antioxidants": {
        "simple": "Substances that protect your cells from damage",
        "detail": "Antioxidants are like bodyguards for your cells. They neutralize 'free radicals'—harmful molecules that damage cells and contribute to aging and disease. Different antioxidants (vitamin C, vitamin E, beta-carotene) protect different parts of cells.",
        "why_matters": "Eating antioxidant-rich foods helps prevent cell damage linked to cancer, heart disease, and aging.",
        "food_connection": "berries, colorful vegetables, green tea, dark chocolate, tomatoes, citrus fruits"
    },
    "Anti-inflammatory": {
        "simple": "Foods that calm down irritation and swelling in your body",
        "detail": "Inflammation is your body's response to injury or stress—helpful short-term, harmful long-term. Anti-inflammatory foods are like a fire extinguisher, calming down chronic inflammation that causes disease.",
        "why_matters": "Chronic inflammation underlies most modern diseases. Food is powerful medicine here.",
        "food_connection": "berries, turmeric, ginger, fatty fish, olive oil, leafy greens"
    },
}

SYMPTOM_EXPLANATIONS = {
    "fatigue": {
        "what_it_means": "Feeling tired even after rest",
        "common_causes": "Low iron, low B12, poor sleep, thyroid issues, inflammation",
        "food_help": "Iron-rich foods (spinach, lentils), B12 foods (eggs, fortified cereals), anti-inflammatory foods"
    },
    "brain_fog": {
        "what_it_means": "Difficulty concentrating, memory issues, feeling 'cloudy'",
        "common_causes": "Low B12, poor methylation, inflammation, blood sugar swings",
        "food_help": "Omega-3s (salmon, walnuts), B vitamins (eggs, greens), stable protein/fiber meals"
    },
    "joint_pain": {
        "what_it_means": "Aching, stiffness, or swelling in joints",
        "common_causes": "Inflammation, omega-3 deficiency, vitamin D deficiency",
        "food_help": "Fatty fish, turmeric, ginger, berries, leafy greens"
    },
    "anxiety": {
        "what_it_means": "Excessive worry, nervousness, or unease",
        "common_causes": "Magnesium deficiency, B vitamin deficiency, blood sugar swings, gut issues",
        "food_help": "Magnesium foods (pumpkin seeds, spinach), complex carbs, fermented foods"
    },
    "digestive_issues": {
        "what_it_means": "Bloating, constipation, diarrhea, or stomach pain",
        "common_causes": "Low fiber, food sensitivities, poor gut bacteria balance",
        "food_help": "Fiber (oats, beans, vegetables), fermented foods (yogurt), plenty of water"
    },
    "weak_immunity": {
        "what_it_means": "Getting sick often, slow healing",
        "common_causes": "Low vitamin D, low zinc, low vitamin C, poor nutrition overall",
        "food_help": "Citrus fruits, bell peppers, mushrooms, fortified milk, pumpkin seeds"
    }
}


def init_session_state():
    """Initialize session state variables."""
    if 'user_context' not in st.session_state:
        st.session_state.user_context = None
    if 'nutrient_priorities' not in st.session_state:
        st.session_state.nutrient_priorities = None
    if 'resource_map' not in st.session_state:
        st.session_state.resource_map = None
    if 'shopping_list' not in st.session_state:
        st.session_state.shopping_list = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your EatWell nutrition assistant. 🥕 Ask me anything about health terms, nutrients, foods, or how to use this app. I'm here to help you understand your health in plain language!"}
        ]
    if 'openai_api_key' not in st.session_state:
        # Check environment variable first
        st.session_state.openai_api_key = os.environ.get('OPENAI_API_KEY', '')


# =============================================================================
# CHATBOT LOGIC
# =============================================================================

def build_system_prompt() -> str:
    """Build a system prompt for the AI chatbot with health context."""
    base_prompt = """You are a friendly, helpful nutrition assistant for EatWell, an app focused on health equity. Your role is to:

1. Explain health and nutrition concepts in simple, plain language that anyone can understand
2. Help users understand their lab results, symptoms, and nutrient needs
3. Provide food-based recommendations for health concerns
4. Be especially helpful to people with low health literacy - avoid jargon, use examples
5. Be sensitive to budget constraints and food access challenges
6. Focus on practical, actionable advice

Key health terms to explain simply when asked:
- MTHFR: A gene that affects how your body uses B vitamins (folate, B12). Some people have variations that mean they need more of these vitamins.
- Methylation: How your body activates vitamins and processes nutrients. Think of it as your body's "processing system."
- Homocysteine: An amino acid in blood. High levels can indicate you need more B vitamins.
- CRP: A marker of inflammation in the body. Higher = more inflammation.
- Ferritin: Shows how much iron your body has stored.
- B12: Essential vitamin for energy, brain function, and blood health.
- Folate: A B vitamin needed for cell growth, especially important during pregnancy.
- Vitamin D: The "sunshine vitamin" - important for bones, mood, and immune system.

Budget-friendly nutrition tips:
- Eggs, beans, and lentils are affordable protein sources
- Frozen vegetables are just as nutritious as fresh
- Canned fish (sardines, salmon) provides omega-3s cheaply
- Oats are an economical, filling breakfast
- SNAP benefits can be used at farmers markets (often doubled!)

Always be encouraging and non-judgmental. Meet people where they are."""
    
    # Add user context if available
    if st.session_state.analysis_complete and st.session_state.user_context:
        user = st.session_state.user_context
        nutrients = st.session_state.nutrient_priorities
        
        context_info = "\n\nCurrent user context:\n"
        context_info += f"- Budget: ${user.financials.weekly_grocery_budget}/week\n"
        context_info += f"- SNAP: {'Yes' if user.financials.snap_eligible else 'No'}\n"
        
        if user.medical.symptoms:
            context_info += f"- Symptoms: {', '.join(user.medical.symptoms)}\n"
        
        if nutrients and nutrients.needs:
            top_nutrients = [n.nutrient for n in nutrients.needs[:5]]
            context_info += f"- Top nutrient needs: {', '.join(top_nutrients)}\n"
        
        base_prompt += context_info
    
    return base_prompt


def get_ai_response(user_message: str) -> Optional[str]:
    """Get a response from OpenAI API."""
    if not OPENAI_AVAILABLE or not st.session_state.openai_api_key:
        return None
    
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        
        # Build messages with conversation history (last 10 messages)
        messages = [{"role": "system", "content": build_system_prompt()}]
        
        # Add recent conversation history
        recent_messages = st.session_state.chat_messages[-10:]
        for msg in recent_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective, fast model
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Return None on error - will fall back to rule-based
        st.session_state.ai_error = str(e)
        return None


def get_chatbot_response(user_message: str) -> str:
    """
    Generate a response to the user's message.
    Uses AI if available, falls back to rule-based responses.
    """
    # Try AI first
    ai_response = get_ai_response(user_message)
    if ai_response:
        return ai_response
    
    # Fall back to rule-based responses
    return get_rule_based_response(user_message)


def get_rule_based_response(user_message: str) -> str:
    """
    Generate a rule-based response using the health knowledge base.
    This is the fallback when AI is not available.
    """
    message_lower = user_message.lower().strip()
    
    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'help', 'start']
    if any(message_lower == g or message_lower.startswith(g + ' ') for g in greetings):
        return """Hello! I'm here to help you understand nutrition and health. Here are some things you can ask me:

• **"What is MTHFR?"** - Learn about health terms
• **"Why do I need B12?"** - Understand nutrients
• **"What foods help with fatigue?"** - Get food suggestions
• **"How do I use this app?"** - Get guidance
• **"What is SNAP?"** - Learn about food assistance

What would you like to know?"""
    
    # Check for app usage questions
    app_questions = ['how do i use', 'how does this work', 'what do i do', 'getting started', 'how to start']
    if any(q in message_lower for q in app_questions):
        return """**How to use this app:**

1️⃣ **Fill out the sidebar form** (on the left) with your:
   - Budget and food assistance status
   - Location and transportation
   - Health symptoms and family history
   - Lab results (optional but helpful)

2️⃣ **Click "Generate My Plan"** to get personalized recommendations

3️⃣ **Explore your results** in the tabs:
   - 🛒 Shopping List - What to buy
   - 🔬 Nutrient Analysis - Why you need it
   - 📍 Store Finder - Where to shop
   - ❓ Ask Why - Understand the science
   - 📚 Learn - Health education

💡 **Tip:** Click "Load Demo Data" to see an example first!"""
    
    # Check for glossary terms
    for term, info in HEALTH_GLOSSARY.items():
        term_lower = term.lower()
        if term_lower in message_lower or (len(term_lower) > 3 and term_lower[:4] in message_lower):
            return f"""**{term}**

📝 **Simple explanation:** {info['simple']}

📖 **More detail:** {info['detail']}

💡 **Why it matters:** {info['why_matters']}

🥗 **Foods that help:** {info['food_connection']}"""
    
    # Check for symptom questions
    symptom_keywords = {
        'fatigue': 'fatigue', 'tired': 'fatigue', 'exhausted': 'fatigue', 'no energy': 'fatigue',
        'brain fog': 'brain_fog', 'foggy': 'brain_fog', 'concentrate': 'brain_fog', 'memory': 'brain_fog',
        'joint': 'joint_pain', 'joints': 'joint_pain', 'arthritis': 'joint_pain',
        'anxiety': 'anxiety', 'anxious': 'anxiety', 'nervous': 'anxiety', 'worry': 'anxiety',
        'digest': 'digestive_issues', 'stomach': 'digestive_issues', 'bloat': 'digestive_issues', 'gut': 'digestive_issues',
        'sick': 'weak_immunity', 'immunity': 'weak_immunity', 'immune': 'weak_immunity', 'cold': 'weak_immunity'
    }
    
    for keyword, symptom_key in symptom_keywords.items():
        if keyword in message_lower:
            if symptom_key in SYMPTOM_EXPLANATIONS:
                info = SYMPTOM_EXPLANATIONS[symptom_key]
                return f"""**About {symptom_key.replace('_', ' ').title()}:**

🤔 **What it means:** {info['what_it_means']}

⚠️ **Common causes:** {info['common_causes']}

🥗 **Foods that can help:** {info['food_help']}

💡 Fill out the sidebar form and I can give you personalized food recommendations for this!"""
    
    # Check for food questions
    food_questions = ['what should i eat', 'what foods', 'best foods', 'food for', 'foods for', 'what to eat']
    if any(q in message_lower for q in food_questions):
        # Check if they mentioned a specific condition
        if 'inflam' in message_lower:
            return """**Anti-inflammatory foods:**

🥗 **Best choices:**
• Fatty fish (salmon, sardines)
• Berries (blueberries, strawberries)
• Leafy greens (spinach, kale)
• Turmeric and ginger
• Olive oil
• Nuts (walnuts, almonds)

❌ **Foods to limit:**
• Processed foods
• Sugary drinks
• Refined carbs
• Fried foods

💡 Fill out the form with your symptoms to get personalized recommendations!"""
        
        if 'energy' in message_lower or 'tired' in message_lower:
            return """**Foods for energy:**

🥗 **Best choices:**
• Iron-rich: spinach, lentils, beans, fortified cereals
• B12-rich: eggs, fortified cereals, nutritional yeast
• Complex carbs: oats, brown rice, quinoa
• Healthy fats: nuts, avocado, olive oil

💧 Also make sure you're drinking enough water!

💡 Low energy often signals low iron or B vitamins. Fill out the sidebar form to get personalized recommendations!"""
        
        return """To give you the best food recommendations, I need to know more about your health needs!

**Please fill out the sidebar form** with your symptoms and any lab results you have.

Or ask me about a specific condition, like:
- 'What foods help with inflammation?'
- 'What should I eat for more energy?'
- 'What foods are good for brain health?'"""
    
    # Check for budget/assistance questions
    if 'snap' in message_lower or 'food stamp' in message_lower:
        return HEALTH_GLOSSARY['SNAP']['detail'] + "\n\n" + "✅ This app shows you which stores accept SNAP and prioritizes SNAP-eligible foods in your shopping list!"
    
    if 'wic' in message_lower:
        return HEALTH_GLOSSARY['WIC']['detail'] + "\n\n" + "✅ This app marks WIC-eligible foods and shows WIC-authorized stores near you!"
    
    if 'budget' in message_lower or 'cheap' in message_lower or 'afford' in message_lower or 'money' in message_lower:
        return """**Eating healthy on a budget:**

💰 **Budget-friendly nutritious foods:**
• Eggs - cheap protein with B12
• Canned beans - protein and fiber for ~$1
• Frozen vegetables - just as nutritious as fresh
• Oats - filling breakfast for pennies
• Bananas - cheapest fruit, good nutrition
• Peanut butter - protein that lasts

🆓 **Free resources:**
• Food pantries (we'll show you nearby ones!)
• SNAP doubles at many farmers markets

💡 Set your budget in the sidebar and we'll prioritize affordable options for you!"""
    
    # Check for lab result questions
    lab_keywords = ['lab', 'blood test', 'bloodwork', 'test result', 'numbers']
    if any(k in message_lower for k in lab_keywords):
        return """**Understanding your lab results:**

Common tests and what they mean:

🔬 **Vitamin B12** (pg/mL)
• Below 300 = deficient
• 300-500 = low-normal
• 500-900 = optimal

☀️ **Vitamin D** (ng/mL)
• Below 20 = deficient
• 20-30 = insufficient
• 30-60 = optimal

🩸 **Iron** (mcg/dL)
• Below 60 = low
• 60-170 = normal

🔥 **CRP** (mg/L) - inflammation
• Below 1 = low inflammation
• 1-3 = moderate
• Above 3 = high

💡 Enter your lab values in the sidebar form and I'll explain what they mean for YOUR health!"""
    
    # Personalized responses if user data is available
    if st.session_state.analysis_complete and st.session_state.user_context:
        user = st.session_state.user_context
        nutrients = st.session_state.nutrient_priorities
        
        # Check if asking about their specific results
        if 'my' in message_lower or 'mine' in message_lower or 'for me' in message_lower:
            if nutrients and nutrients.needs:
                top_needs = nutrients.needs[:3]
                response = "**Based on your health profile:**\n\n"
                response += "Your top nutrient priorities are:\n"
                for need in top_needs:
                    response += f"• **{need.nutrient}** - {need.reason[:80]}...\n"
                response += "\n💡 Check the 🛒 Shopping List tab to see foods that address these needs!"
                return response
    
    # Default response
    return """I'm not sure I understood that. Here are some things you can ask me:

• **Health terms:** "What is MTHFR?" "What does CRP mean?"
• **Symptoms:** "Why am I tired?" "What helps with brain fog?"
• **Food advice:** "What foods reduce inflammation?"
• **App help:** "How do I use this app?"
• **Benefits:** "What is SNAP?" "How does WIC work?"

Or just describe what you're curious about and I'll try to help!"""


def render_chatbot():
    """Render the chatbot interface."""
    st.markdown("### 💬 Ask Your Nutrition Assistant")
    
    # AI status indicator and API key input
    if OPENAI_AVAILABLE:
        with st.expander("🤖 AI Settings", expanded=False):
            api_key = st.text_input(
                "OpenAI API Key (optional)",
                value=st.session_state.openai_api_key,
                type="password",
                help="Enter your OpenAI API key to enable AI-powered responses. Without it, I'll use built-in responses.",
                key="api_key_input"
            )
            if api_key != st.session_state.openai_api_key:
                st.session_state.openai_api_key = api_key
            
            if st.session_state.openai_api_key:
                st.success("✅ AI Mode: Powered by GPT-4")
            else:
                st.info("💡 Basic Mode: Using built-in health knowledge")
                st.caption("Add an API key above to ask any question!")
    else:
        st.caption("Ask me about health terms, nutrients, or how to use this app!")
    
    # Chat container (taller now that it's in a tab)
    chat_container = st.container(height=450)
    
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Show any AI errors
    if hasattr(st.session_state, 'ai_error') and st.session_state.ai_error:
        st.warning(f"AI unavailable, using basic mode. Error: {st.session_state.ai_error[:100]}")
        st.session_state.ai_error = None
    
    # Chat input
    if prompt := st.chat_input("Type your question here...", key="chat_input"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get response
        response = get_chatbot_response(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        st.rerun()


def render_sidebar():
    """Render the sidebar with user input forms."""
    with st.sidebar:
        st.markdown('<h2 style="color: #4f7e52; margin-bottom: 0.5rem;">🥕 EatWell</h2>', unsafe_allow_html=True)
        st.caption("Personalized Nutrition")
        st.markdown("---")
        
        st.markdown("##### 📋 Your Information")
        
        # Quick demo option
        if st.button("🚀 Load Demo Data", use_container_width=True):
            user = create_sample_user()
            st.session_state.user_context = user
            run_analysis()
            st.rerun()
        
        st.markdown("---")
        
        # User name
        name = st.text_input("Your Name", value="", placeholder="Enter your name")
        
        # Financial Information
        st.markdown("##### 💰 Financial")
        weekly_budget = st.slider("Weekly Grocery Budget ($)", 20, 300, 75, step=5)
        
        col1, col2 = st.columns(2)
        with col1:
            snap_status = st.checkbox("SNAP Benefits")
        with col2:
            wic_status = st.checkbox("WIC Benefits")
        
        # Logistics
        st.markdown("##### 🚗 Location & Transport")
        zip_code = st.text_input("ZIP Code", value="30312", max_chars=5)
        
        col1, col2 = st.columns(2)
        with col1:
            has_vehicle = st.checkbox("Vehicle Access")
        with col2:
            has_transit = st.checkbox("Public Transit")
        
        trips_per_week = st.slider("Grocery Trips/Week", 1, 7, 2)
        
        # Medical History
        st.markdown("##### 🩺 Health Information")
        st.caption("ℹ️ Helps us recommend foods for YOUR body")
        
        # Family History
        family_history = st.multiselect(
            "Family Health History",
            ["Diabetes", "Heart Disease", "Hypertension", "Cancer", "Obesity", "Thyroid Issues", 
             "Alzheimer's/Dementia", "Autoimmune Disease", "Mental Health Conditions"],
            default=[],
            help="Select conditions that run in your family (parents, grandparents, siblings)"
        )
        
        # Current Symptoms
        current_symptoms = st.multiselect(
            "Current Symptoms",
            ["Fatigue", "Brain Fog", "Joint Pain", "Anxiety", "Poor Sleep", "Digestive Issues", 
             "Weak Immunity", "Headaches", "Skin Problems", "Muscle Cramps", "Mood Swings",
             "Hair Loss", "Cold Hands/Feet", "Dizziness", "Shortness of Breath"],
            default=[],
            help="Select symptoms you currently experience regularly"
        )
        
        # Allergies
        allergies = st.multiselect(
            "Food Allergies & Intolerances",
            ["Gluten", "Dairy", "Shellfish", "Tree Nuts", "Peanuts", "Eggs", "Soy", "Fish", "Corn",
             "Sesame", "Nightshades", "Sulfites", "Histamine", "FODMAPs", "Latex-Fruit"],
            default=[],
            help="Select foods that cause you allergic reactions or digestive problems"
        )
        
        # Lab Results (Expandable) with educational content
        with st.expander("🧬 Lab Results (Optional) - Click to learn more!"):
            st.info("💡 **Don't have lab results?** That's okay! We can still help based on your symptoms and family history. But if you have recent bloodwork, entering it here makes our recommendations more precise.")
            
            st.markdown("##### 🧬 Genetic Markers")
            st.caption("These come from special genetic tests, not regular bloodwork")
            
            mthfr_variant = st.selectbox(
                "MTHFR Variant",
                ["Not Tested", "Normal", "C677T", "A1298C", "Compound"],
                index=0,
                help="MTHFR affects how your body uses B vitamins. Ask your doctor about genetic testing if interested."
            )
            if mthfr_variant not in ["Not Tested", "Normal"]:
                st.caption(f"ℹ️ {HEALTH_GLOSSARY['MTHFR']['simple']}")
            
            comt_variant = st.selectbox(
                "COMT Variant",
                ["Not Tested", "Normal", "Slow", "Fast"],
                index=0,
                help="COMT affects how you process stress hormones and caffeine."
            )
            
            st.markdown("##### 💉 Vitamin Levels")
            st.caption("These are from standard blood tests your doctor can order")
            
            b12_level = st.number_input(
                "Vitamin B12 (pg/mL)", 0, 2000, 0, 
                help="Normal: 300-900. Below 500 may cause fatigue. Find this on your bloodwork as 'B12' or 'Cobalamin'."
            )
            vit_d_level = st.number_input(
                "Vitamin D (ng/mL)", 0, 150, 0, 
                help="Optimal: 30-60. Below 20 is deficient. Listed as '25-OH Vitamin D' or 'Vitamin D, 25-Hydroxy'."
            )
            iron_level = st.number_input(
                "Iron (mcg/dL)", 0, 300, 0, 
                help="Normal: 60-170. Low iron = fatigue. Listed as 'Serum Iron' on bloodwork."
            )
            
            st.markdown("##### 🔥 Inflammation Markers")
            st.caption("These show if your body is dealing with hidden inflammation")
            
            crp_level = st.number_input(
                "CRP (mg/L)", 0.0, 50.0, 0.0, 
                help="Optimal: <1.0. High CRP = inflammation. Listed as 'C-Reactive Protein' or 'hs-CRP'."
            )
            if crp_level > 0:
                st.caption(f"ℹ️ {HEALTH_GLOSSARY['CRP']['simple']}")
                
            homocysteine = st.number_input(
                "Homocysteine (umol/L)", 0.0, 50.0, 0.0, 
                help="Optimal: <10. High levels stress blood vessels. B vitamins help lower it."
            )
            
            st.markdown("##### 🍬 Metabolic")
            glucose = st.number_input(
                "Fasting Glucose (mg/dL)", 0, 400, 0, 
                help="Normal: <100. 100-125 = pre-diabetic. Listed as 'Glucose, Fasting' or 'FBS'."
            )
            if glucose > 0:
                st.caption(f"ℹ️ {HEALTH_GLOSSARY['Fasting Glucose']['simple']}")
        
        st.markdown("---")
        
        # Generate button
        if st.button("✨ Generate My Plan", type="primary", use_container_width=True):
            if not name:
                name = "User"
            
            # Build user context
            financials = Financials(
                weekly_budget=float(weekly_budget),
                snap_status=snap_status,
                wic_status=wic_status
            )
            
            logistics = Logistics(
                zip_code=zip_code,
                has_vehicle=has_vehicle,
                has_public_transit=has_transit,
                grocery_trips_per_week=trips_per_week,
                max_travel_distance_miles=15.0 if has_vehicle else (5.0 if has_transit else 2.0)
            )
            
            # Combine preset selections with custom entries
            all_family_history = list(family_history)
            
            all_symptoms = list(current_symptoms)
            
            all_allergies = list(allergies)
            
            medical = MedicalHistory(
                family_history=[h.lower().replace(" ", "_") for h in all_family_history],
                current_symptoms=[s.lower().replace(" ", "_") for s in all_symptoms],
                known_allergies=[a.lower() for a in all_allergies]
            )
            
            # Lab results
            lab_results = None
            if any([b12_level, vit_d_level, iron_level, crp_level, homocysteine, glucose, 
                   mthfr_variant != "Not Tested", comt_variant != "Not Tested"]):
                lab_results = LabResults(
                    mthfr_variant=mthfr_variant if mthfr_variant not in ["Not Tested", "Normal"] else None,
                    comt_variant=comt_variant.lower() if comt_variant not in ["Not Tested", "Normal"] else None,
                    vitamin_b12_level=float(b12_level) if b12_level > 0 else None,
                    vitamin_d_level=float(vit_d_level) if vit_d_level > 0 else None,
                    iron_level=float(iron_level) if iron_level > 0 else None,
                    crp_level=float(crp_level) if crp_level > 0 else None,
                    homocysteine_level=float(homocysteine) if homocysteine > 0 else None,
                    glucose_fasting=float(glucose) if glucose > 0 else None
                )
            
            user = UserContext(
                user_id=f"user_{name.lower().replace(' ', '_')}",
                name=name,
                financials=financials,
                logistics=logistics,
                medical=medical,
                lab_results=lab_results
            )
            
            st.session_state.user_context = user
            run_analysis()
            st.rerun()


def run_analysis():
    """Run the full analysis pipeline."""
    user = st.session_state.user_context
    if user:
        st.session_state.nutrient_priorities = analyze_lab_data(user)
        st.session_state.resource_map = resource_locator(user)
        st.session_state.shopping_list = generate_shopping_list(
            user,
            st.session_state.nutrient_priorities,
            st.session_state.resource_map
        )
        st.session_state.analysis_complete = True


def render_welcome():
    """Render welcome screen when no analysis is complete."""
    # Clean header
    st.markdown('<h1 class="main-header">🥕 EatWell</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Personalized nutrition planning for everyone, regardless of income, location, or circumstances.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="simple-explain">
            <strong>💰 Budget-Aware</strong><br>
            We consider your budget and benefits (SNAP/WIC) to find affordable nutrition that works for you.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="simple-explain">
            <strong>🧬 Science-Based</strong><br>
            Recommendations based on your symptoms, family history, and lab results — explained in plain language.
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="simple-explain">
            <strong>📍 Location-Smart</strong><br>
            Find nearby stores and free food pantries that match your transportation options.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabbed welcome content for cleaner organization
    welcome_tab1, welcome_tab2, welcome_tab3, welcome_tab4 = st.tabs(["🚀 Get Started", "📚 Learn Health Terms", "❓ FAQ", "💬 Ask AI"])
    
    with welcome_tab1:
        st.info("👈 Fill out the form in the sidebar, or click **Load Demo Data** to see how it works!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **What you'll need (optional but helpful):**
            - Your weekly grocery budget
            - Any recent blood test results
            - Current health symptoms you're experiencing
            """)
        
        with col2:
            st.success("💡 **Don't have lab results?** No problem! We can still help based on your symptoms and family history alone.")
    
    with welcome_tab2:
        st.markdown("### 🧬 Genetic Markers")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="simple-explain">
                <strong>MTHFR (B-Vitamin Helper)</strong><br>
                Helps your body use folate for energy and heart health.
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="simple-explain">
                <strong>COMT (Stress Manager)</strong><br>
                Helps your brain process stress and stay calm.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 💊 Vitamins & Minerals")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="simple-explain">
                <strong>Vitamin B12 (Energy Spark)</strong><br>
                Keeps your brain sharp and your energy levels up.
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="simple-explain">
                <strong>Vitamin D (Sunshine Shield)</strong><br>
                Keeps your bones strong and helps you fight off colds.
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="simple-explain">
                <strong>Iron (Oxygen Mover)</strong><br>
                Carries oxygen to your muscles so you don't feel weak or dizzy.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Health Markers")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="simple-explain">
                <strong>CRP (The Body's Fire)</strong><br>
                Measures "inflammation" (internal stress). High levels can wear your body down.
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="simple-explain">
                <strong>Homocysteine (Heart Warning)</strong><br>
                A protein that can irritate blood vessels if it gets too high.
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="simple-explain">
                <strong>Fasting Glucose (Blood Sugar)</strong><br>
                Measures sugar in your blood to check your risk for Diabetes.
            </div>
            """, unsafe_allow_html=True)
        
        st.caption("⚠️ Note: These definitions are for educational purposes. Please consult with a healthcare provider to discuss your specific lab results or starting new supplements.")
    
    with welcome_tab3:
        st.markdown("### ❓ Frequently Asked Questions")
        
        st.markdown("""
        **Q: Do I need blood test results to use this?**
        
        A: No! We can create recommendations based on your symptoms and family history alone. Lab results just make it more precise.
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Q: What is SNAP and how do I qualify?**
        
        A: SNAP (Supplemental Nutrition Assistance Program) helps low-income individuals and families buy food. Eligibility depends on income and household size. Visit [fns.usda.gov/snap](https://www.fns.usda.gov/snap) to learn more.
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Q: I don't understand medical terms. Will I be able to use this?**
        
        A: Absolutely! We explain every health term in plain, simple language. Look for the 📚 Learn tab after generating your plan.
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Q: Is this medical advice?**
        
        A: This app provides nutrition education and suggestions, not medical advice. Always consult with a doctor for medical decisions.
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **🥗 Why does food matter for health?**
        
        Food is powerful medicine. What you eat directly affects:
        
        - **Energy levels** — The right nutrients give you lasting energy
        - **Brain function** — B vitamins and omega-3s support clear thinking
        - **Inflammation** — Some foods calm inflammation, others increase it
        - **Disease risk** — Diet can help prevent diabetes, heart disease, and more
        - **How you feel daily** — Better nutrition = better mood and fewer symptoms
        
        The challenge? Knowing WHICH foods YOUR specific body needs. That's what this app helps with!
        """)
    
    with welcome_tab4:
        render_chatbot()
    
    # Ethical Disclaimer
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #ffd09b40; border: 1px solid #ec813b; border-radius: 10px; padding: 1.5rem; margin-top: 1rem;">
        <h4 style="color: #4f7e52; margin-top: 0;">⚖️ Ethical Notice</h4>
        <p style="font-size: 0.9rem; color: #555;">
            This tool is for <strong>informational and educational purposes only</strong> and is not a substitute for professional medical advice, diagnosis, or treatment. Our AI-driven insights are recommendations based on your inputs and may contain false positives or inaccuracies; always verify results with a healthcare provider.
        </p>
        <p style="font-size: 0.9rem; color: #555;">
            To protect your dignity and safety, we prioritize <strong>on-device privacy</strong>: your sensitive health and financial data is analyzed locally on your phone and is not stored on our servers or sold to third parties. By using this app, you acknowledge that you are responsible for your own health decisions and should consult a professional before starting any new supplement or dietary regimen.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_dashboard():
    """Render the main dashboard with analysis results."""
    user = st.session_state.user_context
    nutrients = st.session_state.nutrient_priorities
    resources = st.session_state.resource_map
    shopping = st.session_state.shopping_list
    
    # Header
    st.markdown(f'<h1 class="main-header">🥕 Welcome back, {user.name}!</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Here\'s your personalized EatWell nutrition plan.</p>', unsafe_allow_html=True)
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Weekly Budget",
            f"${user.financials.weekly_budget:.0f}",
            delta=f"${shopping.budget_remaining:.0f} left" if shopping.budget_remaining > 0 else None
        )
    
    with col2:
        st.metric(
            "Priority Nutrients",
            len(nutrients.needs),
            delta=f"{len([n for n in nutrients.needs if n.priority <= 2])} critical"
        )
    
    with col3:
        st.metric(
            "Nearby Stores",
            len(resources.accessible_stores),
            delta=f"{len(resources.food_pantries)} pantries"
        )
    
    with col4:
        st.metric(
            "Shopping Items",
            len(shopping.items),
            delta=f"${shopping.total_estimated_cost:.0f} total"
        )
    
    st.markdown("---")
    
    # Main content tabs (chatbot included as a tab for cleaner layout)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛒 Shopping List", 
        "🔬 Nutrients", 
        "📍 Stores",
        "❓ Why",
        "📚 Learn",
        "💬 Ask AI"
    ])
    
    with tab1:
        render_shopping_list(shopping, user, nutrients)
    
    with tab2:
        render_nutrient_analysis(nutrients, user)
    
    with tab3:
        render_store_finder(resources, user)
    
    with tab4:
        render_why_section(shopping, nutrients, user)
    
    with tab5:
        render_learn_section(user, nutrients)
    
    with tab6:
        render_chatbot()


def render_shopping_list(shopping: ShoppingList, user: UserContext, nutrients: NutrientPriorityList):
    """Render the shopping list tab."""
    st.markdown("## 🛒 Your Curated Shopping List")
    
    # Budget bar
    budget = user.financials.weekly_budget
    spent = shopping.total_estimated_cost
    pct = min(100, (spent / budget) * 100) if budget > 0 else 0
    
    st.progress(pct / 100, text=f"Budget: ${spent:.2f} / ${budget:.2f}")
    
    # Benefits badges
    badges = []
    if user.financials.snap_status:
        badges.append("✓ SNAP Applied")
    if user.financials.wic_status:
        badges.append("✓ WIC Applied")
    if badges:
        st.success(" | ".join(badges))
    
    # Food Pantry recommendations
    if shopping.pantry_items:
        st.markdown("### 🆓 From Food Pantry (FREE)")
        for item in shopping.pantry_items:
            st.markdown(f"""
            <div class="store-card">
                <span class="free-badge">FREE</span>
                <strong>{item.food.name}</strong><br>
                <small>📍 {item.suggested_store}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Main shopping list by priority
    st.markdown("### 📋 Items to Purchase")
    
    priority_items = {
        ShoppingPriority.CRITICAL: [],
        ShoppingPriority.HIGH: [],
        ShoppingPriority.MODERATE: [],
        ShoppingPriority.OPTIONAL: []
    }
    
    for item in shopping.items:
        priority_items[item.priority].append(item)
    
    priority_config = {
        ShoppingPriority.CRITICAL: ("🔴 Critical", "priority-critical"),
        ShoppingPriority.HIGH: ("🟠 High Priority", "priority-high"),
        ShoppingPriority.MODERATE: ("🟡 Moderate", "priority-moderate"),
        ShoppingPriority.OPTIONAL: ("🟢 Optional", "priority-optional")
    }
    
    for priority, items in priority_items.items():
        if items:
            label, css_class = priority_config[priority]
            st.markdown(f"**{label}**")
            
            for item in items:
                snap_badge = ' <span class="snap-badge">SNAP✓</span>' if item.food.snap_eligible else ''
                nutrients_str = ", ".join(item.nutrients_addressed[:3])
                
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>{item.food.name}</strong> — ${item.estimated_cost:.2f}{snap_badge}<br>
                    <small>🎯 Nutrients: {nutrients_str}</small><br>
                    <small>🏪 Suggested: {item.suggested_store or 'Any store'}</small>
                </div>
                """, unsafe_allow_html=True)


def render_nutrient_analysis(nutrients: NutrientPriorityList, user: UserContext):
    """Render the nutrient analysis tab."""
    st.markdown("## 🔬 Your Nutrient Analysis")
    
    # Warnings
    if nutrients.warnings:
        for warning in nutrients.warnings:
            st.warning(warning)
    
    # Lab results summary
    if user.lab_results:
        st.markdown("### 🧬 Your Biomarkers")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if user.lab_results.mthfr_variant:
                st.error(f"**MTHFR:** {user.lab_results.mthfr_variant}")
            if user.lab_results.vitamin_b12_level:
                status = "🔴" if user.lab_results.vitamin_b12_level < 500 else "🟢"
                st.info(f"{status} **B12:** {user.lab_results.vitamin_b12_level} pg/mL")
        
        with col2:
            if user.lab_results.vitamin_d_level:
                status = "🔴" if user.lab_results.vitamin_d_level < 30 else "🟢"
                st.info(f"{status} **Vitamin D:** {user.lab_results.vitamin_d_level} ng/mL")
            if user.lab_results.iron_level:
                status = "🔴" if user.lab_results.iron_level < 60 else "🟢"
                st.info(f"{status} **Iron:** {user.lab_results.iron_level} mcg/dL")
        
        with col3:
            if user.lab_results.crp_level:
                status = "🔴" if user.lab_results.crp_level > 1 else "🟢"
                st.info(f"{status} **CRP:** {user.lab_results.crp_level} mg/L")
            if user.lab_results.glucose_fasting:
                status = "🔴" if user.lab_results.glucose_fasting > 100 else "🟢"
                st.info(f"{status} **Glucose:** {user.lab_results.glucose_fasting} mg/dL")
    
    st.markdown("---")
    
    # Nutrient priorities
    st.markdown("### 📊 Prioritized Nutrient Needs")
    
    priority_labels = {1: "🔴 Critical", 2: "🟠 High", 3: "🟡 Moderate", 4: "🟢 Preventive", 5: "⚪ Supportive"}
    
    for need in nutrients.needs:
        with st.expander(f"{priority_labels.get(need.priority, '⚪')} **{need.nutrient}**"):
            st.markdown(f"**Why this matters for you:**")
            st.write(need.reason)
            
            if need.related_markers:
                st.markdown(f"**Related markers:** {', '.join(need.related_markers[:4])}")
            
            if need.food_sources:
                st.markdown(f"**Best food sources:**")
                st.write(", ".join(need.food_sources[:6]))


def render_store_finder(resources: ResourceMap, user: UserContext):
    """Render the store finder tab."""
    st.markdown("## 📍 Nearby Food Resources")
    
    st.info(f"📍 Showing results for ZIP: **{resources.user_zip}** | 🚗 Mobility: **{user.logistics.mobility_level.upper()}**")
    
    # Food Pantries
    if resources.food_pantries:
        st.markdown("### 🆓 Food Pantries (FREE)")
        
        for tf in resources.food_pantries:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="store-card">
                    <span class="free-badge">FREE</span>
                    <strong>{tf.store.name}</strong><br>
                    📍 {tf.store.distance_miles} miles ({tf.travel_method}, ~{tf.estimated_time_minutes} min)<br>
                    🕐 {tf.store.hours}<br>
                    📦 Items: {', '.join(tf.store.specialty_items[:3])}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.metric("Score", f"{tf.accessibility_score:.0%}")
    
    st.markdown("---")
    
    # SNAP Stores
    if user.financials.snap_status and resources.snap_stores:
        st.markdown("### 🏪 SNAP-Authorized Stores")
        
        for tf in resources.snap_stores[:5]:
            if tf.store.store_type != StoreType.FOOD_PANTRY:
                price_tier = "💲" * tf.store.price_tier
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    wic_badge = ' <span style="background:#9c27b0;color:white;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.7rem;">WIC</span>' if tf.store.wic_accepted else ''
                    st.markdown(f"""
                    <div class="store-card">
                        <span class="snap-badge">SNAP</span>{wic_badge}
                        <strong>{tf.store.name}</strong> {price_tier}<br>
                        📍 {tf.store.distance_miles} miles ({tf.travel_method})<br>
                        📦 Inventory: {tf.store.inventory_level.value}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.metric("Score", f"{tf.accessibility_score:.0%}")
    
    st.markdown("---")
    
    # All stores
    st.markdown("### 🗺️ All Accessible Stores")
    
    store_data = []
    for tf in resources.accessible_stores[:8]:
        store_data.append({
            "Store": tf.store.name,
            "Type": tf.store.store_type.value.replace("_", " ").title(),
            "Distance": f"{tf.store.distance_miles} mi",
            "Travel": f"{tf.travel_method} ({tf.estimated_time_minutes} min)",
            "Price": "FREE" if tf.store.store_type == StoreType.FOOD_PANTRY else "💲" * tf.store.price_tier,
            "SNAP": "✓" if tf.store.snap_accepted else "—",
            "Score": f"{tf.accessibility_score:.0%}"
        })
    
    st.dataframe(store_data, use_container_width=True, hide_index=True)


def render_why_section(shopping: ShoppingList, nutrients: NutrientPriorityList, user: UserContext):
    """Render the interactive 'Why' explanation section."""
    st.markdown("## ❓ Ask Why")
    st.markdown("*Understand the connection between your health markers and food recommendations.*")
    
    # Select an item to explain
    item_names = [item.food.name for item in shopping.items]
    
    if not item_names:
        st.warning("Generate a shopping list first to see explanations.")
        return
    
    selected_item = st.selectbox(
        "Select an item to understand why it was recommended:",
        item_names,
        index=0
    )
    
    # Find the item
    selected = None
    for item in shopping.items:
        if item.food.name == selected_item:
            selected = item
            break
    
    if selected:
        st.markdown("---")
        
        # Visual explanation
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"### 📦 {selected.food.name}")
            st.metric("Price", f"${selected.estimated_cost:.2f}")
            st.metric("Priority", selected.priority.name)
            
            if selected.food.snap_eligible:
                st.success("✓ SNAP Eligible")
        
        with col2:
            st.markdown("### 🔬 Biological Connection")
            
            for nutrient in selected.nutrients_addressed:
                # Find the matching nutrient need
                for need in nutrients.needs:
                    if need.nutrient == nutrient:
                        st.markdown(f"""
                        <div class="explanation-box">
                            <strong>➤ {nutrient}</strong><br>
                            {need.reason}<br><br>
                            <small><strong>Related markers:</strong> {', '.join(need.related_markers[:3])}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        break
        
        # Full nutrient profile
        st.markdown("### 🥗 Nutrient Profile")
        st.write(f"**This food provides:** {', '.join(selected.food.nutrients_provided)}")
        
        # Symptoms connection
        if user.medical.current_symptoms:
            matching = []
            for symptom in user.medical.current_symptoms:
                for nutrient in selected.nutrients_addressed:
                    if any(symptom.lower() in marker.lower() for need in nutrients.needs 
                          if need.nutrient == nutrient for marker in need.related_markers):
                        matching.append(symptom)
            
            if matching:
                st.info(f"🩺 **Connected to your symptoms:** {', '.join(set(matching))}")
    
    st.markdown("---")
    
    # Quick nutrient lookup
    st.markdown("### 🔍 Nutrient Deep Dive")
    
    nutrient_names = [need.nutrient for need in nutrients.needs]
    selected_nutrient = st.selectbox("Select a nutrient to learn more:", nutrient_names)
    
    for need in nutrients.needs:
        if need.nutrient == selected_nutrient:
            st.markdown(f"""
            <div class="explanation-box">
                <h4>{need.nutrient}</h4>
                <p><strong>Priority Level:</strong> {need.priority}</p>
                <p><strong>Why it matters:</strong> {need.reason}</p>
                <p><strong>Related markers:</strong> {', '.join(need.related_markers)}</p>
                <p><strong>Best food sources:</strong> {', '.join(need.food_sources[:6])}</p>
            </div>
            """, unsafe_allow_html=True)
            break


def render_learn_section(user: UserContext, nutrients: NutrientPriorityList):
    """Render the health education/literacy section."""
    st.markdown("## 📚 Learn: Understanding Your Health")
    st.markdown("*We believe everyone deserves to understand their health. Here's what these terms mean in plain language.*")
    
    # Personalized learning based on user's conditions
    st.markdown("---")
    
    # Section 1: Terms relevant to YOUR results
    st.markdown("### 🎯 Terms Relevant to You")
    st.caption("Based on your health profile, here are the most important concepts to understand:")
    
    relevant_terms = []
    
    # Add terms based on user's lab results
    if user.lab_results:
        if user.lab_results.mthfr_variant:
            relevant_terms.extend(["MTHFR", "Methylation"])
        if user.lab_results.vitamin_b12_level:
            relevant_terms.append("Vitamin B12")
        if user.lab_results.vitamin_d_level:
            relevant_terms.append("Vitamin D")
        if user.lab_results.iron_level:
            relevant_terms.append("Iron")
        if user.lab_results.crp_level:
            relevant_terms.extend(["CRP", "Anti-inflammatory"])
        if user.lab_results.homocysteine_level:
            relevant_terms.append("Homocysteine")
        if user.lab_results.glucose_fasting:
            relevant_terms.append("Fasting Glucose")
    
    # Add terms based on nutrients identified
    for need in nutrients.needs[:5]:
        if "Omega" in need.nutrient:
            relevant_terms.append("Omega-3 Fatty Acids")
        if "inflammatory" in need.nutrient.lower():
            relevant_terms.append("Anti-inflammatory")
    
    # Add benefit terms
    if user.financials.snap_status:
        relevant_terms.append("SNAP")
    if user.financials.wic_status:
        relevant_terms.append("WIC")
    
    # Remove duplicates while preserving order
    relevant_terms = list(dict.fromkeys(relevant_terms))
    
    if relevant_terms:
        for term in relevant_terms[:6]:
            if term in HEALTH_GLOSSARY:
                info = HEALTH_GLOSSARY[term]
                with st.expander(f"📖 **{term}** — {info['simple']}"):
                    st.markdown(f"""
                    <div class="edu-card">
                        <h4>🤔 What is it?</h4>
                        <p>{info['detail']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="simple-explain">
                        <strong>💡 Why it matters for you:</strong><br>
                        {info['why_matters']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success(f"🥗 **Foods that help:** {info['food_connection']}")
    else:
        st.info("Fill out the sidebar form to see personalized health education!")
    
    st.markdown("---")
    
    # Section 2: Understanding your symptoms
    if user.medical.current_symptoms:
        st.markdown("### 🩺 Understanding Your Symptoms")
        st.caption("Here's what your symptoms might mean and how food can help:")
        
        for symptom in user.medical.current_symptoms[:4]:
            symptom_key = symptom.lower().replace(" ", "_")
            if symptom_key in SYMPTOM_EXPLANATIONS:
                info = SYMPTOM_EXPLANATIONS[symptom_key]
                with st.expander(f"💭 **{symptom.replace('_', ' ').title()}**"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**What it means:** {info['what_it_means']}")
                        st.markdown(f"**Common causes:** {info['common_causes']}")
                    with col2:
                        st.success(f"**🥗 Foods that can help:**\n\n{info['food_help']}")
    
    st.markdown("---")
    
    # Section 3: Full glossary
    st.markdown("### 📖 Health Glossary")
    st.caption("Browse all health terms explained in plain language")
    
    search_term = st.text_input("🔍 Search for a term:", placeholder="e.g., B12, inflammation, SNAP")
    
    # Filter glossary
    filtered_terms = HEALTH_GLOSSARY
    if search_term:
        filtered_terms = {k: v for k, v in HEALTH_GLOSSARY.items() 
                        if search_term.lower() in k.lower() or search_term.lower() in v['simple'].lower()}
    
    if filtered_terms:
        cols = st.columns(2)
        for idx, (term, info) in enumerate(filtered_terms.items()):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="glossary-term">
                    <strong>{term}</strong><br>
                    <small>{info['simple']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Learn more"):
                    st.write(info['detail'])
                    st.caption(f"🥗 Foods: {info['food_connection']}")
    else:
        st.warning(f"No terms found matching '{search_term}'")
    
    st.markdown("---")
    
    # Section 4: Quick tips
    st.markdown("### 💡 Quick Tips for Healthy Eating on a Budget")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🛒 Shopping Smart:**
        - Buy frozen vegetables — just as nutritious, last longer, often cheaper
        - Canned beans/lentils are excellent protein sources
        - Store brands are usually the same quality as name brands
        - Shop the perimeter of the store for whole foods
        - Buy in-season produce for best prices
        """)
        
        st.markdown("""
        **🏪 Using Food Assistance:**
        - SNAP can be used at most farmers markets (often doubled!)
        - Food pantries are there to help — no shame in using them
        - WIC provides nutritious staples for families
        """)
    
    with col2:
        st.markdown("""
        **🍳 Cooking Tips:**
        - Batch cook on weekends to save time and money
        - One-pot meals (soups, stews) stretch ingredients further
        - Eggs are cheap, versatile, and nutritious
        - Beans + rice = complete protein for pennies
        """)
        
        st.markdown("""
        **🧠 Reading Your Body:**
        - Fatigue often = need more iron or B vitamins
        - Joint pain often = need more omega-3s and anti-inflammatory foods
        - Getting sick a lot = might need more vitamin D and zinc
        - Listen to your body — cravings sometimes signal deficiencies
        """)
    
    # Disclaimer
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** This app provides general nutrition information for educational purposes. It is not medical advice. Always consult with a healthcare provider for personalized medical guidance.")


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    # Full-width main content area (chatbot is now a tab)
    if st.session_state.analysis_complete:
        render_dashboard()
    else:
        render_welcome()


if __name__ == "__main__":
    main()
