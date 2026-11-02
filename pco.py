

from __future__ import annotations


def Total_Production_Cost(x1, x2, x3, x4, x5):
    equation_results = np.zeros(2, dtype=float)

    equation_results[0] = x1.iloc[0] + x2.iloc[0] + x3.iloc[0] + x4.iloc[0] + x5.iloc[0]
    equation_results[1] = x1.iloc[1] + x2.iloc[1] + x3.iloc[1] + x4.iloc[1] + x5.iloc[1]
    
    return equation_results


def Lifetime_Elec_Use_Private_Owned_Vehicle(x1, x3, x4):

    equation_results = np.zeros_like(x1, dtype=float)
    
    
    driving_mean = df_consumer['Driving - mean (km)'].iloc[0]
    lifetime_km = df_consumer['Lifetime kilometers'].iloc[0] 
    
    equation_results[:5] = 0
    
    equation_results[5:11] = (
        (driving_mean * x1[5:11]) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[5:11]
    )
    
    equation_results[11] = 0
    
    equation_results[12:17] = 0
    
    equation_results[17:23] = (
        (driving_mean * x1[17:23]) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[17:23]
    )
    
    equation_results[23] = 0
    
    return equation_results


def Lifetime_Fuel_Use_Private_Owned_Vehicle(x1, x3, x4):
    x1 = x1.values if hasattr(x1, 'values') else x1
    x3 = x3.values if hasattr(x3, 'values') else x3
    x4 = x4.values if hasattr(x4, 'values') else x4
    
    equation_results = np.zeros_like(x1, dtype=float)
    
    driving_mean = df_consumer['Driving - mean (km)'].iloc[0] 
    lifetime_km = df_consumer['Lifetime kilometers'].iloc[0]  

    equation_results[:5] = (
        (driving_mean * (1 - x1[:5])) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[:5]
    )

    equation_results[5:11] = (
        (driving_mean * (1 - x1[5:11])) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[5:11]
    )

    equation_results[11] = (
        (driving_mean * x1[11]) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[11]
    )
    
    equation_results[12:17] = (
        (driving_mean * (1 - x1[12:17])) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[12:17]
    )
    
    equation_results[17:23] = (
        (driving_mean * (1 - x1[17:23])) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[17:23]
    )
    
    equation_results[23] = (
        (driving_mean * x1[23]) 
        / driving_mean 
        * lifetime_km 
        / 100 
        * x4[23]
    )
    
    return equation_results


def Price_to_consumers_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10):
    equation_results = np.zeros_like(x1, dtype=float)
    
    equation_results[:5] = x1[:5] * x2.iloc[0] - x3[:5] - x4[:5] - x5[:5] - x6[:5] + x9[:5] + x10[:5]
    equation_results[5:11] = x1[5:11] * x7.iloc[0] - np.minimum(x3[5:11] + x4[5:11] + x5[5:11], x1[5:11] * x7.iloc[0] * 0.7) - x6[5:11] + x9[5:11] + x10[5:11]
    equation_results[11] = x1[11] * x2.iloc[0] - x3[11] - x4[11] - x5[11] - x6[11] + x9[11] + x10[11]
    equation_results[12:17] = x1[12:17] * x8.iloc[0] - x3[12:17] - x4[12:17] - x5[12:17] - x6[12:17] + x9[12:17] + x10[12:17]
    equation_results[17:23] = x1[17:23] * x7.iloc[0] - np.minimum(x3[17:23] + x4[17:23] + x5[17:23], x1[17:23] * x7.iloc[0] * 0.7) - x6[17:23] + x9[17:23] + x10[17:23]
    equation_results[23] = x1[23] * x7.iloc[0] - x3[23] - x4[23] - x5[23] - x6[23] + x9[23] + x10[23]

    return equation_results


def Refilling_Inconvenience_Costs_Public(x1, x2):
    equation_results = np.zeros(2, dtype=float)
    
    equation_results[0] = x1.iloc[0] * x2.iloc[0]
    equation_results[1] = x1.iloc[1] * x2.iloc[1]
    
    return equation_results


