#!/usr/bin/env python3
"""
Test fuzzy matching for location names with spelling errors
"""

def test_fuzzy_match():
    """Test the fuzzy matching logic"""
    reference_locations = {
        "street gardens": [-35.36088387, 149.16674193],
        "desert square": [-35.36309804, 149.16348567],
        "alexander center area": [-35.37111574, 149.17183885],
        "village area": [-35.35723482, 149.17015126],
        "compound area": [-35.35389604, 149.15062472],
        "south sector area": [-35.363261, 149.165230]
    }
    
    # Test cases with spelling errors
    test_cases = [
        "deserrt square",      # Missing 'e', double 'r'
        "desert sqare",        # Missing 'u'
        "desrt square",        # Missing 'e'
        "street garden",       # Singular instead of plural
        "streeet gardens",     # Extra 'e'
        "alexander center",    # Missing "area"
        "village",             # Just the first word
        "compond area",        # Missing 'u'
        "south sector",        # Missing "area"
    ]
    
    print("🧪 Testing Fuzzy Location Matching")
    print("=" * 60)
    
    def char_similarity(s1, s2):
        """Calculate character-level similarity between two strings"""
        s1_chars = set(s1)
        s2_chars = set(s2)
        if not s1_chars or not s2_chars:
            return 0
        common = s1_chars & s2_chars
        return len(common) / max(len(s1_chars), len(s2_chars))
    
    for test_input in test_cases:
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
                # Try matching against full name and individual words
                score1 = char_similarity(ref_location_clean, k)
                # Also check if key words are present (for "desert square" variations)
                ref_words = ref_location_clean.split()
                k_words = k.split()
                word_scores = []
                for rw in ref_words:
                    for kw in k_words:
                        word_scores.append(char_similarity(rw, kw))
                score2 = max(word_scores) if word_scores else 0
                score = max(score1, score2)
                
                if score > best_score and score > 0.6:  # At least 60% character similarity
                    best_score = score
                    best_match = k
            
            if best_match:
                ref_key = best_match
                print(f"✅ '{test_input}' → '{best_match}' (fuzzy similarity: {best_score:.2f})")
            else:
                print(f"❌ '{test_input}' → No match found")
        else:
            print(f"✅ '{test_input}' → '{ref_key}' (exact substring)")
    
    print("=" * 60)

if __name__ == "__main__":
    test_fuzzy_match()
