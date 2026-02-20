"""
Phase 1: Questionnaire Data Input
UserContext class for storing user health equity app inputs.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Financials:
    """Financial information for resource planning."""
    weekly_budget: float  # In dollars
    snap_status: bool = False  # SNAP (Supplemental Nutrition Assistance Program)
    wic_status: bool = False  # WIC (Women, Infants, and Children)
    annual_income: Optional[float] = None  # Optional for privacy
    
    @property
    def has_assistance(self) -> bool:
        """Check if user has any food assistance."""
        return self.snap_status or self.wic_status
    
    @property
    def budget_tier(self) -> str:
        """Categorize budget for planning purposes."""
        if self.weekly_budget < 50:
            return "very_low"
        elif self.weekly_budget < 100:
            return "low"
        elif self.weekly_budget < 200:
            return "moderate"
        else:
            return "comfortable"


@dataclass
class Logistics:
    """Logistical constraints for resource access."""
    zip_code: str
    has_vehicle: bool = False
    has_public_transit: bool = False
    grocery_trips_per_week: int = 1
    max_travel_distance_miles: float = 5.0  # Default walking distance
    
    @property
    def mobility_level(self) -> str:
        """Assess mobility for resource planning."""
        if self.has_vehicle:
            return "high"
        elif self.has_public_transit:
            return "moderate"
        else:
            return "limited"


@dataclass
class MedicalHistory:
    """Medical information for nutritional analysis."""
    family_history: List[str] = field(default_factory=list)
    # e.g., ["diabetes", "heart_disease", "hypertension"]
    
    previous_conditions: List[str] = field(default_factory=list)
    # e.g., ["anemia", "vitamin_d_deficiency"]
    
    current_symptoms: List[str] = field(default_factory=list)
    # e.g., ["fatigue", "brain_fog", "joint_pain"]
    
    known_allergies: List[str] = field(default_factory=list)
    # e.g., ["gluten", "dairy", "shellfish"]
    
    medications: List[str] = field(default_factory=list)
    # e.g., ["metformin", "lisinopril"]


@dataclass
class LabResults:
    """Simulated lab and methylation results."""
    mthfr_variant: Optional[str] = None  # e.g., "C677T", "A1298C", "compound"
    comt_variant: Optional[str] = None  # e.g., "slow", "fast"
    vitamin_b12_level: Optional[float] = None  # pg/mL
    vitamin_d_level: Optional[float] = None  # ng/mL
    iron_level: Optional[float] = None  # mcg/dL
    ferritin_level: Optional[float] = None  # ng/mL
    crp_level: Optional[float] = None  # mg/L (inflammation marker)
    homocysteine_level: Optional[float] = None  # umol/L
    glucose_fasting: Optional[float] = None  # mg/dL
    omega3_index: Optional[float] = None  # percentage


@dataclass
class UserContext:
    """
    Complete user context combining all questionnaire inputs.
    This is the central data structure for the health equity app.
    """
    user_id: str
    name: str
    financials: Financials
    logistics: Logistics
    medical: MedicalHistory
    lab_results: Optional[LabResults] = None
    
    def summary(self) -> dict:
        """Generate a summary of user context for display."""
        return {
            "user": self.name,
            "budget_tier": self.financials.budget_tier,
            "has_assistance": self.financials.has_assistance,
            "mobility": self.logistics.mobility_level,
            "zip_code": self.logistics.zip_code,
            "medical_concerns": len(self.medical.family_history) + len(self.medical.current_symptoms),
            "has_lab_data": self.lab_results is not None
        }


def collect_user_context_cli() -> UserContext:
    """
    Interactive CLI to collect user context data.
    Returns a fully populated UserContext object.
    """
    print("\n" + "="*60)
    print("  HEALTH EQUITY APP - User Questionnaire")
    print("="*60 + "\n")
    
    # Basic info
    name = input("Enter your name: ").strip() or "Anonymous"
    user_id = f"user_{name.lower().replace(' ', '_')}"
    
    # Financials
    print("\n--- Financial Information ---")
    try:
        weekly_budget = float(input("Weekly grocery budget ($): ") or "75")
    except ValueError:
        weekly_budget = 75.0
    
    snap = input("Do you receive SNAP benefits? (y/n): ").lower().startswith('y')
    wic = input("Do you receive WIC benefits? (y/n): ").lower().startswith('y')
    
    financials = Financials(
        weekly_budget=weekly_budget,
        snap_status=snap,
        wic_status=wic
    )
    
    # Logistics
    print("\n--- Location & Transportation ---")
    zip_code = input("Enter your zip code: ").strip() or "00000"
    has_vehicle = input("Do you have access to a vehicle? (y/n): ").lower().startswith('y')
    has_transit = input("Do you have access to public transit? (y/n): ").lower().startswith('y')
    
    try:
        trips = int(input("How many grocery trips per week? (1-7): ") or "1")
        trips = max(1, min(7, trips))
    except ValueError:
        trips = 1
    
    logistics = Logistics(
        zip_code=zip_code,
        has_vehicle=has_vehicle,
        has_public_transit=has_transit,
        grocery_trips_per_week=trips,
        max_travel_distance_miles=15.0 if has_vehicle else (5.0 if has_transit else 2.0)
    )
    
    # Medical
    print("\n--- Medical History ---")
    print("(Enter comma-separated values, or press Enter to skip)")
    
    family_raw = input("Family health history (e.g., diabetes, heart_disease): ")
    family_history = [x.strip() for x in family_raw.split(',') if x.strip()]
    
    conditions_raw = input("Previous health conditions: ")
    previous_conditions = [x.strip() for x in conditions_raw.split(',') if x.strip()]
    
    symptoms_raw = input("Current symptoms (e.g., fatigue, joint_pain): ")
    current_symptoms = [x.strip() for x in symptoms_raw.split(',') if x.strip()]
    
    allergies_raw = input("Known food allergies: ")
    allergies = [x.strip() for x in allergies_raw.split(',') if x.strip()]
    
    medical = MedicalHistory(
        family_history=family_history,
        previous_conditions=previous_conditions,
        current_symptoms=current_symptoms,
        known_allergies=allergies
    )
    
    return UserContext(
        user_id=user_id,
        name=name,
        financials=financials,
        logistics=logistics,
        medical=medical
    )


def create_sample_user() -> UserContext:
    """Create a sample user for testing and demonstration."""
    return UserContext(
        user_id="sample_user_001",
        name="Sample User",
        financials=Financials(
            weekly_budget=60.0,
            snap_status=True,
            wic_status=False,
            annual_income=28000
        ),
        logistics=Logistics(
            zip_code="30312",
            has_vehicle=False,
            has_public_transit=True,
            grocery_trips_per_week=2,
            max_travel_distance_miles=5.0
        ),
        medical=MedicalHistory(
            family_history=["diabetes", "hypertension"],
            previous_conditions=["anemia"],
            current_symptoms=["fatigue", "brain_fog"],
            known_allergies=["shellfish"]
        ),
        lab_results=LabResults(
            mthfr_variant="C677T",
            vitamin_b12_level=280,  # Low-normal
            vitamin_d_level=18,  # Deficient
            iron_level=50,  # Low
            crp_level=3.5,  # Elevated
            homocysteine_level=14,  # Elevated
            glucose_fasting=105  # Pre-diabetic range
        )
    )
