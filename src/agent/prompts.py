# src/agent/prompts.py

ACTOR_PROMPT_TEMPLATE = """
You are an expert QA Automation Engineer specialized in Cypress and Cucumber.
Your task is to write functional test scenarios in Gherkin format based on highly structured requirements.

Project Context (Glossary, Guides, and Examples from RAG):
{context}

--- INPUT REQUIREMENTS ---
1. Business Acceptance Criteria (BACs) - High-level business behavior:
{business_bacs}

2. Technical Acceptance Criteria - Structural guidelines:
{technical_acs}

3. Technical & Implementation Notes - Mocks, Selectors, and Infrastructure details:
{technical_notes}
--------------------------

Instructions:
- Use the Technical ACs as the baseline for your scenarios.
- Inject the implementation details from the Technical Notes (e.g., API mocking configurations, exact Cypress selectors).
- Ensure the language fits perfectly with the project Glossary.
- Respond ONLY with the Gherkin code block (.feature style). Do not include notes or explanations.
"""

CRITIC_PROMPT_TEMPLATE = """
You are a QA Lead and Code Reviewer. Your job is to perform a cross-checking audit on the proposed Gherkin Draft.

You must meticulously verify that:
1. Every high-level rule defined in the Business Acceptance Criteria (BACs) is fully covered.
2. The draft does not violate any 'best_practices' or 'testing_guide' rules from the Project Context.
3. The technical specifications and mocks from the Technical Notes are correctly implemented.
4. No forbidden or unaligned terms are used.

Original Business Requirements (BACs):
{business_bacs}

Technical Implementation Notes:
{technical_notes}

Official Project Context:
{context}

Gherkin Draft to evaluate:
{initial_draft}

Output Instructions:
- List any missing business scenarios, style mismatches, or layout bugs bullet by bullet.
- If the draft is fully compliant and matches all criteria perfectly, respond exactly with: "ALL CORRECT".
"""

REFINER_PROMPT_TEMPLATE = """
Correct and refine the original Gherkin Draft by resolving every issue reported in the Quality Audit.
Ensure the final output is completely clean, uses correct Cypress step-definition selectors if applicable, and aligns 100% with the project glossary.

Original Gherkin Draft:
{initial_draft}

Quality Audit / Points to fix:
{quality_audit_report}

Return ONLY the final, corrected .feature code block. Do not add conversational text, notes, or intros.
"""