# Subunit 6.3: Cabinet Bucket Shared Assets Integration

**Objective:** Extend the shared assets architecture to the Cabinet bucket (Hermes documentation website), ensuring consistent CodeRipple branding across both Showroom and Cabinet while maintaining their distinct purposes and content.

## Architecture Overview

### Current Cabinet Structure (Hermes)
```
s3_cabinet/
├── index.html              # Basic Docsify setup
├── README.md               # Hermes documentation
├── _sidebar.md             # Navigation menu
└── logs/                   # Event logs directory
    └── [timestamp-files]
```

### Target Integrated Structure
```
/coderipple/
├── shared-assets/          # Already created in Subunit 6.2
│   ├── css/coderipple.css
│   ├── images/coderipple-logo.png
│   ├── fonts/JetBrainsMono-Regular.ttf
│   └── templates/
│       ├── base-index.html
│       └── docsify-config.js
├── s3_showroom/           # Updated in Subunit 6.2
└── s3_cabinet/
    ├── content/
    │   ├── README.md       # Cabinet-specific content
    │   └── _sidebar.md     # Cabinet navigation
    ├── config/
    │   └── cabinet-config.js # Cabinet-specific configuration
    └── deploy.sh           # Cabinet deployment script
```

## Cabinet-Specific Requirements

### Purpose Differentiation
**Showroom (Analysis Results):**
- Public-facing analysis dashboard
- Recent analyses list
- Download capabilities
- User-focused interface

**Cabinet (System Documentation):**
- Internal system documentation
- Event logs and monitoring
- Developer/admin interface
- Technical documentation focus

### Branding Consistency
**Shared Elements:**
- ✅ CodeRipple logo and colors
- ✅ Typography (JetBrains Mono)
- ✅ Header structure and styling
- ✅ Footer format and content

**Cabinet-Specific Elements:**
- 📋 Navigation sidebar (enabled for Cabinet)
- 📊 Documentation-focused layout
- 🔍 Technical content organization
- 📝 Event log presentation

## Implementation Plan

### Phase 1: Cabinet Configuration

#### 1.1 Create Cabinet-Specific Config
```javascript
// s3_cabinet/config/cabinet-config.js
const cabinetConfig = {
  siteName: 'CodeRipple Cabinet',
  siteTitle: 'CodeRipple Cabinet - System Documentation',
  siteDescription: 'CodeRipple system documentation and event monitoring',
  loadSidebar: true,  // Enable sidebar for documentation
  loadNavbar: false,
  maxLevel: 4,
  subMaxLevel: 3,
  loadingContent: `
    <div style="text-align: center; padding: 50px; color: #021A2D;">
      <h2>Loading CodeRipple Cabinet...</h2>
      <p>System documentation and monitoring</p>
    </div>
  `,
  header: {
    title: 'CodeRipple Cabinet',
    tagline: 'system documentation and event monitoring',
    logo: 'assets/images/coderipple-logo.png'
  },
  footer: {
    title: 'CodeRipple Cabinet',
    tagline: 'system documentation and event monitoring',
    showTimestamp: true
  },
  search: {
    maxAge: 86400000,
    paths: 'auto',
    placeholder: 'Search documentation...',
    noData: 'No documentation found.',
    depth: 4
  }
};

module.exports = cabinetConfig;
```

#### 1.2 Reorganize Cabinet Content
```
s3_cabinet/content/
├── README.md           # Main documentation page
├── _sidebar.md         # Navigation structure
├── architecture/
│   ├── overview.md
│   └── components.md
├── events/
│   ├── event-types.md
│   └── monitoring.md
└── logs/
    └── README.md       # Log access instructions
```

### Phase 2: Template Customization

#### 2.1 Extend Base Template for Cabinet
```html
<!-- Template modifications for Cabinet -->
{{#if ENABLE_SIDEBAR}}
<style>
  .sidebar {
    display: block !important;
    background-color: var(--coderipple-dark);
    border-right: 2px solid var(--coderipple-blue);
  }
  
  .sidebar-nav > ul > li > a {
    color: var(--coderipple-light);
  }
  
  .sidebar-nav > ul > li > a:hover {
    color: var(--coderipple-blue);
  }
  
  .content {
    left: 300px !important;
  }
</style>
{{/if}}
```

#### 2.2 Cabinet-Specific Styling
```css
/* Additional CSS for Cabinet in shared-assets/css/cabinet-extensions.css */
.cabinet-header {
  background: linear-gradient(135deg, var(--coderipple-dark), #0a2a3d);
  border-bottom: 3px solid var(--coderipple-blue);
}

.log-entry {
  background-color: #f8f9fa;
  border-left: 4px solid var(--coderipple-blue);
  padding: 12px;
  margin: 8px 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
}

.event-timestamp {
  color: var(--coderipple-blue);
  font-weight: 600;
}

.component-badge {
  background-color: var(--coderipple-blue);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}
```

