"""
RZS - FINAL PERFECT CALIBRATION
Simultaneous adjustment of V_scale and lambda to hit both Ω_φ and w targets
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ==================== TARGET VALUES ====================
H0_TARGET = 73.0
OMEGA_PHI_TARGET = 0.70
OMEGA_M_TARGET = 0.30
W_TARGET = -0.95
ALPHA = 1.5

# ==================== OPTIMIZATION FUNCTION ====================
def find_optimal_parameters():
    """Find V_scale and lambda that simultaneously satisfy Ω_φ and w constraints"""
    
    print("="*70)
    print("FINAL PARAMETER OPTIMIZATION")
    print("="*70)
    
    # Grid search for optimal parameters
    V_scales = np.linspace(60000, 80000, 20)  # Higher values for higher Ω_φ
    lambdas = np.linspace(0.5, 2.0, 15)       # Lower lambda for w > -1
    
    best_score = 1e10
    best_params = None
    best_results = None
    
    for V_scale in V_scales:
        for lambda_param in lambdas:
            # Fixed parameters
            beta_param = 0.05
            Lambda_RZS = 0.1
            xi0 = 0.01
            phi_initial = 1.55
            X_initial = -0.00005
            
            # Functions
            def V_potential(phi):
                return V_scale * ((lambda_param/4.0) * (phi**2 - ALPHA**2)**2 + Lambda_RZS)
            
            def dV_dphi(phi):
                return V_scale * lambda_param * phi * (phi**2 - ALPHA**2)
            
            def F_func(phi):
                return 0.5 + xi0 * (phi/ALPHA)**2
            
            def dF_dphi(phi):
                return 2.0 * xi0 * phi / ALPHA**2
            
            # Integration
            def equations(N, y):
                phi, X = y
                
                # Use H0_TARGET for matter density scaling
                rho_m = OMEGA_M_TARGET * np.exp(-3*N) * (H0_TARGET**2)
                
                V = V_potential(phi)
                dV = dV_dphi(phi)
                F = F_func(phi)
                dF = dF_dphi(phi)
                
                # Hubble parameter
                A = 3.0 * F
                B = 3.0 * dF * X
                C = -(rho_m + 0.5*X**2 + V)
                disc = B**2 - 4.0*A*C
                
                if disc < 0:
                    H = 1e-5
                else:
                    H = (-B + np.sqrt(disc)) / (2.0*A)
                    if H <= 0:
                        H = 1e-5
                
                damping_factor = 1.0 / (1.0 + 0.1 * abs(X))
                
                rho_phi = 0.5 * X**2 + V
                w_phi = (0.5 * X**2 - V) / rho_phi if rho_phi > 0 else -1.0
                H_dot_approx = -1.5 * H**2 * (1 + w_phi)
                
                dX_dt = (-3.0 * H * X * damping_factor - dV +
                         3.0 * (2.0 * H**2 + H_dot_approx) * dF +
                         beta_param * rho_m)
                
                max_velocity = 100.0
                if abs(dX_dt) > max_velocity:
                    dX_dt = np.sign(dX_dt) * max_velocity
                
                dphi_dN = X / H if H > 1e-6 else 0.0
                dX_dN = dX_dt / H if H > 1e-6 else 0.0
                
                return [dphi_dN, dX_dN]
            
            try:
                sol = solve_ivp(equations, [-3.0, 0.0], [phi_initial, X_initial],
                               method='RK45', t_eval=np.linspace(-3.0, 0.0, 500),
                               rtol=1e-8, atol=1e-10, max_step=0.001)
                
                if not sol.success:
                    continue
                
                # Calculate final values
                N = sol.t
                phi = sol.y[0]
                X = sol.y[1]
                idx_today = -1
                
                V = V_potential(phi[idx_today])
                F = F_func(phi[idx_today])
                dF = dF_dphi(phi[idx_today])
                rho_m = OMEGA_M_TARGET * (H0_TARGET**2)
                
                A = 3.0 * F
                B = 3.0 * dF * X[idx_today]
                C = -(rho_m + 0.5*X[idx_today]**2 + V)
                disc = B**2 - 4.0*A*C
                
                if disc >= 0:
                    H0_result = (-B + np.sqrt(disc)) / (2.0*A)
                else:
                    continue
                
                # Calculate densities
                rho_crit = 3.0 * (H0_result**2)
                rho_phi = 0.5 * X[idx_today]**2 + V
                Omega_phi_result = rho_phi / rho_crit
                
                # Equation of state
                p_phi = 0.5 * X[idx_today]**2 - V
                w_result = p_phi / rho_phi if rho_phi > 0 else 0
                
                # Field deviation
                phi_deviation = abs(phi[idx_today] - ALPHA)
                
                # Score function - prioritize Ω_φ and w
                score = (abs(Omega_phi_result - OMEGA_PHI_TARGET) * 2.0 +
                         abs(w_result - W_TARGET) +
                         abs(H0_result - H0_TARGET)/H0_TARGET * 0.5)
                
                if score < best_score:
                    best_score = score
                    best_params = (V_scale, lambda_param, phi_initial, X_initial)
                    best_results = (H0_result, Omega_phi_result, w_result, phi[idx_today])
                    
                    print(f"  New best: V={V_scale:,.0f}, λ={lambda_param:.2f}")
                    print(f"    H₀={H0_result:.1f}, Ω_φ={Omega_phi_result:.3f}, w={w_result:.3f}")
                
            except:
                continue
    
    return best_params, best_results

# ==================== MAIN EXECUTION ====================
print("RZS - FINAL PERFECT CALIBRATION")
print("Searching for parameters that give Ω_φ ≈ 0.70 and w ≈ -0.95...")

best_params, best_results = find_optimal_parameters()

if best_params:
    V_scale_opt, lambda_opt, phi_initial_opt, X_initial_opt = best_params
    H0_opt, Omega_phi_opt, w_opt, phi_final_opt = best_results
    
    print("\n" + "="*70)
    print("OPTIMAL PARAMETERS FOUND")
    print("="*70)
    
    print(f"V_scale = {V_scale_opt:,.0f}")
    print(f"lambda = {lambda_opt:.3f}")
    print(f"phi_initial = {phi_initial_opt:.4f}")
    print(f"X_initial = {X_initial_opt:.6f}")
    
    print(f"\nExpected results:")
    print(f"  H₀ ≈ {H0_opt:.1f} km/s/Mpc")
    print(f"  Ω_φ ≈ {Omega_phi_opt:.4f}")
    print(f"  w ≈ {w_opt:.4f}")
    print(f"  φ_final ≈ {phi_final_opt:.4f}")
    
    # ==================== FINAL SIMULATION WITH DETAILED OUTPUT ====================
    print("\n" + "="*70)
    print("FINAL DETAILED SIMULATION")
    print("="*70)
    
    # Run full simulation with optimal parameters
    beta_param = 0.05
    Lambda_RZS = 0.1
    xi0 = 0.01
    
    def V_potential(phi):
        return V_scale_opt * ((lambda_opt/4.0) * (phi**2 - ALPHA**2)**2 + Lambda_RZS)
    
    def dV_dphi(phi):
        return V_scale_opt * lambda_opt * phi * (phi**2 - ALPHA**2)
    
    def F_func(phi):
        return 0.5 + xi0 * (phi/ALPHA)**2
    
    def dF_dphi(phi):
        return 2.0 * xi0 * phi / ALPHA**2
    
    def equations(N, y):
        phi, X = y
        rho_m = OMEGA_M_TARGET * np.exp(-3*N) * (H0_TARGET**2)
        
        V = V_potential(phi)
        dV = dV_dphi(phi)
        F = F_func(phi)
        dF = dF_dphi(phi)
        
        # Hubble parameter
        A = 3.0 * F
        B = 3.0 * dF * X
        C = -(rho_m + 0.5*X**2 + V)
        disc = B**2 - 4.0*A*C
        
        if disc < 0:
            H = 1e-5
        else:
            H = (-B + np.sqrt(disc)) / (2.0*A)
            if H <= 0:
                H = 1e-5
        
        damping_factor = 1.0 / (1.0 + 0.1 * abs(X))
        
        rho_phi = 0.5 * X**2 + V
        w_phi = (0.5 * X**2 - V) / rho_phi if rho_phi > 0 else -1.0
        H_dot_approx = -1.5 * H**2 * (1 + w_phi)
        
        dX_dt = (-3.0 * H * X * damping_factor - dV +
                 3.0 * (2.0 * H**2 + H_dot_approx) * dF +
                 beta_param * rho_m)
        
        max_velocity = 100.0
        if abs(dX_dt) > max_velocity:
            dX_dt = np.sign(dX_dt) * max_velocity
        
        dphi_dN = X / H if H > 1e-6 else 0.0
        dX_dN = dX_dt / H if H > 1e-6 else 0.0
        
        return [dphi_dN, dX_dN]
    
    print("\nRunning final simulation...")
    N_eval = np.linspace(-3.0, 0.0, 2000)
    sol = solve_ivp(equations, [-3.0, 0.0], [phi_initial_opt, X_initial_opt],
                   method='RK45', t_eval=N_eval, rtol=1e-8, atol=1e-10,
                   max_step=0.001)
    
    if sol.success:
        print("✅ Final simulation successful!")
        
        # Process results
        N = sol.t
        phi = sol.y[0]
        X = sol.y[1]
        z = np.exp(-N) - 1
        
        # Calculate all quantities
        H_vals = []
        Omega_phi_vals = []
        w_phi_vals = []
        Geff_vals = []
        
        for i in range(len(N)):
            rho_m = OMEGA_M_TARGET * np.exp(-3*N[i]) * (H0_TARGET**2)
            V = V_potential(phi[i])
            F = F_func(phi[i])
            dF = dF_dphi(phi[i])
            
            A = 3.0 * F
            B = 3.0 * dF * X[i]
            C = -(rho_m + 0.5*X[i]**2 + V)
            disc = B**2 - 4.0*A*C
            
            if disc >= 0:
                H = (-B + np.sqrt(disc)) / (2.0*A)
            else:
                H = 1e-5
            
            H_vals.append(H)
            
            rho_phi = 0.5 * X[i]**2 + V
            total_energy = rho_m + rho_phi
            Omega_phi_vals.append(rho_phi / total_energy if total_energy > 0 else 0)
            
            p_phi = 0.5 * X[i]**2 - V
            w_phi_vals.append(p_phi / rho_phi if rho_phi > 0 else 0)
            
            xi = xi0 * (phi[i]/ALPHA)**2
            Geff_vals.append(1.0 / (1.0 + 2.0 * xi))
        
        H_vals = np.array(H_vals)
        Omega_phi_vals = np.array(Omega_phi_vals)
        w_phi_vals = np.array(w_phi_vals)
        Geff_vals = np.array(Geff_vals)
        
        # Today's values
        idx_today = np.argmin(np.abs(z))
        H0_result = H_vals[idx_today]
        phi_today = phi[idx_today]
        X_today = X[idx_today]
        Omega_phi_today = Omega_phi_vals[idx_today]
        Omega_m_today = 1 - Omega_phi_today
        w_phi_today = w_phi_vals[idx_today]
        V_today = V_potential(phi_today)
        Geff_today = Geff_vals[idx_today]
        
        # Correct densities
        rho_crit_actual = 3.0 * (H0_result**2)
        rho_m_actual = OMEGA_M_TARGET * (H0_TARGET**2) * (H0_result/H0_TARGET)**2
        rho_phi_actual = 0.5 * X_today**2 + V_today
        
        Omega_m_corrected = rho_m_actual / rho_crit_actual
        Omega_phi_corrected = rho_phi_actual / rho_crit_actual
        
        print("\n" + "="*70)
        print("FINAL PERFECT RESULTS")
        print("="*70)
        
        print(f"H0 = {H0_result:.2f} km/s/Mpc")
        print(f"Omega_phi = {Omega_phi_corrected:.4f} (raw: {Omega_phi_today:.4f})")
        print(f"Omega_m = {Omega_m_corrected:.4f} (raw: {Omega_m_today:.4f})")
        print(f"w_phi = {w_phi_today:.4f}")
        print(f"phi = {phi_today:.4f} (alpha = {ALPHA}, Δ = {abs(phi_today-ALPHA):.4f})")
        print(f"dphi/dt = {X_today:.2e}")
        print(f"G_eff/G = {Geff_today:.4f}")
        print(f"V(phi) = {V_today:.1f}")
        
        print(f"\nKey ratios:")
        print(f"  H0/H0_target = {H0_result/H0_TARGET:.3f}")
        print(f"  Omega_phi/Omega_phi_target = {Omega_phi_corrected/OMEGA_PHI_TARGET:.3f}")
        print(f"  w/w_target = {w_phi_today/W_TARGET:.3f}")
        
        # Final assessment
        print("\n" + "="*70)
        print("FINAL ASSESSMENT")
        print("="*70)
        
        criteria_met = 0
        
        if 72.0 <= H0_result <= 74.0:
            print(f"✅ H0 = {H0_result:.1f} km/s/Mpc (SH0ES range: 72-74)")
            criteria_met += 1
        else:
            print(f"❌ H0 = {H0_result:.1f} (outside SH0ES range)")
        
        if 0.68 <= Omega_phi_corrected <= 0.72:
            print(f"✅ Ω_φ = {Omega_phi_corrected:.4f} (Planck range: 0.68-0.72)")
            criteria_met += 1
        else:
            print(f"❌ Ω_φ = {Omega_phi_corrected:.4f} (outside range)")
        
        if -1.00 <= w_phi_today <= -0.90:
            print(f"✅ w = {w_phi_today:.4f} (acceptable range: -1.00 to -0.90)")
            criteria_met += 1
        else:
            print(f"❌ w = {w_phi_today:.4f} (outside range)")
        
        if abs(phi_today - ALPHA) < 0.1:
            print(f"✅ φ stabilized: Δ = {abs(phi_today-ALPHA):.4f} < 0.1")
            criteria_met += 1
        else:
            print(f"❌ φ not stabilized: Δ = {abs(phi_today-ALPHA):.4f}")
        
        print(f"\nCriteria met: {criteria_met}/4")
        
        if criteria_met == 4:
            print("\n" + "="*70)
            print("🎯 RZS MODEL PERFECTLY CALIBRATED! 🎯")
            print("="*70)
            print("The model successfully reproduces:")
            print("  • Hubble constant from SH0ES")
            print("  • Dark energy density from Planck")
            print("  • Equation of state from cosmological constraints")
            print("  • Field stabilization at critical value")
        elif criteria_met >= 3:
            print("\n✅ RZS MODEL WELL CALIBRATED")
            print("   Minor adjustments could improve it further")
        else:
            print("\n⚠️  RZS MODEL PARTIALLY CALIBRATED")
            print("   Some parameters need adjustment")
        
        # ==================== PLOTS ====================
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # Plot 1: Field evolution
        axes[0,0].plot(z, phi, 'b-', linewidth=2)
        axes[0,0].axhline(y=ALPHA, color='r', linestyle='--', label=f'α={ALPHA}')
        axes[0,0].set_xlabel('Redshift (z)')
        axes[0,0].set_ylabel('Φ(z)')
        axes[0,0].set_title('Latency Field Evolution')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].set_xlim(0, min(10, max(z)))
        axes[0,0].set_ylim(ALPHA*0.95, ALPHA*1.05)
        
        # Plot 2: Field velocity
        axes[0,1].plot(z, X, 'r-', linewidth=2)
        axes[0,1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axes[0,1].set_xlabel('z')
        axes[0,1].set_ylabel('dΦ/dt')
        axes[0,1].set_title('Field Velocity')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].set_xlim(0, min(10, max(z)))
        
        # Plot 3: Hubble parameter
        H_ratio = H_vals / H0_result
        axes[0,2].plot(z, H_ratio, 'g-', linewidth=2, label=f'RZS (H₀={H0_result:.1f})')
        z_theory = np.linspace(0, min(10, max(z)), 100)
        H_lcdm = np.sqrt(OMEGA_M_TARGET*(1+z_theory)**3 + OMEGA_PHI_TARGET)
        axes[0,2].plot(z_theory, H_lcdm, 'k--', label='ΛCDM (H₀=73.0)')
        axes[0,2].set_xlabel('z')
        axes[0,2].set_ylabel('H(z)/H₀')
        axes[0,2].set_title('Hubble Parameter Evolution')
        axes[0,2].legend()
        axes[0,2].grid(True, alpha=0.3)
        axes[0,2].set_xlim(0, min(10, max(z)))
        
        # Plot 4: Density parameters
        axes[1,0].plot(z, Omega_phi_vals, 'r-', linewidth=2, label='Ω_φ (RZS)')
        axes[1,0].plot(z, 1-Omega_phi_vals, 'b-', linewidth=2, label='Ω_m')
        axes[1,0].axhline(y=0.7, color='r', linestyle='--', alpha=0.5)
        axes[1,0].axhline(y=0.3, color='b', linestyle='--', alpha=0.5)
        axes[1,0].set_xlabel('z')
        axes[1,0].set_ylabel('Density Parameter')
        axes[1,0].set_title('Density Evolution')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].set_xlim(0, min(10, max(z)))
        
        # Plot 5: Equation of state
        axes[1,1].plot(z, w_phi_vals, 'purple', linewidth=2)
        axes[1,1].axhline(y=-0.95, color='k', linestyle='--', label='w=-0.95 (target)')
        axes[1,1].axhline(y=-1.03, color='r', linestyle=':', alpha=0.7, label='Planck bounds')
        axes[1,1].axhline(y=-0.97, color='r', linestyle=':', alpha=0.7)
        axes[1,1].fill_between(z, -1.06, -1.00, alpha=0.2, color='green', label='Acceptable')
        axes[1,1].set_xlabel('z')
        axes[1,1].set_ylabel('w_φ(z)')
        axes[1,1].set_title('Equation of State Evolution')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].set_xlim(0, min(10, max(z)))
        axes[1,1].set_ylim(-1.1, -0.8)
        
        # Plot 6: Potential shape
        phi_range = np.linspace(ALPHA*0.8, ALPHA*1.2, 200)
        V_vals = V_potential(phi_range)
        axes[1,2].plot(phi_range, V_vals, 'orange', linewidth=2)
        axes[1,2].axvline(x=ALPHA, color='r', linestyle='--', label=f'α={ALPHA}')
        axes[1,2].scatter([phi_today], [V_today], color='red', s=100, label='Today')
        axes[1,2].set_xlabel('Φ')
        axes[1,2].set_ylabel('V(Φ)')
        axes[1,2].set_title(f'Potential (V_scale={V_scale_opt:,.0f}, λ={lambda_opt:.2f})')
        axes[1,2].legend()
        axes[1,2].grid(True, alpha=0.3)
        
        plt.suptitle(f'RZS Perfect Calibration: H₀={H0_result:.1f}, Ω_φ={Omega_phi_corrected:.3f}, w={w_phi_today:.3f}', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('rzs_perfect_calibration.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # ==================== EXPORT ====================
        data = np.column_stack((z, phi, X, H_vals, Omega_phi_vals, w_phi_vals, Geff_vals))
        header = f"""# RZS Perfect Calibration
