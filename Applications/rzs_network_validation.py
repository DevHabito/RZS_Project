"""
RZS Network Engineering Framework - Minimum Viable Product (MVP)
Author: Felipe Romero
Year: 2026
Description: Implementation of the Relational Zero State (RZS) hypothesis in 
             communication networks, featuring LZc biomarkers, dissipative 
             thermodynamics, and the Axiom of Inheritance.
"""

import math
import time
import random
import matplotlib.pyplot as plt
import numpy as np

# --- 1. CORE RZS ALGORITHMS ---

def calculate_lzc(binary_string):
    """
    Calculates Lempel-Ziv Complexity (LZc) to measure informational health.
    Reference: Lempel, A., & Ziv, J. (1976).
    """
    n = len(binary_string)
    if n == 0: return 0
    c, l, i, k, k_max = 1, 1, 0, 1, 1
    while l + k <= n:
        if binary_string[i + k - 1] == binary_string[l + k - 1]:
            k += 1
        else:
            k_max = max(k, k_max)
            i += 1
            if i == l:
                c += 1
                l += k_max
                if l + 1 > n: break
                i, k, k_max = 0, 1, 1
            else:
                k = 1
    # Normalized LZc: (c * log2(n)) / n
    return (c * math.log2(n)) / n

class RZSNode:
    def __init__(self, node_id, rho_c=5000, alpha=1.0, beta=0.1):
        self.node_id = node_id
        self.rho_c = rho_c  # Critical point as defined in the paper
        self.alpha = alpha  # Stability coefficient
        self.beta = beta    # Coupling coefficient
        self.latency = 0.01 # T_latency (Operational temperature analogue)
        self.throughput = 100.0 # dQ_traffic (Energy/Flow analogue)
        self.is_active = True
        self.neighbors = []
        self.inheritance_vault = {} # Decentralized Shared Zero State

    def calculate_entropy_variation(self):
        """
        Calculates the relative entropy variation proxy.
        Formula: (throughput / latency) - rho_c
        This tracks the distance to the critical thermodynamic point.
        """
        return (self.throughput / self.latency) - self.rho_c

    def get_phase_functional(self):
        """
        Calculates Psi(rho) - The free-energy-like functional governing state stability.
        Psi(rho) = alpha * (rho - rho_c) + beta * phi^2
        """
        rho = self.throughput / self.latency
        phi = rho # Order parameter
        psi = self.alpha * (rho - self.rho_c) + self.beta * (phi**2)
        return psi

    def diagnose(self, stream):
        """
        Node health diagnosis based on Table 1 of the RZS Network paper.
        """
        lzc = calculate_lzc(stream)
        if lzc > 0.7:
            return lzc, "Noise Attack", "Stochastic Filtering"
        elif 0.3 <= lzc <= 0.7:
            return lzc, "Healthy Homeostasis", "Stable"
        else:
            return lzc, "Rigidity/Bottleneck", "Phase Transition"

    def generate_relational_hash(self):
        """Generates a probabilistic sketch for the Axiom of Inheritance."""
        state_data = f"{self.node_id}-{self.latency}-{self.throughput}"
        return hash(state_data)

# --- 2. NETWORK DYNAMICS ---

