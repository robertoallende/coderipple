"""
Smart Project Type Detection for CodeRipple
Automatically detects project type and applies specialized prompts for instant wow factor.
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
                # Backend Frameworks - Java
                              'spring_boot': {
            'files': ['pom.xml', 'build.gradle', 'src/main/java/', 'application.properties'],
            'content_patterns': ['spring-boot-starter', '@SpringBootApplication', '@RestController'],
            'wow_factor': 'Spring Boot auto-configuration and enterprise patterns'
        },

            # Backend Frameworks - PHP
        'laravel': {
            'files': ['composer.json', 'artisan', 'app/', 'routes/web.php'],
            'content_patterns': ['laravel/framework', 'Illuminate', 'Route::'],
            'wow_factor': 'Laravel Eloquent ORM and Artisan commands'
        },

        # Backend Frameworks - C#
        'dotnet': {
            'files': ['*.csproj', 'Program.cs', 'Startup.cs', 'appsettings.json'],
            'content_patterns': ['Microsoft.AspNetCore', 'WebApplication', '[ApiController]'],
            'wow_factor': '.NET dependency injection and minimal APIs'
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
        'vue': {
            'files': ['package.json', 'src/main.js', 'vue.config.js'],
            'content_patterns': ['"vue":', 'createApp', '<template>'],
            'wow_factor': 'Vue composition API and component lifecycle'
        },
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

        # Libraries/Tools
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

    # Example usage function for the Lambda
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
                'specialized_prompt': GETTING_STARTED_PROMPT,  # Your existing prompt
                'wow_factor': 'comprehensive project analysis',
                'analysis_focus': "General project analysis"
            }

    # Integration example for your Lambda B
    def lambda_b_enhanced_handler(event, context):
        """
        Enhanced Lambda B handler with smart project detection
        """
        # Download repo from S3 (your existing code)
        file_list = get_file_list_from_repo()

        # Read key files for content analysis
        file_contents = {}
        key_files = ['package.json', 'requirements.txt', 'manage.py', 'Dockerfile']
        for file in key_files:
            if file in file_list:
                file_contents[file] = read_file_content(file)

        # Enhance analysis with project type detection
        enhanced_analysis = enhance_coderipple_analysis(file_list, file_contents)

        # Use specialized prompt for analysis
        if enhanced_analysis['project_type'] != 'generic':
            print(f"🎯 Detected {enhanced_analysis['project_type']} project!")
            print(f"🌟 Focusing on: {enhanced_analysis['wow_factor']}")

            # Use the specialized prompt instead of generic one
            analysis_result = run_strands_analysis(
                prompt=enhanced_analysis['specialized_prompt'],
                focus=enhanced_analysis['analysis_focus']
            )
        else:
            # Fall back to generic analysis
            analysis_result = run_strands_analysis(prompt=GETTING_STARTED_PROMPT)

        # Rest of your Lambda B logic...
        return analysis_result

        # Framework-specific customizations
        customizations = {
            'c_project': {
                'framework': 'C',
                'specific_focus': 'C compilation, memory management, and system programming',
                'key_files': 'Makefile, *.c, *.h files',
                'specific_dependencies': 'GCC/Clang compiler, build-essential, specific libraries',
                'specific_setup_steps': 'compilation with make, library linking, header includes',
                'wow_factor': 'manual memory management and system-level programming',
                'framework_sections': '''**C Project Structure:**
    - Source files (.c) and header files (.h) organization
    - Makefile build configuration
    - Library dependencies and linking

    **Compilation & Build:**
    - GCC/Clang compilation flags and optimization
    - Static vs dynamic linking
    - Cross-compilation considerations'''
            },

            'gcc_toolchain': {
                'framework': 'GCC Toolchain',
                'specific_focus': 'GNU Compiler Collection build system and cross-compilation',
                'key_files': 'configure, Makefile.in, config.h, source tree',
                'specific_dependencies': 'autotools, automake, autoconf, build dependencies',
                'specific_setup_steps': './configure && make && make install workflow',
                'wow_factor': 'sophisticated build system and compiler optimization',
                'framework_sections': '''**Build System:**
    - Autotools configuration and feature detection
    - Cross-compilation target setup
    - Dependency resolution and library paths

    **Compiler Features:**
    - Optimization levels and target architectures
    - Plugin system and language frontends
    - Debug symbol generation and profiling'''
            },

            'homebrew_formula': {
                'framework': 'Homebrew',
                'specific_focus': 'macOS package management and formula development',
                'key_files': '*.rb formula files, dependency declarations',
                'specific_dependencies': 'Ruby, Homebrew installation, Xcode tools',
                'specific_setup_steps': 'brew install --build-from-source, formula testing',
                'wow_factor': 'declarative package management and dependency resolution',
                'framework_sections': '''**Formula Structure:**
    - Ruby-based package definitions
    - Dependency management and conflicts
    - Installation and testing procedures

    **Homebrew Ecosystem:**
    - Tap management and formula distribution
    - Bottle generation for binary distribution
    - Integration with macOS system frameworks'''
            },

            'python_analysis_tool': {
                'framework': 'Python Analysis Tool',
                'specific_focus': 'Python AST analysis, static analysis, and code intelligence',
                'key_files': 'analysis scripts, AST parsers, CLI interfaces',
                'specific_dependencies': 'Python 3.x, AST module, argparse/click, analysis libraries',
                'specific_setup_steps': 'virtual environment, tool installation, CLI setup',
                'wow_factor': 'code intelligence and automated analysis capabilities',
                'framework_sections': '''**Analysis Architecture:**
    - AST parsing and code traversal patterns
    - Static analysis rules and metrics
    - Report generation and output formats

    **Tool Integration:**
    - CLI interface design and argument parsing
    - Plugin system for extensible analysis
    - Integration with IDEs and CI/CD pipelines'''
            },

            'react': {
                'framework': 'React',
                'specific_focus': 'React component architecture, hooks, and modern development patterns',
                'key_files': 'package.json, src/App.js, components/, hooks/',
                'specific_dependencies': 'Node.js version, React DevTools browser extension',
                'specific_setup_steps': 'npm/yarn installation, development server startup',
                'wow_factor': 'component reusability and hook patterns',
                'framework_sections': '''**Component Architecture:**
    - Functional components and React hooks
    - State management patterns (useState, useReducer, Context)
    - Component composition and prop drilling solutions

    **Development Workflow:**
    - Hot reloading and Fast Refresh
    - Code splitting and lazy loading
    - Testing with React Testing Library'''
            },

            'django': {
                'framework': 'Django',
                'specific_focus': 'Django models, views, templates, and URL routing',
                'key_files': 'manage.py, settings.py, models.py, urls.py, templates/',
                'specific_dependencies': 'Python version, database (PostgreSQL/MySQL), virtual environment',
                'specific_setup_steps': 'virtual environment, pip install, database migrations, collectstatic',
                'wow_factor': 'Django admin interface and ORM capabilities',
                'framework_sections': '''**Django Architecture:**
    - Model-View-Template (MVT) pattern
    - ORM relationships and database migrations
    - URL routing and view-based architecture

    **Django Features:**
    - Admin interface customization
    - Authentication and permissions system
    - Template inheritance and static file handling'''
            },

            'rust_project': {
                'framework': """
    Smart Project Type Detection for CodeRipple
    Automatically detects project type and applies specialized prompts for instant wow factor.
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
                # Backend Frameworks - Java
                              'spring_boot': {
            'files': ['pom.xml', 'build.gradle', 'src/main/java/', 'application.properties'],
            'content_patterns': ['spring-boot-starter', '@SpringBootApplication', '@RestController'],
            'wow_factor': 'Spring Boot auto-configuration and enterprise patterns'
        },

            # Backend Frameworks - PHP
        'laravel': {
            'files': ['composer.json', 'artisan', 'app/', 'routes/web.php'],
            'content_patterns': ['laravel/framework', 'Illuminate', 'Route::'],
            'wow_factor': 'Laravel Eloquent ORM and Artisan commands'
        },

        # Backend Frameworks - C#
        'dotnet': {
            'files': ['*.csproj', 'Program.cs', 'Startup.cs', 'appsettings.json'],
            'content_patterns': ['Microsoft.AspNetCore', 'WebApplication', '[ApiController]'],
            'wow_factor': '.NET dependency injection and minimal APIs'
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
        'vue': {
            'files': ['package.json', 'src/main.js', 'vue.config.js'],
            'content_patterns': ['"vue":', 'createApp', '<template>'],
            'wow_factor': 'Vue composition API and component lifecycle'
        },
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

        # Libraries/Tools
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

    # Example usage function for the Lambda
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
                'specialized_prompt': GETTING_STARTED_PROMPT,  # Your existing prompt
                'wow_factor': 'comprehensive project analysis',
                'analysis_focus': "General project analysis"
            }

    # Integration example for your Lambda B
    def lambda_b_enhanced_handler(event, context):
        """
        Enhanced Lambda B handler with smart project detection
        """
        # Download repo from S3 (your existing code)
        file_list = get_file_list_from_repo()

        # Read key files for content analysis
        file_contents = {}
        key_files = ['package.json', 'requirements.txt', 'manage.py', 'Dockerfile']
        for file in key_files:
            if file in file_list:
                file_contents[file] = read_file_content(file)

        # Enhance analysis with project type detection
        enhanced_analysis = enhance_coderipple_analysis(file_list, file_contents)

        # Use specialized prompt for analysis
        if enhanced_analysis['project_type'] != 'generic':
            print(f"🎯 Detected {enhanced_analysis['project_type']} project!")
            print(f"🌟 Focusing on: {enhanced_analysis['wow_factor']}")

            # Use the specialized prompt instead of generic one
            analysis_result = run_strands_analysis(
                prompt=enhanced_analysis['specialized_prompt'],
                focus=enhanced_analysis['analysis_focus']
            )
        else:
            # Fall back to generic analysis
            analysis_result = run_strands_analysis(prompt=GETTING_STARTED_PROMPT)

        # Rest of your Lambda B logic...
        return analysis_result

        'rust_project': {
            'framework': 'Rust',
            'specific_focus': 'Rust ownership system, memory safety, and performance',
            'key_files': 'Cargo.toml, src/main.rs, src/lib.rs',
            'specific_dependencies': 'Rust toolchain (rustc, cargo), specific crate dependencies',
            'specific_setup_steps': 'cargo build, cargo run, dependency management',
            'wow_factor': 'zero-cost abstractions and memory safety without garbage collection',
            'framework_sections': '''**Rust Concepts:**
    - Ownership, borrowing, and lifetime management
    - Pattern matching and error handling with Result/Option
    - Trait system and generic programming

    **Cargo Ecosystem:**
    - Dependency management and semantic versioning
    - Workspace configuration for multi-crate projects
    - Testing, benchmarking, and documentation generation'''
        },

        'go_project': {
            'framework': 'Go',
            'specific_focus': 'Go concurrency patterns, simplicity, and deployment',
            'key_files': 'go.mod, main.go, package structure',
            'specific_dependencies': 'Go runtime, module dependencies',
            'specific_setup_steps': 'go build, go run, go mod tidy',
            'wow_factor': 'goroutines, channels, and single binary deployment',
            'framework_sections': '''**Go Features:**
    - Goroutines and channel-based concurrency
    - Interface composition and embedding
    - Built-in testing and benchmarking

    **Go Toolchain:**
    - Module system and dependency management
    - Cross-compilation and static linking
    - Profiling and performance analysis tools'''
        },

        'cmake_project': {
            'framework': 'CMake',
            'specific_focus': 'Cross-platform build configuration and dependency management',
            'key_files': 'CMakeLists.txt, cmake/ directory, *.cmake files',
            'specific_dependencies': 'CMake build system, platform-specific compilers',
            'specific_setup_steps': 'mkdir build && cd build && cmake .. && make',
            'wow_factor': 'declarative build configuration and cross-platform compatibility',
            'framework_sections': '''**CMake Build System:**
    - Target-based build configuration
    - Dependency management with find_package
    - Generator expressions and build type handling

    **Cross-Platform Features:**
    - Compiler detection and feature testing
    - Platform-specific configurations
    - Integration with IDEs and build tools'''
        },

        'docker': {
            'framework': 'Docker',
            'specific_focus': 'Container orchestration, multi-stage builds, and deployment',
            'key_files': 'Dockerfile, docker-compose.yml, .dockerignore',
            'specific_dependencies': 'Docker Engine, Docker Compose',
            'specific_setup_steps': 'docker build, docker run, docker-compose up',
            'wow_factor': 'application containerization and consistent environments',
            'framework_sections': '''**Container Strategy:**
    - Multi-stage builds for optimized images
    - Layer caching and build optimization
    - Security best practices and minimal base images

    **Orchestration:**
    - Docker Compose service definitions
    - Network configuration and volume management
    - Health checks and restart policies'''
        },

        'kubernetes': {
            'framework': 'Kubernetes',
            'specific_focus': 'Container orchestration, declarative configuration, and scaling',
            'key_files': 'deployment.yaml, service.yaml, configmap.yaml',
            'specific_dependencies': 'kubectl, cluster access, container registry',
            'specific_setup_steps': 'kubectl apply -f, cluster configuration, resource monitoring',
            'wow_factor': 'automated scaling, self-healing, and declarative infrastructure',
            'framework_sections': '''**Kubernetes Resources:**
    - Deployment, Service, and Ingress configurations
    - ConfigMaps and Secrets management
    - Persistent Volumes and storage classes

    **Cluster Operations:**
    - Rolling updates and rollback strategies
    - Resource limits and quality of service
    - Monitoring and logging integration'''
        },

        'spring_boot': {
            'framework': 'Spring Boot',
            'specific_focus': 'Spring Boot auto-configuration and enterprise patterns',
            'key_files': 'pom.xml/build.gradle, Application.java, application.properties',
            'specific_dependencies': 'Java JDK, Maven/Gradle, Spring Boot starters',
            'specific_setup_steps': 'mvn spring-boot:run or gradle bootRun',
            'wow_factor': 'convention over configuration and production-ready features',
            'framework_sections': '''**Spring Ecosystem:**
    - Dependency injection and auto-configuration
    - Data JPA and transaction management
    - Security configuration and OAuth integration

    **Enterprise Features:**
    - Actuator endpoints for monitoring
    - Profile-based configuration
    - Testing with Spring Boot Test'''
        },

        'angular': {
            'framework': 'Angular',
            'specific_focus': 'Angular services, dependency injection, and TypeScript integration',
            'key_files': 'angular.json, src/app/, package.json',
            'specific_dependencies': 'Node.js, Angular CLI, TypeScript',
            'specific_setup_steps': 'npm install, ng serve, ng build',
            'wow_factor': 'full-featured framework with opinionated architecture',
            'framework_sections': '''**Angular Architecture:**
    - Component-based architecture with decorators
    - Services and dependency injection
    - RxJS observables for reactive programming

    **Angular Features:**
    - Angular CLI for scaffolding and builds
    - Router with lazy loading and guards
    - Forms with validation and reactive patterns'''
        },

        'fastapi': {
            'framework': 'FastAPI',
            'specific_focus': 'FastAPI automatic API documentation and async type hints',
            'key_files': 'main.py, requirements.txt, routers/',
            'specific_dependencies': 'Python version, uvicorn server, Pydantic',
            'specific_setup_steps': 'pip install fastapi uvicorn, uvicorn main:app --reload',
            'wow_factor': 'automatic interactive API docs at /docs and /redoc',
            'framework_sections': '''**API Development:**
    - Type hints for automatic validation
    - Dependency injection system
    - Async request handling and background tasks

    **FastAPI Features:**
    - Interactive API documentation (Swagger/ReDoc)
    - Authentication and security utilities
    - WebSocket support and streaming responses'''
        },

        'nextjs': {
            'framework': 'Next.js',
            'specific_focus': 'Next.js file-based routing, SSR/SSG, and optimization features',
            'key_files': 'next.config.js, pages/ or app/, package.json',
            'specific_dependencies': 'Node.js version, Next.js version',
            'specific_setup_steps': 'npm install, next dev, next build',
            'wow_factor': 'automatic code splitting, image optimization, and hybrid rendering',
            'framework_sections': '''**Next.js Features:**
    - File-based routing with dynamic routes
    - Server-side rendering and static generation
    - API routes and middleware

    **Performance Optimization:**
    - Automatic code splitting and prefetching
    - Image optimization with next/image
    - Built-in CSS and Sass support'''
        }

    }
    'c_project': {
    'framework': 'C',
    'specific_focus': 'C compilation, memory management, and system programming',
    'key_files': 'Makefile, *.c, *.h files',
    'specific_dependencies': 'GCC/Clang compiler, build-essential, specific libraries',
    'specific_setup_steps': 'compilation with make, library linking, header includes',
    'wow_factor': 'manual memory management and system-level programming',
    'framework_sections': '''**C Project Structure:**
    - Source files (.c) and header files (.h) organization
    - Makefile build configuration
    - Library dependencies and linking

    **Compilation & Build:**
    - GCC/Clang compilation flags and optimization
    - Static vs dynamic linking
    - Cross-compilation considerations'''

},

    'gcc_toolchain': {
    'framework': 'GCC Toolchain',
    'specific_focus': 'GNU Compiler Collection build system and cross-compilation',
    'key_files': 'configure, Makefile.in, config.h, source tree',
    'specific_dependencies': 'autotools, automake, autoconf, build dependencies',
    'specific_setup_steps': './configure && make && make install workflow',
    'wow_factor': 'sophisticated build system and compiler optimization',
    'framework_sections': '''**Build System:**
        - Autotools configuration and feature detection
        - Cross-compilation target setup
        - Dependency resolution and library paths
    
        **Compiler Features:**
        - Optimization levels and target architectures
        - Plugin system and language frontends
        - Debug symbol generation and profiling'''

    },

    'homebrew_formula': {
    'framework': 'Homebrew',
    'specific_focus': 'macOS package management and formula development',
    'key_files': '*.rb formula files, dependency declarations',
    'specific_dependencies': 'Ruby, Homebrew installation, Xcode tools',
    'specific_setup_steps': 'brew install --build-from-source, formula testing',
    'wow_factor': 'declarative package management and dependency resolution',
    'framework_sections': '''**Formula Structure:**
        - Ruby-based package definitions
        - Dependency management and conflicts
        - Installation and testing procedures
    
        **Homebrew Ecosystem:**
        - Tap management and formula distribution
        - Bottle generation for binary distribution
        - Integration with macOS system frameworks'''
    },

    'python_analysis_tool': {
    'framework': 'Python Analysis Tool',
    'specific_focus': 'Python AST analysis, static analysis, and code intelligence',
    'key_files': 'analysis scripts, AST parsers, CLI interfaces',
    'specific_dependencies': 'Python 3.x, AST module, argparse/click, analysis libraries',
    'specific_setup_steps': 'virtual environment, tool installation, CLI setup',
    'wow_factor': 'code intelligence and automated analysis capabilities',
    'framework_sections': '''**Analysis Architecture:**
        - AST parsing and code traversal patterns
        - Static analysis rules and metrics
        - Report generation and output formats
    
        **Tool Integration:**
        - CLI interface design and argument parsing
        - Plugin system for extensible analysis
        - Integration with IDEs and CI/CD pipelines'''
    },

    'react': {
    'framework': 'React',
    'specific_focus': 'React component architecture, hooks, and modern development patterns',
    'key_files': 'package.json, src/App.js, components/, hooks/',
    'specific_dependencies': 'Node.js version, React DevTools browser extension',
    'specific_setup_steps': 'npm/yarn installation, development server startup',
    'wow_factor': 'component reusability and hook patterns',
    'framework_sections': '''**Component Architecture:**
        - Functional components and React hooks
        - State management patterns (useState, useReducer, Context)
        - Component composition and prop drilling solutions
    
        **Development Workflow:**
        - Hot reloading and Fast Refresh
        - Code splitting and lazy loading
        - Testing with React Testing Library'''
    },

    'django': {
    'framework': 'Django',
    'specific_focus': 'Django models, views, templates, and URL routing',
    'key_files': 'manage.py, settings.py, models.py, urls.py, templates/',
    'specific_dependencies': 'Python version, database (PostgreSQL/MySQL), virtual environment',
    'specific_setup_steps': 'virtual environment, pip install, database migrations, collectstatic',
    'wow_factor': 'Django admin interface and ORM capabilities',
    'framework_sections': '''**Django Architecture:**
        - Model-View-Template (MVT) pattern
        - ORM relationships and database migrations
        - URL routing and view-based architecture
    
        **Django Features:**
        - Admin interface customization
        - Authentication and permissions system
        - Template inheritance and static file handling'''
    },

    'rust_project': {
    'framework': """
        Smart Project Type Detection for CodeRipple
        Automatically detects project type and applies specialized prompts for instant wow factor.
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
                # Backend Frameworks - Java
                              'spring_boot': {
            'files': ['pom.xml', 'build.gradle', 'src/main/java/', 'application.properties'],
            'content_patterns': ['spring-boot-starter', '@SpringBootApplication', '@RestController'],
            'wow_factor': 'Spring Boot auto-configuration and enterprise patterns'
        },

            # Backend Frameworks - PHP
        'laravel': {
            'files': ['composer.json', 'artisan', 'app/', 'routes/web.php'],
            'content_patterns': ['laravel/framework', 'Illuminate', 'Route::'],
            'wow_factor': 'Laravel Eloquent ORM and Artisan commands'
        },

        # Backend Frameworks - C#
        'dotnet': {
            'files': ['*.csproj', 'Program.cs', 'Startup.cs', 'appsettings.json'],
            'content_patterns': ['Microsoft.AspNetCore', 'WebApplication', '[ApiController]'],
            'wow_factor': '.NET dependency injection and minimal APIs'
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
        'vue': {
            'files': ['package.json', 'src/main.js', 'vue.config.js'],
            'content_patterns': ['"vue":', 'createApp', '<template>'],
            'wow_factor': 'Vue composition API and component lifecycle'
        },
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

        # Libraries/Tools
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

    # Example usage function for the Lambda
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
                'specialized_prompt': GETTING_STARTED_PROMPT,  # Your existing prompt
                'wow_factor': 'comprehensive project analysis',
                'analysis_focus': "General project analysis"
            }

    # Integration example for your Lambda B
    def lambda_b_enhanced_handler(event, context):
        """
        Enhanced Lambda B handler with smart project detection
        """
        # Download repo from S3 (your existing code)
        file_list = get_file_list_from_repo()

        # Read key files for content analysis
        file_contents = {}
        key_files = ['package.json', 'requirements.txt', 'manage.py', 'Dockerfile']
        for file in key_files:
            if file in file_list:
                file_contents[file] = read_file_content(file)

        # Enhance analysis with project type detection
        enhanced_analysis = enhance_coderipple_analysis(file_list, file_contents)

        # Use specialized prompt for analysis
        if enhanced_analysis['project_type'] != 'generic':
            print(f"🎯 Detected {enhanced_analysis['project_type']} project!")
            print(f"🌟 Focusing on: {enhanced_analysis['wow_factor']}")

            # Use the specialized prompt instead of generic one
            analysis_result = run_strands_analysis(
                prompt=enhanced_analysis['specialized_prompt'],
                focus=enhanced_analysis['analysis_focus']
            )
        else:
            # Fall back to generic analysis
            analysis_result = run_strands_analysis(prompt=GETTING_STARTED_PROMPT)

        # Rest of your Lambda B logic...
        return analysis_result
