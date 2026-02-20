"""
Phase 4: The Curated Planner
Shopping list generator that prioritizes based on biological needs, budget, and store inventory.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from user_context import UserContext
from bio_analyzer import NutrientPriorityList, NutrientNeed
from resource_locator import ResourceMap, TravelFeasibility, StoreType, InventoryLevel


class ShoppingPriority(Enum):
    CRITICAL = 1  # Must buy
    HIGH = 2  # Important
    MODERATE = 3  # Helpful
    OPTIONAL = 4  # If budget allows


@dataclass
class FoodItem:
    """Represents a food item with pricing and nutrient info."""
    name: str
    category: str
    price_estimate: float  # Per unit/serving
    snap_eligible: bool = True
    wic_eligible: bool = False
    nutrients_provided: List[str] = field(default_factory=list)
    serving_size: str = "1 serving"
    shelf_life_days: int = 7


@dataclass
class ShoppingListItem:
    """An item on the curated shopping list."""
    food: FoodItem
    quantity: int
    priority: ShoppingPriority
    reason: str  # Why this was selected
    suggested_store: Optional[str] = None
    estimated_cost: float = 0.0
    nutrients_addressed: List[str] = field(default_factory=list)


@dataclass
class ShoppingList:
    """Complete curated shopping list."""
    user_id: str
    items: List[ShoppingListItem] = field(default_factory=list)
    total_estimated_cost: float = 0.0
    budget_remaining: float = 0.0
    pantry_items: List[ShoppingListItem] = field(default_factory=list)  # From food pantries
    store_visits: Dict[str, List[ShoppingListItem]] = field(default_factory=dict)
    reasoning_log: List[str] = field(default_factory=list)  # For "Why?" questions


# Food database with pricing (simulated)
FOOD_DATABASE: Dict[str, FoodItem] = {
    # Leafy Greens & Vegetables
    "spinach": FoodItem("Spinach (fresh bunch)", "produce", 2.50, True, True, 
                        ["Iron", "Methylfolate", "Magnesium", "Anti-inflammatory Foods"], "1 bunch", 5),
    "spinach_frozen": FoodItem("Spinach (frozen bag)", "frozen", 1.50, True, False,
                               ["Iron", "Methylfolate", "Magnesium"], "16 oz bag", 180),
    "broccoli": FoodItem("Broccoli", "produce", 1.75, True, True,
                         ["Fiber", "Chromium", "Anti-inflammatory Foods"], "1 head", 7),
    "kale": FoodItem("Kale", "produce", 2.00, True, False,
                     ["Iron", "Antioxidants", "Anti-inflammatory Foods"], "1 bunch", 5),
    
    # Legumes & Beans
    "lentils_dry": FoodItem("Lentils (dry)", "dry goods", 1.50, True, False,
                            ["Iron", "Fiber", "Methylfolate"], "1 lb bag", 365),
    "black_beans_canned": FoodItem("Black Beans (canned)", "canned", 0.89, True, False,
                                    ["Fiber", "Iron", "Magnesium"], "15 oz can", 730),
    "chickpeas_canned": FoodItem("Chickpeas (canned)", "canned", 1.00, True, False,
                                  ["Iron", "Fiber"], "15 oz can", 730),
    
    # Proteins
    "eggs": FoodItem("Eggs (dozen)", "dairy", 3.50, True, True,
                     ["Vitamin B12", "Vitamin D"], "12 eggs", 21),
    "sardines_canned": FoodItem("Sardines (canned)", "canned", 2.00, True, False,
                                 ["Vitamin B12", "Vitamin D", "Omega-3 Fatty Acids"], "4 oz can", 1095),
    "salmon_canned": FoodItem("Salmon (canned)", "canned", 3.50, True, False,
                               ["Vitamin B12", "Vitamin D", "Omega-3 Fatty Acids"], "6 oz can", 1095),
    "chicken_thighs": FoodItem("Chicken Thighs", "meat", 4.00, True, False,
                                ["Vitamin B12", "Iron"], "1 lb", 2),
    "beef_liver": FoodItem("Beef Liver", "meat", 3.00, True, False,
                           ["Vitamin B12", "Iron", "Vitamin D"], "1 lb", 2),
    
    # Grains & Cereals
    "oats": FoodItem("Oats (rolled)", "dry goods", 2.50, True, True,
                     ["Fiber", "Magnesium"], "42 oz container", 365),
    "fortified_cereal": FoodItem("Fortified Cereal", "dry goods", 3.00, True, True,
                                  ["Vitamin B12", "Iron", "Methylfolate"], "12 oz box", 180),
    "quinoa": FoodItem("Quinoa", "dry goods", 5.00, True, False,
                       ["Iron", "Magnesium", "Fiber"], "16 oz bag", 365),
    
    # Nuts & Seeds
    "walnuts": FoodItem("Walnuts", "nuts", 6.00, True, False,
                        ["Omega-3 Fatty Acids", "Magnesium"], "8 oz bag", 180),
    "flaxseed": FoodItem("Ground Flaxseed", "nuts", 4.00, True, False,
                         ["Omega-3 Fatty Acids", "Fiber"], "16 oz bag", 180),
    "chia_seeds": FoodItem("Chia Seeds", "nuts", 5.50, True, False,
                           ["Omega-3 Fatty Acids", "Fiber"], "12 oz bag", 365),
    "pumpkin_seeds": FoodItem("Pumpkin Seeds", "nuts", 4.50, True, False,
                               ["Iron", "Magnesium"], "8 oz bag", 180),
    
    # Anti-inflammatory & Specialty
    "turmeric": FoodItem("Turmeric (ground)", "spices", 3.50, True, False,
                         ["Anti-inflammatory Foods"], "2 oz jar", 730),
    "ginger_root": FoodItem("Ginger Root", "produce", 1.00, True, False,
                            ["Anti-inflammatory Foods"], "1 piece", 21),
    "berries_frozen": FoodItem("Mixed Berries (frozen)", "frozen", 3.50, True, True,
                                ["Antioxidants", "Anti-inflammatory Foods", "Fiber"], "16 oz bag", 365),
    "olive_oil": FoodItem("Olive Oil (extra virgin)", "oils", 7.00, True, False,
                          ["Anti-inflammatory Foods", "Omega-3 Fatty Acids"], "16 oz bottle", 730),
    
    # Dairy & Alternatives
    "fortified_milk": FoodItem("Fortified Milk (or plant milk)", "dairy", 3.00, True, True,
                                ["Vitamin D", "Vitamin B12"], "half gallon", 10),
    "yogurt": FoodItem("Yogurt", "dairy", 4.00, True, True,
                        ["Vitamin B12", "Vitamin D"], "32 oz container", 14),
    
    # Budget-friendly staples
    "brown_rice": FoodItem("Brown Rice", "dry goods", 2.00, True, False,
                           ["Fiber", "Magnesium"], "2 lb bag", 365),
    "peanut_butter": FoodItem("Peanut Butter", "dry goods", 3.00, True, True,
                               ["Magnesium"], "16 oz jar", 180),
    "bananas": FoodItem("Bananas", "produce", 0.50, True, True,
                        ["Magnesium", "Fiber"], "per lb", 5),
}

# Budget-tier food alternatives
BUDGET_ALTERNATIVES: Dict[str, str] = {
    "salmon_canned": "sardines_canned",
    "quinoa": "brown_rice",
    "walnuts": "flaxseed",
    "chia_seeds": "flaxseed",
    "kale": "spinach_frozen",
    "spinach": "spinach_frozen",
    "chicken_thighs": "eggs",
}


def get_foods_for_nutrient(nutrient: str) -> List[FoodItem]:
    """Get all foods that provide a specific nutrient, sorted by price."""
    matching_foods = []
    for food in FOOD_DATABASE.values():
        if nutrient in food.nutrients_provided:
            matching_foods.append(food)
    return sorted(matching_foods, key=lambda x: x.price_estimate)


def calculate_priority(nutrient_priority: int, budget_tier: str) -> ShoppingPriority:
    """Map nutrient priority to shopping priority based on budget."""
    if nutrient_priority == 1:
        return ShoppingPriority.CRITICAL
    elif nutrient_priority == 2:
        return ShoppingPriority.HIGH
    elif nutrient_priority <= 3:
        return ShoppingPriority.MODERATE
    else:
        return ShoppingPriority.OPTIONAL


def generate_shopping_list(
    user_context: UserContext,
    nutrient_priorities: NutrientPriorityList,
    resource_map: ResourceMap
) -> ShoppingList:
    """
    Generate a curated shopping list based on biological needs, budget, and store availability.
    
    Logic:
    1. If budget is very low, prioritize Food Pantries first
    2. Then prioritize SNAP-authorized stores for remaining needs
    3. Select cheapest sources for highest biological needs
    4. Respect allergies and dietary restrictions
    
    Args:
        user_context: User's complete context
        nutrient_priorities: Analyzed nutrient needs
        resource_map: Available stores and resources
        
    Returns:
        ShoppingList with prioritized, affordable items
    """
    shopping_list = ShoppingList(user_id=user_context.user_id)
    budget = user_context.financials.weekly_budget
    budget_tier = user_context.financials.budget_tier
    remaining_budget = budget
    
    # Track which nutrients we've addressed
    nutrients_addressed: Dict[str, List[str]] = {}
    reasoning = []
    
    # Get top nutrient needs
    top_needs = nutrient_priorities.get_top_priorities(8)
    
    reasoning.append(f"Budget tier: {budget_tier} (${budget}/week)")
    reasoning.append(f"Top {len(top_needs)} nutrient priorities identified")
    
    # Phase 1: If low budget, recommend food pantry first
    if budget_tier in ["very_low", "low"] and resource_map.food_pantries:
        reasoning.append("LOW BUDGET: Recommending food pantry as primary resource")
        
        pantry = resource_map.food_pantries[0]
        pantry_items_text = ", ".join(pantry.store.specialty_items[:3])
        
        # Add pantry recommendation
        shopping_list.reasoning_log.append(
            f"RECOMMENDATION: Visit {pantry.store.name} first (FREE). "
            f"Available: {pantry_items_text}. Hours: {pantry.store.hours}"
        )
        
        # Estimate what can be gotten from pantry
        pantry_foods = ["bread", "canned goods", "produce"]
        for pf in pantry_foods:
            if pf in pantry.store.specialty_items or "produce" in pantry.store.specialty_items:
                shopping_list.pantry_items.append(ShoppingListItem(
                    food=FoodItem(f"Pantry: {pf.title()}", "pantry", 0.0, False, False, [], "varies", 7),
                    quantity=1,
                    priority=ShoppingPriority.HIGH,
                    reason="Available FREE at food pantry",
                    suggested_store=pantry.store.name,
                    estimated_cost=0.0
                ))
    
    # Phase 2: Select foods for each nutrient priority
    for need in top_needs:
        if remaining_budget <= 0:
            reasoning.append(f"BUDGET EXHAUSTED: Skipping {need.nutrient}")
            continue
            
        # Get food options for this nutrient (already sorted by price)
        food_options = get_foods_for_nutrient(need.nutrient)
        
        if not food_options:
            reasoning.append(f"No foods found for {need.nutrient}")
            continue
        
        # Filter by allergies
        allergies = [a.lower() for a in user_context.medical.known_allergies]
        safe_options = [f for f in food_options if not any(
            allergy in f.name.lower() for allergy in allergies
        )]
        
        if not safe_options:
            reasoning.append(f"All foods for {need.nutrient} conflict with allergies")
            continue
        
        # Select best option based on budget
        selected_food = None
        for food in safe_options:
            # Check for budget alternatives if tight budget
            food_key = [k for k, v in FOOD_DATABASE.items() if v.name == food.name]
            if budget_tier in ["very_low", "low"] and food_key:
                alt_key = BUDGET_ALTERNATIVES.get(food_key[0])
                if alt_key and alt_key in FOOD_DATABASE:
                    food = FOOD_DATABASE[alt_key]
            
            # Check if affordable
            if food.price_estimate <= remaining_budget:
                # Check if SNAP eligible and user has SNAP
                if user_context.financials.snap_status and not food.snap_eligible:
                    continue  # Skip non-SNAP items for SNAP users
                    
                selected_food = food
                break
        
        if not selected_food:
            # Take cheapest option even if over budget slightly
            selected_food = safe_options[0]
        
        # Find best store for this item
        best_store = None
        for tf in resource_map.accessible_stores:
            if user_context.financials.snap_status and not tf.store.snap_accepted:
                continue
            if tf.store.inventory_level != InventoryLevel.LOW:
                best_store = tf.store.name
                break
        
        # Create shopping list item
        priority = calculate_priority(need.priority, budget_tier)
        
        item = ShoppingListItem(
            food=selected_food,
            quantity=1,
            priority=priority,
            reason=f"Addresses {need.nutrient}: {need.reason[:80]}...",
            suggested_store=best_store,
            estimated_cost=selected_food.price_estimate,
            nutrients_addressed=[need.nutrient]
        )
        
        # Track nutrients and add to list if not duplicate
        already_have = any(
            selected_food.name == existing.food.name 
            for existing in shopping_list.items
        )
        
        if not already_have:
            shopping_list.items.append(item)
            remaining_budget -= selected_food.price_estimate
            
            if need.nutrient not in nutrients_addressed:
                nutrients_addressed[need.nutrient] = []
            nutrients_addressed[need.nutrient].append(selected_food.name)
            
            reasoning.append(
                f"Added {selected_food.name} (${selected_food.price_estimate:.2f}) "
                f"for {need.nutrient} [Priority {need.priority}]"
            )
        else:
            # Add nutrient to existing item's list
            for existing in shopping_list.items:
                if existing.food.name == selected_food.name:
                    if need.nutrient not in existing.nutrients_addressed:
                        existing.nutrients_addressed.append(need.nutrient)
                    break
    
    # Phase 3: Fill in with budget-friendly staples if budget allows
    staples = ["oats", "brown_rice", "black_beans_canned", "bananas", "peanut_butter"]
    
    for staple_key in staples:
        if remaining_budget <= 2:
            break
            
        staple = FOOD_DATABASE.get(staple_key)
        if not staple:
            continue
            
        already_have = any(staple.name == item.food.name for item in shopping_list.items)
        
        if not already_have and staple.price_estimate <= remaining_budget:
            shopping_list.items.append(ShoppingListItem(
                food=staple,
                quantity=1,
                priority=ShoppingPriority.OPTIONAL,
                reason="Budget-friendly staple for general nutrition",
                estimated_cost=staple.price_estimate
            ))
            remaining_budget -= staple.price_estimate
            reasoning.append(f"Added staple: {staple.name}")
    
    # Calculate totals
    shopping_list.total_estimated_cost = sum(item.estimated_cost for item in shopping_list.items)
    shopping_list.budget_remaining = remaining_budget
    shopping_list.reasoning_log.extend(reasoning)
    
    # Organize by store
    for item in shopping_list.items:
        store = item.suggested_store or "Any Store"
        if store not in shopping_list.store_visits:
            shopping_list.store_visits[store] = []
        shopping_list.store_visits[store].append(item)
    
    # Sort items by priority
    shopping_list.items.sort(key=lambda x: x.priority.value)
    
    return shopping_list


def print_shopping_list(shopping_list: ShoppingList, user_context: UserContext) -> None:
    """Print a formatted shopping list."""
    print("\n" + "="*60)
    print("  CURATED SHOPPING LIST")
    print("="*60)
    
    budget = user_context.financials.weekly_budget
    print(f"\n💰 Budget: ${budget:.2f} | Estimated Total: ${shopping_list.total_estimated_cost:.2f}")
    print(f"   Remaining: ${shopping_list.budget_remaining:.2f}")
    
    if user_context.financials.snap_status:
        print("   ✓ SNAP benefits applied")
    
    # Food Pantry recommendations
    if shopping_list.pantry_items:
        print("\n🆓 FROM FOOD PANTRY (FREE):")
        for item in shopping_list.pantry_items:
            print(f"   • {item.food.name}")
            if item.suggested_store:
                print(f"     Location: {item.suggested_store}")
    
    # Main shopping list
    print("\n📋 SHOPPING LIST (by priority):")
    
    priority_labels = {
        ShoppingPriority.CRITICAL: "🔴 CRITICAL",
        ShoppingPriority.HIGH: "🟠 HIGH",
        ShoppingPriority.MODERATE: "🟡 MODERATE", 
        ShoppingPriority.OPTIONAL: "🟢 OPTIONAL"
    }
    
    current_priority = None
    for item in shopping_list.items:
        if item.priority != current_priority:
            current_priority = item.priority
            print(f"\n   {priority_labels[current_priority]}:")
        
        snap_tag = " [SNAP✓]" if item.food.snap_eligible else ""
        print(f"      □ {item.food.name} - ${item.estimated_cost:.2f}{snap_tag}")
        print(f"        Nutrients: {', '.join(item.nutrients_addressed[:3])}")
        if item.suggested_store:
            print(f"        Get at: {item.suggested_store}")
    
    # Store visits summary
    if len(shopping_list.store_visits) > 1:
        print("\n🏪 SUGGESTED STORE VISITS:")
        for store, items in shopping_list.store_visits.items():
            total = sum(i.estimated_cost for i in items)
            print(f"   {store}: {len(items)} items (~${total:.2f})")


def get_item_explanation(item: ShoppingListItem, nutrient_priorities: NutrientPriorityList) -> str:
    """
    Generate a detailed explanation of why an item was chosen.
    Used for the interactive "Why?" feature.
    """
    explanation_parts = []
    
    explanation_parts.append(f"📦 {item.food.name}")
    explanation_parts.append(f"\n   Price: ${item.estimated_cost:.2f}")
    explanation_parts.append(f"   Priority: {item.priority.name}")
    
    explanation_parts.append(f"\n   🔬 BIOLOGICAL CONNECTION:")
    
    for nutrient in item.nutrients_addressed:
        # Find the matching nutrient need
        for need in nutrient_priorities.needs:
            if need.nutrient == nutrient:
                explanation_parts.append(f"\n   → {nutrient}:")
                explanation_parts.append(f"     {need.reason}")
                if need.related_markers:
                    explanation_parts.append(f"     Related markers: {', '.join(need.related_markers[:3])}")
                break
    
    explanation_parts.append(f"\n   📊 This food provides: {', '.join(item.food.nutrients_provided)}")
    explanation_parts.append(f"\n   💡 Selection reason: {item.reason}")
    
    return "\n".join(explanation_parts)
