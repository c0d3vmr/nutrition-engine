"""
Phase 2: The Bio-Analytical Engine
Simulates ingestion of methylation and clinical lab results.
Outputs a Nutrient Priority List based on genetic markers and symptoms.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from user_context import UserContext, LabResults, MedicalHistory


@dataclass
class NutrientNeed:
    """Represents a single nutrient need with reasoning."""
    nutrient: str
    priority: int  # 1 = highest, 5 = lowest
    reason: str
    related_markers: List[str] = field(default_factory=list)
    food_sources: List[str] = field(default_factory=list)
    
    def explain(self) -> str:
        """Generate a human-readable explanation."""
        return f"{self.nutrient} (Priority {self.priority}): {self.reason}"


@dataclass
class NutrientPriorityList:
    """Complete nutrient priority analysis results."""
    user_id: str
    needs: List[NutrientNeed] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def get_top_priorities(self, n: int = 5) -> List[NutrientNeed]:
        """Get the top N priority nutrients."""
        sorted_needs = sorted(self.needs, key=lambda x: x.priority)
        return sorted_needs[:n]
    
    def get_all_food_sources(self) -> Dict[str, List[str]]:
        """Get all recommended food sources grouped by nutrient."""
        return {need.nutrient: need.food_sources for need in self.needs}


# Reference ranges for lab values
LAB_REFERENCE_RANGES = {
    "vitamin_b12": {"low": 300, "optimal_low": 500, "optimal_high": 900, "unit": "pg/mL"},
    "vitamin_d": {"low": 20, "optimal_low": 40, "optimal_high": 60, "unit": "ng/mL"},
    "iron": {"low": 60, "optimal_low": 80, "optimal_high": 170, "unit": "mcg/dL"},
    "ferritin": {"low": 30, "optimal_low": 50, "optimal_high": 150, "unit": "ng/mL"},
    "crp": {"optimal_high": 1.0, "elevated": 3.0, "high": 10.0, "unit": "mg/L"},
    "homocysteine": {"optimal_high": 7, "elevated": 12, "high": 15, "unit": "umol/L"},
    "glucose_fasting": {"optimal_high": 100, "prediabetic": 125, "diabetic": 126, "unit": "mg/dL"},
    "omega3_index": {"low": 4, "optimal_low": 8, "optimal_high": 12, "unit": "%"}
}


# Nutrient-to-food mapping
NUTRIENT_FOOD_SOURCES = {
    "Vitamin B12": [
        "eggs", "fortified cereals", "nutritional yeast", "sardines", 
        "beef liver", "clams", "fortified plant milk"
    ],
    "Methylfolate": [
        "spinach", "lentils", "asparagus", "broccoli", "avocado",
        "black-eyed peas", "brussels sprouts", "romaine lettuce"
    ],
    "Vitamin D": [
        "fortified milk", "egg yolks", "salmon", "sardines",
        "fortified orange juice", "mushrooms (UV-exposed)"
    ],
    "Iron": [
        "spinach", "lentils", "chickpeas", "beef", "fortified cereals",
        "pumpkin seeds", "quinoa", "dark chocolate"
    ],
    "Omega-3 Fatty Acids": [
        "salmon", "sardines", "walnuts", "flaxseed", "chia seeds",
        "mackerel", "hemp seeds"
    ],
    "Anti-inflammatory Foods": [
        "turmeric", "ginger", "berries", "leafy greens", "fatty fish",
        "olive oil", "tomatoes", "nuts", "green tea"
    ],
    "Magnesium": [
        "spinach", "pumpkin seeds", "black beans", "almonds",
        "avocado", "dark chocolate", "quinoa"
    ],
    "Fiber": [
        "oats", "beans", "lentils", "berries", "broccoli",
        "apples", "whole grains", "chia seeds"
    ],
    "Antioxidants": [
        "berries", "dark leafy greens", "pecans", "artichokes",
        "beets", "red cabbage", "dark chocolate"
    ],
    "Chromium": [
        "broccoli", "grape juice", "whole grains", "beef",
        "green beans", "potatoes"
    ]
}


def analyze_methylation_markers(lab_results: LabResults) -> List[NutrientNeed]:
    """Analyze methylation-related genetic markers."""
    needs = []
    
    # MTHFR Analysis
    if lab_results.mthfr_variant:
        variant = lab_results.mthfr_variant.upper()
        
        if variant in ["C677T", "COMPOUND", "HOMOZYGOUS"]:
            needs.append(NutrientNeed(
                nutrient="Methylfolate",
                priority=1,
                reason=f"MTHFR {variant} variant detected - reduced ability to convert folic acid to active methylfolate",
                related_markers=["MTHFR", "homocysteine"],
                food_sources=NUTRIENT_FOOD_SOURCES["Methylfolate"]
            ))
            needs.append(NutrientNeed(
                nutrient="Vitamin B12",
                priority=1,
                reason=f"MTHFR {variant} requires adequate B12 for proper methylation cycle function",
                related_markers=["MTHFR", "methylation"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin B12"]
            ))
        elif variant == "A1298C":
            needs.append(NutrientNeed(
                nutrient="Methylfolate",
                priority=2,
                reason="MTHFR A1298C variant - moderately reduced folate metabolism",
                related_markers=["MTHFR", "BH4"],
                food_sources=NUTRIENT_FOOD_SOURCES["Methylfolate"]
            ))
    
    # COMT Analysis
    if lab_results.comt_variant:
        if lab_results.comt_variant.lower() == "slow":
            needs.append(NutrientNeed(
                nutrient="Magnesium",
                priority=2,
                reason="Slow COMT variant - magnesium supports stress response and catecholamine metabolism",
                related_markers=["COMT", "catecholamines"],
                food_sources=NUTRIENT_FOOD_SOURCES["Magnesium"]
            ))
    
    return needs


def analyze_vitamin_levels(lab_results: LabResults) -> List[NutrientNeed]:
    """Analyze vitamin and mineral levels from lab results."""
    needs = []
    
    # Vitamin B12
    if lab_results.vitamin_b12_level is not None:
        level = lab_results.vitamin_b12_level
        ref = LAB_REFERENCE_RANGES["vitamin_b12"]
        
        if level < ref["low"]:
            needs.append(NutrientNeed(
                nutrient="Vitamin B12",
                priority=1,
                reason=f"B12 level ({level} {ref['unit']}) is deficient - urgent supplementation recommended",
                related_markers=["B12", "MCV", "homocysteine"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin B12"]
            ))
        elif level < ref["optimal_low"]:
            needs.append(NutrientNeed(
                nutrient="Vitamin B12",
                priority=2,
                reason=f"B12 level ({level} {ref['unit']}) is suboptimal - dietary increase recommended",
                related_markers=["B12"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin B12"]
            ))
    
    # Vitamin D
    if lab_results.vitamin_d_level is not None:
        level = lab_results.vitamin_d_level
        ref = LAB_REFERENCE_RANGES["vitamin_d"]
        
        if level < ref["low"]:
            needs.append(NutrientNeed(
                nutrient="Vitamin D",
                priority=1,
                reason=f"Vitamin D level ({level} {ref['unit']}) is deficient - significant health impact",
                related_markers=["25-OH Vitamin D", "calcium", "PTH"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin D"]
            ))
        elif level < ref["optimal_low"]:
            needs.append(NutrientNeed(
                nutrient="Vitamin D",
                priority=2,
                reason=f"Vitamin D level ({level} {ref['unit']}) is insufficient",
                related_markers=["25-OH Vitamin D"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin D"]
            ))
    
    # Iron
    if lab_results.iron_level is not None:
        level = lab_results.iron_level
        ref = LAB_REFERENCE_RANGES["iron"]
        
        if level < ref["low"]:
            needs.append(NutrientNeed(
                nutrient="Iron",
                priority=1,
                reason=f"Iron level ({level} {ref['unit']}) is low - may cause fatigue and anemia",
                related_markers=["serum iron", "ferritin", "TIBC"],
                food_sources=NUTRIENT_FOOD_SOURCES["Iron"]
            ))
    
    return needs


def analyze_inflammation_markers(lab_results: LabResults) -> List[NutrientNeed]:
    """Analyze inflammation markers and recommend anti-inflammatory nutrients."""
    needs = []
    
    # CRP (C-Reactive Protein)
    if lab_results.crp_level is not None:
        level = lab_results.crp_level
        ref = LAB_REFERENCE_RANGES["crp"]
        
        if level > ref["elevated"]:
            priority = 1 if level > ref["high"] else 2
            needs.append(NutrientNeed(
                nutrient="Anti-inflammatory Foods",
                priority=priority,
                reason=f"CRP level ({level} {ref['unit']}) indicates systemic inflammation",
                related_markers=["CRP", "ESR", "inflammation"],
                food_sources=NUTRIENT_FOOD_SOURCES["Anti-inflammatory Foods"]
            ))
            needs.append(NutrientNeed(
                nutrient="Omega-3 Fatty Acids",
                priority=priority,
                reason=f"Omega-3s help reduce inflammation markers like CRP ({level} {ref['unit']})",
                related_markers=["CRP", "omega-3 index"],
                food_sources=NUTRIENT_FOOD_SOURCES["Omega-3 Fatty Acids"]
            ))
    
    # Homocysteine
    if lab_results.homocysteine_level is not None:
        level = lab_results.homocysteine_level
        ref = LAB_REFERENCE_RANGES["homocysteine"]
        
        if level > ref["elevated"]:
            priority = 1 if level > ref["high"] else 2
            needs.append(NutrientNeed(
                nutrient="Methylfolate",
                priority=priority,
                reason=f"Homocysteine ({level} {ref['unit']}) is elevated - B vitamins help lower it",
                related_markers=["homocysteine", "cardiovascular risk"],
                food_sources=NUTRIENT_FOOD_SOURCES["Methylfolate"]
            ))
    
    return needs


def analyze_metabolic_markers(lab_results: LabResults) -> List[NutrientNeed]:
    """Analyze metabolic markers like glucose."""
    needs = []
    
    if lab_results.glucose_fasting is not None:
        level = lab_results.glucose_fasting
        ref = LAB_REFERENCE_RANGES["glucose_fasting"]
        
        if level > ref["optimal_high"]:
            priority = 2 if level < ref["prediabetic"] else 1
            needs.append(NutrientNeed(
                nutrient="Fiber",
                priority=priority,
                reason=f"Fasting glucose ({level} {ref['unit']}) elevated - fiber helps regulate blood sugar",
                related_markers=["glucose", "HbA1c", "insulin"],
                food_sources=NUTRIENT_FOOD_SOURCES["Fiber"]
            ))
            needs.append(NutrientNeed(
                nutrient="Chromium",
                priority=priority + 1,
                reason=f"Chromium supports glucose metabolism with elevated fasting glucose ({level})",
                related_markers=["glucose", "insulin sensitivity"],
                food_sources=NUTRIENT_FOOD_SOURCES["Chromium"]
            ))
    
    return needs


def analyze_symptoms(medical: MedicalHistory) -> List[NutrientNeed]:
    """Analyze symptoms and suggest supportive nutrients."""
    needs = []
    symptoms = [s.lower() for s in medical.current_symptoms]
    
    symptom_nutrient_map = {
        "fatigue": [
            NutrientNeed(
                nutrient="Iron",
                priority=3,
                reason="Fatigue reported - iron deficiency is a common cause",
                related_markers=["symptoms: fatigue"],
                food_sources=NUTRIENT_FOOD_SOURCES["Iron"]
            ),
            NutrientNeed(
                nutrient="Vitamin B12",
                priority=3,
                reason="Fatigue reported - B12 supports energy metabolism",
                related_markers=["symptoms: fatigue"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin B12"]
            )
        ],
        "brain_fog": [
            NutrientNeed(
                nutrient="Omega-3 Fatty Acids",
                priority=3,
                reason="Brain fog reported - omega-3s support cognitive function",
                related_markers=["symptoms: brain fog"],
                food_sources=NUTRIENT_FOOD_SOURCES["Omega-3 Fatty Acids"]
            )
        ],
        "joint_pain": [
            NutrientNeed(
                nutrient="Anti-inflammatory Foods",
                priority=3,
                reason="Joint pain reported - anti-inflammatory foods may help",
                related_markers=["symptoms: joint pain"],
                food_sources=NUTRIENT_FOOD_SOURCES["Anti-inflammatory Foods"]
            )
        ],
        "anxiety": [
            NutrientNeed(
                nutrient="Magnesium",
                priority=3,
                reason="Anxiety reported - magnesium supports nervous system calm",
                related_markers=["symptoms: anxiety"],
                food_sources=NUTRIENT_FOOD_SOURCES["Magnesium"]
            )
        ],
        "weak_immunity": [
            NutrientNeed(
                nutrient="Vitamin D",
                priority=3,
                reason="Immune concerns - Vitamin D is crucial for immune function",
                related_markers=["symptoms: immunity"],
                food_sources=NUTRIENT_FOOD_SOURCES["Vitamin D"]
            )
        ]
    }
    
    for symptom in symptoms:
        for key, nutrient_needs in symptom_nutrient_map.items():
            if key in symptom:
                needs.extend(nutrient_needs)
    
    return needs


def analyze_family_history(medical: MedicalHistory) -> List[NutrientNeed]:
    """Analyze family history for preventive nutrition."""
    needs = []
    history = [h.lower() for h in medical.family_history]
    
    if any("diabetes" in h for h in history):
        needs.append(NutrientNeed(
            nutrient="Fiber",
            priority=4,
            reason="Family history of diabetes - fiber helps maintain healthy blood sugar",
            related_markers=["family history: diabetes"],
            food_sources=NUTRIENT_FOOD_SOURCES["Fiber"]
        ))
        needs.append(NutrientNeed(
            nutrient="Chromium",
            priority=4,
            reason="Family history of diabetes - chromium supports glucose metabolism",
            related_markers=["family history: diabetes"],
            food_sources=NUTRIENT_FOOD_SOURCES["Chromium"]
        ))
    
    if any("heart" in h or "cardiovascular" in h for h in history):
        needs.append(NutrientNeed(
            nutrient="Omega-3 Fatty Acids",
            priority=4,
            reason="Family history of heart disease - omega-3s support cardiovascular health",
            related_markers=["family history: cardiovascular"],
            food_sources=NUTRIENT_FOOD_SOURCES["Omega-3 Fatty Acids"]
        ))
    
    if any("cancer" in h for h in history):
        needs.append(NutrientNeed(
            nutrient="Antioxidants",
            priority=4,
            reason="Family history considerations - antioxidants support cellular health",
            related_markers=["family history: cancer"],
            food_sources=NUTRIENT_FOOD_SOURCES["Antioxidants"]
        ))
    
    return needs


def consolidate_nutrient_needs(all_needs: List[NutrientNeed]) -> List[NutrientNeed]:
    """Consolidate duplicate nutrients, keeping highest priority."""
    nutrient_map: Dict[str, NutrientNeed] = {}
    
    for need in all_needs:
        if need.nutrient in nutrient_map:
            existing = nutrient_map[need.nutrient]
            # Keep the higher priority (lower number)
            if need.priority < existing.priority:
                # Merge reasons and markers
                combined_markers = list(set(existing.related_markers + need.related_markers))
                combined_reason = f"{need.reason}; Also: {existing.reason}"
                nutrient_map[need.nutrient] = NutrientNeed(
                    nutrient=need.nutrient,
                    priority=need.priority,
                    reason=combined_reason,
                    related_markers=combined_markers,
                    food_sources=need.food_sources
                )
            else:
                # Just add markers to existing
                existing.related_markers = list(set(existing.related_markers + need.related_markers))
        else:
            nutrient_map[need.nutrient] = need
    
    return list(nutrient_map.values())


def analyze_lab_data(user_context: UserContext) -> NutrientPriorityList:
    """
    Main function: Analyze all lab data and user context to generate
    a comprehensive Nutrient Priority List.
    
    Args:
        user_context: Complete user context including lab results
        
    Returns:
        NutrientPriorityList with prioritized nutrient recommendations
    """
    all_needs: List[NutrientNeed] = []
    warnings: List[str] = []
    
    # Analyze lab results if available
    if user_context.lab_results:
        all_needs.extend(analyze_methylation_markers(user_context.lab_results))
        all_needs.extend(analyze_vitamin_levels(user_context.lab_results))
        all_needs.extend(analyze_inflammation_markers(user_context.lab_results))
        all_needs.extend(analyze_metabolic_markers(user_context.lab_results))
    else:
        warnings.append("No lab results provided - recommendations based on symptoms and history only")
    
    # Analyze medical history
    all_needs.extend(analyze_symptoms(user_context.medical))
    all_needs.extend(analyze_family_history(user_context.medical))
    
    # Check for allergies that might conflict with food sources
    allergies = [a.lower() for a in user_context.medical.known_allergies]
    for need in all_needs:
        filtered_sources = []
        for source in need.food_sources:
            if not any(allergy in source.lower() for allergy in allergies):
                filtered_sources.append(source)
        need.food_sources = filtered_sources
        if not filtered_sources:
            warnings.append(f"Limited food sources for {need.nutrient} due to allergies")
    
    # Consolidate and sort
    consolidated_needs = consolidate_nutrient_needs(all_needs)
    consolidated_needs.sort(key=lambda x: x.priority)
    
    return NutrientPriorityList(
        user_id=user_context.user_id,
        needs=consolidated_needs,
        warnings=warnings
    )


def print_nutrient_report(priority_list: NutrientPriorityList) -> None:
    """Print a formatted nutrient priority report."""
    print("\n" + "="*60)
    print("  NUTRIENT PRIORITY ANALYSIS REPORT")
    print("="*60)
    
    if priority_list.warnings:
        print("\n⚠️  WARNINGS:")
        for warning in priority_list.warnings:
            print(f"   - {warning}")
    
    print("\n📊 PRIORITIZED NUTRIENT NEEDS:\n")
    
    for i, need in enumerate(priority_list.needs, 1):
        priority_label = ["🔴 CRITICAL", "🟠 HIGH", "🟡 MODERATE", "🟢 PREVENTIVE", "⚪ SUPPORTIVE"][min(need.priority - 1, 4)]
        print(f"{i}. {need.nutrient} [{priority_label}]")
        print(f"   Reason: {need.reason}")
        print(f"   Markers: {', '.join(need.related_markers[:3])}")
        print(f"   Food Sources: {', '.join(need.food_sources[:4])}")
        print()
