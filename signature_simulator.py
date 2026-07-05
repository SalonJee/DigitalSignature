"""
Digital Signature Simulator — RSA & ElGamal
=============================================
Interactive Streamlit app companion to the "Digital Signatures: Number-Theoretic
Foundations and Applications" report/presentation.

Run with:
    streamlit run signature_simulator.py
"""

import random
import math
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="Digital Signature Simulator", page_icon="🔐", layout="wide")

# ----------------------------------------------------------------------------
# Number theory helpers
# ----------------------------------------------------------------------------

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def small_primes(limit=200):
    return [n for n in range(11, limit) if is_prime(n)]


def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m


def modpow_with_steps(base, exp, mod):
    """Repeated-squaring modular exponentiation, recording every step."""
    steps = []
    result = 1
    b = base % mod
    e = exp
    i = 0
    while e > 0:
        if e & 1:
            result = (result * b) % mod
        steps.append({
            "step": i,
            "exp_bit": e & 1,
            "base_squared": b,
            "running_result": result,
        })
        b = (b * b) % mod
        e >>= 1
        i += 1
    return result, steps


def find_valid_e(phi):
    for e in [17, 3, 5, 7, 11, 13, 19, 23, 29, 31]:
        if e < phi and math.gcd(e, phi) == 1:
            return e
    e = 3
    while math.gcd(e, phi) != 1:
        e += 2
    return e


