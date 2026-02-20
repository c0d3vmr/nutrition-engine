"""
Phase 5: Interactive Feedback
CLI loop where users can ask 'Why was this chosen?' and get AI explanations.
"""

import re
from typing import Optional, List, Tuple

from user_context import UserContext
from bio_analyzer import NutrientPriorityList, NutrientNeed
from shopping_planner import ShoppingList, ShoppingListItem, get_item_explanation


class InteractiveCLI:
    """
    Interactive command-line interface for exploring recommendations.
    Allows users to ask "Why?" about their personalized food recommendations.
    """
    
    def __init__(
        self,
        user_context: UserContext,
        nutrient_priorities: NutrientPriorityList,
        shopping_list: ShoppingList
    ):
        self.user = user_context
        self.nutrients = nutrient_priorities
        self.shopping = shopping_list
        self.running = False
    
    def show_help(self) -> None:
        """Display available commands."""
        print("\n" + "-"*50)
        print("  INTERACTIVE ASSISTANT - Commands")
        print("-"*50)
        print("""
  why [item]     - Explain why an item was recommended
                   Example: 'why spinach' or 'why eggs'
  
  list           - Show the shopping list again
  
  nutrients      - Show your nutrient priority analysis
  
  explain [nutrient] - Explain a specific nutrient need
                       Example: 'explain B12' or 'explain methylfolate'
  
  markers        - Show your methylation/lab markers analysis
  
  budget         - Show budget breakdown
  
  stores         - Brief store recommendations
  
  help           - Show this help message
  
  quit / exit    - Exit the interactive session
""")
    
    def find_item_by_name(self, search: str) -> Optional[ShoppingListItem]:
        """Find a shopping list item by partial name match."""
        search_lower = search.lower()
        for item in self.shopping.items:
            if search_lower in item.food.name.lower():
                return item
        return None
    
    def find_nutrient_need(self, search: str) -> Optional[NutrientNeed]:
        """Find a nutrient need by partial name match."""
        search_lower = search.lower()
        for need in self.nutrients.needs:
            if search_lower in need.nutrient.lower():
                return need
        return None
    
    def explain_item(self, item_name: str) -> str:
        """Generate explanation for why an item was chosen."""
        item = self.find_item_by_name(item_name)
        
        if not item:
            # Check pantry items too
            for pantry_item in self.shopping.pantry_items:
                if item_name.lower() in pantry_item.food.name.lower():
                    return (
                        f"📦 {pantry_item.food.name}\n"
                        f"   Source: Food Pantry (FREE)\n"
                        f"   This was recommended because your budget tier is "
                        f"'{self.user.financials.budget_tier}'.\n"
                        f"   Food pantries provide essential nutrition at no cost."
                    )
            
            available_items = [i.food.name for i in self.shopping.items[:8]]
            return (
                f"❓ Item '{item_name}' not found in your shopping list.\n"
                f"   Available items: {', '.join(available_items)}"
            )
        
        return get_item_explanation(item, self.nutrients)
    
    def explain_nutrient(self, nutrient_name: str) -> str:
        """Explain why a nutrient was prioritized."""
        need = self.find_nutrient_need(nutrient_name)
        
        if not need:
            available = [n.nutrient for n in self.nutrients.needs[:6]]
            return (
                f"❓ Nutrient '{nutrient_name}' not found in your priorities.\n"
                f"   Your priority nutrients: {', '.join(available)}"
            )
        
        explanation = []
        explanation.append(f"🔬 {need.nutrient}")
        explanation.append(f"\n   Priority Level: {need.priority} " + 
                          ["🔴 CRITICAL", "🟠 HIGH", "🟡 MODERATE", "🟢 PREVENTIVE", "⚪ SUPPORTIVE"][min(need.priority-1, 4)])
        explanation.append(f"\n   ➤ Why this matters for you:")
        explanation.append(f"     {need.reason}")
        
        if need.related_markers:
            explanation.append(f"\n   📊 Related health markers:")
            for marker in need.related_markers[:5]:
                explanation.append(f"      • {marker}")
        
        # Show connection to symptoms/history
        symptoms = self.user.medical.current_symptoms
        history = self.user.medical.family_history
        
        matching_symptoms = [s for s in symptoms if any(
            s.lower() in marker.lower() or marker.lower() in s.lower() 
            for marker in need.related_markers
        )]
        
        if matching_symptoms:
            explanation.append(f"\n   🩺 Connected to your symptoms:")
            for s in matching_symptoms:
                explanation.append(f"      • {s}")
        
        if need.food_sources:
            explanation.append(f"\n   🥗 Best food sources:")
            for food in need.food_sources[:5]:
                explanation.append(f"      • {food}")
        
        return "\n".join(explanation)
    
    def show_markers_analysis(self) -> str:
        """Show methylation and lab markers analysis."""
        output = []
        output.append("\n🧬 YOUR METHYLATION & LAB MARKERS ANALYSIS")
        output.append("="*50)
        
        lab = self.user.lab_results
        if not lab:
            output.append("\n   No lab results on file.")
            output.append("   Recommendations are based on symptoms and history only.")
            return "\n".join(output)
        
        # Methylation markers
        output.append("\n📍 METHYLATION MARKERS:")
        if lab.mthfr_variant:
            output.append(f"   MTHFR: {lab.mthfr_variant}")
            output.append(f"      → Impact: Affects folate metabolism and methylation cycle")
            output.append(f"      → Action: Prioritize methylfolate and B12 from food")
        else:
            output.append("   MTHFR: Not tested/Normal")
        
        if lab.comt_variant:
            output.append(f"   COMT: {lab.comt_variant}")
            if lab.comt_variant.lower() == "slow":
                output.append(f"      → Impact: Slower catecholamine breakdown")
                output.append(f"      → Action: Support with magnesium, limit stimulants")
        
        # Key lab values
        output.append("\n📊 KEY LAB VALUES:")
        
        if lab.vitamin_b12_level:
            status = "Low ⚠️" if lab.vitamin_b12_level < 500 else "Adequate ✓"
            output.append(f"   Vitamin B12: {lab.vitamin_b12_level} pg/mL [{status}]")
        
        if lab.vitamin_d_level:
            status = "Deficient ⚠️" if lab.vitamin_d_level < 30 else "Adequate ✓"
            output.append(f"   Vitamin D: {lab.vitamin_d_level} ng/mL [{status}]")
        
        if lab.iron_level:
            status = "Low ⚠️" if lab.iron_level < 60 else "Adequate ✓"
            output.append(f"   Iron: {lab.iron_level} mcg/dL [{status}]")
        
        if lab.crp_level:
            status = "Elevated ⚠️" if lab.crp_level > 1 else "Normal ✓"
            output.append(f"   CRP (Inflammation): {lab.crp_level} mg/L [{status}]")
        
        if lab.homocysteine_level:
            status = "Elevated ⚠️" if lab.homocysteine_level > 10 else "Normal ✓"
            output.append(f"   Homocysteine: {lab.homocysteine_level} umol/L [{status}]")
        
        if lab.glucose_fasting:
            if lab.glucose_fasting >= 126:
                status = "Diabetic range ⚠️"
            elif lab.glucose_fasting >= 100:
                status = "Pre-diabetic ⚠️"
            else:
                status = "Normal ✓"
            output.append(f"   Fasting Glucose: {lab.glucose_fasting} mg/dL [{status}]")
        
        # Connection to recommendations
        output.append("\n🔗 HOW THIS SHAPED YOUR RECOMMENDATIONS:")
        for need in self.nutrients.get_top_priorities(3):
            output.append(f"   • {need.nutrient}: {need.reason[:60]}...")
        
        return "\n".join(output)
    
    def show_budget_breakdown(self) -> str:
        """Show budget allocation."""
        output = []
        output.append("\n💰 BUDGET BREAKDOWN")
        output.append("="*50)
        
        budget = self.user.financials.weekly_budget
        output.append(f"\n   Weekly Budget: ${budget:.2f}")
        output.append(f"   Budget Tier: {self.user.financials.budget_tier.upper()}")
        
        if self.user.financials.snap_status:
            output.append("   ✓ SNAP benefits - EBT accepted items prioritized")
        if self.user.financials.wic_status:
            output.append("   ✓ WIC benefits - eligible items noted")
        
        output.append(f"\n   Estimated Shopping Cost: ${self.shopping.total_estimated_cost:.2f}")
        output.append(f"   Budget Remaining: ${self.shopping.budget_remaining:.2f}")
        
        # Breakdown by priority
        priority_costs = {}
        for item in self.shopping.items:
            p = item.priority.name
            if p not in priority_costs:
                priority_costs[p] = 0
            priority_costs[p] += item.estimated_cost
        
        output.append("\n   Cost by Priority:")
        for priority, cost in priority_costs.items():
            pct = (cost / self.shopping.total_estimated_cost * 100) if self.shopping.total_estimated_cost > 0 else 0
            output.append(f"      {priority}: ${cost:.2f} ({pct:.0f}%)")
        
        if self.shopping.pantry_items:
            output.append(f"\n   🆓 Plus {len(self.shopping.pantry_items)} items from food pantry (FREE)")
        
        return "\n".join(output)
    
    def show_store_tips(self) -> str:
        """Show brief store recommendations."""
        output = []
        output.append("\n🏪 STORE RECOMMENDATIONS")
        output.append("="*50)
        
        for store, items in self.shopping.store_visits.items():
            total = sum(i.estimated_cost for i in items)
            item_names = [i.food.name.split('(')[0].strip() for i in items[:3]]
            output.append(f"\n   📍 {store}")
            output.append(f"      Items: {', '.join(item_names)}")
            output.append(f"      Est. Total: ${total:.2f}")
        
        return "\n".join(output)
    
    def process_command(self, user_input: str) -> Tuple[bool, str]:
        """
        Process a user command and return (should_continue, response).
        """
        user_input = user_input.strip().lower()
        
        if not user_input:
            return True, "Type 'help' for available commands."
        
        # Parse command and argument
        parts = user_input.split(maxsplit=1)
        command = parts[0]
        argument = parts[1] if len(parts) > 1 else ""
        
        # Exit commands
        if command in ['quit', 'exit', 'q']:
            return False, "Thank you for using the Health Equity App! Stay healthy! 🌱"
        
        # Help
        if command == 'help':
            self.show_help()
            return True, ""
        
        # Why command
        if command == 'why':
            if not argument:
                return True, "Please specify an item. Example: 'why spinach'"
            return True, self.explain_item(argument)
        
        # Explain nutrient
        if command == 'explain':
            if not argument:
                return True, "Please specify a nutrient. Example: 'explain B12'"
            return True, self.explain_nutrient(argument)
        
        # Show list
        if command == 'list':
            output = []
            output.append("\n📋 YOUR SHOPPING LIST:")
            for i, item in enumerate(self.shopping.items, 1):
                output.append(f"   {i}. {item.food.name} - ${item.estimated_cost:.2f}")
            return True, "\n".join(output)
        
        # Show nutrients
        if command == 'nutrients':
            output = []
            output.append("\n🔬 YOUR NUTRIENT PRIORITIES:")
            for i, need in enumerate(self.nutrients.needs, 1):
                output.append(f"   {i}. {need.nutrient} [Priority {need.priority}]")
            return True, "\n".join(output)
        
        # Show markers
        if command == 'markers':
            return True, self.show_markers_analysis()
        
        # Budget breakdown
        if command == 'budget':
            return True, self.show_budget_breakdown()
        
        # Store tips
        if command == 'stores':
            return True, self.show_store_tips()
        
        # Unknown command - try to interpret as "why X"
        if self.find_item_by_name(command):
            return True, self.explain_item(command)
        
        return True, f"❓ Unknown command: '{command}'. Type 'help' for options."
    
    def run(self) -> None:
        """Run the interactive CLI loop."""
        print("\n" + "="*60)
        print("  INTERACTIVE FEEDBACK SESSION")
        print("="*60)
        print(f"\n  Welcome, {self.user.name}!")
        print("  Ask me about your personalized nutrition recommendations.")
        print("  Type 'help' for commands or 'why [item]' to learn more.")
        print("  Type 'quit' to exit.\n")
        
        self.running = True
        
        while self.running:
            try:
                user_input = input("🤖 Ask me > ").strip()
                should_continue, response = self.process_command(user_input)
                
                if response:
                    print(response)
                
                if not should_continue:
                    self.running = False
                    
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                self.running = False
            except EOFError:
                print("\n\n👋 Session ended. Goodbye!")
                self.running = False


def run_interactive_session(
    user_context: UserContext,
    nutrient_priorities: NutrientPriorityList,
    shopping_list: ShoppingList
) -> None:
    """Convenience function to run the interactive CLI."""
    cli = InteractiveCLI(user_context, nutrient_priorities, shopping_list)
    cli.run()
