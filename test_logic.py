import sys
import os
import numpy as np

# Add logic directory
sys.path.append(os.path.join(os.getcwd(), 'reservoir_tool'))
from logic.mbe import calculate_f, calculate_eo, calculate_efw, estimate_ooip

def test_mbe_logic():
    # Test values from my manual calculation
    # Np = 5.0e6, Bo = 1.3, Rs = 600, Rp = 1000, Bg = 0.001
    # Boi = 1.25, Rsi = 800
    # cf = 4e-6, dp = 500, swi = 0.2, cw = 3e-6, we = 0
    
    np_val = 5.0e6
    bo = 1.3
    rs = 600
    rp = 1000
    bg = 0.001
    boi = 1.25
    rsi = 800
    cf = 4e-6
    dp = 500
    swi = 0.2
    cw = 3e-6
    we = 0
    m = 0
    
    f = calculate_f(np_val, bo, rs, bg, rp)
    eo = calculate_eo(bo, boi, rsi, rs, bg)
    efw = calculate_efw(boi, cw, swi, cf, dp)
    ooip = estimate_ooip(f, we, eo, eg=0, efw=efw, m=m)
    
    print(f"Calculated F: {f:,.2f} (Expected: 8,500,000.00)")
    print(f"Calculated Eo: {eo:,.4f} (Expected: 0.2500)")
    print(f"Calculated Efw: {efw:,.6f} (Expected: 0.003594)")
    print(f"Calculated OOIP: {ooip:,.2f} (Expected: ~33,518,000)")
    
    assert np.isclose(f, 8500000.0)
    assert np.isclose(eo, 0.25)
    assert np.isclose(efw, 0.00359375)
    assert ooip > 33e6 and ooip < 34e6
    
    print("\n✅ MBE Logic Verification Passed!")

if __name__ == "__main__":
    try:
        test_mbe_logic()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        sys.exit(1)
