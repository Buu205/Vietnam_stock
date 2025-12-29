"""
Demo script to understand and test latitude/longitude coordinates
Shows practical examples from BHX store data
"""
import pandas as pd
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula

    Args:
        lat1, lon1: First coordinate (degrees)
        lat2, lon2: Second coordinate (degrees)

    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Earth radius in kilometers
    r = 6371

    return c * r


def find_nearest_stores(df, lat, lng, n=5):
    """
    Find N nearest stores to a given coordinate

    Args:
        df: DataFrame with store data
        lat, lng: Your location coordinates
        n: Number of nearest stores to return

    Returns:
        DataFrame with nearest stores sorted by distance
    """
    # Calculate distance to all stores
    df['distance_km'] = df.apply(
        lambda row: haversine_distance(lat, lng, row['lat'], row['lng']),
        axis=1
    )

    # Sort by distance and return top N
    return df.nsmallest(n, 'distance_km')


def demo_google_maps_links(df):
    """Generate Google Maps links for sample stores"""
    print("\n" + "="*80)
    print("📍 GOOGLE MAPS DEMO")
    print("="*80)

    print("\nPaste these links into your browser to see exact store locations:\n")

    # Sample 5 stores
    samples = df.sample(5)

    for i, (_, store) in enumerate(samples.iterrows(), 1):
        lat, lng = store['lat'], store['lng']
        location = store['storeLocation'][:60]

        # Google Maps link
        maps_url = f"https://www.google.com/maps?q={lat},{lng}"

        print(f"{i}. {location}...")
        print(f"   Coordinates: ({lat:.6f}, {lng:.6f})")
        print(f"   Google Maps: {maps_url}")
        print()


def demo_distance_calculation(df):
    """Demo distance calculation between stores"""
    print("\n" + "="*80)
    print("📏 DISTANCE CALCULATION DEMO")
    print("="*80)

    # Get extreme stores
    north = df.loc[df['lat'].idxmax()]
    south = df.loc[df['lat'].idxmin()]

    distance = haversine_distance(
        north['lat'], north['lng'],
        south['lat'], south['lng']
    )

    print(f"\n🔹 From NORTHERNMOST to SOUTHERNMOST store:")
    print(f"\n   Store A (North): {north['storeLocation'][:50]}...")
    print(f"   Coordinates: ({north['lat']:.6f}, {north['lng']:.6f})")

    print(f"\n   Store B (South): {south['storeLocation'][:50]}...")
    print(f"   Coordinates: ({south['lat']:.6f}, {south['lng']:.6f})")

    print(f"\n   📍 Distance: {distance:,.1f} km (≈ {distance/1.5:.0f} minutes driving)")
    print(f"                  ({distance:.1f} km / 80 km/h ≈ {distance/80*60:.0f} minutes)")


def demo_nearest_store_finder(df):
    """Demo finding nearest stores to a location"""
    print("\n" + "="*80)
    print("🔍 NEAREST STORE FINDER DEMO")
    print("="*80)

    # Example: Find stores near TP. Hồ Chí Minh center
    hcm_center_lat = 10.7769
    hcm_center_lng = 106.7009

    print(f"\n📍 Your location: TP. Hồ Chí Minh Center")
    print(f"   Coordinates: ({hcm_center_lat}, {hcm_center_lng})")

    nearest = find_nearest_stores(df, hcm_center_lat, hcm_center_lng, n=5)

    print(f"\n🏪 Top 5 Nearest BHX Stores:\n")
    print(f"{'Rank':>5} {'Distance':>10} {'Store ID':>10} {'Location':<50}")
    print("-" * 80)

    for i, (_, store) in enumerate(nearest.iterrows(), 1):
        print(f"{i:>5} {store['distance_km']:>9.2f} km {store['storeId']:>10} {store['storeLocation'][:48]}")


def demo_regional_centers(df):
    """Calculate average coordinates for each region"""
    print("\n" + "="*80)
    print("🌏 REGIONAL CENTERS DEMO")
    print("="*80)

    # Define regions by latitude
    df_temp = df.copy()
    df_temp['region'] = pd.cut(
        df_temp['lat'],
        bins=[0, 11, 16, 25],
        labels=['Southern', 'Central', 'Northern']
    )

    print("\n📊 Average coordinates for each region:\n")

    for region in ['Southern', 'Central', 'Northern']:
        region_df = df_temp[df_temp['region'] == region]
        avg_lat = region_df['lat'].mean()
        avg_lng = region_df['lng'].mean()
        count = len(region_df)

        maps_url = f"https://www.google.com/maps?q={avg_lat},{avg_lng}"

        print(f"{region:>10} Region:")
        print(f"   Stores: {count:,}")
        print(f"   Center: ({avg_lat:.6f}, {avg_lng:.6f})")
        print(f"   Map: {maps_url}")
        print()


if __name__ == '__main__':
    # Load data
    df = pd.read_parquet('bhx_stores_20251229.parquet')

    print("\n" + "="*80)
    print("LATITUDE & LONGITUDE PRACTICAL DEMO")
    print("="*80)
    print(f"\nTotal stores: {len(df):,}")

    # Run demos
    demo_google_maps_links(df)
    demo_distance_calculation(df)
    demo_nearest_store_finder(df)
    demo_regional_centers(df)

    print("\n" + "="*80)
    print("✅ Demo complete!")
    print("="*80 + "\n")
