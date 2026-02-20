#!/usr/bin/env python3
"""
Health Equity Nutrition App
===========================

A comprehensive Python application that creates personalized nutrition
recommendations based on:
- Financial constraints (budget, SNAP/WIC status)
- Geographic accessibility (zip code, transportation)
- Medical needs (symptoms, family history, lab results)
- Methylation and genetic markers

Phases:
1. Questionnaire Data Input (UserContext)
2. Bio-Analytical Engine (analyze_lab_data)
3. Geographic & Financial Mapping (ResourceLocator)
4. Curated Shopping Planner (generate_shopping_list)
5. Interactive Feedback CLI (ask "Why?")

Usage:
    python main.py              # Run with sample user data (demo mode)
    python main.py --interactive # Run with user questionnaire input
"""

import sys
import argparse

# Import all modules
from user_context import (
    UserContext, 
    Financials, 
    Logistics, 
    MedicalHistory, 
    LabResults,
    collect_user_context_cli,
    create_sample_user
)
from bio_analyzer import (
    analyze_lab_data, 
    print_nutrient_report,
    NutrientPriorityList
)
from resource_locator import (
    resource_locator, 
    print_resource_map,
    ResourceMap
)
from shopping_planner import (
    generate_shopping_list, 
    print_shopping_list,
    ShoppingList
)
from interactive_cli import run_interactive_session


def print_banner():
    """Print the app banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🌿 HEALTH EQUITY NUTRITION APP 🌿                   ║
║                                                              ║
║   Personalized nutrition planning for everyone,              ║
║   regardless of income, location, or circumstances.          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_full_analysis(user: UserContext) -> tuple:
    """
    Run the complete analysis pipeline.
    
    Returns:
        Tuple of (NutrientPriorityList, ResourceMap, ShoppingList)
    """
    print("\n" + "─"*60)
    print("  PHASE 2: Analyzing Biological Needs...")
    print("─"*60)
    
    # Phase 2: Bio-Analytical Engine
    nutrient_priorities = analyze_lab_data(user)
    print_nutrient_report(nutrient_priorities)
    
    print("\n" + "─"*60)
    print("  PHASE 3: Mapping Local Resources...")
    print("─"*60)
    
    # Phase 3: Resource Locator
    resource_map = resource_locator(user)
    print_resource_map(resource_map, user)
    
    print("\n" + "─"*60)
    print("  PHASE 4: Generating Curated Shopping Plan...")
    print("─"*60)
    
    # Phase 4: Shopping Planner
    shopping_list = generate_shopping_list(user, nutrient_priorities, resource_map)
    print_shopping_list(shopping_list, user)
    
    return nutrient_priorities, resource_map, shopping_list


def demo_mode():
    """Run the app with sample data for demonstration."""
    print_banner()
    print("  Running in DEMO MODE with sample user data...")
    print("  (Use --interactive flag for real questionnaire input)")
    
    # Create sample user
    user = create_sample_user()
    
    print("\n" + "─"*60)
    print("  PHASE 1: User Context Summary")
    print("─"*60)
    
    print(f"""
    👤 User: {user.name}
    
    💰 FINANCIAL:
       Budget: ${user.financials.weekly_budget}/week ({user.financials.budget_tier})
       SNAP: {'Yes ✓' if user.financials.snap_status else 'No'}
       WIC: {'Yes ✓' if user.financials.wic_status else 'No'}
    
    🚗 LOGISTICS:
       Location: ZIP {user.logistics.zip_code}
       Vehicle: {'Yes' if user.logistics.has_vehicle else 'No'}
       Transit: {'Yes' if user.logistics.has_public_transit else 'No'}
       Mobility: {user.logistics.mobility_level.upper()}
    
    🩺 MEDICAL:
       Family History: {', '.join(user.medical.family_history) or 'None reported'}
       Previous Conditions: {', '.join(user.medical.previous_conditions) or 'None'}
       Current Symptoms: {', '.join(user.medical.current_symptoms) or 'None'}
       Allergies: {', '.join(user.medical.known_allergies) or 'None'}
    
    🧬 LAB RESULTS:
       MTHFR Variant: {user.lab_results.mthfr_variant or 'Not tested'}
       B12: {user.lab_results.vitamin_b12_level} pg/mL
       Vitamin D: {user.lab_results.vitamin_d_level} ng/mL
       CRP (Inflammation): {user.lab_results.crp_level} mg/L
    """)
    
    # Run full analysis
    nutrient_priorities, resource_map, shopping_list = run_full_analysis(user)
    
    # Phase 5: Interactive Session
    print("\n" + "─"*60)
    print("  PHASE 5: Interactive Feedback Session")
    print("─"*60)
    
    run_interactive_session(user, nutrient_priorities, shopping_list)


def interactive_mode():
    """Run the app with user questionnaire input."""
    print_banner()
    print("  Running in INTERACTIVE MODE")
    print("  Please answer the following questions...\n")
    
    # Phase 1: Collect user context via CLI
    user = collect_user_context_cli()
    
    # Ask about lab results
    print("\n--- Lab Results (Optional) ---")
    has_labs = input("Do you have lab results to enter? (y/n): ").lower().startswith('y')
    
    if has_labs:
        print("Enter values or press Enter to skip:")
        
        def safe_float(prompt, default=None):
            try:
                val = input(prompt).strip()
                return float(val) if val else default
            except ValueError:
                return default
        
        mthfr = input("MTHFR variant (e.g., C677T, A1298C, or press Enter): ").strip() or None
        comt = input("COMT variant (slow/fast, or press Enter): ").strip() or None
        
        b12 = safe_float("Vitamin B12 level (pg/mL): ")
        vit_d = safe_float("Vitamin D level (ng/mL): ")
        iron = safe_float("Iron level (mcg/dL): ")
        crp = safe_float("CRP level (mg/L): ")
        homocysteine = safe_float("Homocysteine level (umol/L): ")
        glucose = safe_float("Fasting glucose (mg/dL): ")
        
        user.lab_results = LabResults(
            mthfr_variant=mthfr,
            comt_variant=comt,
            vitamin_b12_level=b12,
            vitamin_d_level=vit_d,
            iron_level=iron,
            crp_level=crp,
            homocysteine_level=homocysteine,
            glucose_fasting=glucose
        )
    
    print("\n✓ User context collected successfully!")
    
    # Run full analysis
    nutrient_priorities, resource_map, shopping_list = run_full_analysis(user)
    
    # Phase 5: Interactive Session
    print("\n" + "─"*60)
    print("  PHASE 5: Interactive Feedback Session")
    print("─"*60)
    
    run_interactive_session(user, nutrient_priorities, shopping_list)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Health Equity Nutrition App - Personalized nutrition planning"
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode with questionnaire input'
    )
    parser.add_argument(
        '--demo', '-d',
        action='store_true',
        help='Run in demo mode with sample data (default)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.interactive:
            interactive_mode()
        else:
            demo_mode()
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
