"""
Quality Measurement Alignment Tools for Step 8: Quality Measurement Alignment

This module provides Strands @tool decorated functions that align scoring methodologies
between Bedrock enhancement and validation pipeline systems to prevent conflicts
where enhanced content still fails validation due to misaligned scoring.
"""

import json
import boto3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from strands import tool
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualityAlignment:
    """Result of quality measurement alignment"""
    aligned_bedrock_score: float  # Bedrock score normalized to 0-100 scale
    aligned_validation_score: float  # Validation score with Bedrock context
    alignment_confidence: float  # How confident we are in the alignment
    scoring_methodology: str  # Which methodology was used for alignment
    alignment_notes: List[str]  # Detailed notes about the alignment process


@dataclass
class UnifiedQualityMetrics:
    """Unified quality metrics that work across both systems"""
    overall_score: float  # 0-100 scale
    bedrock_raw_score: float  # Original 0-1 Bedrock score
    validation_raw_score: float  # Original 0-100 validation score
    category_breakdown: Dict[str, float]  # Category scores from validation
    alignment_factor: float  # Adjustment factor applied
    confidence_level: str  # "high", "medium", "low"


@tool
def align_quality_scores(bedrock_result: Dict[str, Any], validation_result: Dict[str, Any], 
                        content: str) -> Dict[str, Any]:
    """
    Align Bedrock enhancement scores with validation pipeline scores to prevent conflicts.
    
    Args:
        bedrock_result: Result from enhance_content_with_bedrock()
        validation_result: Result from validate_documentation_quality_detailed()
        content: The content being scored (for contextual analysis)
    
    Returns:
        Dictionary with aligned scores and methodology explanation
    """
    try:
        # Extract scores from results
        bedrock_score = bedrock_result.get('content', [{}])[0].get('json', {}).get('quality_score', 0.0)
        validation_score = validation_result.get('overall_quality_score', validation_result.get('overall_score', 0.0))
        category_scores = validation_result.get('category_scores', {})
        
        logger.info(f"Aligning scores: Bedrock={bedrock_score:.3f}, Validation={validation_score:.1f}")
        
        # Apply alignment methodology
        alignment_result = _calculate_score_alignment(
            bedrock_score, validation_score, category_scores, content
        )
        
        # Generate unified metrics
        unified_metrics = UnifiedQualityMetrics(
            overall_score=alignment_result.aligned_validation_score,
            bedrock_raw_score=bedrock_score,
            validation_raw_score=validation_score,
            category_breakdown=category_scores,
            alignment_factor=alignment_result.aligned_validation_score / max(validation_score, 1.0),
            confidence_level=_determine_confidence_level(alignment_result.alignment_confidence)
        )
        
        return {
            "status": "success",
            "content": [{
                "json": {
                    "aligned_score": alignment_result.aligned_validation_score,
                    "bedrock_normalized": alignment_result.aligned_bedrock_score,
                    "alignment_confidence": alignment_result.alignment_confidence,
                    "methodology": alignment_result.scoring_methodology,
                    "unified_metrics": {
                        "overall_score": unified_metrics.overall_score,
                        "bedrock_raw": unified_metrics.bedrock_raw_score,
                        "validation_raw": unified_metrics.validation_raw_score,
                        "category_breakdown": unified_metrics.category_breakdown,
                        "alignment_factor": unified_metrics.alignment_factor,
                        "confidence_level": unified_metrics.confidence_level
                    },
                    "alignment_notes": alignment_result.alignment_notes,
                    "recommendation": _generate_score_recommendation(unified_metrics)
                }
            }]
        }
        
    except Exception as e:
        logger.error(f"Quality score alignment failed: {str(e)}")
        return {
            "status": "error",
            "content": [{"text": f"Score alignment failed: {str(e)}"}]
        }


def _calculate_score_alignment(bedrock_score: float, validation_score: float, 
                              category_scores: Dict[str, float], content: str) -> QualityAlignment:
    """Calculate aligned scores using multiple methodologies."""
    
    # Normalize Bedrock score to 0-100 scale
    bedrock_normalized = bedrock_score * 100.0
    
    # Determine best alignment methodology based on score patterns
    methodology, aligned_score, confidence, notes = _select_alignment_methodology(
        bedrock_score, bedrock_normalized, validation_score, category_scores, content
    )
    
    return QualityAlignment(
        aligned_bedrock_score=bedrock_normalized,
        aligned_validation_score=aligned_score,
        alignment_confidence=confidence,
        scoring_methodology=methodology,
        alignment_notes=notes
    )


