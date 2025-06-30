#!/bin/bash

# HTML Template Generator for CodeRipple Sites
# Usage: ./generate-html.sh <site-type> <output-file>

set -e

SITE_TYPE=${1:-showroom}
OUTPUT_FILE=${2:-index.html}
TEMPLATE_DIR="$(dirname "$0")/templates"
TEMPLATE_FILE="$TEMPLATE_DIR/base-index.html"

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    exit 1
fi

# Site configurations
case $SITE_TYPE in
    "showroom")
        SITE_NAME="CodeRipple"
        SITE_TITLE="CodeRipple - Code Analysis Platform"
        SITE_DESCRIPTION="CodeRipple - documentation that evolves with your code, automatically"
        LOADING_MESSAGE="Professional code analysis"
        LOAD_SIDEBAR="false"
        SEARCH_PLACEHOLDER="Search analyses..."
        HEADER_TITLE="CodeRipple"
        HEADER_TAGLINE="documentation that evolves with your code, automatically"
        FOOTER_TITLE="CodeRipple"
        FOOTER_TAGLINE="documentation that evolves with your code, automatically"
        ;;
    "cabinet")
        SITE_NAME="CodeRipple Cabinet"
        SITE_TITLE="CodeRipple Cabinet - Event Logs"
        SITE_DESCRIPTION="CodeRipple event logging and system monitoring"
        LOADING_MESSAGE="Event logging and monitoring"
        LOAD_SIDEBAR="false"
        SEARCH_PLACEHOLDER="Search events..."
        HEADER_TITLE="CodeRipple Cabinet"
        HEADER_TAGLINE="event logging and system monitoring"
        FOOTER_TITLE="CodeRipple Cabinet"
        FOOTER_TAGLINE="event logging and system monitoring"
        ;;
    *)
        echo "❌ Unknown site type: $SITE_TYPE"
        echo "Usage: $0 <showroom|cabinet> [output-file]"
        exit 1
        ;;
esac

echo "🔧 Generating $SITE_TYPE HTML from template..."

# Generate HTML by replacing template variables
sed \
    -e "s|{{SITE_NAME}}|$SITE_NAME|g" \
    -e "s|{{SITE_TITLE}}|$SITE_TITLE|g" \
    -e "s|{{SITE_DESCRIPTION}}|$SITE_DESCRIPTION|g" \
    -e "s|{{LOADING_MESSAGE}}|$LOADING_MESSAGE|g" \
    -e "s|{{LOAD_SIDEBAR}}|$LOAD_SIDEBAR|g" \
    -e "s|{{SEARCH_PLACEHOLDER}}|$SEARCH_PLACEHOLDER|g" \
    -e "s|{{HEADER_TITLE}}|$HEADER_TITLE|g" \
    -e "s|{{HEADER_TAGLINE}}|$HEADER_TAGLINE|g" \
    -e "s|{{FOOTER_TITLE}}|$FOOTER_TITLE|g" \
    -e "s|{{FOOTER_TAGLINE}}|$FOOTER_TAGLINE|g" \
    "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo "✅ Generated $OUTPUT_FILE for $SITE_TYPE"
