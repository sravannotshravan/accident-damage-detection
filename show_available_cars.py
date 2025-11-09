"""
Show all available car brands and models in database
"""

import mysql.connector
from config import mysql_credentials

def show_available_cars():
    conn = mysql.connector.connect(**mysql_credentials)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🚗 AVAILABLE CAR BRANDS AND MODELS IN DATABASE")
    print("=" * 70)
    print()
    
    # Get all brands
    cursor.execute("SELECT DISTINCT brand FROM car_models ORDER BY brand")
    brands = cursor.fetchall()
    
    print(f"📋 Total Brands: {len(brands)}")
    print("-" * 70)
    
    for brand in brands:
        brand_name = brand[0]
        
        # Get models for this brand
        cursor.execute(
            "SELECT DISTINCT model FROM car_models WHERE brand = %s ORDER BY model",
            (brand_name,)
        )
        models = cursor.fetchall()
        
        # Get sample parts and prices
        cursor.execute(
            "SELECT part, price FROM car_models WHERE brand = %s LIMIT 3",
            (brand_name,)
        )
        sample_parts = cursor.fetchall()
        
        print(f"\n🏢 Brand: {brand_name}")
        print(f"   Models ({len(models)}): {', '.join([m[0] for m in models])}")
        print(f"   Sample Parts:")
        for part in sample_parts:
            print(f"      • {part[0]}: ₹{part[1]}")
    
    print()
    print("=" * 70)
    
    # Show total statistics
    cursor.execute("SELECT COUNT(*) FROM car_models")
    total_parts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT part) FROM car_models")
    unique_parts = cursor.fetchone()[0]
    
    print(f"\n📊 DATABASE STATISTICS:")
    print(f"   Total entries: {total_parts}")
    print(f"   Unique parts: {unique_parts}")
    print()
    
    # Show all available part types
    cursor.execute("SELECT DISTINCT part FROM car_models ORDER BY part")
    parts = cursor.fetchall()
    print(f"🔧 AVAILABLE PART TYPES:")
    for part in parts:
        print(f"   • {part[0]}")
    
    print()
    print("=" * 70)
    
    # Show what the current user has
    cursor.execute("SELECT name, car_brand, model FROM user_info")
    users = cursor.fetchall()
    
    if users:
        print(f"\n👤 REGISTERED USERS AND THEIR CARS:")
        print("-" * 70)
        for user in users:
            print(f"\n   User: {user[0]}")
            print(f"   Car: {user[1]} {user[2]}")
            
            # Check if this combination exists in database
            cursor.execute(
                "SELECT COUNT(*) FROM car_models WHERE brand = %s AND model = %s",
                (user[1], user[2])
            )
            match_count = cursor.fetchone()[0]
            
            if match_count > 0:
                print(f"   Status: ✅ Match found ({match_count} parts available)")
            else:
                print(f"   Status: ❌ No exact match in database")
                
                # Suggest similar
                cursor.execute(
                    "SELECT DISTINCT model FROM car_models WHERE UPPER(brand) = UPPER(%s)",
                    (user[1],)
                )
                similar = cursor.fetchall()
                if similar:
                    print(f"   💡 Available models for {user[1]}: {', '.join([s[0] for s in similar])}")
    
    print()
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    show_available_cars()
