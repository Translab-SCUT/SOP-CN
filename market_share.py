"""Selected province-generic SOP-CN functions; runtime inputs are supplied by the parent model."""

from __future__ import annotations


def safe_log(x):
    return np.log(np.where(x <= 0, 1e-6, x))


def safe_exp(x):
    return np.exp(np.clip(x, MIN_EXP_VALUE, None))


def safe_divide(numerator, denominator):
    try:
        return numerator / denominator if denominator != 0 else np.nan
    except Exception as e:
        print("Division error:", e)
        return np.nan


def Pcosteff_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15):
    equation_results = np.zeros_like(x2, dtype=float)

    
    equation_results[0:3] = safe_divide(safe_exp(x1.iloc[0] * x2[0:3]), x3.iloc[0])
    equation_results[3:5] = safe_divide(safe_exp(x1.iloc[0] * x2[3:5]), x14.iloc[0])
    equation_results[5:8] = safe_divide(safe_exp(x4.iloc[0] * x2[5:8]), x5.iloc[0])
    equation_results[8:11] = safe_divide(safe_exp(x6.iloc[0] * x2[8:11]), x7.iloc[0])
    equation_results[11] = safe_divide(safe_exp(x8.iloc[0] * x2[11]), x9.iloc[0])
    equation_results[12:15] = safe_divide(safe_exp(x1.iloc[0] * x2[12:15]), x10.iloc[0])
    equation_results[15:17] = safe_divide(safe_exp(x1.iloc[0] * x2[15:17]), x15.iloc[0])
    equation_results[17:20] = safe_divide(safe_exp(x4.iloc[0] * x2[17:20]), x11.iloc[0])
    equation_results[20:23] = safe_divide(safe_exp(x6.iloc[0] * x2[20:23]), x12.iloc[0])
    equation_results[23] = safe_divide(safe_exp(x8.iloc[0] * x2[23]), x13.iloc[0])

    return equation_results


def Pptrain_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[0:3] = EXP(LN(x1.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x4.iloc[0]
    equation_results[3:5] = EXP(LN(x18.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x4.iloc[0]
    equation_results[5:8] = EXP(LN(x5.iloc[0]) / x6.iloc[0] * x3.iloc[0]) / x4.iloc[0]
    equation_results[8:11] = EXP(LN(x7.iloc[0])/ x8.iloc[0] * x9.iloc[0]) / x4.iloc[0]
    equation_results[11] = EXP(LN(x10.iloc[0]) / x11.iloc[0] * x12.iloc[0]) / x4.iloc[0]
    equation_results[12:15] = EXP(LN(x13.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x14.iloc[0]
    equation_results[15:17] = EXP(LN(x19.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x14.iloc[0]
    equation_results[17:20] = EXP(LN(x15.iloc[0]) / x6.iloc[0] * x3.iloc[0]) / x14.iloc[0]
    equation_results[20:23] = EXP(LN(x16.iloc[0]) / x8.iloc[0] * x9.iloc[0]) / x14.iloc[0]
    equation_results[23] = EXP(LN(x17.iloc[0]) / x11.iloc[0] * x12.iloc[0]) / x14.iloc[0]

    return equation_results


def Pclass_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[0:12] = (EXP(LN(x1.iloc[0]) / x2.iloc[0] * x3.iloc[0]) + EXP(LN(x1.iloc[0]) / x4.iloc[0] * x3.iloc[0]) + EXP(LN(x1.iloc[0]) / x5.iloc[0] * x3.iloc[0])) / x6.iloc[0]
    equation_results[12:24] = (EXP(LN(x7.iloc[0]) / x2.iloc[0] * x8.iloc[0]) + EXP(LN(x7.iloc[0]) / x4.iloc[0] * x8.iloc[0]) + EXP(LN(x7.iloc[0]) / x5.iloc[0] * x8.iloc[0])) / x6.iloc[0]

    return equation_results


def Market_Share_Private_Owned_Vehicle(x1, x2, x3):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[0:24] = x1[0:24] * x2[0:24] * x3[0:24]

    return equation_results


def Pcosteff_Non_Private_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15):
    equation_results = np.zeros_like(x2, dtype=float)

    equation_results[0:3] = EXP(x1.iloc[0] * x2[0:3]) / x3.iloc[0]
    equation_results[3:5] = EXP(x1.iloc[0] * x2[3:5]) / x14.iloc[0]
    equation_results[5:8] = EXP(x4.iloc[0] * x2[5:8]) / x5.iloc[0]
    equation_results[8:11] = EXP(x6.iloc[0] * x2[8:11]) / x7.iloc[0]
    equation_results[11] = EXP(x8.iloc[0] * x2[11]) / x9.iloc[0]
    equation_results[12:15] = EXP(x1.iloc[0] * x2[12:15]) / x10.iloc[0]
    equation_results[15:17] = EXP(x1.iloc[0] * x2[15:17]) / x15.iloc[0]
    equation_results[17:20] = EXP(x4.iloc[0] * x2[17:20]) / x11.iloc[0]
    equation_results[20:23] = EXP(x6.iloc[0] * x2[20:23]) / x12.iloc[0]
    equation_results[23] = EXP(x8.iloc[0] * x2[23]) / x13.iloc[0]

    return equation_results


def Pptrain_Non_Private_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[0:3] = EXP(LN(x1.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x4.iloc[0]
    equation_results[3:5] = EXP(LN(x18.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x4.iloc[0]
    equation_results[5:8] = EXP(LN(x5.iloc[0]) / x6.iloc[0] * x3.iloc[0]) / x4.iloc[0]
    equation_results[8:11] = EXP(LN(x7.iloc[0])/ x8.iloc[0] * x9.iloc[0]) / x4.iloc[0]
    equation_results[11] = EXP(LN(x10.iloc[0]) / x11.iloc[0] * x12.iloc[0]) / x4.iloc[0]
    equation_results[12:15] = EXP(LN(x13.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x14.iloc[0]
    equation_results[15:17] = EXP(LN(x19.iloc[0]) / x2.iloc[0] * x3.iloc[0]) / x14.iloc[0]
    equation_results[17:20] = EXP(LN(x15.iloc[0]) / x6.iloc[0] * x3.iloc[0]) / x14.iloc[0]
    equation_results[20:23] = EXP(LN(x16.iloc[0]) / x8.iloc[0] * x9.iloc[0]) / x14.iloc[0]
    equation_results[23] = EXP(LN(x17.iloc[0]) / x11.iloc[0] * x12.iloc[0]) / x14.iloc[0]

    return equation_results


def Pclass_Non_Private_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[0:12] = (EXP(LN(x1.iloc[0]) / x2.iloc[0] * x3.iloc[0]) + EXP(LN(x1.iloc[0]) / x4.iloc[0] * x3.iloc[0]) + EXP(LN(x1.iloc[0]) / x5.iloc[0] * x3.iloc[0])) / x6.iloc[0]
    equation_results[12:24] = (EXP(LN(x7.iloc[0]) / x2.iloc[0] * x8.iloc[0]) + EXP(LN(x7.iloc[0]) / x4.iloc[0] * x8.iloc[0]) + EXP(LN(x7.iloc[0]) / x5.iloc[0] * x8.iloc[0])) / x6.iloc[0]

    return equation_results


def Market_Share_Non_Private_Vehicle(x1, x2, x3):
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[0:24] = x1[0:24] * x2[0:24] * x3[0:24]

    return equation_results
