# Requirements & Architecture Specification: SpendWise

## 1. Customer Statement of Requirements
**SpendWise** is a minimalist personal finance web application designed to help individuals **track their daily expenses** and **stick to a monthly budget**. The primary objective of the application is to offer a clean, simple, and clutter-free alternative to corporate finance apps that often confuse users with complex charts and mandatory bank account synchronizations. Specifically targeting college students, young professionals, and budgeting beginners, SpendWise enables users to instantly visualize their remaining balance, manually categorize transactions, and receive clear visual warnings when close to overspending, all through a responsive and secure interface.

---

## 2. Requirements Specification

### Functional Requirements (FR)
* **FR-1: User Authentication.** The system must allow users to securely register an account, log in, and log out.
* **FR-2: Budget Configuration.** The user must be able to input and modify their overall target budget for the current month.
* **FR-3: Expense Logging.** The system must provide an input form allowing users to manually enter an expense with an amount, a category (via a dropdown menu), and a date.
* **FR-4: Real-Time Dashboard.** The application must dynamically recalculate and display the "Total Budget" and "Remaining Balance" instantly after an expense is submitted.
* **FR-5: Transaction History.** The system must display a clean, chronological table listing the user's recent transactions.
* **FR-6: Overspending Alerts.** The system must automatically trigger a simple visual warning on the dashboard when the user's spending approaches or exceeds the preset budget threshold.

### Non-Functional Requirements (NFR)
* **NFR-1: Security.** User passwords must be heavily encrypted (e.g., using bcrypt) before being saved into the database.
* **NFR-2: Performance.** Expense insertion and dashboard updates must execute and render in under 2 seconds.
* **NFR-3: Usability & Accessibility (UI/UX).** The web interface must be clean, minimalist, and fully responsive across both desktop browsers and mobile devices.
* **NFR-4: Availability.** The web application should maintain high availability (24/7) to allow users to log their expenses immediately at the point of sale.

---

## 3. Data and Storage Blueprint

### Data Input
The application relies strictly on **manual data entry by the user** through the graphical user interface (UI).
* Users interact with HTML5/JavaScript forms to submit their profile credentials (registration/login) and transactional data.
* To preserve the tool's core simplicity and minimize scope creep, no external file ingestion (such as CSV uploads) or third-party banking APIs are implemented in this first iteration.

### Database or Storage
The application utilizes **MongoDB** as its primary storage engine, serving as a flexible, NoSQL document-oriented database.
* **Justification:** MongoDB integrates seamlessly with the **Node.js and Express** backend environment. Its JSON-like document structure (BSON) provides the agility needed to store user profiles and evolving transaction histories without rigid schema constraints.
* **Core Collections/Entities:**
  * *Users:* Unique ID, name, email address, encrypted password, and preset monthly budget amount.
  * *Expenses:* Unique ID, associated User ID (foreign reference), transaction amount, category (e.g., Food, Rent, Entertainment), and transaction date.
