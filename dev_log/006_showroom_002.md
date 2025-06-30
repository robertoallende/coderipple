# Subunit 6.2: Shared Assets Architecture Implementation

**Objective:** Refactor the Showroom website code into a shared assets structure to enable reuse across multiple S3 buckets (Showroom and Cabinet), ensuring consistent branding and maintainability.

## Architecture Overview

### Current Structure Problem
```
s3_showroom/website/
├── assets/
│   ├── css/coderipple.css
│   ├── images/coderipple-logo.png
│   └── fonts/JetBrainsMono-Regular.ttf
├── index.html
├── README.md
└── howto.md
```

**Issues:**
- Assets duplicated between buckets
- Inconsistent branding when updates are needed
- Multiple maintenance points for same resources

### Target Shared Structure
```
/coderipple/
├── shared-assets/
│   ├── css/
│   │   └── coderipple.css
│   ├── images/
│   │   └── coderipple-logo.png
│   ├── fonts/
│   │   └── JetBrainsMono-Regular.ttf
│   └── templates/
│       ├── base-index.html
│       └── docsify-config.js
├── s3_showroom/
│   ├── content/
│   │   ├── README.md
│   │   └── howto.md
│   └── deploy.sh (updated)
└── s3_cabinet/
    ├── content/
    └── deploy.sh (future)
```

## Implementation Plan

### Phase 1: Create Shared Assets Structure

#### 1.1 Create Shared Directory
```bash
mkdir -p shared-assets/{css,images,fonts,templates}
```

#### 1.2 Move Common Assets
- **CSS:** Move `coderipple.css` to `shared-assets/css/`
- **Images:** Move `coderipple-logo.png` to `shared-assets/images/`
- **Fonts:** Move `JetBrainsMono-Regular.ttf` to `shared-assets/fonts/`

#### 1.3 Create Template System
- **Base HTML template:** `shared-assets/templates/base-index.html`
- **Docsify configuration:** `shared-assets/templates/docsify-config.js`
- **Parameterized for bucket-specific customization**

### Phase 2: Refactor Showroom Structure

#### 2.1 Reorganize Showroom Directory
```
s3_showroom/
├── content/
│   ├── README.md          # Showroom-specific content
│   └── howto.md           # Showroom-specific content
├── config/
│   └── showroom-config.js # Showroom-specific configuration
└── deploy.sh              # Updated deployment script
```

#### 2.2 Update Deployment Script
Enhanced `deploy.sh` to:
- Copy shared assets to local build directory
- Merge with showroom-specific content
- Apply showroom-specific configuration
- Deploy to S3 bucket

### Phase 3: Template Parameterization

#### 3.1 Base HTML Template
```html
<!-- shared-assets/templates/base-index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{SITE_TITLE}}</title>
  <meta name="description" content="{{SITE_DESCRIPTION}}">
  <!-- ... common head elements ... -->
</head>
<body>
  <div id="app">{{LOADING_CONTENT}}</div>
  <script>
    window.$docsify = {{DOCSIFY_CONFIG}};
  </script>
  <!-- ... common scripts ... -->
</body>
</html>
```

#### 3.2 Configuration System
```javascript
// shared-assets/templates/docsify-config.js
function createDocsifyConfig(options) {
  return {
    name: options.siteName || 'CodeRipple',
    loadSidebar: options.loadSidebar || false,
    search: options.search || defaultSearchConfig,
    plugins: [
      createHeaderPlugin(options.header),
      createFooterPlugin(options.footer),
      ...options.additionalPlugins || []
    ]
  };
}
```

## Deployment Script Enhancement

### Updated deploy.sh for Showroom
```bash
#!/bin/bash

# Showroom Deployment Script with Shared Assets
set -e

# Configuration
BUCKET_NAME="coderipple-showroom"
REGION="us-east-1"
BUILD_DIR="./build"
SHARED_ASSETS="../shared-assets"

echo "🚀 Deploying Showroom with shared assets..."

# 1. Clean and create build directory
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/assets/{css,images,fonts}

# 2. Copy shared assets
echo "📦 Copying shared assets..."
cp -r $SHARED_ASSETS/css/* $BUILD_DIR/assets/css/
cp -r $SHARED_ASSETS/images/* $BUILD_DIR/assets/images/
cp -r $SHARED_ASSETS/fonts/* $BUILD_DIR/assets/fonts/

# 3. Generate index.html from template
echo "🔧 Generating index.html from template..."
node generate-index.js showroom > $BUILD_DIR/index.html

# 4. Copy showroom-specific content
echo "📄 Copying showroom content..."
cp content/*.md $BUILD_DIR/

# 5. Deploy to S3
echo "☁️ Deploying to S3..."
aws s3 sync $BUILD_DIR/ s3://$BUCKET_NAME/ --region $REGION --delete

# 6. Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo $WEBSITE_URL > website-url.txt

echo "✅ Showroom deployment complete!"
echo "🌐 Website URL: $WEBSITE_URL"
```

