# 📋 Jira Projects to Create Manually

If you don't have admin permissions to create projects via API, create these projects manually in Jira first:

## 🎯 Project Details

### Project 1: Infotainment System
- **Project Key**: `IFS`
- **Project Name**: `Next-generation in-vehicle infotainment system with Android Automotive`
  - (Or shorter): `Infotainment System - Android Automotive`
- **Project Type**: Software Development (Scrum or Kanban)
- **Description**: Next-generation in-vehicle infotainment system with Android Automotive OS integration

### Project 2: ADAS Driver Assistance
- **Project Key**: `ADAS`
- **Project Name**: `Advanced Driver Assistance Systems (ADAS) with adaptive cruise control`
  - (Or shorter): `ADAS - Driver Assistance Systems`
- **Project Type**: Software Development (Scrum or Kanban)
- **Description**: Advanced Driver Assistance Systems (ADAS) featuring adaptive cruise control and lane keeping

### Project 3: Vehicle Diagnostics
- **Project Key**: `VD`
- **Project Name**: `Comprehensive vehicle diagnostics and telemetry system`
  - (Or shorter): `Vehicle Diagnostics & Telemetry`
- **Project Type**: Software Development (Scrum or Kanban)
- **Description**: Comprehensive vehicle diagnostics and telemetry system with cloud connectivity

---

## 🛠️ How to Create Projects in Jira

1. **Log into Jira**: https://adhivp04.atlassian.net

2. **Click "Projects" in the top navigation**

3. **Click "Create project"**

4. **Select a template**:
   - Choose "Scrum" or "Kanban" (recommended: Scrum)
   - Click "Use template"

5. **Fill in project details**:
   - **Project type**: Team-managed
   - **Project name**: Copy from above (e.g., "Infotainment System - Android Automotive")
   - **Project key**: Enter the key from above (e.g., `IFS`)
   - Click "Create"

6. **Repeat for all 3 projects**

---

## ✅ Verification

After creating all projects, verify you can access them:

```bash
# Test if projects exist
curl -u adhivp04@example.com:YOUR_JIRA_API_TOKEN \
  https://adhivp04.atlassian.net/rest/api/3/project/IFS

curl -u adhivp04@example.com:YOUR_JIRA_API_TOKEN \
  https://adhivp04.atlassian.net/rest/api/3/project/ADAS

curl -u adhivp04@example.com:YOUR_JIRA_API_TOKEN \
  https://adhivp04.atlassian.net/rest/api/3/project/VD
```

If all three return project details (not 404), you're ready to run the script!

---

## 🚀 Run the Script

Once all 3 projects are created in Jira:

```bash
cd "/Users/adhivp/Desktop/Projects not deployed/AutoPM/fastapi_backend"
python3 generate_fake_data.py
```

The script will:
- ✅ Detect existing Jira projects (IFS, ADAS, VD)
- ✅ Create 40 issues per project (120 total)
- ✅ Add comments and transitions
- ✅ Link them to corresponding GitHub repositories

---

## 📊 Project Mapping

| GitHub Repository | Jira Project Key | Jira Project Name |
|------------------|------------------|-------------------|
| `infotainment-system-autopmtestproject` | IFS | Infotainment System |
| `adas-driver-assistance-autopmtestproject` | ADAS | ADAS Driver Assistance |
| `vehicle-diagnostics-autopmtestproject` | VD | Vehicle Diagnostics |

---

## 🎨 Optional: Customize Project Keys

If you want different project keys, edit `generate_fake_data.py` at line ~1168:

```python
project_key_map = {
    "infotainment-system": "IFS",        # Change "IFS" to your preferred key
    "adas-driver-assistance": "ADAS",    # Change "ADAS" to your preferred key
    "vehicle-diagnostics": "VD"          # Change "VD" to your preferred key
}
```

Then create projects in Jira with your custom keys!

---

## ⚡ Quick Summary

**Create these 3 projects in Jira with these exact keys:**

1. Project Key: `IFS` - Name: "Infotainment System - Android Automotive"
2. Project Key: `ADAS` - Name: "ADAS - Driver Assistance Systems"
3. Project Key: `VD` - Name: "Vehicle Diagnostics & Telemetry"

Then run: `python3 generate_fake_data.py` 🎉