### Phase 3: Cabinet Deployment Script

#### 3.1 Create Cabinet deploy.sh
```bash
#!/bin/bash

# Cabinet Deployment Script with Shared Assets
set -e

# Configuration
BUCKET_NAME="coderipple-cabinet"
REGION="us-east-1"
BUILD_DIR="./build"
SHARED_ASSETS="../shared-assets"

echo "🚀 Deploying Cabinet with shared assets..."

# 1. Clean and create build directory
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/assets/{css,images,fonts}

# 2. Copy shared assets
echo "📦 Copying shared assets..."
cp -r $SHARED_ASSETS/css/* $BUILD_DIR/assets/css/
cp -r $SHARED_ASSETS/images/* $BUILD_DIR/assets/images/
cp -r $SHARED_ASSETS/fonts/* $BUILD_DIR/assets/fonts/

# 3. Copy cabinet-specific CSS extensions
echo "🎨 Adding cabinet-specific styling..."
cat $SHARED_ASSETS/css/coderipple.css > $BUILD_DIR/assets/css/combined.css
cat $SHARED_ASSETS/css/cabinet-extensions.css >> $BUILD_DIR/assets/css/combined.css

# 4. Generate index.html from template
echo "🔧 Generating index.html from template..."
node ../shared-assets/generate-index.js cabinet > $BUILD_DIR/index.html

# 5. Copy cabinet-specific content
echo "📄 Copying cabinet content..."
cp -r content/* $BUILD_DIR/

# 6. Ensure bucket exists and configure
echo "🪣 Configuring S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html --region $REGION

# 7. Set bucket policy for public read access
echo "🔓 Setting public read access policy..."
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-public-access-block --bucket $BUCKET_NAME --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false --region $REGION
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json --region $REGION

# 8. Deploy to S3
echo "☁️ Deploying to S3..."
aws s3 sync $BUILD_DIR/ s3://$BUCKET_NAME/ --region $REGION --delete

# 9. Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo $WEBSITE_URL > website-url.txt

echo "✅ Cabinet deployment complete!"
echo "🌐 Website URL: $WEBSITE_URL"
echo "📚 Documentation: $WEBSITE_URL/#/"
echo "📊 Event Logs: $WEBSITE_URL/#/logs/"
```

### Phase 4: Template Generator Enhancement

#### 4.1 Add Cabinet Configuration to generate-index.js
```javascript
// Addition to existing generate-index.js
const configs = {
  showroom: { /* existing showroom config */ },
  
  cabinet: {
    siteName: 'CodeRipple Cabinet',
    siteTitle: 'CodeRipple Cabinet - System Documentation',
    siteDescription: 'CodeRipple system documentation and event monitoring',
    loadSidebar: true,  // Key difference from showroom
    loadingContent: `
      <div style="text-align: center; padding: 50px; color: #021A2D;">
        <h2>Loading CodeRipple Cabinet...</h2>
        <p>System documentation and monitoring</p>
      </div>
    `,
    header: {
      title: 'CodeRipple Cabinet',
      tagline: 'system documentation and event monitoring',
      logo: 'assets/images/coderipple-logo.png'
    },
    footer: {
      title: 'CodeRipple Cabinet',
      tagline: 'system documentation and event monitoring',
      showTimestamp: true
    },
    enableSidebar: true,
    cssFile: 'assets/css/combined.css'  // Use combined CSS with extensions
  }
};

function createDocsifyConfig(config) {
  return {
    name: config.siteName,
    loadSidebar: config.loadSidebar || false,
    loadNavbar: false,
    maxLevel: 4,
    subMaxLevel: 3,
    auto2top: true,
    search: config.search || {
      maxAge: 86400000,
      paths: 'auto',
      placeholder: 'Search...',
      noData: 'No results found.',
      depth: 3
    },
    plugins: [
      createHeaderPlugin(config.header),
      createFooterPlugin(config.footer)
    ]
  };
}
```

## Content Migration Strategy

### Phase 1: Preserve Existing Hermes Content
1. **Backup current Cabinet content** to ensure no data loss
2. **Migrate existing documentation** to new content structure
3. **Preserve event logs** and access patterns
4. **Maintain existing URLs** where possible

