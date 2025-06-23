"""
Existing Content Discovery Tool

Enhances agents' ability to read and understand existing documentation content,
not just discover file names. This enables intelligent content updates rather
than wholesale replacement.

Existing content discovery for intelligent documentation updates.
"""

import os
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import hashlib

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

try:
    from .config import get_config, get_output_dir
except ImportError:
    def get_output_dir():
        return "coderipple"


@dataclass
class DocumentationSection:
    """Represents a section within a documentation file"""
    title: str
    content: str
    section_type: str  # 'heading', 'code_block', 'list', 'paragraph'
    line_start: int
    line_end: int
    subsections: List['DocumentationSection'] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class DocumentationFile:
    """Represents a complete documentation file with parsed content"""
    file_path: str
    file_name: str
    category: str  # 'user', 'system', 'decisions'
    title: str
    summary: str
    sections: List[DocumentationSection]
    topics_covered: List[str]
    apis_mentioned: List[str]
    cross_references: List[str]
    last_modified: str
    content_hash: str
    word_count: int
    completeness_score: float  # 0-1 scale


@dataclass
class DocumentationGap:
    """Represents a gap between existing docs and actual code"""
    gap_type: str  # 'missing_api', 'outdated_info', 'missing_section', 'broken_reference'
    description: str
    severity: str  # 'critical', 'important', 'minor'
    suggested_action: str
    related_code_entities: List[str]
    related_files: List[str]


@dataclass
class DocumentationState:
    """Complete state of existing documentation"""
    files: List[DocumentationFile]
    coverage_by_category: Dict[str, float]
    gaps: List[DocumentationGap]
    cross_reference_integrity: float
    overall_completeness: float
    topics_documented: Set[str]
    topics_missing: Set[str]


