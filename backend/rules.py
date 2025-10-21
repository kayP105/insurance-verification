# from durable.lang import ruleset, when_all, m,post

# @ruleset
# def insurance_workflow(c):
#     # Rule 1: Auto-Reject
#     @when_all((m.verification_status == "REJECT") | (m.policy_is_active == False))
#     def auto_reject(c):
#         c.s.decision = "REJECT"
#         c.s.reason = f"Policy verification failed: {c.m.verification_reason}"
#         print(f"Rule: AUTO-REJECT triggered for {c.m.policy_no}")

#     # Rule 2: Manual Review (High Fraud/Anomaly)
#     @when_all(m.verification_status != "REJECT", m.fraud_risk_score > 0.75)
#     def manual_review_fraud(c):
#         c.s.decision = "MANUAL_REVIEW"
#         c.s.reason = "High fraud risk score detected."
#         print(f"Rule: MANUAL_REVIEW (FRAUD) triggered for {c.m.policy_no}")

#     # Rule 3: Manual Review (Eligibility Model)
#     @when_all(m.verification_status != "REJECT", m.is_eligible == False)
#     def manual_review_eligibility(c):
#         c.s.decision = "MANUAL_REVIEW"
#         c.s.reason = f"Eligibility model flagged as ineligible (Prob: {c.m.ineligible_prob:.2f})."
#         print(f"Rule: MANUAL_REVIEW (ELIGIBILITY) triggered for {c.m.policy_no}")

#     # Rule 4: Manual Review (Coverage/Name Flags)
#     @when_all(m.verification_status == "MANUAL_REVIEW")
#     def manual_review_flags(c):
#         c.s.decision = "MANUAL_REVIEW"
#         c.s.reason = f"Policy flags raised: {c.m.verification_reason}"
#         print(f"Rule: MANUAL_REVIEW (FLAGS) triggered for {c.m.policy_no}")

#     # Rule 5: Auto-Approve (Default)
#     @when_all(m.decision == None) # If no other rule has set a decision
#     def auto_approve(c):
#         c.s.decision = "AUTO_APPROVE"
#         c.s.reason = "All checks passed."
#         print(f"Rule: AUTO-APPROVE triggered for {c.m.policy_no}")



# rules.py
from durable.lang import ruleset, when_all, m

# Register the ruleset
with ruleset('insurance_workflow'):

    # Rule 1: Auto-Reject
    @when_all((m.verification_status == "REJECT") | (m.policy_is_active == False))
    def auto_reject(c):
        # --- ADD PRINT ---
        print("DEBUG: Rule 'auto_reject' FIRED!")
        c.s.decision = "REJECT"
        c.s.reason = f"Policy verification failed: {getattr(c.m, 'verification_reason', 'N/A')}"

    # Rule 2: Manual Review — high fraud risk
    @when_all((m.verification_status != "REJECT") & (m.fraud_risk_score > 0.75))
    def manual_review_fraud(c):
        # --- ADD PRINT ---
        print("DEBUG: Rule 'manual_review_fraud' FIRED!")
        c.s.decision = "MANUAL_REVIEW"
        c.s.reason = "High fraud risk score detected."

    # Rule 3: Manual Review — failed eligibility
    @when_all((m.verification_status != "REJECT") & (m.is_eligible == False))
    def manual_review_eligibility(c):
        # --- ADD PRINT ---
        print("DEBUG: Rule 'manual_review_eligibility' FIRED!")
        c.s.decision = "MANUAL_REVIEW"
        c.s.reason = f"Eligibility model flagged as ineligible (Prob: {getattr(c.m, 'ineligible_prob', 0):.2f})."

    # Rule 4: Manual Review — flags from verification
    @when_all(m.verification_status == "MANUAL_REVIEW")
    def manual_review_flags(c):
        # --- ADD PRINT ---
        print("DEBUG: Rule 'manual_review_flags' FIRED!")
        c.s.decision = "MANUAL_REVIEW"
        c.s.reason = f"Policy flags raised: {getattr(c.m, 'verification_reason', 'Unknown reason')}"

    # Rule 5: Auto-Approve — no issues found
    @when_all(m.decision == None)
    def auto_approve(c):
        # --- ADD PRINT ---
        print("DEBUG: Rule 'auto_approve' FIRED!")
        c.s.decision = "AUTO_APPROVE"
        c.s.reason = "All checks passed."