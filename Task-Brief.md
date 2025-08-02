# Take-Home Engineering Challenge: Smart Trash Collection System

**Role:** Generalist Engineer (Fresh Graduate)  
**Duration:** Approx. 2 Days  
**Keyword:** Trash

## 🧠 Overview

Design a **Smart Trash Collection System** web app that simulates managing trash bins in a city. This system should provide real-time bin status, collection routing suggestions, and general waste management visibility using mock data.

## 📌 Objectives

1. **System Architecture**
   - Outline components: bin data simulator, API backend, and management dashboard.
   - Include a short explanation or diagram showing how data flows between components.

2. **Frontend - Trash Bin Dashboard**
   - Build a React (or similar) app that:
     - Displays a list or map of bins with fill level indicators (e.g., 30%, 75%, full).
     - Allows filtering by location or fill status.
     - Highlights bins that require immediate collection.

3. **Backend - Trash Bin Simulation API**
   - Create an endpoint `/api/bins` that returns mock bin data.
   - Each bin should include: ID, location, current fill %, last emptied timestamp, and status (OK/Needs Collection).
   - Simulate fill levels changing every few minutes.

4. **Bonus (Optional)**
   - Add a basic collection route suggestion (e.g., sort bins by urgency).
   - Deploy the app and backend and provide a link.
   - Show simple analytics (e.g., average fill time, collection frequency).

## 🧪 Deliverables

- GitHub repo or downloadable zip with code.
- A `README.md` including:
  - Setup instructions.
  - Description of system components and logic.
  - Optional demo link or screenshots.
- Short reflection: how would this scale to thousands of smart bins?

## ✅ Evaluation Criteria

- Code organization and modularity.
- Effectiveness and simplicity of the dashboard.
- Simulation of changing bin conditions.
- Overall completeness and clarity of documentation.

---

**Tip:** Think of each bin like an IoT device. You don’t need hardware integrations—just focus on simulating data updates and designing a clear, extensible management interface.