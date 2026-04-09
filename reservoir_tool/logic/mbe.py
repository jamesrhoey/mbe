import numpy as np

def calculate_f(np_val, bo, rs, bg, rp, wp=0, bw=1.0):
    """
    Calculate Underground Withdrawal (F).
    
    Parameters:
    - np_val: Cumulative oil production (STB)
    - bo: Current oil formation volume factor (bbl/STB)
    - rs: Current solution gas-oil ratio (scf/STB)
    - bg: Current gas formation volume factor (bbl/scf)
    - rp: Cumulative gas-oil ratio (scf/STB)
    - wp: Cumulative water production (STB)
    - bw: Water formation volume factor (bbl/STB)
    
    Returns:
    - F: Underground withdrawal (res bbl)
    """
    return np_val * (bo + (rp - rs) * bg) + (wp * bw)

def calculate_eo(bo, boi, rsi, rs, bg):
    """
    Calculate Oil and Dissolved Gas Expansion (Eo).
    
    Parameters:
    - bo: Current oil FVF (bbl/STB)
    - boi: Initial oil FVF (bbl/STB)
    - rsi: Initial solution GOR (scf/STB)
    - rs: Current solution GOR (scf/STB)
    - bg: Current gas FVF (bbl/scf)
    """
    return (bo - boi) + (rsi - rs) * bg

def calculate_eg(boi, bg, bgi):
    """
    Calculate Gas Cap Expansion (Eg).
    
    Parameters:
    - boi: Initial oil FVF (bbl/STB)
    - bg: Current gas FVF (bbl/scf)
    - bgi: Initial gas FVF (bbl/scf)
    """
    return boi * (bg / bgi - 1)

def calculate_efw(boi, cw, swi, cf, dp):
    """
    Calculate Formation and Connate Water Expansion (Efw).
    
    Parameters:
    - boi: Initial oil FVF (bbl/STB)
    - cw: Water compressibility (psi^-1)
    - swi: Initial water saturation (fraction)
    - cf: Formation (pore) compressibility (psi^-1)
    - dp: Pressure drop (Pi - P) (psi)
    """
    return boi * ((cw * swi + cf) / (1 - swi)) * dp

def estimate_ooip(f, we, eo, eg=0, efw=0, m=0):
    """
    Estimate Original Oil in Place (N) using Havlena-Odeh MBE.
    F = N * (Eo + m*Eg + Efw) + We
    
    Returns:
    - N: Original Oil in Place (STB)
    """
    e_total = eo + (m * eg) + efw
    # Avoid division by zero
    if np.any(e_total == 0):
        return np.zeros_like(f)
    return (f - we) / e_total

def calculate_error(calculated, expected):
    """Compute percentage error."""
    if expected == 0:
        return 0
    return np.abs((calculated - expected) / expected) * 100
