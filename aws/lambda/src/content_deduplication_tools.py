"""
Content Deduplication Tools for CodeRipple

This module provides intelligent content deduplication capabilities to prevent
the accumulation of duplicate or redundant content in documentation files.
Implements smart content similarity detection, section merging, and cleanup.
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from strands import tool


@dataclass
class ContentSection:
    """Represents a section of content for deduplication analysis"""
    header: str
    content: str
    line_start: int
    line_end: int
    level: int  # Header level (1 for #, 2 for ##, etc.)
    similarity_hash: str


@dataclass
class DuplicationResult:
    """Result of content deduplication analysis"""
    original_sections: int
    deduplicated_sections: int
    removed_duplicates: List[str]
    merged_sections: List[str]
    similarity_threshold: float
    cleaned_content: str


@tool
def deduplicate_content(content: str, similarity_threshold: float = 0.8) -> Dict[str, any]:
    """
    Remove duplicate and highly similar content sections from documentation.
    
    Args:
        content: The markdown content to deduplicate
        similarity_threshold: Threshold for considering content as duplicate (0.0-1.0)
    
    Returns:
        Dictionary with deduplication results and cleaned content
    """
    try:
        # Parse content into sections
        sections = _parse_content_sections(content)
        
        if len(sections) <= 1:
            return {
                "status": "success",
                "content": [{
                    "json": {
                        "deduplicated": False,
                        "reason": "Content has only one section",
                        "original_content": content,
                        "cleaned_content": content,
                        "sections_analyzed": len(sections)
                    }
                }]
            }
        
        # Detect and remove duplicates
        dedup_result = _remove_duplicate_sections(sections, similarity_threshold)
        
        # Reconstruct content from deduplicated sections
        cleaned_content = _reconstruct_content(dedup_result.cleaned_sections)
        
        return {
            "status": "success", 
            "content": [{
                "json": {
                    "deduplicated": True,
                    "original_sections": dedup_result.original_sections,
                    "final_sections": dedup_result.deduplicated_sections,
                    "removed_duplicates": dedup_result.removed_duplicates,
                    "merged_sections": dedup_result.merged_sections,
                    "similarity_threshold": similarity_threshold,
                    "cleaned_content": cleaned_content,
                    "space_saved": len(content) - len(cleaned_content)
                }
            }]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"Content deduplication failed: {str(e)}"}]
        }


def _parse_content_sections(content: str) -> List[ContentSection]:
    """Parse markdown content into logical sections by headers."""
    lines = content.split('\n')
    sections = []
    current_header = ""
    current_content = []
    current_start = 0
    current_level = 0
    
    for i, line in enumerate(lines):
        # Check if this is a markdown header
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        
        if header_match:
            # Save previous section if it exists
            if current_header or current_content:
                section_content = '\n'.join(current_content).strip()
                if section_content:  # Only save non-empty sections
                    sections.append(ContentSection(
                        header=current_header,
                        content=section_content,
                        line_start=current_start,
                        line_end=i-1,
                        level=current_level,
                        similarity_hash=_calculate_content_hash(section_content)
                    ))
            
            # Start new section
            current_header = header_match.group(2).strip()
            current_level = len(header_match.group(1))
            current_content = []
            current_start = i
        else:
            # Add line to current section content
            current_content.append(line)
    
    # Add final section
    if current_header or current_content:
        section_content = '\n'.join(current_content).strip()
        if section_content:
            sections.append(ContentSection(
                header=current_header,
                content=section_content,
                line_start=current_start,
                line_end=len(lines)-1,
                level=current_level,
                similarity_hash=_calculate_content_hash(section_content)
            ))
    
    return sections


def _calculate_content_hash(content: str) -> str:
    """Calculate a similarity hash for content comparison."""
    # Normalize content for comparison
    normalized = re.sub(r'\s+', ' ', content.lower().strip())
    # Remove common markdown formatting for better comparison
    normalized = re.sub(r'[*_`\[\]()]', '', normalized)
    # Remove quality score annotations
    normalized = re.sub(r'>\s*\*\*.*?score.*?\*\*.*', '', normalized, flags=re.IGNORECASE)
    return normalized


@dataclass
class DeduplicationAnalysis:
    """Result of section deduplication analysis"""
    original_sections: int
    deduplicated_sections: int
    removed_duplicates: List[str]
    merged_sections: List[str]
    cleaned_sections: List[ContentSection]


def _remove_duplicate_sections(sections: List[ContentSection], threshold: float) -> DeduplicationAnalysis:
    """Remove duplicate and similar sections from the content."""
    if not sections:
        return DeduplicationAnalysis(0, 0, [], [], [])
    
    cleaned_sections = []
    removed_duplicates = []
    merged_sections = []
    seen_hashes = set()
    
    # Group sections by similarity
    section_groups = _group_similar_sections(sections, threshold)
    
    for group in section_groups:
        if len(group) == 1:
            # Single section, keep as-is
            cleaned_sections.append(group[0])
        else:
            # Multiple similar sections, merge them
            merged_section = _merge_similar_sections(group)
            cleaned_sections.append(merged_section)
            
            # Track what was merged
            merged_headers = [s.header for s in group]
            merged_sections.append(f"Merged: {', '.join(merged_headers)}")
            
            # Track removed duplicates (all but the first)
            for section in group[1:]:
                removed_duplicates.append(section.header)
    
    return DeduplicationAnalysis(
        original_sections=len(sections),
        deduplicated_sections=len(cleaned_sections),
        removed_duplicates=removed_duplicates,
        merged_sections=merged_sections,
        cleaned_sections=cleaned_sections
    )


def _group_similar_sections(sections: List[ContentSection], threshold: float) -> List[List[ContentSection]]:
    """Group sections by content similarity."""
    groups = []
    used_indices = set()
    
    for i, section in enumerate(sections):
        if i in used_indices:
            continue
            
        # Start a new group with this section
        current_group = [section]
        used_indices.add(i)
        
        # Find similar sections
        for j, other_section in enumerate(sections[i+1:], i+1):
            if j in used_indices:
                continue
                
            similarity = _calculate_similarity(section, other_section)
            if similarity >= threshold:
                current_group.append(other_section)
                used_indices.add(j)
        
        groups.append(current_group)
    
    return groups


def _calculate_similarity(section1: ContentSection, section2: ContentSection) -> float:
    """Calculate similarity between two content sections."""
    # Header similarity
    header_similarity = difflib.SequenceMatcher(None, section1.header.lower(), section2.header.lower()).ratio()
    
    # Content similarity  
    content_similarity = difflib.SequenceMatcher(None, section1.similarity_hash, section2.similarity_hash).ratio()
    
    # Weighted combination (content matters more than header)
    return (header_similarity * 0.3) + (content_similarity * 0.7)


def _merge_similar_sections(sections: List[ContentSection]) -> ContentSection:
    """Merge multiple similar sections into one comprehensive section."""
    if len(sections) == 1:
        return sections[0]
    
    # Use the most comprehensive content (longest)
    best_section = max(sections, key=lambda s: len(s.content))
    
    # Use the most common header (or the first one)
    header_counts = {}
    for section in sections:
        header_counts[section.header] = header_counts.get(section.header, 0) + 1
    
    most_common_header = max(header_counts.keys(), key=lambda h: header_counts[h])
    
    # Combine unique content elements
    combined_content = _combine_section_content([s.content for s in sections])
    
    return ContentSection(
        header=most_common_header,
        content=combined_content,
        line_start=min(s.line_start for s in sections),
        line_end=max(s.line_end for s in sections),
        level=best_section.level,
        similarity_hash=_calculate_content_hash(combined_content)
    )


def _combine_section_content(content_list: List[str]) -> str:
    """Intelligently combine content from multiple similar sections."""
    if len(content_list) == 1:
        return content_list[0]
    
    # For now, use the longest content as the authoritative version
    # TODO: Implement smarter content merging in future versions
    return max(content_list, key=len)


def _reconstruct_content(sections: List[ContentSection]) -> str:
    """Reconstruct markdown content from deduplicated sections."""
    if not sections:
        return ""
    
    content_parts = []
    
    for section in sections:
        # Add header
        header_prefix = "#" * section.level
        content_parts.append(f"{header_prefix} {section.header}")
        content_parts.append("")  # Empty line after header
        
        # Add content
        content_parts.append(section.content)
        content_parts.append("")  # Empty line after section
    
    return '\n'.join(content_parts).strip()


@tool  
def analyze_content_duplication(content: str) -> Dict[str, any]:
    """
    Analyze content for potential duplication without modifying it.
    
    Args:
        content: The markdown content to analyze
    
    Returns:
        Dictionary with duplication analysis results
    """
    try:
        sections = _parse_content_sections(content)
        
        # Find potential duplicates
        duplicates = []
        similarities = []
        
        for i, section1 in enumerate(sections):
            for j, section2 in enumerate(sections[i+1:], i+1):
                similarity = _calculate_similarity(section1, section2)
                if similarity > 0.6:  # Lower threshold for analysis
                    similarities.append({
                        "section1": section1.header,
                        "section2": section2.header,
                        "similarity": similarity,
                        "likely_duplicate": similarity > 0.8
                    })
                    
                    if similarity > 0.8:
                        duplicates.append({
                            "original": section1.header,
                            "duplicate": section2.header,
                            "similarity": similarity
                        })
        
        return {
            "status": "success",
            "content": [{
                "json": {
                    "total_sections": len(sections),
                    "potential_duplicates": len(duplicates),
                    "duplicate_pairs": duplicates,
                    "similarity_analysis": similarities,
                    "recommendation": "Run deduplication" if duplicates else "Content appears clean",
                    "estimated_savings": sum(len(s.content) for s in sections[1:] if any(d["duplicate"] == s.header for d in duplicates))
                }
            }]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"Duplication analysis failed: {str(e)}"}]
        }


@tool
def remove_quality_annotations(content: str) -> Dict[str, any]:
    """
    Remove quality score annotations from existing content.
    
    Args:
        content: Content that may contain quality score annotations
        
    Returns:
        Dictionary with cleaned content
    """
    try:
        # Remove quality score annotations
        patterns = [
            r'>\s*\*\*.*?Score:.*?\*\*.*?\n',  # Score annotations
            r'>\s*\*\*.*?Quality.*?Section.*?\*\*.*?\n',  # Quality section annotations
            r'>\s*.*?Quality.*?\(Score:.*?\).*?\n',  # Various quality annotations
        ]
        
        cleaned_content = content
        removed_annotations = 0
        
        for pattern in patterns:
            matches = re.findall(pattern, cleaned_content, re.IGNORECASE | re.DOTALL)
            removed_annotations += len(matches)
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
        
        return {
            "status": "success",
            "content": [{
                "json": {
                    "annotations_removed": removed_annotations,
                    "original_length": len(content),
                    "cleaned_length": len(cleaned_content),
                    "space_saved": len(content) - len(cleaned_content),
                    "cleaned_content": cleaned_content
                }
            }]
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "content": [{"text": f"Annotation removal failed: {str(e)}"}]
        }