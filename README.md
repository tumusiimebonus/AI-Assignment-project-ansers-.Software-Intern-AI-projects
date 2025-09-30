# Medical Report Processing Frontend

This is a **React frontend application** for submitting and processing medical reports. It allows users to:

- Enter or paste medical reports in a textarea.
- Upload plain text (`.txt`) medical reports.
- Process reports to extract **Drug, Adverse Events, Severity, and Outcome** via a backend API.
- View a **history of previously processed reports**.
- Translate the **Outcome** field to French for both current and historical reports.

---

## **Features**

1. **Report Submission**
   - Textarea input or `.txt` file upload.
   - Validates input to prevent empty submissions.
   - Sends POST request to `/process-report` backend endpoint.

2. **Current Report Display**
   - Shows extracted Drug, Adverse Events, Severity, and Outcome.
   - Translate Outcome to French with a button click.

3. **Report History**
   - Fetches previous reports from `/reports` endpoint.
   - Translate Outcome for each historical report individually.

4. **User Experience**
   - Loading states during API calls.
   - Clean, readable UI with defaults for missing data.

---

## **Installation & Setup**

### **Prerequisites**
- Node.js (v16+ recommended)
- npm or yarn
- Backend server running with endpoints:
  - `POST /process-report`
  - `GET /reports`
  - `POST /translate`

### **Steps**

1. Clone the repository:

```bash
git clone <repository-url>
cd <project-folder>