# Parameters: alpha=1.5, beta=0.05, lambda={lambda_opt:.3f}, V_scale={V_scale_opt}, xi0=0.01
# phi_initial={phi_initial_opt}, X_initial={X_initial_opt}
# Results: H0={H0_result:.2f}, Omega_phi={Omega_phi_corrected:.4f}, w={w_phi_today:.4f}
# z, phi, X(dphi/dt), H, Omega_phi, w_phi, Geff_over_G"""
        
        np.savetxt('rzs_perfect_calibration.csv', data, delimiter=',', header=header, fmt='%.6f')
        
        print(f"\n💾 Data saved to 'rzs_perfect_calibration.csv'")
        print(f"📈 Plot saved to 'rzs_perfect_calibration.png'")
        
        # ==================== SUMMARY ====================
        print("\n" + "="*70)
        print("RZS MODEL - FINAL SUMMARY")
        print("="*70)
        print(f"Parameter values from optimization:")
        print(f"  • V_scale = {V_scale_opt:,.0f}")
        print(f"  • λ = {lambda_opt:.3f}")
        print(f"  • α = {ALPHA} (fixed)")
        print(f"  • β = {beta_param} (fixed)")
        print(f"  • ξ₀ = {xi0} (fixed)")
        print(f"  • Λ_RZS = {Lambda_RZS} (fixed)")
        
        print(f"\nCosmological results:")
        print(f"  • Hubble constant: H₀ = {H0_result:.1f} km/s/Mpc")
        print(f"  • Dark energy density: Ω_φ = {Omega_phi_corrected:.4f}")
        print(f"  • Matter density: Ω_m = {Omega_m_corrected:.4f}")
        print(f"  • Equation of state: w = {w_phi_today:.4f}")
        print(f"  • Field value today: Φ = {phi_today:.4f}")
        
        print(f"\nPhysical interpretation:")
        print(f"  • Potential energy scale: V_scale = {V_scale_opt:,.0f}")
        print(f"  • Potential curvature: λ = {lambda_opt:.3f}")
        print(f"  • Field stabilization: Φ → α within {abs(phi_today-ALPHA):.3f}")
        print(f"  • Effective gravitational constant: G_eff/G = {Geff_today:.4f}")
        
    else:
        print("Final simulation failed!")
else:
    print("Could not find optimal parameters!")

print("\n" + "="*70)
print("FINAL CALIBRATION COMPLETE")
print("="*70)