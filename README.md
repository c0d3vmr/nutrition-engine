# Health Equity Nutrition App

A comprehensive Python application that creates personalized nutrition recommendations based on financial constraints, geographic accessibility, medical needs, and genetic/methylation markers.

## Overview

This app addresses health equity by helping users with limited resources access personalized nutrition guidance that considers:

- **Financial Reality**: Weekly budget, SNAP/WIC benefits, income level
- **Geographic Access**: Location, transportation, nearby stores
- **Health Needs**: Symptoms, family history, previous conditions
- **Biomarkers**: Methylation variants (MTHFR, COMT), lab results

## Project Structure

```
nutrition-project/
├── main.py              # Entry point - run the app
├── user_context.py      # Phase 1: User questionnaire data
├── bio_analyzer.py      # Phase 2: Bio-analytical engine
├── resource_locator.py  # Phase 3: Geographic/financial mapping
├── shopping_planner.py  # Phase 4: Curated shopping list
├── interactive_cli.py   # Phase 5: Interactive feedback
└── README.md
```

## Usage

### Demo Mode (default)
```bash
python main.py
```
Runs with sample user data to demonstrate all features.

### Interactive Mode
```bash
python main.py --interactive
```
Collects real user input via questionnaire.

## Phases

### Phase 1: Questionnaire Data Input
The `UserContext` class stores:
- **Financials**: Weekly budget, SNAP/WIC status, income
- **Logistics**: Zip code, vehicle access, grocery trip frequency
- **Medical**: Family history, previous conditions, current symptoms
- **Lab Results**: Methylation markers, vitamin levels, inflammation markers

### Phase 2: Bio-Analytical Engine
The `analyze_lab_data()` function:
- Analyzes methylation markers (MTHFR, COMT variants)
- Evaluates vitamin/mineral levels
- Assesses inflammation markers (CRP, homocysteine)
- Considers symptoms and family history
- Outputs a prioritized **Nutrient Priority List**

Example output:
- "Requires Methylfolate due to MTHFR C677T variant"
- "Requires Anti-inflammatories due to elevated CRP"

### Phase 3: Geographic & Financial Mapping
The `resource_locator()` function:
- Uses synthetic database of nearby stores
- Calculates travel feasibility based on transportation
- Identifies SNAP/WIC authorized locations
- Prioritizes food pantries for low-budget users

### Phase 4: Curated Shopping Planner
The `generate_shopping_list()` function:
- Matches biological needs with affordable food sources
- Prioritizes cheapest sources for highest-priority nutrients
- Recommends food pantries first for low budgets
- Filters by SNAP eligibility when applicable
- Respects food allergies

### Phase 5: Interactive Feedback
CLI commands:
- `why [item]` - Explain why a food was recommended
- `explain [nutrient]` - Detail a nutrient's importance
- `markers` - Show methylation/lab analysis
- `budget` - Show budget breakdown
- `list` - Display shopping list
- `stores` - Show store recommendations

## Example Session

```
🤖 Ask me > why spinach

📦 Spinach (frozen bag)
   Price: $1.50
   Priority: CRITICAL

   🔬 BIOLOGICAL CONNECTION:
   → Iron:
     Iron level (50 mcg/dL) is low - may cause fatigue and anemia
     Related markers: serum iron, ferritin, TIBC

   → Methylfolate:
     MTHFR C677T variant detected - reduced ability to convert folic acid
     Related markers: MTHFR, homocysteine

   📊 This food provides: Iron, Methylfolate, Magnesium

   💡 Selection reason: Addresses Iron: Iron level (50 mcg/dL) is low...
```

## Requirements

- Python 3.7+
- No external dependencies (stdlib only)

## Features

- **Health Equity Focus**: Prioritizes accessibility and affordability
- **Methylation-Aware**: Considers MTHFR/COMT variants
- **Budget-Conscious**: Alternatives for tight budgets
- **Transparent**: Users can ask "why?" about any recommendation
- **Privacy-Respecting**: All data stays local

## Sample Data

The demo uses a sample user with:
- $60/week budget with SNAP benefits
- No vehicle, public transit available
- Family history of diabetes, hypertension
- MTHFR C677T variant
- Low vitamin D, elevated CRP

## License

Open source - use freely for health equity initiatives.