class ExistingContentAnalyzer:
    """Analyzes existing documentation content for comprehensive understanding"""
    
    def __init__(self, docs_directory: str = None, source_analysis: Dict[str, Any] = None):
        if docs_directory is None:
            docs_directory = get_output_dir()
        self.docs_directory = Path(docs_directory)
        self.source_analysis = source_analysis or {}
        
    def analyze_existing_documentation(self) -> DocumentationState:
        """
        Perform comprehensive analysis of existing documentation
        
        Returns:
            DocumentationState with complete understanding of current docs
        """
        # Discover and parse all documentation files
        doc_files = self._discover_documentation_files()
        parsed_files = []
        
        for file_path in doc_files:
            parsed_file = self._parse_documentation_file(file_path)
            if parsed_file:
                parsed_files.append(parsed_file)
        
        # Analyze coverage and gaps
        coverage = self._analyze_coverage(parsed_files)
        gaps = self._identify_gaps(parsed_files)
        cross_ref_integrity = self._check_cross_reference_integrity(parsed_files)
        
        # Determine topics
        topics_documented = self._extract_documented_topics(parsed_files)
        topics_missing = self._identify_missing_topics(topics_documented)
        
        # Calculate overall completeness
        overall_completeness = self._calculate_overall_completeness(coverage, gaps, cross_ref_integrity)
        
        return DocumentationState(
            files=parsed_files,
            coverage_by_category=coverage,
            gaps=gaps,
            cross_reference_integrity=cross_ref_integrity,
            overall_completeness=overall_completeness,
            topics_documented=topics_documented,
            topics_missing=topics_missing
        )
    
    def _discover_documentation_files(self) -> List[Path]:
        """Discover all documentation files"""
        if not self.docs_directory.exists():
            return []
        
        doc_files = []
        
        # Look for markdown files
        for file_path in self.docs_directory.rglob("*.md"):
            if not file_path.name.startswith('.'):
                doc_files.append(file_path)
        
        return doc_files
    
    def _parse_documentation_file(self, file_path: Path) -> Optional[DocumentationFile]:
        """Parse a documentation file into structured content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return None
            
            # Extract basic metadata
            file_name = file_path.name
            category = self._categorize_file(file_path)
            title = self._extract_title(content)
            summary = self._generate_summary(content)
            
            # Parse content structure
            sections = self._parse_sections(content)
            
            # Extract semantic information
            topics_covered = self._extract_topics(content, sections)
            apis_mentioned = self._extract_api_mentions(content)
            cross_references = self._extract_cross_references(content)
            
            # Calculate metrics
            word_count = len(content.split())
            content_hash = hashlib.md5(content.encode()).hexdigest()
            completeness_score = self._calculate_completeness_score(content, sections)
            
            # Get modification time
            last_modified = os.path.getmtime(file_path)
            from datetime import datetime
            last_modified_str = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S")
            
            return DocumentationFile(
                file_path=str(file_path),
                file_name=file_name,
                category=category,
                title=title,
                summary=summary,
                sections=sections,
                topics_covered=topics_covered,
                apis_mentioned=apis_mentioned,
                cross_references=cross_references,
                last_modified=last_modified_str,
                content_hash=content_hash,
                word_count=word_count,
                completeness_score=completeness_score
            )
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize documentation file by purpose"""
        path_str = str(file_path).lower()
        
        if 'decision' in path_str:
            return 'decisions'
        elif any(keyword in path_str for keyword in ['system', 'architecture', 'capability']):
            return 'system'
        else:
            return 'user'
    
    def _extract_title(self, content: str) -> str:
        """Extract document title from content"""
        lines = content.split('\n')
        
        # Look for h1 heading
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback to first non-empty line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('*'):
                return line[:50]  # Truncate if too long
        
        return "Untitled Document"
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of the document content"""
        # Remove markdown formatting for summary
        clean_content = re.sub(r'[#*`\[\]()]', '', content)
        
        # Get all paragraphs
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
        
        if len(paragraphs) > 1:
            # Skip title-only first paragraph, use second paragraph
            summary = paragraphs[1] if len(paragraphs[1]) > 20 else paragraphs[0]
        elif paragraphs:
            summary = paragraphs[0]
        else:
            return "No summary available"
        
        # Ensure minimum length for meaningful summary
        if len(summary) < 20 and len(paragraphs) > 1:
            # Combine first two paragraphs
            summary = paragraphs[0] + " " + paragraphs[1]
        
        # Truncate if too long
        if len(summary) > 200:
            summary = summary[:200] + "..."
            
        return summary if len(summary) > 10 else "No detailed summary available"
    
    def _parse_sections(self, content: str) -> List[DocumentationSection]:
        """Parse content into structured sections"""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        line_num = 0
        
        for line in lines:
            line_num += 1
            
            # Check for heading
            if line.strip().startswith('#'):
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    current_section.line_end = line_num - 1
                    sections.append(current_section)
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                title = line.strip()[level:].strip()
                current_section = DocumentationSection(
                    title=title,
                    content="",
                    section_type=f"h{level}",
                    line_start=line_num,
                    line_end=line_num
                )
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            current_section.line_end = line_num
            sections.append(current_section)
        
        return sections
    
    def _extract_topics(self, content: str, sections: List[DocumentationSection]) -> List[str]:
        """Extract main topics covered in the documentation"""
        topics = set()
        
        # Extract from section titles
        for section in sections:
            # Clean and split section titles
            title_words = re.findall(r'\b[a-zA-Z]{3,}\b', section.title.lower())
            topics.update(title_words)
        
        # Extract from content using common patterns
        topic_patterns = [
            r'\b(api|endpoint|function|class|method|feature|component|service|tool)\b',
            r'\b(authentication|authorization|configuration|deployment|installation)\b',
            r'\b(webhook|agent|documentation|validation|integration|analysis)\b',
            r'\b(python|aws|strands|bedrock|boto3|flask|fastapi)\b',
            r'\b(module|package|library|framework|system|architecture)\b'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, content.lower())
            topics.update(matches)
        
        # Also extract general meaningful words from content
        content_words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        # Filter for meaningful technical terms
        meaningful_words = set()
        for word in content_words:
            if word in ['python', 'technology', 'implementation', 'development', 'project', 'system', 'guide', 'documentation', 'installation', 'usage', 'advanced', 'basic']:
                meaningful_words.add(word)
        
        topics.update(meaningful_words)
        
        return list(topics)
    
    def _extract_api_mentions(self, content: str) -> List[str]:
        """Extract API/function mentions from documentation"""
        api_mentions = set()
        
        # Look for inline code first
        inline_code = re.findall(r'`([^`]+)`', content)
        for code in inline_code:
            # Extract function calls
            function_calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
            api_mentions.update(function_calls)
        
        # Look for code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', content, re.MULTILINE | re.DOTALL)
        for block in code_blocks:
            # Extract function calls from code blocks
            function_calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', block)
            api_mentions.update(function_calls)
        
        # Also look for class mentions (ClassName format)
        class_mentions = re.findall(r'\b([A-Z][a-zA-Z0-9_]*)\b', content)
        api_mentions.update(class_mentions)
        
        # Filter out common words that aren't APIs
        common_words = {'This', 'The', 'For', 'With', 'When', 'Where', 'Why', 'How', 'What', 'Which'}
        api_mentions = {api for api in api_mentions if api not in common_words}
        
        return list(api_mentions)
    
    def _extract_cross_references(self, content: str) -> List[str]:
        """Extract cross-references to other documentation"""
        cross_refs = []
        
        # Markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in md_links:
            if url.endswith('.md') or '/' in url:
                cross_refs.append(url)
        
        return cross_refs
    
    def _calculate_completeness_score(self, content: str, sections: List[DocumentationSection]) -> float:
        """Calculate how complete/comprehensive the documentation is"""
        score = 0.0
        
        # Length factor (longer docs tend to be more complete)
        word_count = len(content.split())
        if word_count > 500:
            score += 0.3
        elif word_count > 200:
            score += 0.2
        elif word_count > 50:
            score += 0.1
        
        # Structure factor (well-structured docs are more complete)
        if len(sections) > 3:
            score += 0.2
        elif len(sections) > 1:
            score += 0.1
        
        # Code examples factor
        if '```' in content:
            score += 0.2
        
        # Cross-references factor
        if '[' in content and '](' in content:
            score += 0.1
        
        # Introduction/overview factor
        if any(keyword in content.lower() for keyword in ['overview', 'introduction', 'getting started']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_coverage(self, files: List[DocumentationFile]) -> Dict[str, float]:
        """Analyze documentation coverage by category"""
        coverage = {'user': 0.0, 'system': 0.0, 'decisions': 0.0}
        counts = {'user': 0, 'system': 0, 'decisions': 0}
        
        for file in files:
            coverage[file.category] += file.completeness_score
            counts[file.category] += 1
        
        # Calculate averages
        for category in coverage:
            if counts[category] > 0:
                coverage[category] = coverage[category] / counts[category]
        
        return coverage
    
    def _identify_gaps(self, files: List[DocumentationFile]) -> List[DocumentationGap]:
        """Identify gaps between existing docs and actual code"""
        gaps = []
        
        if not self.source_analysis:
            return gaps
        
        # Check for missing API documentation
        documented_apis = set()
        for file in files:
            documented_apis.update(file.apis_mentioned)
        
        source_apis = set()
        if 'public_api' in self.source_analysis:
            for api in self.source_analysis['public_api']:
                source_apis.add(api['name'])
        
        missing_apis = source_apis - documented_apis
        for api in missing_apis:
            gaps.append(DocumentationGap(
                gap_type='missing_api',
                description=f"API function '{api}' is not documented",
                severity='important',
                suggested_action=f"Add documentation for {api} function",
                related_code_entities=[api],
                related_files=[]
            ))
        
        # Check for missing categories
        existing_categories = {f.category for f in files}
        if 'user' not in existing_categories:
            gaps.append(DocumentationGap(
                gap_type='missing_section',
                description="No user-facing documentation found",
                severity='critical',
                suggested_action="Create getting started and usage documentation",
                related_code_entities=[],
                related_files=[]
            ))
        
        if 'system' not in existing_categories:
            gaps.append(DocumentationGap(
                gap_type='missing_section',
                description="No system architecture documentation found",
                severity='important',
                suggested_action="Create system architecture and design documentation",
                related_code_entities=[],
                related_files=[]
            ))
        
        return gaps
    
    def _check_cross_reference_integrity(self, files: List[DocumentationFile]) -> float:
        """Check integrity of cross-references between docs"""
        total_refs = 0
        valid_refs = 0
        
        file_names = {f.file_name for f in files}
        
        for file in files:
            for ref in file.cross_references:
                total_refs += 1
                
                # Check if referenced file exists
                ref_name = os.path.basename(ref)
                if ref_name in file_names:
                    valid_refs += 1
        
        if total_refs == 0:
            return 1.0  # No refs means no broken refs
        
        return valid_refs / total_refs
    
    def _extract_documented_topics(self, files: List[DocumentationFile]) -> Set[str]:
        """Extract all topics that are currently documented"""
        topics = set()
        
        for file in files:
            topics.update(file.topics_covered)
        
        return topics
    
    def _identify_missing_topics(self, documented_topics: Set[str]) -> Set[str]:
        """Identify topics that should be documented but aren't"""
        missing = set()
        
        if not self.source_analysis:
            return missing
        
        # Topics we should expect based on source analysis
        expected_topics = set()
        
        if 'key_technologies' in self.source_analysis:
            for tech in self.source_analysis['key_technologies']:
                tech_words = tech.lower().split()
                expected_topics.update(tech_words)
        
        if 'main_modules' in self.source_analysis:
            for module in self.source_analysis['main_modules']:
                module_words = re.findall(r'[a-z]+', module.lower())
                expected_topics.update(module_words)
        
        # Find missing topics
        missing = expected_topics - documented_topics
        
        # Filter out too common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        missing = {topic for topic in missing if topic not in common_words and len(topic) > 2}
        
        return missing
    
    def _calculate_overall_completeness(self, coverage: Dict[str, float], gaps: List[DocumentationGap], cross_ref_integrity: float) -> float:
        """Calculate overall documentation completeness score"""
        # Average coverage across categories
        avg_coverage = sum(coverage.values()) / len(coverage) if coverage else 0.0
        
        # Gap penalty
        critical_gaps = len([g for g in gaps if g.severity == 'critical'])
        important_gaps = len([g for g in gaps if g.severity == 'important'])
        gap_penalty = (critical_gaps * 0.3) + (important_gaps * 0.1)
        
        # Combine factors
        completeness = (avg_coverage * 0.6) + (cross_ref_integrity * 0.2) - gap_penalty
        
        return max(0.0, min(1.0, completeness))