### Template Generation Script
```javascript
// generate-index.js
const fs = require('fs');
const path = require('path');

const configs = {
  showroom: {
    siteName: 'CodeRipple',
    siteTitle: 'CodeRipple - Code Analysis Platform',
    siteDescription: 'CodeRipple - documentation that evolves with your code, automatically',
    loadingContent: `
      <div style="text-align: center; padding: 50px; color: #021A2D;">
        <h2>Loading CodeRipple...</h2>
        <p>Professional code analysis</p>
      </div>
    `,
    header: {
      title: 'CodeRipple',
      tagline: 'documentation that evolves with your code, automatically',
      logo: 'assets/images/coderipple-logo.png'
    },
    footer: {
      title: 'CodeRipple',
      tagline: 'documentation that evolves with your code, automatically',
      showTimestamp: true
    }
  }
};

function generateIndex(type) {
  const config = configs[type];
  const template = fs.readFileSync(
    path.join(__dirname, '../shared-assets/templates/base-index.html'), 
    'utf8'
  );
  
  return template
    .replace('{{SITE_TITLE}}', config.siteTitle)
    .replace('{{SITE_DESCRIPTION}}', config.siteDescription)
    .replace('{{LOADING_CONTENT}}', config.loadingContent)
    .replace('{{DOCSIFY_CONFIG}}', JSON.stringify(createDocsifyConfig(config)));
}

// Usage: node generate-index.js showroom
const type = process.argv[2] || 'showroom';
console.log(generateIndex(type));
```

## Benefits of Shared Assets Architecture

### Maintenance Benefits
- ✅ **Single source of truth** - Update branding once, applies everywhere
- ✅ **Consistent styling** - Same CSS, fonts, and images across all buckets
- ✅ **Version control** - All shared assets tracked in one location
- ✅ **Reduced duplication** - No more copying files between projects

### Development Benefits
- ✅ **Parameterized templates** - Easy customization per bucket
- ✅ **Build-time generation** - Flexible configuration system
- ✅ **Domain neutrality** - All URLs remain relative and portable
- ✅ **Scalable architecture** - Easy to add new buckets/sites

### Deployment Benefits
- ✅ **Automated asset copying** - No manual file management
- ✅ **Build verification** - Ensure all assets are present before deploy
- ✅ **Clean deployments** - Fresh build directory for each deployment
- ✅ **Rollback capability** - Easy to revert to previous versions

## Migration Steps

### Step 1: Create Shared Assets
1. Create `shared-assets` directory structure
2. Move existing assets from `s3_showroom/website/assets/`
3. Create base template from current `index.html`
4. Extract common Docsify configuration

### Step 2: Update Showroom
1. Reorganize `s3_showroom` directory structure
2. Move content files to `content/` subdirectory
3. Create showroom-specific configuration
4. Update deployment script

### Step 3: Create Build System
1. Implement template generation script
2. Add asset copying logic to deployment
3. Test build and deployment process
4. Verify website functionality

### Step 4: Validation
1. Deploy updated showroom and verify functionality
2. Check all assets load correctly
3. Verify domain neutrality maintained
4. Test responsive design and mobile compatibility

## Success Criteria

1. ✅ Shared assets directory created with all common resources
2. ✅ Template system implemented for HTML generation
3. ✅ Showroom deployment script updated to use shared assets
4. ✅ Website functionality maintained after migration
5. ✅ All assets load correctly from new structure
6. ✅ Domain neutrality preserved
7. ✅ Build system generates correct HTML from templates
8. ✅ Deployment process automated and reliable

## Future Extensibility

This architecture prepares for:
- **Cabinet bucket integration** (Subunit 6.3)
- **Additional S3 websites** with consistent branding
- **Theme variations** while maintaining core assets
- **Multi-environment deployments** (dev, staging, prod)

The shared assets architecture provides a solid foundation for scaling the CodeRipple UI across multiple deployment targets while maintaining consistency and reducing maintenance overhead.
