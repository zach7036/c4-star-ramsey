r"""Run every verifier in sequence; exit nonzero on the first failure.

Order: fast checks first.  Runtime is typically one to two minutes but varies
with hardware and system load.  Tested environment: Python 3.11.9, sympy 1.13.3,
numpy 2.2.3, networkx 3.6.1, python-sat (CaDiCaL 1.9.5 bindings).
"""
import subprocess, sys, time

STEPS = [
    ("Theorem 1 certificate (all-rational)", "check_certificates.py"),
    ("Theorem 2 + f(83) proposition", "verify_51.py"),
    ("fifth-moment identity on six known graphs", "verify_m5.py"),
    ("Theorem 1 full check incl. SAT encoder audits", "verify.py"),
    ("independent (OpenAI): factored f(39) certificate",
     "verification_independent_openai/verify_ramsey_C4_K1_39.py"),
    ("independent (OpenAI): check of this repo's certificate",
     "verification_independent_openai/verify_pasted_f39_certificate.py"),
    ("independent (OpenAI): all-orders norm scan",
     "verification_independent_openai/verify_ramsey_C4_K1_51_norms.py"),
]

t0 = time.time()
for name, script in STEPS:
    print(f"\n===== {name}  ({script}) =====", flush=True)
    r = subprocess.run([sys.executable, "-u", script])
    if r.returncode != 0:
        print(f"\nFAILED at: {script}", flush=True)
        sys.exit(1)
print(f"\nALL VERIFIERS PASSED  ({time.time()-t0:.0f}s)")
print("Conclusions: R(C4,K_{1,39}) = 46;  R(C4,K_{1,51}) = 59;  R(C4,K_{1,83}) <= 93.")
