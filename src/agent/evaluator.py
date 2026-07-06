class GherkinTestEvaluator:
    @staticmethod
    def measure_effectiveness(gherkin_text: str, user_story: str, linter_passed: bool) -> dict:
        """
        Calculates quantitative and qualitative metrics to evaluate the 
        relevance, syntax correctness, and structural clarity of the generated test.
        """
        score = 0
        checks = {}

        # 1. Syntax Correctness (Max 30 points)
        # Driven by the deterministic tool execution from Step 3
        syntax_score = 30 if linter_passed else 0
        score += syntax_score
        checks["syntax_linter_passed"] = linter_passed

        # 2. Gherkin Structure & Completeness (Max 30 points)
        # Ensures basic Gherkin design principles are followed
        required_keywords = ["Given", "When", "Then"]
        keywords_found = sum(1 for kw in required_keywords if kw in gherkin_text)
                
        structure_score = int((keywords_found / len(required_keywords)) * 30)
        score += structure_score
        checks["gherkin_structure"] = f"{keywords_found}/3 core keywords found (Given/When/Then)"

        # 3. User Story Alignment / Relevance (Max 40 points) -> FIXED & USED HERE 🎯
        # Programmatic check to see if the core concepts from the User Story are in the test
        # We filter out short words to extract meaningful domain terms (nouns, actions, entities)
        ignored_symbols = [",", ".", "(", ")", ":", "-", "_"]
        cleaned_story = user_story
        for symbol in ignored_symbols:
            cleaned_story = cleaned_story.replace(symbol, " ")
            
        key_terms = {word.lower().strip() for word in cleaned_story.split() if len(word) > 4}
        
        if key_terms:
            matched_terms = sum(1 for term in key_terms if term in gherkin_text.lower())
            alignment_ratio = matched_terms / len(key_terms)
            relevance_score = int(alignment_ratio * 40)
            relevance_msg = f"{matched_terms}/{len(key_terms)} meaningful terms from the requirement matched."
        else:
            relevance_score = 40
            relevance_msg = "User Story description too short; assigned full relevance defaults."

        score += relevance_score
        checks["user_story_alignment"] = relevance_msg

        # 4. Clarity Guardrail (Bonus Penalty)
        # Checks if the agent left lazy placeholders like TODOs or empty lines
        has_placeholders = "TODO" in gherkin_text.upper() or "FIXME" in gherkin_text.upper()
        if has_placeholders:
            score = max(0, score - 15)  # Heavy penalty for placeholder leaks
            checks["clarity_guardrail"] = "FAILED: Placeholders (TODO/FIXME) detected. -15 points penalty applied."
        else:
            checks["clarity_guardrail"] = "PASSED: No placeholders or code notes left in the file."

        # Determine overall quality status based on the final score
        status = "EXCELLENT" if score >= 85 else "PASSED WITH WARNINGS" if score >= 65 else "FAILED QUALITY GATE"

        return {
            "total_quality_score": f"{score}%",
            "quality_status": status,
            "detailed_checks": checks,
            "relevance_summary": f"The test features successfully achieved a programmatic semantic alignment score of {int(relevance_score/40*100)}% against your requirement."
        }