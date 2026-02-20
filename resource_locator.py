"""
Phase 3: Geographic & Financial Mapping
ResourceLocator function with synthetic store data and travel feasibility.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from user_context import UserContext, Logistics


class StoreType(Enum):
    GROCERY = "grocery"
    FOOD_PANTRY = "food_pantry"
    FARMERS_MARKET = "farmers_market"
    DISCOUNT = "discount"
    SPECIALTY = "specialty"


class InventoryLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Store:
    """Represents a nearby store/resource."""
    name: str
    store_type: StoreType
    distance_miles: float
    snap_accepted: bool
    wic_accepted: bool
    inventory_level: InventoryLevel
    price_tier: int  # 1=cheapest, 5=most expensive
    specialty_items: List[str] = field(default_factory=list)
    hours: str = "9am-9pm"
    
    @property
    def is_food_assistance_friendly(self) -> bool:
        return self.snap_accepted or self.wic_accepted


@dataclass
class TravelFeasibility:
    """Calculated travel feasibility for a store."""
    store: Store
    is_accessible: bool
    travel_method: str  # "walk", "transit", "drive"
    estimated_time_minutes: int
    accessibility_score: float  # 0-1, higher is better
    notes: List[str] = field(default_factory=list)


@dataclass
class ResourceMap:
    """Complete resource mapping for a user."""
    user_zip: str
    accessible_stores: List[TravelFeasibility]
    food_pantries: List[TravelFeasibility]
    snap_stores: List[TravelFeasibility]
    all_stores: List[Store]


# Synthetic store database - simulates real-world data
# Organized by zip code prefix for demo purposes
SYNTHETIC_STORES_DATABASE: Dict[str, List[Store]] = {
    "default": [
        Store(
            name="SaveMart Grocery",
            store_type=StoreType.GROCERY,
            distance_miles=1.2,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["organic produce", "gluten-free"],
            hours="7am-10pm"
        ),
        Store(
            name="Community Food Pantry",
            store_type=StoreType.FOOD_PANTRY,
            distance_miles=0.8,
            snap_accepted=False,  # Free food
            wic_accepted=False,
            inventory_level=InventoryLevel.MEDIUM,
            price_tier=1,  # Free
            specialty_items=["canned goods", "bread", "produce"],
            hours="Mon/Wed/Fri 10am-2pm"
        ),
        Store(
            name="Budget Foods",
            store_type=StoreType.DISCOUNT,
            distance_miles=2.5,
            snap_accepted=True,
            wic_accepted=False,
            inventory_level=InventoryLevel.HIGH,
            price_tier=1,
            specialty_items=["bulk items", "frozen foods"],
            hours="8am-9pm"
        ),
        Store(
            name="Fresh Farmers Market",
            store_type=StoreType.FARMERS_MARKET,
            distance_miles=1.8,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.MEDIUM,
            price_tier=2,
            specialty_items=["local produce", "eggs", "honey"],
            hours="Sat 8am-1pm"
        ),
        Store(
            name="Whole Health Foods",
            store_type=StoreType.SPECIALTY,
            distance_miles=3.2,
            snap_accepted=False,
            wic_accepted=False,
            inventory_level=InventoryLevel.HIGH,
            price_tier=5,
            specialty_items=["supplements", "organic", "specialty diet"],
            hours="9am-8pm"
        ),
        Store(
            name="Dollar General",
            store_type=StoreType.DISCOUNT,
            distance_miles=0.5,
            snap_accepted=True,
            wic_accepted=False,
            inventory_level=InventoryLevel.LOW,
            price_tier=2,
            specialty_items=["canned goods", "snacks", "basic staples"],
            hours="8am-10pm"
        ),
        Store(
            name="St. Mary's Food Bank",
            store_type=StoreType.FOOD_PANTRY,
            distance_miles=2.1,
            snap_accepted=False,
            wic_accepted=False,
            inventory_level=InventoryLevel.HIGH,
            price_tier=1,
            specialty_items=["fresh produce", "meat", "dairy"],
            hours="Tue/Thu 9am-3pm"
        ),
        Store(
            name="ALDI",
            store_type=StoreType.DISCOUNT,
            distance_miles=4.0,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=1,
            specialty_items=["produce", "dairy", "frozen", "specialty imports"],
            hours="9am-8pm"
        ),
        Store(
            name="Target",
            store_type=StoreType.GROCERY,
            distance_miles=5.5,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["organic", "fresh produce", "supplements"],
            hours="8am-10pm"
        ),
        Store(
            name="Neighborhood Co-op",
            store_type=StoreType.SPECIALTY,
            distance_miles=1.5,
            snap_accepted=True,
            wic_accepted=False,
            inventory_level=InventoryLevel.MEDIUM,
            price_tier=4,
            specialty_items=["local", "organic", "bulk bins", "specialty"],
            hours="10am-7pm"
        )
    ],
    # Additional zip-code-specific stores can be added here
    "303": [  # Denver area example
        Store(
            name="King Soopers",
            store_type=StoreType.GROCERY,
            distance_miles=1.0,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["organic", "deli", "pharmacy"],
            hours="6am-11pm"
        ),
    ],
    "300": [  # Atlanta area example
        Store(
            name="Publix",
            store_type=StoreType.GROCERY,
            distance_miles=1.3,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["deli", "bakery", "organic"],
            hours="7am-10pm"
        ),
    ]
}


def get_stores_for_zip(zip_code: str) -> List[Store]:
    """Get stores near a zip code (simulated lookup)."""
    # Check for zip-code-specific stores
    zip_prefix = zip_code[:3] if len(zip_code) >= 3 else zip_code
    
    stores = list(SYNTHETIC_STORES_DATABASE.get("default", []))
    
    # Add any zip-specific stores
    if zip_prefix in SYNTHETIC_STORES_DATABASE:
        stores.extend(SYNTHETIC_STORES_DATABASE[zip_prefix])
    
    return stores


def calculate_travel_time(distance_miles: float, method: str) -> int:
    """Calculate estimated travel time in minutes."""
    speeds = {
        "walk": 3.0,  # mph
        "transit": 12.0,  # mph average including wait
        "drive": 25.0  # mph average with traffic
    }
    speed = speeds.get(method, 3.0)
    base_time = (distance_miles / speed) * 60
    
    # Add overhead
    if method == "transit":
        base_time += 10  # Wait time
    elif method == "walk":
        base_time += 5  # Round trip buffer
    
    return int(base_time)


def calculate_travel_feasibility(store: Store, logistics: Logistics) -> TravelFeasibility:
    """
    Calculate travel feasibility for a specific store based on user logistics.
    """
    notes = []
    
    # Determine best travel method
    if logistics.has_vehicle:
        travel_method = "drive"
        max_practical_distance = 15.0
    elif logistics.has_public_transit:
        travel_method = "transit"
        max_practical_distance = 8.0
    else:
        travel_method = "walk"
        max_practical_distance = 2.0
    
    # Check accessibility
    is_accessible = store.distance_miles <= logistics.max_travel_distance_miles
    
    # If not accessible by preferred method, check alternatives
    if not is_accessible:
        if store.distance_miles <= 2.0:
            travel_method = "walk"
            is_accessible = True
            notes.append("Walking distance")
        elif store.distance_miles <= 8.0 and logistics.has_public_transit:
            travel_method = "transit"
            is_accessible = True
            notes.append("Accessible via public transit")
    
    # Calculate travel time
    travel_time = calculate_travel_time(store.distance_miles, travel_method)
    
    # Calculate accessibility score
    distance_score = max(0, 1 - (store.distance_miles / max_practical_distance))
    time_score = max(0, 1 - (travel_time / 60))  # Penalize trips over 60 min
    inventory_score = {InventoryLevel.HIGH: 1.0, InventoryLevel.MEDIUM: 0.7, InventoryLevel.LOW: 0.4}[store.inventory_level]
    
    accessibility_score = (distance_score * 0.4 + time_score * 0.3 + inventory_score * 0.3)
    
    # Add notes
    if store.store_type == StoreType.FOOD_PANTRY:
        notes.append("FREE - Food pantry")
    if store.distance_miles <= 1.0:
        notes.append("Very close")
    if travel_time > 45:
        notes.append("Long travel time")
        is_accessible = is_accessible and logistics.grocery_trips_per_week >= 2
    
    return TravelFeasibility(
        store=store,
        is_accessible=is_accessible,
        travel_method=travel_method,
        estimated_time_minutes=travel_time,
        accessibility_score=round(accessibility_score, 2),
        notes=notes
    )


def resource_locator(user_context: UserContext) -> ResourceMap:
    """
    Main function: Locate and evaluate all nearby resources based on user context.
    
    Args:
        user_context: User's complete context including logistics
        
    Returns:
        ResourceMap with accessible stores, food pantries, and SNAP stores
    """
    # Get all stores for user's zip code
    all_stores = get_stores_for_zip(user_context.logistics.zip_code)
    
    # Calculate travel feasibility for each store
    all_feasibility: List[TravelFeasibility] = []
    for store in all_stores:
        feasibility = calculate_travel_feasibility(store, user_context.logistics)
        all_feasibility.append(feasibility)
    
    # Filter accessible stores
    accessible_stores = [f for f in all_feasibility if f.is_accessible]
    accessible_stores.sort(key=lambda x: (-x.accessibility_score, x.store.distance_miles))
    
    # Filter food pantries
    food_pantries = [f for f in accessible_stores if f.store.store_type == StoreType.FOOD_PANTRY]
    
    # Filter SNAP-accepting stores
    snap_stores = [f for f in accessible_stores if f.store.snap_accepted]
    
    # Prioritize based on user's financial situation
    if user_context.financials.has_assistance:
        # Move SNAP/WIC stores to top
        snap_stores.sort(key=lambda x: (x.store.price_tier, x.store.distance_miles))
    
    return ResourceMap(
        user_zip=user_context.logistics.zip_code,
        accessible_stores=accessible_stores,
        food_pantries=food_pantries,
        snap_stores=snap_stores,
        all_stores=all_stores
    )


def print_resource_map(resource_map: ResourceMap, user_context: UserContext) -> None:
    """Print a formatted resource map."""
    print("\n" + "="*60)
    print("  RESOURCE LOCATOR - Nearby Food Resources")
    print("="*60)
    print(f"\n📍 Location: ZIP {resource_map.user_zip}")
    print(f"🚗 Transportation: {user_context.logistics.mobility_level.upper()}")
    
    # Food Pantries (if budget is low)
    if resource_map.food_pantries and user_context.financials.budget_tier in ["very_low", "low"]:
        print("\n🆓 FREE FOOD PANTRIES:")
        for tf in resource_map.food_pantries[:3]:
            print(f"   • {tf.store.name}")
            print(f"     Distance: {tf.store.distance_miles} mi ({tf.travel_method}, ~{tf.estimated_time_minutes} min)")
            print(f"     Hours: {tf.store.hours}")
            print(f"     Items: {', '.join(tf.store.specialty_items[:3])}")
    
    # SNAP-Authorized Stores
    if resource_map.snap_stores and user_context.financials.snap_status:
        print("\n🏪 SNAP-AUTHORIZED STORES:")
        for tf in resource_map.snap_stores[:4]:
            if tf.store.store_type != StoreType.FOOD_PANTRY:
                price_symbol = "$" * tf.store.price_tier
                print(f"   • {tf.store.name} [{price_symbol}]")
                print(f"     Distance: {tf.store.distance_miles} mi ({tf.travel_method})")
                print(f"     Inventory: {tf.store.inventory_level.value}")
    
    # All Accessible Stores
    print("\n📋 ALL ACCESSIBLE STORES (by score):")
    for i, tf in enumerate(resource_map.accessible_stores[:6], 1):
        price_symbol = "FREE" if tf.store.store_type == StoreType.FOOD_PANTRY else "$" * tf.store.price_tier
        snap_marker = " [SNAP]" if tf.store.snap_accepted else ""
        wic_marker = " [WIC]" if tf.store.wic_accepted else ""
        
        print(f"   {i}. {tf.store.name} [{price_symbol}]{snap_marker}{wic_marker}")
        print(f"      Type: {tf.store.store_type.value} | Score: {tf.accessibility_score}")
        print(f"      {tf.store.distance_miles} mi via {tf.travel_method} (~{tf.estimated_time_minutes} min)")
        if tf.notes:
            print(f"      Notes: {', '.join(tf.notes)}")


def get_stores_with_item(resource_map: ResourceMap, item: str) -> List[TravelFeasibility]:
    """Find stores that likely have a specific item."""
    matching_stores = []
    
    # Keywords for different food categories
    item_keywords = {
        "produce": ["produce", "fresh", "farmers", "organic"],
        "spinach": ["produce", "fresh", "organic", "leafy"],
        "eggs": ["eggs", "dairy", "fresh", "farmers"],
        "fish": ["fresh", "specialty", "salmon", "seafood"],
        "salmon": ["fresh", "specialty", "seafood"],
        "beans": ["bulk", "canned", "staples", "basic"],
        "lentils": ["bulk", "specialty", "organic"],
        "nuts": ["bulk", "specialty", "snacks"],
        "supplements": ["supplements", "specialty", "health"],
    }
    
    item_lower = item.lower()
    search_keywords = item_keywords.get(item_lower, [item_lower])
    
    for feasibility in resource_map.accessible_stores:
        store = feasibility.store
        # Check if store might have this item
        store_items = " ".join(store.specialty_items).lower()
        if any(kw in store_items for kw in search_keywords):
            matching_stores.append(feasibility)
        elif store.inventory_level == InventoryLevel.HIGH:
            # High inventory stores likely have most items
            matching_stores.append(feasibility)
    
    return matching_stores