### Phase 2: Enhance Documentation Structure
```markdown
<!-- s3_cabinet/content/README.md -->
# CodeRipple Cabinet

System documentation and event monitoring for the CodeRipple analysis platform.

## 🏗️ System Architecture

CodeRipple is a serverless code analysis pipeline built on AWS, consisting of multiple integrated components working together to provide automated code analysis and delivery.

## 📊 System Components

- **[Gatekeeper](architecture/gatekeeper.md)** - API Gateway webhook endpoint
- **[Telephonist](architecture/telephonist.md)** - EventBridge event routing
- **[Hermes](architecture/hermes.md)** - Event logging and documentation
- **[Receptionist](architecture/receptionist.md)** - Repository processing
- **[Analyst](architecture/analyst.md)** - Code analysis engine
- **[Deliverer](architecture/deliverer.md)** - Results packaging and delivery

## 📈 Event Monitoring

- **[Event Types](events/event-types.md)** - Complete event catalog
- **[Event Flow](events/event-flow.md)** - Pipeline event sequences
- **[Monitoring Dashboard](events/monitoring.md)** - System health and metrics

## 📝 Event Logs

- **[Recent Events](logs/)** - Latest system events and processing logs
- **[Log Analysis](logs/analysis.md)** - Event pattern analysis and insights
```

### Phase 3: Update Navigation Structure
```markdown
<!-- s3_cabinet/content/_sidebar.md -->
* [🏠 Home](/)

* **🏗️ Architecture**
  * [System Overview](architecture/overview.md)
  * [Component Details](architecture/components.md)
  * [Event Flow](architecture/event-flow.md)

* **📊 Components**
  * [Gatekeeper](components/gatekeeper.md)
  * [Telephonist](components/telephonist.md)
  * [Hermes](components/hermes.md)
  * [Receptionist](components/receptionist.md)
  * [Analyst](components/analyst.md)
  * [Deliverer](components/deliverer.md)

* **📈 Monitoring**
  * [Event Types](events/event-types.md)
  * [System Health](events/monitoring.md)
  * [Performance Metrics](events/metrics.md)

* **📝 Event Logs**
  * [Recent Events](logs/)
  * [Log Analysis](logs/analysis.md)
  * [Troubleshooting](logs/troubleshooting.md)

---

* **🔧 Development**
  * [API Reference](dev/api.md)
  * [Deployment Guide](dev/deployment.md)
  * [Contributing](dev/contributing.md)

---

<small>*CodeRipple Cabinet*</small>
```

## Integration with Hermes Lambda

### Event Log Integration
The Cabinet will continue to receive and display event logs from the Hermes Lambda, but with enhanced presentation using the shared assets styling.

```javascript
// Enhanced log display with shared styling
function displayEventLog(event) {
  return `
    <div class="log-entry">
      <div class="event-timestamp">${event.timestamp}</div>
      <div class="component-badge">${event.component}</div>
      <div class="event-details">${event.message}</div>
    </div>
  `;
}
```

## Benefits of Cabinet Integration

### Consistency Benefits
- ✅ **Unified branding** - Same CodeRipple look and feel as Showroom
- ✅ **Consistent navigation** - Familiar user experience across platforms
- ✅ **Shared maintenance** - Single point of updates for common elements
- ✅ **Professional appearance** - Cohesive CodeRipple ecosystem

### Functional Benefits
- ✅ **Enhanced documentation** - Better organized and styled content
- ✅ **Improved navigation** - Sidebar structure for complex documentation
- ✅ **Better log presentation** - Styled event logs with consistent formatting
- ✅ **Search functionality** - Comprehensive search across all documentation

### Technical Benefits
- ✅ **Shared deployment pipeline** - Consistent build and deploy process
- ✅ **Template reuse** - Same base template with cabinet-specific customization
- ✅ **Asset optimization** - Shared CSS, fonts, and images
- ✅ **Domain neutrality** - Easy to change domains for both sites

## Success Criteria

1. ✅ Cabinet bucket configured with shared assets architecture
2. ✅ Consistent CodeRipple branding applied to Cabinet
3. ✅ Documentation structure enhanced and organized
4. ✅ Sidebar navigation implemented for Cabinet
5. ✅ Event logs maintain functionality with improved styling
6. ✅ Deployment script automated and reliable
7. ✅ All existing Hermes functionality preserved
8. ✅ Website performance maintained or improved
9. ✅ Mobile responsiveness across all Cabinet pages
10. ✅ Search functionality working across documentation

## Future Enhancements

### Phase 1 Extensions
- **Real-time event updates** - WebSocket integration for live log updates
- **Event filtering** - Advanced filtering and search capabilities
- **Performance dashboards** - Visual metrics and system health indicators

### Phase 2 Extensions
- **User authentication** - Secure access to sensitive system information
- **API documentation** - Interactive API explorer and testing tools
- **Deployment automation** - CI/CD integration for documentation updates

This implementation ensures the Cabinet bucket maintains its technical documentation purpose while benefiting from the shared assets architecture and consistent CodeRipple branding established in the Showroom.
