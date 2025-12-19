from durable.lang import ruleset, when_all, m

with ruleset('insurance_workflow'):

    @when_all((m.verification_status == "REJECT") | (m.policy_is_active == False))
    def auto_reject(c):
        print("DEBUG: Rule 'auto_reject' FIRED!")
        c.s.decision = "REJECT"
        c.s.reason = f"Policy verification failed: {getattr(c.m, 'verification_reason', 'N/A')}"

    
    @when_all((m.decision == None) & (m.fraud_risk_score > 0.75))
    def manual_review_fraud(c):
        print("DEBUG: Rule 'manual_review_fraud' FIRED!")
        c.s.decision = "MANUAL_REVIEW"
        c.s.reason = "High fraud risk score detected."

    
    @when_all((m.decision == None) & (m.is_eligible == False))
    def manual_review_eligibility(c):
        print("DEBUG: Rule 'manual_review_eligibility' FIRED!")
        c.s.decision = "MANUAL_REVIEW"
        c.s.reason = f"Eligibility model flagged as ineligible (Prob: {getattr(c.m, 'ineligible_prob', 0):.2f})."

   
    @when_all((m.decision == None) & (m.verification_status == "MANUAL_REVIEW"))
    def manual_review_flags(c):
        print("DEBUG: Rule 'manual_review_flags' FIRED!")
        c.s.decision = "MANUAL_REVIEW"
        c.s.reason = f"Policy flags raised: {getattr(c.m, 'verification_reason', 'Unknown reason')}"

    
    @when_all(m.decision == None)
    def auto_approve(c):
        print("DEBUG: Rule 'auto_approve' FIRED!")
        c.s.decision = "AUTO_APPROVE"
        c.s.reason = "All policy and ML checks passed."

    @when_all((m.has_duplicates == True) & (m.decision == None))
    def reject_duplicate(c):
        print("DEBUG: Rule 'reject_duplicate' FIRED!")
        c.s.decision = 'REJECT_DUPLICATE'
        c.s.reason = 'Duplicate claim detected'

