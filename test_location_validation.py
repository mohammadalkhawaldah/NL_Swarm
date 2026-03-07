#!/usr/bin/env python3
"""
Test location validation - reject unrecognized locations
"""

def test_location_validation():
    """Test that unrecognized locations are rejected"""
    
    reference_locations = {
        "street gardens": [-35.36088387, 149.16674193],
        "desert square": [-35.36309804, 149.16348567],
        "alexander center area": [-35.37111574, 149.17183885],
        "village area": [-35.35723482, 149.17015126],
        "compound area": [-35.35389604, 149.15062472],
        "south sector area": [-35.363261, 149.165230]
    }
    
    def char_similarity(s1, s2):
        """Calculate character-level similarity between two strings"""
        s1_chars = set(s1)
        s2_chars = set(s2)
        if not s1_chars or not s2_chars:
            return 0
        common = s1_chars & s2_chars
        return len(common) / max(len(s1_chars), len(s2_chars))
    
    test_cases = [
        # Valid cases (should match)
        ("desert square", True, "desert square"),
        ("deserrt square", True, "desert square"),  # typo but close
        ("street gardens", True, "street gardens"),
        ("village area", True, "village area"),
        
        # Invalid cases (should NOT match)
        ("random park", False, None),
        ("unknown place", False, None),
        ("city center", False, None),
        ("downtown area", False, None),
        ("airport", False, None),
    ]
    
    print("🧪 Testing Location Validation (Reject Unknown Locations)")
    print("=" * 70)
    
    for test_input, should_match, expected_match in test_cases:
        ref_location_clean = test_input.strip().lower()
        ref_key = None
        
        # First try: exact substring match
        for k in reference_locations:
            if ref_location_clean in k or k in ref_location_clean:
                ref_key = k
                break
        
        # Second try: character-level similarity for spelling errors
        if not ref_key:
            best_match = None
            best_score = 0
            for k in reference_locations:
                # Split into words for better matching
                ref_words = ref_location_clean.split()
                k_words = k.split()
                
                # If user input has multiple words, require at least one UNIQUE word match
                # (not common words like "area", "center", "square")
                common_generic_words = {'area', 'square', 'center', 'gardens', 'sector'}
                ref_specific = [w for w in ref_words if w not in common_generic_words]
                k_specific = [w for w in k_words if w not in common_generic_words]
                
                # Calculate word-level similarity
                word_scores = []
                for rw in ref_specific:
                    for kw in k_specific:
                        word_scores.append(char_similarity(rw, kw))
                
                # If there are no specific words, fall back to full string similarity
                if not ref_specific or not k_specific or not word_scores:
                    score = char_similarity(ref_location_clean, k)
                else:
                    score = max(word_scores)
                
                if score > best_score and score > 0.75:  # At least 75% character similarity (stricter)
                    best_score = score
                    best_match = k
            
            if best_match:
                ref_key = best_match
        
        # Check result
        if ref_key:
            if should_match:
                status = "✅ PASS"
                msg = f"Matched to '{ref_key}'"
            else:
                status = "❌ FAIL"
                msg = f"Should NOT match, but matched to '{ref_key}'"
        else:
            if not should_match:
                status = "✅ PASS"
                msg = "Correctly REJECTED (unknown location)"
            else:
                status = "❌ FAIL"
                msg = f"Should match '{expected_match}', but was rejected"
        
        print(f"{status} | '{test_input}' → {msg}")
    
    print("=" * 70)
    print("\n📋 Summary:")
    print("✅ Valid locations (exact or fuzzy match) → Accepted")
    print("❌ Unknown locations (no match) → Rejected with error message")

if __name__ == "__main__":
    test_location_validation()