def find_generator(p):
    """Find a generator of Z_p* by trial (fine for small demo primes)."""
    order = p - 1
    factors = set()
    n = order
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.add(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.add(n)
    for g in range(2, p):
        if all(pow(g, order // f, p) != 1 for f in factors):
            return g
    return 2


# ----------------------------------------------------------------------------
# Visualization helper: "modular clock" showing exponentiation trajectory
# ----------------------------------------------------------------------------

def draw_modular_clock(mod, trajectory, highlight_labels, title):
    fig, ax = plt.subplots(figsize=(4.2, 4.2), subplot_kw={"aspect": "equal"})
    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color="#444", lw=1)

    n_points = min(mod, 60)  # cap tick marks for readability
    for k in range(n_points):
        angle = 2 * np.pi * k / n_points
        ax.plot(np.cos(angle) * 1.0, np.sin(angle) * 1.0, ".", color="#ccc", ms=2)

    cmap = plt.cm.viridis(np.linspace(0, 1, len(trajectory)))
    for idx, val in enumerate(trajectory):
        angle = 2 * np.pi * (val % mod) / mod
        x, y = np.cos(angle), np.sin(angle)
        ax.plot(x, y, "o", color=cmap[idx], ms=10, zorder=3)
        if idx < len(highlight_labels):
            ax.annotate(highlight_labels[idx], (x, y), textcoords="offset points",
                        xytext=(6, 6), fontsize=8, color="white")

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.axis("off")
    ax.set_title(title, color="white", fontsize=11)
    fig.patch.set_facecolor("#0f1220")
    ax.set_facecolor("#0f1220")
    return fig


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------

for key, default in [
    ("rsa_keys", None),
    ("rsa_sig", None),
    ("eg_keys", None),
    ("eg_sig", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------

st.title("🔐 Digital Signature Simulator")
st.caption("Companion tool for *Digital Signatures: Number-Theoretic Foundations and Applications*")

tab_rsa, tab_elgamal, tab_theory = st.tabs(
    ["🔑 RSA Signatures", "🔒 ElGamal Signatures", "📘 Theory Cheat-Sheet"]
)

# =============================================================================
# RSA TAB
# =============================================================================
with tab_rsa:
    st.subheader("1 · Key Generation")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        p = st.number_input("Prime p", min_value=5, value=61, step=1, key="rsa_p")
    with col2:
        q = st.number_input("Prime q", min_value=5, value=53, step=1, key="rsa_q")
    with col3:
        st.write("")
        st.write("")
        random_btn = st.button("🎲 Random small primes")

    if random_btn:
        primes = small_primes(120)
        pp, qq = random.sample(primes, 2)
        st.session_state["rsa_p"] = pp
        st.session_state["rsa_q"] = qq
        st.rerun()

    gen_btn = st.button("Generate RSA Keys", type="primary")

    if gen_btn or st.session_state["rsa_keys"] is None:
        if not is_prime(p) or not is_prime(q):
            st.error("Both p and q must be prime.")
        elif p == q:
            st.error("p and q must be different primes.")
        else:
            n = p * q
            phi = (p - 1) * (q - 1)
            e = find_valid_e(phi)
            d = modinv(e, phi)
            st.session_state["rsa_keys"] = dict(p=p, q=q, n=n, phi=phi, e=e, d=d)
            st.session_state["rsa_sig"] = None

    keys = st.session_state["rsa_keys"]
    if keys:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("n = p·q", keys["n"])
        c2.metric("φ(n)", keys["phi"])
        c3.metric("public e", keys["e"])
        c4.metric("private d", keys["d"])
        st.info(f"**Public key:** (n={keys['n']}, e={keys['e']})  |  **Private key:** d={keys['d']}")

        st.divider()
        st.subheader("2 · Sign a Message")
        m = st.number_input(f"Message m  (0 ≤ m < {keys['n']})", min_value=0,
                             max_value=keys["n"] - 1, value=min(65, keys["n"] - 1), key="rsa_m")

        if st.button("✍️ Sign message"):
            sigma, steps = modpow_with_steps(m, keys["d"], keys["n"])
            st.session_state["rsa_sig"] = dict(m=m, sigma=sigma, steps=steps)

        if st.session_state["rsa_sig"]:
            sig_data = st.session_state["rsa_sig"]
            st.success(f"σ = {sig_data['m']}^{keys['d']} mod {keys['n']} = **{sig_data['sigma']}**")

            with st.expander("Show repeated-squaring steps"):
                df = pd.DataFrame(sig_data["steps"])
                st.dataframe(df, use_container_width=True)

            fig = draw_modular_clock(
                keys["n"],
                [s["running_result"] for s in sig_data["steps"]],
                [f"r{s['step']}" for s in sig_data["steps"]],
                "Signing trajectory on Z_n (running result mod n)",
            )
            st.pyplot(fig, use_container_width=False)

        st.divider()
        st.subheader("3 · Verify a Signature")
        vcol1, vcol2 = st.columns(2)
        default_m = st.session_state["rsa_sig"]["m"] if st.session_state["rsa_sig"] else m
        default_sig = st.session_state["rsa_sig"]["sigma"] if st.session_state["rsa_sig"] else 0
        with vcol1:
            v_m = st.number_input("Message m'", min_value=0, value=int(default_m), key="rsa_vm")
        with vcol2:
            v_sig = st.number_input("Signature σ", min_value=0, value=int(default_sig), key="rsa_vsig")

        vb1, vb2 = st.columns(2)
        verify_clicked = vb1.button("✅ Verify")
        tamper_clicked = vb2.button("⚠️ Tamper message (+1) & re-verify")

        if tamper_clicked:
            st.session_state["rsa_vm"] = v_m + 1
            st.rerun()

        if verify_clicked or tamper_clicked:
            check, vsteps = modpow_with_steps(v_sig, keys["e"], keys["n"])
            if check == v_m:
                st.success(f"✓ VALID — σ^e mod n = {check} = m. Signature authentic.")
            else:
                st.error(f"✗ INVALID — σ^e mod n = {check} ≠ {v_m}. Signature rejected!")

            with st.expander("Show verification steps"):
                st.dataframe(pd.DataFrame(vsteps), use_container_width=True)

# =============================================================================
# ELGAMAL TAB
# =============================================================================
with tab_elgamal:
    st.subheader("1 · Domain & Key Setup")
    col1, col2 = st.columns([1, 1])
    with col1:
        eg_p = st.number_input("Prime p", min_value=7, value=467, step=1, key="eg_p")
    with col2:
        random_p_btn = st.button("🎲 Random small prime p")

    if random_p_btn:
        candidates = [n for n in small_primes(600) if n > 100]
        st.session_state["eg_p"] = random.choice(candidates)
        st.rerun()

    if st.button("Generate ElGamal Keys", type="primary") or st.session_state["eg_keys"] is None:
        if not is_prime(eg_p):
            st.error("p must be prime.")
        else:
            g = find_generator(eg_p)
            x = random.randint(2, eg_p - 2)
            y = pow(g, x, eg_p)
            st.session_state["eg_keys"] = dict(p=eg_p, g=g, x=x, y=y)
            st.session_state["eg_sig"] = None

    ekeys = st.session_state["eg_keys"]
    if ekeys:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("prime p", ekeys["p"])
        c2.metric("generator g", ekeys["g"])
        c3.metric("private x", ekeys["x"])
        c4.metric("public y = g^x mod p", ekeys["y"])

        st.divider()
        st.subheader("2 · Sign a Message")
        eg_m = st.number_input(f"Message m (0 ≤ m < {ekeys['p']-1})", min_value=0,
                                max_value=ekeys["p"] - 2, value=42, key="eg_m")

        if st.button("✍️ Sign with ElGamal"):
            p_, g_, x_ = ekeys["p"], ekeys["g"], ekeys["x"]
            while True:
                k = random.randint(2, p_ - 2)
                if math.gcd(k, p_ - 1) == 1:
                    break
            r = pow(g_, k, p_)
            k_inv = modinv(k, p_ - 1)
            s = ((eg_m - x_ * r) * k_inv) % (p_ - 1)
            st.session_state["eg_sig"] = dict(m=eg_m, r=r, s=s, k=k)

        if st.session_state["eg_sig"]:
            sd = st.session_state["eg_sig"]
            st.success(f"Signature (r, s) = ({sd['r']}, {sd['s']})   [ephemeral k = {sd['k']}, kept secret]")

        st.divider()
        st.subheader("3 · Verify")
        default_m = st.session_state["eg_sig"]["m"] if st.session_state["eg_sig"] else eg_m
        default_r = st.session_state["eg_sig"]["r"] if st.session_state["eg_sig"] else 0
        default_s = st.session_state["eg_sig"]["s"] if st.session_state["eg_sig"] else 0

        vc1, vc2, vc3 = st.columns(3)
        with vc1:
            vv_m = st.number_input("m'", min_value=0, value=int(default_m), key="eg_vm")
        with vc2:
            vv_r = st.number_input("r", min_value=0, value=int(default_r), key="eg_vr")
        with vc3:
            vv_s = st.number_input("s", min_value=0, value=int(default_s), key="eg_vs")

        vb1, vb2 = st.columns(2)
        verify_eg = vb1.button("✅ Verify signature", key="eg_verify_btn")
        tamper_eg = vb2.button("⚠️ Tamper message (+1)", key="eg_tamper_btn")

        if tamper_eg:
            st.session_state["eg_vm"] = vv_m + 1
            st.rerun()

        if verify_eg or tamper_eg:
            p_, g_, y_ = ekeys["p"], ekeys["g"], ekeys["y"]
            lhs = pow(g_, vv_m, p_)
            rhs = (pow(y_, vv_r, p_) * pow(vv_r, vv_s, p_)) % p_
            if lhs == rhs:
                st.success(f"✓ VALID — g^m mod p = {lhs} = y^r · r^s mod p. Signature authentic.")
            else:
                st.error(f"✗ INVALID — g^m mod p = {lhs} ≠ y^r · r^s mod p = {rhs}. Rejected!")

# =============================================================================
# THEORY TAB
# =============================================================================
with tab_theory:
    st.subheader("Quick Reference")
    st.markdown(
        """
| | RSA | ElGamal |
|---|---|---|
| Hard problem | Integer factorization | Discrete logarithm |
| Sign | σ = m^d mod n | (r,s) with r=g^k, s=(m−xr)k⁻¹ mod (p−1) |
| Verify | σ^e mod n =? m | g^m =? y^r · r^s (mod p) |
| Correctness | Euler: m^φ(n) ≡ 1 (mod n) | order-(p−1) exponent arithmetic |

**Golden rule for ElGamal/DSA/ECDSA:** never reuse the ephemeral secret `k` for two
different messages — reuse leaks the private key `x` via simple linear algebra.

**Why tampering is caught:** changing `m` (or `σ`, or `r,s`) by even one unit breaks the
modular identity that the correctness proof relies on, so verification fails deterministically.
        """
    )

st.divider()
st.caption("Uses small parameters for hand-checkable arithmetic — real systems use "
           "primes hundreds of digits long (RSA) or 256-bit curves (ECDSA).")