@tool
def analyze_existing_content(docs_directory: str = None, source_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze existing documentation content to understand current state and gaps.
    
    This tool enables agents to read and understand existing documentation content,
    not just discover file names. It provides comprehensive understanding of what's
    already documented vs what's missing.
    
    Args:
        docs_directory: Directory containing documentation files
        source_analysis: Optional source code analysis results for gap detection
        
    Returns:
        Dictionary containing comprehensive documentation state including:
        - Parsed content from all documentation files
        - Coverage analysis by category
        - Identified gaps between docs and code
        - Cross-reference integrity
        - Overall completeness assessment
    """
    try:
        analyzer = ExistingContentAnalyzer(docs_directory, source_analysis)
        doc_state = analyzer.analyze_existing_documentation()
        
        # Convert to dictionary for easy consumption by agents
        return {
            'status': 'success',
            'documentation_files': [
                {
                    'file_name': f.file_name,
                    'category': f.category,
                    'title': f.title,
                    'summary': f.summary,
                    'sections': [
                        {
                            'title': s.title,
                            'content': s.content[:200] + "..." if len(s.content) > 200 else s.content,
                            'section_type': s.section_type
                        }
                        for s in f.sections
                    ],
                    'topics_covered': f.topics_covered,
                    'apis_mentioned': f.apis_mentioned,
                    'cross_references': f.cross_references,
                    'last_modified': f.last_modified,
                    'word_count': f.word_count,
                    'completeness_score': f.completeness_score
                }
                for f in doc_state.files
            ],
            'coverage_analysis': {
                'by_category': doc_state.coverage_by_category,
                'overall_completeness': doc_state.overall_completeness,
                'cross_reference_integrity': doc_state.cross_reference_integrity
            },
            'content_gaps': [
                {
                    'type': gap.gap_type,
                    'description': gap.description,
                    'severity': gap.severity,
                    'suggested_action': gap.suggested_action,
                    'related_entities': gap.related_code_entities
                }
                for gap in doc_state.gaps
            ],
            'topics_analysis': {
                'documented': list(doc_state.topics_documented),
                'missing': list(doc_state.topics_missing)
            },
            'summary': f"Found {len(doc_state.files)} documentation files with {doc_state.overall_completeness:.1%} overall completeness. Identified {len(doc_state.gaps)} content gaps.",
            'insights': [
                f"Coverage by category: User ({doc_state.coverage_by_category.get('user', 0):.1%}), System ({doc_state.coverage_by_category.get('system', 0):.1%}), Decisions ({doc_state.coverage_by_category.get('decisions', 0):.1%})",
                f"Cross-reference integrity: {doc_state.cross_reference_integrity:.1%}",
                f"Topics documented: {len(doc_state.topics_documented)}, Missing: {len(doc_state.topics_missing)}"
            ]
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'summary': f"Failed to analyze existing documentation: {str(e)}"
        }


if __name__ == "__main__":
    # Test the tool with source code analysis
    import sys
    sys.path.append('.')
    
    try:
        from source_code_analysis_tool import analyze_source_code
        source_analysis = analyze_source_code(".")
        print("Source analysis loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load source analysis: {e}")
        source_analysis = None
    
    # Test existing content analysis
    result = analyze_existing_content("coderipple", source_analysis)
    
    print("=== Existing Content Discovery Test ===")
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")
    
    if result['status'] == 'success':
        print(f"\nDocumentation Files Found: {len(result['documentation_files'])}")
        for file in result['documentation_files']:
            print(f"  - {file['file_name']} ({file['category']}): {file['word_count']} words, {file['completeness_score']:.1%} complete")
        
        print(f"\nCoverage Analysis:")
        for insight in result['insights']:
            print(f"  • {insight}")
        
        print(f"\nContent Gaps ({len(result['content_gaps'])}):")
        for gap in result['content_gaps'][:5]:  # Show first 5 gaps
            print(f"  • {gap['severity'].upper()}: {gap['description']}")
        
        print(f"\nTopics Analysis:")
        print(f"  Documented ({len(result['topics_analysis']['documented'])}): {', '.join(result['topics_analysis']['documented'][:10])}")
        if result['topics_analysis']['missing']:
            print(f"  Missing ({len(result['topics_analysis']['missing'])}): {', '.join(list(result['topics_analysis']['missing'])[:10])}")