def _select_alignment_methodology(bedrock_score: float, bedrock_normalized: float, 
                                 validation_score: float, category_scores: Dict[str, float],
                                 content: str) -> Tuple[str, float, float, List[str]]:
    """Select the best alignment methodology based on score patterns."""
    
    notes = []
    score_diff = abs(bedrock_normalized - validation_score)
    
    # Method 1: Close scores - use weighted average
    if score_diff < 15.0:
        methodology = "weighted_average"
        # Weight Bedrock more heavily since it has broader context
        aligned_score = (bedrock_normalized * 0.6) + (validation_score * 0.4)
        confidence = 0.9
        notes.append(f"Scores are close (diff: {score_diff:.1f}), using weighted average")
        
    # Method 2: Large gap with high Bedrock score - trust category analysis
    elif bedrock_normalized > validation_score + 20.0:
        methodology = "category_adjusted"
        # Use category scores to adjust Bedrock confidence
        category_avg = sum(category_scores.values()) / max(len(category_scores), 1)
        adjustment_factor = category_avg / 100.0
        aligned_score = bedrock_normalized * adjustment_factor
        confidence = 0.7
        notes.append(f"Large gap (Bedrock higher), adjusted by category performance: {adjustment_factor:.2f}")
        
    # Method 3: Large gap with high validation score - analyze content objectively
    elif validation_score > bedrock_normalized + 20.0:
        methodology = "content_analysis_adjusted"
        content_factor = _analyze_content_objective_quality(content)
        # Blend validation score with content analysis
        aligned_score = (validation_score * 0.7) + (bedrock_normalized * content_factor * 0.3)
        confidence = 0.6
        notes.append(f"Large gap (Validation higher), content analysis factor: {content_factor:.2f}")
        
    # Method 4: Default - conservative weighted blend
    else:
        methodology = "conservative_blend"
        # Conservative approach - slightly favor the lower score to prevent overconfidence
        lower_score = min(bedrock_normalized, validation_score)
        higher_score = max(bedrock_normalized, validation_score)
        aligned_score = (lower_score * 0.6) + (higher_score * 0.4)
        confidence = 0.5
        notes.append(f"Default conservative blend of scores")
    
    # Ensure aligned score is within reasonable bounds
    aligned_score = max(0.0, min(100.0, aligned_score))
    notes.append(f"Final aligned score: {aligned_score:.1f}")
    
    return methodology, aligned_score, confidence, notes


def _analyze_content_objective_quality(content: str) -> float:
    """Analyze content quality objectively to help with alignment."""
    if not content or not content.strip():
        return 0.0
    
    quality_indicators = 0.0
    max_indicators = 8.0  # Total number of indicators
    
    # 1. Has meaningful length
    if len(content.strip()) > 100:
        quality_indicators += 1.0
    
    # 2. Has proper structure (headers)
    if re.search(r'^#{1,6}\s+', content, re.MULTILINE):
        quality_indicators += 1.0
    
    # 3. Has code examples
    if '```' in content:
        quality_indicators += 1.0
    
    # 4. Has bullet points or lists
    if re.search(r'^\s*[-*+]\s+', content, re.MULTILINE):
        quality_indicators += 1.0
    
    # 5. Has proper sentences (ends with punctuation)
    sentences = re.findall(r'[.!?]\s', content)
    if len(sentences) > 2:
        quality_indicators += 1.0
    
    # 6. Has links or references
    if re.search(r'\[.*\]\(.*\)', content) or 'http' in content:
        quality_indicators += 1.0
    
    # 7. Reasonable paragraph structure
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if len(paragraphs) > 1:
        quality_indicators += 1.0
    
    # 8. No obvious formatting issues
    if not re.search(r'#{7,}|```[^`]*$|^\s*$\n^\s*$', content, re.MULTILINE):
        quality_indicators += 1.0
    
    return quality_indicators / max_indicators