class RZSMeshNetwork:
    def __init__(self):
        self.nodes = {}
        self.history = []

    def add_node(self, node):
        self.nodes[node.node_id] = node

    def create_mesh(self):
        """Interconnects nodes in a basic mesh topology."""
        ids = list(self.nodes.keys())
        for i in range(len(ids)):
            self.nodes[ids[i]].neighbors.append(ids[(i+1)%len(ids)])
            self.nodes[ids[i]].neighbors.append(ids[(i-1)%len(ids)])

    def sync_inheritance(self):
        """Implements the Axiom of Inheritance via neighbor synchronization."""
        for nid, node in self.nodes.items():
            if node.is_active:
                h = node.generate_relational_hash()
                for neighbor_id in node.neighbors:
                    self.nodes[neighbor_id].inheritance_vault[nid] = h

    def run_simulation(self, steps=30):
        print(">>> Starting RZS Dynamic Stress Test...")
        for i in range(steps):
            target = self.nodes["Node-0"]
            
            # --- Dynamic Stream Generation (Realistic Stress) ---
            if i < 10:
                # Healthy traffic
                stream = "".join(random.choice("01") for _ in range(200))
            elif i < 20:
                # High Entropy / Noise Attack
                stream = "".join(random.choice("01") for _ in range(500))
                target.latency += 0.02 # Heating up
            else:
                # Low Entropy / Rigidity (Repetitive)
                stream = "10" * 100
                target.latency += 0.1 # Severe thermal stress
            
            # Monitoring
            lzc, state, action = target.diagnose(stream)
            psi = target.get_phase_functional()
            ds = target.calculate_entropy_variation()
            
            self.history.append({
                "step": i,
                "latency": target.latency,
                "psi": psi,
                "lzc": lzc,
                "ds": ds,
                "state": state
            })
            
            if psi < 0 or action == "Phase Transition":
                print(f"Step {i}: [{state}] - COLLAPSE IMMINENT. Triggering Inheritance.")
                self.recover("Node-0")
                # After recovery, we stop for visualization
                break

    def recover(self, node_id):
        start_t = time.time()
        node = self.nodes[node_id]
        recovered = False
        
        # Hash acts as relational identity, not payload reconstruction
        for nid in node.neighbors:
            if node_id in self.nodes[nid].inheritance_vault:
                h = self.nodes[nid].inheritance_vault[node_id]
                node.latency = 0.01 # Reconstitution of gradient flow
                recovered = True
                break
        
        rec_time_ms = (time.time() - start_t) * 1000
        print(f"Recovery via Hash [{h}]: SUCCESS={recovered} | Time: {rec_time_ms:.4f}ms")

    def generate_analytics(self):
        steps = [h['step'] for h in self.history]
        psi_vals = [h['psi'] for h in self.history]
        lzc_vals = [h['lzc'] for h in self.history]
        ds_vals = [h['ds'] for h in self.history]
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        
        # Stability Functional
        ax1.plot(steps, psi_vals, 'b-o', label='Psi (Stability)')
        ax1.axhline(0, color='red', linestyle='--', label='Critical Threshold')
        ax1.set_title('Thermodynamic Stability Functional (Psi)')
        ax1.set_ylabel('Energy Functional')
        ax1.legend()
        
        # LZc Biomarker
        ax2.plot(steps, lzc_vals, 'g-s', label='LZc (Integrity)')
        ax2.axhline(0.7, color='purple', linestyle='--', label='Noise Threshold')
        ax2.axhline(0.3, color='orange', linestyle='--', label='Rigidity Threshold')
        ax2.set_title('LZc Biomarker Health Monitoring')
        ax2.set_ylabel('Complexity Value')
        ax2.legend()
        
        # Entropy Variation
        ax3.plot(steps, ds_vals, 'r-^', label='Delta S (Entropy Proxy)')
        ax3.set_title('Relative Entropy Variation')
        ax3.set_ylabel('Delta S')
        ax3.set_xlabel('Simulation Step')
        ax3.legend()
        
        plt.tight_layout()
        plt.savefig('rzs_mvp_analytics.png')
        print("\n[SUCCESS] RZS Analytics Report saved as 'rzs_mvp_analytics.png'")

# --- 3. MAIN EXECUTION ---

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("RZS NETWORK ENGINEERING MVP - Felipe Romero (2026)")
    print("--------------------------------------------------")
    
    # Initialization
    network = RZSMeshNetwork()
    for i in range(5):
        network.add_node(RZSNode(f"Node-{i}", rho_c=4000))
    
    network.create_mesh()
    network.sync_inheritance()
    
    # Simulation
    network.run_simulation()
    
    # Data Visualization
    network.generate_analytics()