def Refuelling_Inconvenience_Cost(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10):
    equation_results = np.zeros_like(x1, dtype=float)
    
    equation_results[:3] = x1.iloc[:3] / x2.iloc[0] * x3.iloc[0]
    equation_results[3] = x1.iloc[3] / x2.iloc[0] * x7.iloc[0]
    equation_results[4] = x1.iloc[4] / x2.iloc[0] * x8.iloc[0]
    equation_results[5:8] = x1.iloc[5:8].values / x2.iloc[0] * x3.iloc[0] + np.multiply(x9.iloc[0:3].values, x6.iloc[5:8].values)
    equation_results[8:11] = np.multiply(x5.iloc[0:3].values, x6.iloc[8:11].values)
    equation_results[11] = x4.iloc[0]
    equation_results[12:15] = x1.iloc[12:15] / x2.iloc[0] * x3.iloc[0]
    equation_results[15] = x1.iloc[15] / x2.iloc[0] * x7.iloc[0]
    equation_results[16] = x1.iloc[16] / x2.iloc[0] * x8.iloc[0]
    equation_results[17:20] = x1.iloc[17:20].values / x2.iloc[0] * x3.iloc[0] + np.multiply(x9.iloc[3:6].values, x6.iloc[17:20].values)
    equation_results[20:23] = np.multiply(x5.iloc[3:6].values, x6.iloc[20:23].values)
    equation_results[23] = x4.iloc[1]

    return equation_results


def Range_Cost_BEV_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6):
    """Use the former non-private range-cost logic for private-owned BEVs, with ride parameters fallback."""
    equation_results = np.zeros_like(x1, dtype=float)

    travel_distance_per_ride = x3.iloc[0]
    fare_per_ride = x4.iloc[0]
    if pd.isna(travel_distance_per_ride):
        travel_distance_per_ride = x3.iloc[1]
    if pd.isna(fare_per_ride):
        fare_per_ride = x4.iloc[1]

    lifetime_kilometers = x5.iloc[0]
    daily_driving_mean = x6.iloc[0]
    lifetime_driving_days = lifetime_kilometers / daily_driving_mean

    equation_results[:11] = np.where(
        x1[:11] == 0,
        (x2[:11] / travel_distance_per_ride * fare_per_ride) * lifetime_driving_days,
        0,
    )
    equation_results[11] = (
        (daily_driving_mean - x2[11]) / travel_distance_per_ride * fare_per_ride
    ) * lifetime_driving_days
    equation_results[12:23] = np.where(
        x1[12:23] == 0,
        (x2[12:23] / travel_distance_per_ride * fare_per_ride) * lifetime_driving_days,
        0,
    )
    equation_results[23] = (
        (daily_driving_mean - x2[23]) / travel_distance_per_ride * fare_per_ride
    ) * lifetime_driving_days

    return equation_results


def Ownership_Total_Cost_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6, x7):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[:5] = x1[:5] + x2[:5] + x3[:5] + x4[:5] + x5[:5] + x6[:5] + x7[:5]
    equation_results[5:8] = x1[5:8] + x2[5:8] + x3[5:8] + x5[5:8] + x6[5:8] + x7[5:8]
    equation_results[8:17] = x1[8:17] + x2[8:17] + x3[8:17] + x4[8:17] + x5[8:17] + x6[8:17] + x7[8:17]
    equation_results[17:20] = x1[17:20] + x2[17:20] + x3[17:20] + x5[17:20] + x6[17:20] + x7[17:20]
    equation_results[20:24] = x1[20:24] + x2[20:24] + x3[20:24] + x4[20:24] + x5[20:24] + x6[20:24] + x7[20:24]

    return equation_results


def Ownership_Total_Cost_Non_Private_Vehicle(x1,x2,x3,x4,x5,x6,x7):
    eq = np.zeros(24, dtype=float)
    
    eq[:5]    = x1[:5]    + x2[:5]    + x3[:5]    + x4[:5]    + x5[:5]    + x6[:5]    + x7[:5]
    eq[5:8]   = x1[5:8]   + x2[5:8]   + x3[5:8]   + 0         + x5[5:8]   + x6[5:8]   + x7[5:8]
    eq[8:11]  = x1[8:11]  + 0         + x3[8:11]  + x4[8:11]  + x5[8:11]  + x6[8:11]  + x7[8:11]
    eq[11]    = x1[11]    + x2[11]    + x3[11]    + 0         + x5[11]    + x6[11]    + x7[11]
    
    eq[12:17] = x1[12:17] + x2[12:17] + x3[12:17] + x4[12:17] + x5[12:17] + x6[12:17] + x7[12:17]
    eq[17:20] = x1[17:20] + x2[17:20] + x3[17:20] + 0         + x5[17:20] + x6[17:20] + x7[17:20]
    eq[20:23] = x1[20:23] + 0         + x3[20:23] + x4[20:23] + x5[20:23] + x6[20:23] + x7[20:23]
    eq[23]    = x1[23]    + x2[23]    + x3[23]    + 0         + x5[23]    + x6[23]    + x7[23]
    return eq
