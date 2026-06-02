
# Installation & Setup

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Step-by-Step Installation](#step-by-step-installation)
5. [Modules Installed](#modules-installed)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

## Overview

This documentation covers the installation of the module and some required OCA (Odoo Community Association) modules. 

## Prerequisites

Before starting, ensure you have:

- **Ubuntu 20.04 or later** (or any Debian-based Linux distribution)
- **Git** installed (`sudo apt install git`)
- **Odoo 18.0** installed and configured
- **Basic command line knowledge**
- **Access to terminal** with sudo privileges (if needed)


## Installation

1. **Copy the module** to your Odoo addons directory:
```bash
cp -r lga_legal_management_community /odoo/addons/
```

2. Proccess to the installation script automates the cloning and organization of the following modules:

- **web_widget_x2many_2d_matrix** - From OCA/web repository
- **account_financial_report** - From OCA/account-financial-reporting repository  
- **date_range** & **date_range_account** - From OCA/server-ux repository
- **hr_timesheet_sheet** - From OCA/timesheet repository
- **report_xlsx** - From OCA/reporting-engine repository

### 1. Create the repositories list file

First, create a file that lists all OCA repositories to clone:

```bash
# Navigate to your Odoo directory
cd ~/your-project/odoo

# Create the repositories file
nano oca-repos.txt
```

Add the following content:

```txt
# OCA Repositories for Odoo 
https://github.com/OCA/account-financial-reporting.git
https://github.com/OCA/mis-builder.git
https://github.com/OCA/timesheet.git
https://github.com/OCA/server-ux.git
https://github.com/OCA/reporting-engine.git
https://github.com/OCA/web.git
```

Save and exit (Ctrl+X, then Y, then Enter).

### 2. Create the installation script

Create the installation script:

```bash
# Create scripts directory if it doesn't exist
mkdir -p ~/your-project/odoo/scripts

# Create and edit the script
nano ~/your-project/odoo/scripts/install_oca.sh
```

Copy and paste the installation script provided below:

```bash
#!/bin/bash

BRANCH="18.0"

# Use environment variable if defined, otherwise search
if [ -n "$LEGAL_PLATFORM_HOME" ]; then
    BASE_DIR="$LEGAL_PLATFORM_HOME"
    echo "📁 Using LEGAL_PLATFORM_HOME: $BASE_DIR"
else
    # Search automatically
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Try to find the project (go up until finding odoo/oca-repos.txt)
    CURRENT="$SCRIPT_DIR"
    while [ "$CURRENT" != "/" ]; do
        if [ -f "$CURRENT/odoo/oca-repos.txt" ]; then
            BASE_DIR="$CURRENT"
            break
        fi
        CURRENT="$(dirname "$CURRENT")"
    done
    
    if [ -z "$BASE_DIR" ]; then
        echo "❌ Cannot find project root"
        echo "💡 Set LEGAL_PLATFORM_HOME or run from the project"
        exit 1
    fi
    
    echo "📁 Project detected: $BASE_DIR"
fi

TARGET_DIR="$BASE_DIR/odoo/oca-addons"
REPO_FILE="$BASE_DIR/odoo/oca-repos.txt"

# Verification
if [ ! -f "$REPO_FILE" ]; then
    echo "❌ Error: $REPO_FILE not found"
    exit 1
fi

mkdir -p "$TARGET_DIR"

while read -r repo; do
    [ -z "$repo" ] && continue
    [[ "$repo" =~ ^#.*$ ]] && continue
    
    REPO_NAME=$(basename "$repo" .git)
    echo "🔧 Processing: $REPO_NAME"
    
    cd "$TARGET_DIR" || exit 1
    
    if [ -d "$REPO_NAME" ]; then
        echo "🔄 Updating $REPO_NAME..."
        cd "$REPO_NAME" || exit 1
        git fetch --depth 1 origin "$BRANCH"
        git reset --hard "origin/$BRANCH"
        cd "$TARGET_DIR" || exit 1
    else
        echo "⬇️ Cloning $REPO_NAME..."
        git clone --depth 1 --single-branch -b "$BRANCH" "$repo"
    fi

done < "$REPO_FILE"

echo "✅ OCA modules cloned/updated in: $TARGET_DIR"
echo "🔄 Starting restructuring operations..."

# Go back to target directory
cd "$TARGET_DIR" || exit 1

# 1. Processing web repo (web_widget_x2many_2d_matrix)
if [ -d "web" ] && [ -d "web/web_widget_x2many_2d_matrix" ]; then
    echo "📦 Processing web_widget_x2many_2d_matrix..."
    cp -r "web/web_widget_x2many_2d_matrix" .
    rm -rf "web"
    echo "✅ web_widget_x2many_2d_matrix moved to root"
fi

# 2. Processing mis_builder repo
if [ -d "mis-builder" ] && [ -d "mis-builder/mis_builder" ]; then
    echo "📦 Processing mis_builder..."
    cp -r "mis-builder/mis_builder" .
    rm -rf "mis-builder"
    echo "✅ mis_builder moved to root"
fi

# 3. Processing account-financial-reporting repo
if [ -d "account-financial-reporting" ] && [ -d "account-financial-reporting/account_financial_report" ]; then
    echo "📦 Processing account_financial_report..."
    cp -r "account-financial-reporting/account_financial_report" .
    rm -rf "account-financial-reporting"
    echo "✅ account_financial_report moved to root"
fi

# 4. Processing server-ux repo (date_range and date_range_account)
if [ -d "server-ux" ]; then
    echo "📦 Processing date_range and date_range_account modules..."
    if [ -d "server-ux/date_range" ]; then
        cp -r "server-ux/date_range" .
        echo "   ✅ date_range moved"
    fi
    if [ -d "server-ux/date_range_account" ]; then
        cp -r "server-ux/date_range_account" .
        echo "   ✅ date_range_account moved"
    fi
    rm -rf "server-ux"
    echo "✅ server-ux modules moved to root"
fi

# 5. Processing timesheet repo
if [ -d "timesheet" ] && [ -d "timesheet/hr_timesheet_sheet" ]; then
    echo "📦 Processing hr_timesheet_sheet..."
    cp -r "timesheet/hr_timesheet_sheet" .
    rm -rf "timesheet"
    echo "✅ hr_timesheet_sheet moved to root"
fi

# 6. Processing reporting-engine repo
if [ -d "reporting-engine" ] && [ -d "reporting-engine/report_xlsx" ]; then
    echo "📦 Processing report_xlsx..."
    cp -r "reporting-engine/report_xlsx" .
    rm -rf "reporting-engine"
    echo "✅ report_xlsx moved to root"
fi

echo "🎉 All restructuring operations are complete!"
echo "📁 Final content of $TARGET_DIR :"
ls -la "$TARGET_DIR"

# Final verification
echo "🔍 Checking moved modules:"
MODULES_DEPLACES=(
    "web_widget_x2many_2d_matrix"
    "mis_builder"
    "account_financial_report"
    "date_range"
    "date_range_account"
    "hr_timesheet_sheet"
    "report_xlsx"
)

for module in "${MODULES_DEPLACES[@]}"; do
    if [ -d "$TARGET_DIR/$module" ]; then
        echo "   ✅ $module present"
    else
        echo "   ⚠️ $module not found (may be in another repository)"
    fi
done

echo "✅ Script completed!"
```

### 3. Make the script executable

```bash
chmod +x ~/your-project/odoo/scripts/install_oca.sh
```

## Step-by-Step Installation

### Method 1: Using auto-detection (recommended)

```bash
# Navigate to your project root
cd ~/your-project

# Run the installation script
./odoo/scripts/install_oca.sh
```

### Method 2: Using environment variable

```bash
# Set the project home directory
export LEGAL_PLATFORM_HOME=/path/to/your/project

# Run the script from anywhere
~/your-project/odoo/scripts/install_oca.sh
```

### Method 3: Run with debugging (for troubleshooting)

```bash
bash -x ~/your-project/odoo/scripts/install_oca.sh
```

## Modules Installed

After successful installation, the following modules will be available in `odoo/oca-addons/`:

| Module Name | Description | Original Repository |
|------------|-------------|-------------------|
| **web_widget_x2many_2d_matrix** | 2D matrix widget for many2many fields | OCA/web |
| **account_financial_report** | Enhanced financial reports for accounting | OCA/account-financial-reporting |
| **date_range** | Date range filtering functionality | OCA/server-ux |
| **date_range_account** | Date range integration with accounting | OCA/server-ux |
| **hr_timesheet_sheet** | Timesheet management for employees | OCA/timesheet |
| **report_xlsx** | Excel (XLSX) report generation | OCA/reporting-engine |

## Adding Modules to Odoo

After installation, you need to add these modules to your Odoo addons path:

### 1. Update Odoo configuration

Edit your Odoo configuration file:

```bash
sudo nano /your-project/odoo/odoo.conf
```

Add the following line in the `[options]` section:

```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/path/to/your-project/odoo/oca-addons
```

### 2. Restart Odoo service

```bash
sudo systemctl restart odoo
```

### 3. Update modules list in Odoo

- Log in to Odoo as administrator
- Go to **Apps** menu
- Click on **Update Apps List**
- Search for the new modules and install them

## Troubleshooting


#### Issue 1: Git clone fails
**Solution:** Check your internet connection and git installation:
```bash
git --version
ping github.com
```

#### Issue 2: Permission denied
**Solution:** Make the script executable:
```bash
chmod +x ~/your-project/odoo/scripts/install_oca.sh
```

#### Issue 3: Branch 18.0 doesn't exist
**Solution:** Some repositories might use different branch names. Check available branches:
```bash
git ls-remote --heads https://github.com/OCA/web.git
```

## Maintenance

### Updating Modules

To update all modules to the latest version:

```bash
# Simply re-run the installation script
cd ~/your-project
./odoo/scripts/install_oca.sh
```

### Adding New Modules

1. Edit the `oca-repos.txt` file:
```bash
nano ~/legal-digital-platform/odoo/oca-repos.txt
```

2. Add new repository URLs:
```txt
https://github.com/OCA/new-repository.git
```

3. Update the script to handle the new modules (if needed)

4. Re-run the installation script

### Backup

Before major updates, backup your addons:

```bash
# Create a backup
tar -czf oca-addons-backup-$(date +%Y%m%d).tar.gz ~/your-project/odoo/oca-addons/
```

## Additional Resources

- [OCA Official Website](https://odoo-community.org/)
- [Odoo 18.0 Documentation](https://www.odoo.com/documentation/18.0/)
- [GitHub OCA Repository](https://github.com/OCA)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the script output for error messages
3. Ensure all prerequisites are met
4. Check your internet connection
5. Verify GitHub accessibility

---

**Note**: This installation method extracts only the specific modules needed, keeping your addons directory clean and organized. The original repository folders are removed after extraction to avoid duplicate modules.