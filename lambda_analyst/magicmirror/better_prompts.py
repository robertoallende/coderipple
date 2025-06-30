"""
Smart Project Type Detection for CodeRipple
Automatically detects project type and applies specialized prompts.
"""

import json
from typing import Dict, List, Optional


class ProjectTypeDetector:
    """Detects project type based on files and generates specialized prompts"""

    def __init__(self):
        self.detection_rules = {
            # Web Frameworks - Frontend
            'react': {
                'files': ['package.json', 'src/App.js', 'src/App.tsx', 'public/index.html'],
                'content_patterns': ['"react":', 'import React', 'ReactDOM.render'],
                'wow_factor': 'React component architecture and hook patterns'
            },
            'vue': {
                'files': ['package.json', 'src/main.js', 'vue.config.js'],
                'content_patterns': ['"vue":', 'createApp', '<template>'],
                'wow_factor': 'Vue composition API and component lifecycle'
            },
            'angular': {
                'files': ['package.json', 'angular.json', 'src/app/', 'src/main.ts'],
                'content_patterns': ['"@angular/', 'ng serve', 'Component', '@Component'],
                'wow_factor': 'Angular services, dependency injection, and TypeScript integration'
            },
            'svelte': {
                'files': ['package.json', 'src/App.svelte', 'svelte.config.js'],
                'content_patterns': ['"svelte":', '<script>', 'export let', '$:'],
                'wow_factor': 'Svelte compile-time optimization and reactive declarations'
            },
            'nextjs': {
                'files': ['next.config.js', 'pages/', 'app/', 'package.json'],
                'content_patterns': ['"next":', 'export default function', 'getStaticProps'],
                'wow_factor': 'Next.js routing and SSR/SSG patterns'
            },

            # Backend Frameworks - Node.js
            'express': {
                'files': ['package.json', 'server.js', 'app.js'],
                'content_patterns': ['"express":', 'app.get(', 'app.listen'],
                'wow_factor': 'Express middleware and routing patterns'
            },

            # Backend Frameworks - Python
            'django': {
                'files': ['manage.py', 'settings.py', 'requirements.txt', 'models.py'],
                'content_patterns': ['django', 'INSTALLED_APPS', 'class.*Model'],
                'wow_factor': 'Django models, views, and URL patterns'
            },
            'fastapi': {
                'files': ['main.py', 'requirements.txt'],
                'content_patterns': ['from fastapi', '@app.get', 'FastAPI()'],
                'wow_factor': 'FastAPI automatic API docs and type hints'
            },
            'flask': {
                'files': ['app.py', 'requirements.txt'],
                'content_patterns': ['from flask', '@app.route', 'Flask(__name__)'],
                'wow_factor': 'Flask blueprint organization and routing'
            },

            # Backend Frameworks - Java
            'spring_boot': {
                'files': ['pom.xml', 'build.gradle', 'src/main/java/', 'application.properties'],
                'content_patterns': ['spring-boot-starter', '@SpringBootApplication', '@RestController'],
                'wow_factor': 'Spring Boot auto-configuration and enterprise patterns'
            },

            # Backend Frameworks - C#
            'dotnet': {
                'files': ['*.csproj', 'Program.cs', 'Startup.cs', 'appsettings.json'],
                'content_patterns': ['Microsoft.AspNetCore', 'WebApplication', '[ApiController]'],
                'wow_factor': '.NET dependency injection and minimal APIs'
            },

            # Mobile
            'react_native': {
                'files': ['package.json', 'App.js', 'android/', 'ios/'],
                'content_patterns': ['"react-native":', 'import.*react-native'],
                'wow_factor': 'React Native navigation and native module integration'
            },
            'flutter': {
                'files': ['pubspec.yaml', 'lib/main.dart', 'android/', 'ios/'],
                'content_patterns': ['flutter:', 'Widget', 'StatelessWidget'],
                'wow_factor': 'Flutter widget tree and state management'
            },

            # Systems Programming
            'rust_project': {
                'files': ['Cargo.toml', 'src/main.rs', 'src/lib.rs'],
                'content_patterns': ['[dependencies]', 'fn main()', 'use std::'],
                'wow_factor': 'Rust ownership system and memory safety'
            },
            'go_project': {
                'files': ['go.mod', 'main.go', '*.go'],
                'content_patterns': ['module ', 'func main()', 'package main'],
                'wow_factor': 'Go concurrency with goroutines and channels'
            },
            'c_project': {
                'files': ['Makefile', '*.c', '*.h'],
                'content_patterns': ['#include', 'int main(', 'gcc'],
                'wow_factor': 'C manual memory management and system programming'
            },

            # Data Science / ML
            'jupyter': {
                'files': ['*.ipynb', 'requirements.txt'],
                'content_patterns': ['import pandas', 'import numpy', 'matplotlib'],
                'wow_factor': 'Jupyter notebook data analysis workflow'
            },
            'ml_project': {
                'files': ['model.py', 'train.py', 'requirements.txt'],
                'content_patterns': ['import torch', 'import tensorflow', 'sklearn'],
                'wow_factor': 'ML model training and inference pipeline'
            },

            # Infrastructure
            'docker': {
                'files': ['Dockerfile', 'docker-compose.yml'],
                'content_patterns': ['FROM ', 'RUN ', 'services:'],
                'wow_factor': 'Container orchestration and deployment strategy'
            },
            'kubernetes': {
                'files': ['*.yaml', 'k8s/', 'manifests/'],
                'content_patterns': ['apiVersion:', 'kind: Deployment', 'kind: Service'],
                'wow_factor': 'Kubernetes resource management and scaling'
            },

            # Package Management
            'homebrew_formula': {
                'files': ['*.rb', 'Formula/'],
                'content_patterns': ['class ', 'def install', 'homebrew'],
                'wow_factor': 'Homebrew package management and formula development'
            },
            'npm_library': {
                'files': ['package.json', 'index.js', 'src/'],
                'content_patterns': ['"main":', '"module":', 'export '],
                'wow_factor': 'NPM package structure and distribution'
            },
            'python_package': {
                'files': ['setup.py', '__init__.py', 'pyproject.toml'],
                'content_patterns': ['from setuptools', '__version__', 'import'],
                'wow_factor': 'Python package structure and distribution'
            }
        }

    def detect_project_type(self, file_list: List[str], file_contents: Dict[str, str]) -> Optional[str]:
        """Detect project type based on files and content"""
        scores = {}

        for project_type, rules in self.detection_rules.items():
            score = 0

            # Check for required files
            for file_pattern in rules['files']:
                if any(file_pattern in f for f in file_list):
                    score += 2

            # Check content patterns
            for content_pattern in rules['content_patterns']:
                for file_content in file_contents.values():
                    if content_pattern.lower() in file_content.lower():
                        score += 1
                        break

            if score > 0:
                scores[project_type] = score

        # Return the highest scoring project type
        return max(scores, key=scores.get) if scores else None

    def generate_specialized_prompt(self, project_type: str) -> str:
        """Generate a specialized getting started prompt based on project type"""

        base_prompt = """You are a developer onboarding expert specializing in {framework} projects.

**Your Mission:**
Help new developers get this {framework} project running quickly with minimal friction.

**Framework-Specific Focus:**
{specific_focus}

**Analysis Workflow:**
1. Start with execution_time_status() to understand time constraints
2. Use git_repo_stats() to get project overview
3. Use find_key_files() to locate {key_files}
4. Focus on {framework}-specific setup requirements
5. Highlight {wow_factor}

**Documentation Focus:**
Generate a "Getting Started" section covering:

**Project Overview:**
- What does this {framework} project do?
- Key {framework} features being used

**Prerequisites:**
- {framework} version requirements
- {specific_dependencies}
- Development tools needed

**Installation & Setup:**
- Clone and dependency installation
- {framework}-specific configuration
- Environment setup
- {specific_setup_steps}

**Quick Start:**
- How to run in development mode
- {framework}-specific commands
- How to verify everything works
- Key {framework} concepts demonstrated

**{Framework} Specific Sections:**
{framework_sections}

Remember: Focus on {framework} best practices and help developers understand the {wow_factor}."""

        # Framework-specific customizations
        customizations = {
            'react': {
                'framework': 'React',
                'specific_focus': 'React component architecture, hooks, and modern development patterns',
                'key_files': 'package.json, src/App.js, public/index.html',
                'specific_dependencies': 'Node.js version, React DevTools browser extension',
                'specific_setup_steps': 'npm/yarn installation, development server startup',
                'wow_factor': 'component reusability and hook patterns',
                'framework_sections': '''**Component Structure:**
- Main App component and routing
- Key components and their purposes
- Hook usage patterns

**Development Workflow:**
- Hot reloading and development experience
- Building for production
- Common React patterns used'''
            },

            'django': {
                'framework': 'Django',
                'specific_focus': 'Django models, views, templates, and URL routing',
                'key_files': 'manage.py, settings.py, models.py, urls.py',
                'specific_dependencies': 'Python version, database requirements',
                'specific_setup_steps': 'virtual environment, database migrations, static files',
                'wow_factor': 'Django admin interface and ORM capabilities',
                'framework_sections': '''**Django Structure:**
- Apps and their purposes
- Model relationships and database schema
- URL routing and view patterns

**Django Features:**
- Admin interface setup
- Database migrations
- Template organization'''
            },

            'fastapi': {
                'framework': 'FastAPI',
                'specific_focus': 'FastAPI automatic API documentation and type hints',
                'key_files': 'main.py, requirements.txt, routers/',
                'specific_dependencies': 'Python version, uvicorn server',
                'specific_setup_steps': 'virtual environment, uvicorn server startup',
                'wow_factor': 'automatic interactive API docs at /docs',
                'framework_sections': '''**API Structure:**
- Router organization and endpoints
- Request/response models with Pydantic
- Dependency injection patterns

**FastAPI Features:**
- Interactive API docs (/docs and /redoc)
- Type hints and validation
- Authentication setup'''
            },

            'nextjs': {
                'framework': 'Next.js',
                'specific_focus': 'Next.js file-based routing, SSR/SSG, and optimization features',
                'key_files': 'next.config.js, pages/ or app/, package.json',
                'specific_dependencies': 'Node.js version, Next.js version',
                'specific_setup_steps': 'npm install, development server with next dev',
                'wow_factor': 'automatic code splitting and file-based routing',
                'framework_sections': '''**Next.js Features:**
- File-based routing system
- SSR/SSG pages and data fetching
- API routes and middleware

**Performance Features:**
- Automatic code splitting
- Image optimization
- Built-in CSS support'''
            }
        }

        # Get customization or use generic template
        custom = customizations.get(project_type, {
            'framework': project_type.title(),
            'specific_focus': f'{project_type} specific development patterns',
            'key_files': 'configuration and main files',
            'specific_dependencies': 'Required runtime and tools',
            'specific_setup_steps': 'Standard installation and configuration',
            'wow_factor': f'{project_type} specific features',
            'framework_sections': f'**{project_type.title()} Specific Setup:**\n- Framework-specific considerations'
        })

        return base_prompt.format(**custom)


def enhance_coderipple_analysis(file_list: List[str], file_contents: Dict[str, str]) -> Dict:
    """
    Enhanced CodeRipple analysis with project type detection

    Returns:
        Dict with detected project type and specialized prompt
    """
    detector = ProjectTypeDetector()

    # Detect project type
    project_type = detector.detect_project_type(file_list, file_contents)

    if project_type:
        # Generate specialized prompt
        specialized_prompt = detector.generate_specialized_prompt(project_type)

        return {
            'project_type': project_type,
            'specialized_prompt': specialized_prompt,
            'wow_factor': detector.detection_rules[project_type]['wow_factor'],
            'analysis_focus': f"Specialized {project_type} analysis with framework-specific insights"
        }
    else:
        # Fall back to generic analysis
        return {
            'project_type': 'generic',
            'specialized_prompt': None,
            'wow_factor': 'comprehensive project analysis',
            'analysis_focus': "General project analysis"
        }