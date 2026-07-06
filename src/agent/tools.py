import os

class GherkinTools:
    @staticmethod
    def syntax_linter(gherkin_text: str) -> dict:
        """
        Tool: Inspects a Gherkin string to validate basic syntax structure.
        Returns a dictionary with status and found issues.
        """
        print("🛠️  [Tool - Linter] Inspecting Gherkin syntax structure...")
        issues = []
        
        # Basic keyword checks
        if "Feature:" not in gherkin_text:
            issues.append("Missing 'Feature:' keyword at the top of the file.")
        if "Scenario:" not in gherkin_text and "Scenario Outline:" not in gherkin_text:
            issues.append("Missing at least one 'Scenario:' or 'Scenario Outline:'.")
            
        # Check for standard step keywords
        has_given = "Given " in gherkin_text
        has_when = "When " in gherkin_text
        has_then = "Then " in gherkin_text
        
        if not (has_given or has_when or has_then):
            issues.append("The feature draft does not contain standard steps (Given/When/Then).")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "summary": "ALL PASSED" if len(issues) == 0 else f"Found {len(issues)} syntax anomalies."
        }

    @staticmethod
    def read_reference_feature(base_dir: str, file_name: str) -> str:
        """
        Tool: Inspects and reads a complete real .feature file from disk 
        for deep style alignment when RAG chunks are not enough.
        """
        print(f"🛠️  [Tool - Inspector] Inspecting full file content for: {file_name}")
        target_path = os.path.join(base_dir, "data", "existing_features", file_name)
        
        if not os.path.exists(target_path):
            return f"Error: File {file_name} not found in repository templates."
            
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"