def _determine_confidence_level(confidence_score: float) -> str:
    """Convert confidence score to human-readable level."""
    if confidence_score >= 0.8:
        return "high"
    elif confidence_score >= 0.6:
        return "medium"
    else:
        return "low"


def _generate_score_recommendation(metrics: UnifiedQualityMetrics) -> str:
    """Generate recommendation based on unified metrics."""
    if metrics.overall_score >= 85:
        return "Content quality is excellent. Ready for publication."
    elif metrics.overall_score >= 70:
        return "Content quality is good. Minor improvements may be beneficial."
    elif metrics.overall_score >= 50:
        return "Content quality is acceptable. Consider targeted improvements in lower-scoring categories."
    else:
        return "Content quality needs improvement. Review category breakdown for specific areas to address."


@tool
def calibrate_scoring_systems(content_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calibrate Bedrock and validation scoring systems using sample content.
    
    Args:
        content_samples: List of samples with known quality levels for calibration
                        Each sample should have: content, expected_quality_tier
    
    Returns:
        Dictionary with calibration results and adjustment factors
    """
    try:
        from .bedrock_integration_tools import enhance_content_with_bedrock
        from .content_validation_tools import validate_documentation_quality_detailed
        
        calibration_results = []
        
        for sample in content_samples:
            content = sample.get('content', '')
            expected_tier = sample.get('expected_quality_tier', 'medium')
            
            # Get scores from both systems
            bedrock_result = enhance_content_with_bedrock(content)
            validation_result = validate_documentation_quality_detailed(content)
            
            # Extract scores
            bedrock_score = bedrock_result.get('content', [{}])[0].get('json', {}).get('quality_score', 0.0)
            validation_score = validation_result.get('overall_score', 0.0)
            
            calibration_results.append({
                'content_length': len(content),
                'expected_tier': expected_tier,
                'bedrock_score': bedrock_score,
                'bedrock_normalized': bedrock_score * 100,
                'validation_score': validation_score,
                'score_alignment': align_quality_scores(bedrock_result, validation_result, content)
            })
        
        # Analyze calibration patterns
        patterns = _analyze_calibration_patterns(calibration_results)
        
        return {
            "status": "success",
            "content": [{
                "json": {
                    "calibration_samples": len(content_samples),
                    "patterns": patterns,
                    "recommendations": _generate_calibration_recommendations(patterns),
                    "detailed_results": calibration_results
                }
            }]
        }
        
    except Exception as e:
        logger.error(f"Scoring system calibration failed: {str(e)}")
        return {
            "status": "error",
            "content": [{"text": f"Calibration failed: {str(e)}"}]
        }


def _analyze_calibration_patterns(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze patterns in calibration results."""
    if not results:
        return {}
    
    bedrock_scores = [r['bedrock_normalized'] for r in results]
    validation_scores = [r['validation_score'] for r in results]
    
    return {
        'bedrock_avg': sum(bedrock_scores) / len(bedrock_scores),
        'validation_avg': sum(validation_scores) / len(validation_scores),
        'correlation': _calculate_correlation(bedrock_scores, validation_scores),
        'avg_difference': sum(abs(b - v) for b, v in zip(bedrock_scores, validation_scores)) / len(results),
        'bedrock_tends_higher': sum(1 for b, v in zip(bedrock_scores, validation_scores) if b > v) / len(results)
    }


def _calculate_correlation(x: List[float], y: List[float]) -> float:
    """Calculate simple correlation coefficient."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    sum_y2 = sum(yi * yi for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
    
    return numerator / denominator if denominator != 0 else 0.0


def _generate_calibration_recommendations(patterns: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on calibration patterns."""
    recommendations = []
    
    correlation = patterns.get('correlation', 0)
    if correlation < 0.5:
        recommendations.append("Low correlation between scoring systems - consider methodology review")
    
    bedrock_higher_rate = patterns.get('bedrock_tends_higher', 0.5)
    if bedrock_higher_rate > 0.7:
        recommendations.append("Bedrock consistently scores higher - consider validation criteria adjustment")
    elif bedrock_higher_rate < 0.3:
        recommendations.append("Validation consistently scores higher - consider Bedrock calibration")
    
    avg_diff = patterns.get('avg_difference', 0)
    if avg_diff > 25:
        recommendations.append("Large average score difference - alignment factor may need adjustment")
    
    return recommendations